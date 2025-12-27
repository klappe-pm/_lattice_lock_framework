"""
Tests for the Lattice Lock Admin API (Async).

Tests all REST endpoints for project management and monitoring using
fully async test clients and in-memory SQLite database.
"""

import time
import uuid
from collections.abc import AsyncGenerator
from datetime import datetime, timezone

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from lattice_lock.admin import API_VERSION, ProjectStatus, ValidationStatus, create_app
from lattice_lock.admin.auth import Role, TokenData, get_current_user
from lattice_lock.admin.db import Base, get_db
from lattice_lock.admin.models import Project, ProjectError, RollbackCheckpoint
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

# --- Fixtures ---


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh in-memory database session for each test."""
    # Create async engine with in-memory SQLite
    # check_same_thread=False is needed for sqlite in async contexts
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with session_maker() as session:
        yield session

    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client with database override."""
    app = create_app(debug=True)

    # Override the database dependency
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    # Mock authentication to allow all requests by default
    async def mock_get_current_user() -> TokenData:
        return TokenData(
            sub="test_admin",
            role=Role.ADMIN,
            exp=datetime.now(timezone.utc),
            iat=datetime.now(timezone.utc),
            jti=str(uuid.uuid4()),
        )

    app.dependency_overrides[get_current_user] = mock_get_current_user

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest_asyncio.fixture
async def sample_project(db_session: AsyncSession) -> Project:
    """Create a sample project in the database."""
    project = Project(
        id=f"proj_{uuid.uuid4().hex[:8]}",
        name="Test Project",
        path="/path/to/test-project",
        metadata_json={"version": "1.0.0"},
        status=ProjectStatus.UNKNOWN,
        registered_at=time.time(),
        last_activity=time.time(),
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    return project


# --- Tests ---


@pytest.mark.asyncio
class TestHealthEndpoint:
    """Tests for GET /api/v1/health."""

    async def test_health_check_returns_200(self, client: AsyncClient) -> None:
        """Test that health check returns 200 OK."""
        response = await client.get("/api/v1/health")
        assert response.status_code == 200

    async def test_health_check_response_structure(self, client: AsyncClient) -> None:
        """Test that health check returns expected structure."""
        response = await client.get("/api/v1/health")
        data = response.json()

        assert data["status"] == "healthy"
        assert data["version"] == API_VERSION
        assert "timestamp" in data
        assert "projects_count" in data
        assert "uptime_seconds" in data

    async def test_health_check_projects_count(
        self, client: AsyncClient, sample_project: Project
    ) -> None:
        """Test that health check returns correct project count."""
        response = await client.get("/api/v1/health")
        data = response.json()
        assert data["projects_count"] == 1


@pytest.mark.asyncio
class TestProjectsListEndpoint:
    """Tests for GET /api/v1/projects."""

    async def test_list_projects_empty(self, client: AsyncClient) -> None:
        """Test listing projects when none exist."""
        # We need a clean DB for this test, so we can't use sample_project fixture usage implicitly
        # But fixtures are per test, so if we don't request sample_project, DB is empty
        response = await client.get("/api/v1/projects")
        assert response.status_code == 200

        data = response.json()
        assert data["projects"] == []
        assert data["total"] == 0

    async def test_list_projects_with_projects(
        self, client: AsyncClient, sample_project: Project
    ) -> None:
        """Test listing projects when projects exist."""
        response = await client.get("/api/v1/projects")
        assert response.status_code == 200

        data = response.json()
        assert data["total"] == 1
        assert len(data["projects"]) == 1

        project = data["projects"][0]
        assert project["id"] == sample_project.id
        assert project["name"] == "Test Project"
        assert project["path"] == "/path/to/test-project"


@pytest.mark.asyncio
class TestRegisterProjectEndpoint:
    """Tests for POST /api/v1/projects."""

    async def test_register_project_success(self, client: AsyncClient) -> None:
        """Test successful project registration."""
        response = await client.post(
            "/api/v1/projects",
            json={
                "name": "New Project",
                "path": "/path/to/new-project",
            },
        )
        assert response.status_code == 201

        data = response.json()
        assert "id" in data
        assert data["name"] == "New Project"
        assert data["path"] == "/path/to/new-project"

    async def test_register_project_missing_path(self, client: AsyncClient) -> None:
        """Test project registration with missing path."""
        response = await client.post(
            "/api/v1/projects",
            json={"name": "Project"},
        )
        assert response.status_code == 422


@pytest.mark.asyncio
class TestProjectStatusEndpoint:
    """Tests for GET /api/v1/projects/{id}/status."""

    async def test_get_status_success(self, client: AsyncClient, sample_project: Project) -> None:
        """Test getting project status."""
        response = await client.get(f"/api/v1/projects/{sample_project.id}/status")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == sample_project.id
        assert data["name"] == "Test Project"

    async def test_get_status_not_found(self, client: AsyncClient) -> None:
        """Test getting status for non-existent project."""
        response = await client.get("/api/v1/projects/non_existent/status")
        assert response.status_code == 404


@pytest.mark.asyncio
class TestProjectErrorsEndpoint:
    """Tests for GET /api/v1/projects/{id}/errors."""

    async def test_get_errors_with_errors(
        self, client: AsyncClient, sample_project: Project, db_session: AsyncSession
    ) -> None:
        """Test getting errors when errors exist."""
        # Manually verify recording error via service or direct DB insertion
        error = ProjectError(
            id=f"err_{uuid.uuid4().hex[:8]}",
            project_id=sample_project.id,
            error_code="LL-100",
            message="Schema validation failed",
            severity="high",
            category="validation",
            timestamp=time.time(),
        )
        db_session.add(error)
        await db_session.commit()

        response = await client.get(f"/api/v1/projects/{sample_project.id}/errors")
        data = response.json()

        assert data["total"] == 1
        assert len(data["errors"]) == 1
        assert data["errors"][0]["error_code"] == "LL-100"


@pytest.mark.asyncio
class TestRollbackEndpoint:
    """Tests for POST /api/v1/projects/{id}/rollback."""

    async def test_rollback_dry_run(self, client: AsyncClient, sample_project: Project) -> None:
        """Test rollback dry run."""
        response = await client.post(
            f"/api/v1/projects/{sample_project.id}/rollback",
            json={"dry_run": True, "reason": "Testing rollback"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["dry_run"] is True


@pytest.mark.asyncio
class TestHelperServices:
    """
    Tests for internal service helper functions.
    This replaces the 'TestHelperFunctions' from the old sync test.
    """

    async def test_add_rollback_checkpoint_service(
        self, db_session: AsyncSession, sample_project: Project
    ):
        """Test add_rollback_checkpoint service function."""
        from lattice_lock.admin.services import add_rollback_checkpoint

        result = await add_rollback_checkpoint(
            db_session, sample_project.id, description="Test Checkpoint", files_count=5
        )

        assert result is True

        # Verify in DB
        result = await db_session.execute(
            select(RollbackCheckpoint).where(RollbackCheckpoint.project_id == sample_project.id)
        )
        assert len(result.scalars().all()) == 1

    async def test_update_validation_status_service(
        self, db_session: AsyncSession, sample_project: Project
    ):
        """Test update_validation_status service function."""
        from lattice_lock.admin.services import update_validation_status

        result = await update_validation_status(
            db_session, sample_project.id, schema_status="passed", sheriff_status="failed"
        )

        assert result is True
        await db_session.refresh(sample_project)

        assert sample_project.schema_status == ValidationStatus.PASSED
        assert sample_project.sheriff_status == ValidationStatus.FAILED
        assert (
            sample_project.status == ProjectStatus.ERROR
        )  # Failed validation should trigger error status
