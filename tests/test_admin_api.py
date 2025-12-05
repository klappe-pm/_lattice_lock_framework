"""
Tests for the Lattice Lock Admin API.

Tests all REST endpoints for project management and monitoring.
"""

import time
import pytest
from unittest.mock import patch

from fastapi.testclient import TestClient

from lattice_lock.admin import (
    create_app,
    get_project_store,
    reset_project_store,
    Project,
    ProjectError,
    ProjectStatus,
    ValidationStatus,
    RollbackInfo,
    record_project_error,
    add_rollback_checkpoint,
    update_validation_status,
    API_VERSION,
)


@pytest.fixture
def client() -> TestClient:
    """Create a test client with a fresh project store."""
    reset_project_store()
    app = create_app(debug=True)
    return TestClient(app)


@pytest.fixture
def sample_project() -> Project:
    """Create and register a sample project."""
    reset_project_store()
    store = get_project_store()
    return store.register_project(
        name="Test Project",
        path="/path/to/test-project",
        metadata={"version": "1.0.0"},
    )


class TestHealthEndpoint:
    """Tests for GET /api/v1/health."""

    def test_health_check_returns_200(self, client: TestClient) -> None:
        """Test that health check returns 200 OK."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200

    def test_health_check_response_structure(self, client: TestClient) -> None:
        """Test that health check returns expected structure."""
        response = client.get("/api/v1/health")
        data = response.json()

        assert data["status"] == "healthy"
        assert data["version"] == API_VERSION
        assert "timestamp" in data
        assert "projects_count" in data
        assert "uptime_seconds" in data

    def test_health_check_projects_count(
        self, client: TestClient, sample_project: Project
    ) -> None:
        """Test that health check returns correct project count."""
        response = client.get("/api/v1/health")
        data = response.json()

        assert data["projects_count"] == 1


class TestProjectsListEndpoint:
    """Tests for GET /api/v1/projects."""

    def test_list_projects_empty(self, client: TestClient) -> None:
        """Test listing projects when none exist."""
        response = client.get("/api/v1/projects")
        assert response.status_code == 200

        data = response.json()
        assert data["projects"] == []
        assert data["total"] == 0

    def test_list_projects_with_projects(
        self, client: TestClient, sample_project: Project
    ) -> None:
        """Test listing projects when projects exist."""
        response = client.get("/api/v1/projects")
        assert response.status_code == 200

        data = response.json()
        assert data["total"] == 1
        assert len(data["projects"]) == 1

        project = data["projects"][0]
        assert project["id"] == sample_project.id
        assert project["name"] == "Test Project"
        assert project["path"] == "/path/to/test-project"

    def test_list_projects_multiple(self, client: TestClient) -> None:
        """Test listing multiple projects."""
        store = get_project_store()
        store.register_project(name="Project 1", path="/path/1")
        store.register_project(name="Project 2", path="/path/2")
        store.register_project(name="Project 3", path="/path/3")

        response = client.get("/api/v1/projects")
        data = response.json()

        assert data["total"] == 3
        assert len(data["projects"]) == 3


class TestRegisterProjectEndpoint:
    """Tests for POST /api/v1/projects."""

    def test_register_project_success(self, client: TestClient) -> None:
        """Test successful project registration."""
        response = client.post(
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
        assert data["status"] == "unknown"
        assert "message" in data

    def test_register_project_with_metadata(self, client: TestClient) -> None:
        """Test project registration with metadata."""
        response = client.post(
            "/api/v1/projects",
            json={
                "name": "Project with Metadata",
                "path": "/path/to/project",
                "metadata": {"key": "value", "number": 42},
            },
        )
        assert response.status_code == 201

    def test_register_project_missing_name(self, client: TestClient) -> None:
        """Test project registration with missing name."""
        response = client.post(
            "/api/v1/projects",
            json={"path": "/path/to/project"},
        )
        assert response.status_code == 422

    def test_register_project_missing_path(self, client: TestClient) -> None:
        """Test project registration with missing path."""
        response = client.post(
            "/api/v1/projects",
            json={"name": "Project"},
        )
        assert response.status_code == 422


class TestProjectStatusEndpoint:
    """Tests for GET /api/v1/projects/{id}/status."""

    def test_get_status_success(
        self, client: TestClient, sample_project: Project
    ) -> None:
        """Test getting project status."""
        response = client.get(f"/api/v1/projects/{sample_project.id}/status")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == sample_project.id
        assert data["name"] == "Test Project"
        assert data["status"] == "unknown"
        assert "validation" in data
        assert "error_count" in data
        assert "rollback_checkpoints_count" in data

    def test_get_status_not_found(self, client: TestClient) -> None:
        """Test getting status for non-existent project."""
        response = client.get("/api/v1/projects/non_existent/status")
        assert response.status_code == 404

    def test_get_status_with_validation(
        self, client: TestClient, sample_project: Project
    ) -> None:
        """Test getting status with validation data."""
        update_validation_status(
            sample_project.id,
            schema_status="passed",
            sheriff_status="passed",
            gauntlet_status="failed",
            validation_errors=["Test assertion failed"],
        )

        response = client.get(f"/api/v1/projects/{sample_project.id}/status")
        data = response.json()

        assert data["validation"]["schema_status"] == "passed"
        assert data["validation"]["sheriff_status"] == "passed"
        assert data["validation"]["gauntlet_status"] == "failed"
        assert "Test assertion failed" in data["validation"]["validation_errors"]


class TestProjectErrorsEndpoint:
    """Tests for GET /api/v1/projects/{id}/errors."""

    def test_get_errors_empty(
        self, client: TestClient, sample_project: Project
    ) -> None:
        """Test getting errors when none exist."""
        response = client.get(f"/api/v1/projects/{sample_project.id}/errors")
        assert response.status_code == 200

        data = response.json()
        assert data["project_id"] == sample_project.id
        assert data["errors"] == []
        assert data["total"] == 0

    def test_get_errors_with_errors(
        self, client: TestClient, sample_project: Project
    ) -> None:
        """Test getting errors when errors exist."""
        record_project_error(
            sample_project.id,
            error_code="LL-100",
            message="Schema validation failed",
            severity="high",
            category="validation",
        )

        response = client.get(f"/api/v1/projects/{sample_project.id}/errors")
        data = response.json()

        assert data["total"] == 1
        assert len(data["errors"]) == 1
        assert data["errors"][0]["error_code"] == "LL-100"
        assert data["errors"][0]["severity"] == "high"

    def test_get_errors_not_found(self, client: TestClient) -> None:
        """Test getting errors for non-existent project."""
        response = client.get("/api/v1/projects/non_existent/errors")
        assert response.status_code == 404

    def test_get_errors_exclude_resolved(
        self, client: TestClient, sample_project: Project
    ) -> None:
        """Test that resolved errors are excluded by default."""
        store = get_project_store()

        # Add two errors
        error1 = ProjectError(
            id="err_001",
            error_code="LL-100",
            message="Error 1",
            severity="high",
            category="validation",
            timestamp=time.time(),
        )
        error2 = ProjectError(
            id="err_002",
            error_code="LL-200",
            message="Error 2",
            severity="medium",
            category="validation",
            timestamp=time.time(),
            resolved=True,
            resolved_at=time.time(),
        )

        project = store.get_project(sample_project.id)
        project.errors.extend([error1, error2])

        response = client.get(f"/api/v1/projects/{sample_project.id}/errors")
        data = response.json()

        # Only unresolved error should be returned
        assert data["total"] == 1
        assert data["errors"][0]["id"] == "err_001"

    def test_get_errors_include_resolved(
        self, client: TestClient, sample_project: Project
    ) -> None:
        """Test including resolved errors."""
        store = get_project_store()

        error = ProjectError(
            id="err_001",
            error_code="LL-100",
            message="Resolved error",
            severity="high",
            category="validation",
            timestamp=time.time(),
            resolved=True,
            resolved_at=time.time(),
        )

        project = store.get_project(sample_project.id)
        project.errors.append(error)

        response = client.get(
            f"/api/v1/projects/{sample_project.id}/errors?include_resolved=true"
        )
        data = response.json()

        assert data["total"] == 1
        assert data["errors"][0]["resolved"] is True

    def test_get_errors_limit(
        self, client: TestClient, sample_project: Project
    ) -> None:
        """Test error limit parameter."""
        # Add multiple errors
        for i in range(5):
            record_project_error(
                sample_project.id,
                error_code=f"LL-{100 + i}",
                message=f"Error {i}",
                severity="medium",
                category="validation",
            )

        response = client.get(
            f"/api/v1/projects/{sample_project.id}/errors?limit=3"
        )
        data = response.json()

        assert data["total"] == 3
        assert data["has_more"] is True


class TestRollbackEndpoint:
    """Tests for POST /api/v1/projects/{id}/rollback."""

    def test_rollback_no_checkpoints(
        self, client: TestClient, sample_project: Project
    ) -> None:
        """Test rollback when no checkpoints exist."""
        response = client.post(
            f"/api/v1/projects/{sample_project.id}/rollback",
            json={},
        )
        assert response.status_code == 400

    def test_rollback_project_not_found(self, client: TestClient) -> None:
        """Test rollback for non-existent project."""
        response = client.post(
            "/api/v1/projects/non_existent/rollback",
            json={},
        )
        assert response.status_code == 404

    def test_rollback_dry_run(
        self, client: TestClient, sample_project: Project
    ) -> None:
        """Test rollback dry run."""
        add_rollback_checkpoint(
            sample_project.id,
            description="Before changes",
            files_count=10,
        )

        response = client.post(
            f"/api/v1/projects/{sample_project.id}/rollback",
            json={"dry_run": True, "reason": "Testing rollback"},
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["dry_run"] is True
        assert data["files_restored"] == 10

    def test_rollback_to_specific_checkpoint(
        self, client: TestClient, sample_project: Project
    ) -> None:
        """Test rollback to a specific checkpoint."""
        # Add two checkpoints
        add_rollback_checkpoint(sample_project.id, "First checkpoint", 5)
        add_rollback_checkpoint(sample_project.id, "Second checkpoint", 10)

        store = get_project_store()
        project = store.get_project(sample_project.id)
        first_checkpoint_id = project.rollback_checkpoints[0].checkpoint_id

        response = client.post(
            f"/api/v1/projects/{sample_project.id}/rollback",
            json={"checkpoint_id": first_checkpoint_id},
        )
        assert response.status_code == 200

        data = response.json()
        assert data["checkpoint_id"] == first_checkpoint_id
        assert data["files_restored"] == 5

    def test_rollback_checkpoint_not_found(
        self, client: TestClient, sample_project: Project
    ) -> None:
        """Test rollback to non-existent checkpoint."""
        add_rollback_checkpoint(sample_project.id, "Checkpoint", 5)

        response = client.post(
            f"/api/v1/projects/{sample_project.id}/rollback",
            json={"checkpoint_id": "non_existent_checkpoint"},
        )
        assert response.status_code == 404

    def test_rollback_to_latest_checkpoint(
        self, client: TestClient, sample_project: Project
    ) -> None:
        """Test rollback to most recent checkpoint when no ID specified."""
        add_rollback_checkpoint(sample_project.id, "First checkpoint", 5)
        time.sleep(0.01)  # Ensure different timestamps
        add_rollback_checkpoint(sample_project.id, "Second checkpoint", 10)

        response = client.post(
            f"/api/v1/projects/{sample_project.id}/rollback",
            json={},
        )
        assert response.status_code == 200

        data = response.json()
        # Should rollback to the most recent checkpoint (10 files)
        assert data["files_restored"] == 10


class TestRollbackCheckpointsEndpoint:
    """Tests for GET /api/v1/projects/{id}/rollback/checkpoints."""

    def test_list_checkpoints_empty(
        self, client: TestClient, sample_project: Project
    ) -> None:
        """Test listing checkpoints when none exist."""
        response = client.get(
            f"/api/v1/projects/{sample_project.id}/rollback/checkpoints"
        )
        assert response.status_code == 200
        assert response.json() == []

    def test_list_checkpoints(
        self, client: TestClient, sample_project: Project
    ) -> None:
        """Test listing checkpoints."""
        add_rollback_checkpoint(sample_project.id, "First checkpoint", 5)
        add_rollback_checkpoint(sample_project.id, "Second checkpoint", 10)

        response = client.get(
            f"/api/v1/projects/{sample_project.id}/rollback/checkpoints"
        )
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 2

        # Should be sorted by timestamp (most recent first)
        assert data[0]["description"] == "Second checkpoint"
        assert data[1]["description"] == "First checkpoint"

    def test_list_checkpoints_not_found(self, client: TestClient) -> None:
        """Test listing checkpoints for non-existent project."""
        response = client.get(
            "/api/v1/projects/non_existent/rollback/checkpoints"
        )
        assert response.status_code == 404


class TestRootEndpoint:
    """Tests for GET /."""

    def test_root_endpoint(self, client: TestClient) -> None:
        """Test root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "Lattice Lock Admin API"
        assert data["version"] == API_VERSION
        assert "docs" in data


class TestErrorHandling:
    """Tests for API error handling."""

    def test_validation_error_response(self, client: TestClient) -> None:
        """Test validation error response format."""
        response = client.post(
            "/api/v1/projects",
            json={"invalid": "data"},
        )
        assert response.status_code == 422

        data = response.json()
        assert data["error"] == "ValidationError"
        assert "details" in data

    def test_not_found_error_response(self, client: TestClient) -> None:
        """Test not found error response format."""
        response = client.get("/api/v1/projects/non_existent/status")
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_record_project_error(self, sample_project: Project) -> None:
        """Test recording an error for a project."""
        result = record_project_error(
            sample_project.id,
            error_code="LL-100",
            message="Test error",
            severity="high",
            category="validation",
            details={"file": "test.py"},
        )
        assert result is True

        store = get_project_store()
        project = store.get_project(sample_project.id)
        assert len(project.errors) == 1
        assert project.errors[0].error_code == "LL-100"

    def test_record_project_error_not_found(self) -> None:
        """Test recording error for non-existent project."""
        reset_project_store()
        result = record_project_error(
            "non_existent",
            error_code="LL-100",
            message="Test error",
            severity="high",
            category="validation",
        )
        assert result is False

    def test_add_rollback_checkpoint(self, sample_project: Project) -> None:
        """Test adding a rollback checkpoint."""
        result = add_rollback_checkpoint(
            sample_project.id,
            description="Before changes",
            files_count=10,
        )
        assert result is True

        store = get_project_store()
        project = store.get_project(sample_project.id)
        assert len(project.rollback_checkpoints) == 1
        assert project.rollback_checkpoints[0].description == "Before changes"

    def test_add_rollback_checkpoint_not_found(self) -> None:
        """Test adding checkpoint for non-existent project."""
        reset_project_store()
        result = add_rollback_checkpoint(
            "non_existent",
            description="Test",
            files_count=5,
        )
        assert result is False

    def test_update_validation_status(self, sample_project: Project) -> None:
        """Test updating validation status."""
        result = update_validation_status(
            sample_project.id,
            schema_status="passed",
            sheriff_status="failed",
            validation_errors=["Import error"],
        )
        assert result is True

        store = get_project_store()
        project = store.get_project(sample_project.id)
        assert project.validation.schema_status == ValidationStatus.PASSED
        assert project.validation.sheriff_status == ValidationStatus.FAILED
        assert "Import error" in project.validation.validation_errors

    def test_update_validation_status_not_found(self) -> None:
        """Test updating status for non-existent project."""
        reset_project_store()
        result = update_validation_status(
            "non_existent",
            schema_status="passed",
        )
        assert result is False


class TestProjectStatusUpdates:
    """Tests for automatic project status updates."""

    def test_status_healthy_after_passing_validation(
        self, sample_project: Project
    ) -> None:
        """Test project status becomes healthy after passing validation."""
        update_validation_status(
            sample_project.id,
            schema_status="passed",
            sheriff_status="passed",
            gauntlet_status="passed",
        )

        store = get_project_store()
        project = store.get_project(sample_project.id)
        assert project.status == ProjectStatus.HEALTHY

    def test_status_error_on_schema_failure(self, sample_project: Project) -> None:
        """Test project status becomes error on schema validation failure."""
        update_validation_status(
            sample_project.id,
            schema_status="failed",
        )

        store = get_project_store()
        project = store.get_project(sample_project.id)
        assert project.status == ProjectStatus.ERROR

    def test_status_warning_on_gauntlet_failure(
        self, sample_project: Project
    ) -> None:
        """Test project status becomes warning on gauntlet failure only."""
        update_validation_status(
            sample_project.id,
            schema_status="passed",
            sheriff_status="passed",
            gauntlet_status="failed",
        )

        store = get_project_store()
        project = store.get_project(sample_project.id)
        assert project.status == ProjectStatus.WARNING

    def test_status_error_on_critical_error(self, sample_project: Project) -> None:
        """Test project status becomes error on critical error."""
        record_project_error(
            sample_project.id,
            error_code="LL-100",
            message="Critical error",
            severity="critical",
            category="validation",
        )

        store = get_project_store()
        project = store.get_project(sample_project.id)
        assert project.status == ProjectStatus.ERROR

    def test_status_warning_on_low_severity_error(
        self, sample_project: Project
    ) -> None:
        """Test project status becomes warning on low severity error."""
        record_project_error(
            sample_project.id,
            error_code="LL-100",
            message="Minor issue",
            severity="low",
            category="validation",
        )

        store = get_project_store()
        project = store.get_project(sample_project.id)
        assert project.status == ProjectStatus.WARNING


class TestProjectStore:
    """Tests for ProjectStore class."""

    def test_generate_unique_ids(self) -> None:
        """Test that generated IDs are unique."""
        reset_project_store()
        store = get_project_store()

        ids = set()
        for i in range(100):
            project = store.register_project(
                name=f"Project {i}",
                path=f"/path/{i}",
            )
            ids.add(project.id)

        assert len(ids) == 100

    def test_thread_safety(self) -> None:
        """Test thread-safe operations."""
        import threading

        reset_project_store()
        store = get_project_store()
        errors = []

        def register_projects():
            try:
                for i in range(10):
                    store.register_project(
                        name=f"Project {threading.current_thread().name}-{i}",
                        path=f"/path/{threading.current_thread().name}/{i}",
                    )
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=register_projects) for _ in range(5)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(store.list_projects()) == 50

    def test_delete_project(self) -> None:
        """Test deleting a project."""
        reset_project_store()
        store = get_project_store()

        project = store.register_project(name="Test", path="/test")
        assert store.get_project(project.id) is not None

        result = store.delete_project(project.id)
        assert result is True
        assert store.get_project(project.id) is None

    def test_delete_nonexistent_project(self) -> None:
        """Test deleting non-existent project."""
        reset_project_store()
        store = get_project_store()

        result = store.delete_project("non_existent")
        assert result is False

    def test_clear_store(self) -> None:
        """Test clearing the store."""
        reset_project_store()
        store = get_project_store()

        store.register_project(name="Test 1", path="/test1")
        store.register_project(name="Test 2", path="/test2")

        assert len(store.list_projects()) == 2

        store.clear()

        assert len(store.list_projects()) == 0
