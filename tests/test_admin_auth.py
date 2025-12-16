"""
Unit tests for Lattice Lock Admin API Authentication

Tests cover:
- JWT token generation and validation
- Token refresh and revocation
- API key generation and validation
- API key rotation and revocation
- Role-based access control
- OAuth2 password flow endpoints
"""

import os
from datetime import datetime, timedelta, timezone

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from lattice_lock.admin.auth import (
    AuthConfig,
    Role,
    TokenData,
    User,
    authenticate_user,
    clear_api_keys,
    clear_revoked_tokens,
    clear_users,
    configure,
    create_access_token,
    create_refresh_token,
    create_user,
    delete_user,
    generate_api_key,
    get_config,
    get_user,
    hash_password,
    is_token_revoked,
    list_api_keys,
    require_roles,
    revoke_api_key,
    revoke_token,
    rotate_api_key,
    verify_api_key,
    verify_password,
    verify_token,
)
from lattice_lock.admin.auth_routes import router as auth_router

# Test Secrets
TEST_SECRET_KEY = os.getenv("LATTICE_TEST_SECRET_KEY", "test-secret-key-that-is-at-least-32-chars")
TEST_PASSWORD = os.getenv("LATTICE_TEST_PASSWORD", "password123")
ADMIN_PASSWORD = os.getenv("LATTICE_TEST_ADMIN_PASSWORD", "adminpass123")
OPERATOR_PASSWORD = os.getenv("LATTICE_TEST_OPERATOR_PASSWORD", "operatorpass123")
CUSTOM_SECRET_KEY = os.getenv(
    "LATTICE_TEST_CUSTOM_SECRET_KEY", "custom-secret-key-that-is-at-least-32-chars"
)


@pytest.fixture(autouse=True)
def reset_auth_state():
    """Reset authentication state before each test."""
    clear_revoked_tokens()
    clear_api_keys()
    clear_users()
    configure(
        AuthConfig(
            secret_key=TEST_SECRET_KEY,
            access_token_expire_minutes=30,
            refresh_token_expire_days=7,
        )
    )
    yield
    clear_revoked_tokens()
    clear_api_keys()
    clear_users()


@pytest.fixture
def test_user() -> User:
    """Create a test user."""
    return create_user("testuser", TEST_PASSWORD, Role.VIEWER)


@pytest.fixture
def admin_user() -> User:
    """Create an admin test user."""
    return create_user("adminuser", ADMIN_PASSWORD, Role.ADMIN)


@pytest.fixture
def operator_user() -> User:
    """Create an operator test user."""
    return create_user("operatoruser", OPERATOR_PASSWORD, Role.OPERATOR)


@pytest.fixture
def app() -> FastAPI:
    """Create a test FastAPI application with auth routes."""
    app = FastAPI()
    app.include_router(auth_router, prefix="/api/v1")
    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """Create a test client."""
    return TestClient(app)


class TestAuthConfig:
    """Tests for AuthConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = get_config()
        assert config.algorithm == "HS256"
        assert config.access_token_expire_minutes == 30
        assert config.refresh_token_expire_days == 7
        assert config.api_key_prefix == "llk_"
        assert config.password_min_length == 8

    def test_custom_config(self):
        """Test custom configuration."""
        custom_config = AuthConfig(
            secret_key=CUSTOM_SECRET_KEY,
            access_token_expire_minutes=60,
            refresh_token_expire_days=14,
            api_key_prefix="custom_",
        )
        configure(custom_config)
        config = get_config()
        assert config.access_token_expire_minutes == 60
        assert config.refresh_token_expire_days == 14
        assert config.api_key_prefix == "custom_"

    def test_short_secret_key_raises(self):
        """Test that short secret key raises ValueError."""
        with pytest.raises(ValueError, match="at least 32 characters"):
            AuthConfig(secret_key="short")

    def test_invalid_token_expiry_raises(self):
        """Test that invalid token expiry raises ValueError."""
        with pytest.raises(ValueError, match="at least 1 minute"):
            AuthConfig(
                secret_key=TEST_SECRET_KEY,
                access_token_expire_minutes=0,
            )


class TestPasswordHashing:
    """Tests for password hashing."""

    def test_hash_password(self):
        """Test password hashing."""
        password = TEST_PASSWORD
        hashed = hash_password(password)
        assert hashed != password
        # Accept either argon2 or bcrypt hash prefixes
        assert hashed.startswith("$argon2") or hashed.startswith("$2b$")

    def test_verify_password_correct(self):
        """Test correct password verification."""
        password = TEST_PASSWORD
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test incorrect password verification."""
        password = TEST_PASSWORD
        hashed = hash_password(password)
        assert verify_password("wrongpassword", hashed) is False


class TestJWTTokens:
    """Tests for JWT token generation and validation."""

    def test_create_access_token(self, test_user: User):
        """Test access token creation."""
        token = create_access_token(test_user.username, test_user.role)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token(self, test_user: User):
        """Test refresh token creation."""
        token = create_refresh_token(test_user.username, test_user.role)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_access_token(self, test_user: User):
        """Test access token verification."""
        token = create_access_token(test_user.username, test_user.role)
        token_data = verify_token(token)
        assert token_data.sub == test_user.username
        assert token_data.role == test_user.role
        assert token_data.token_type == "access"

    def test_verify_refresh_token(self, test_user: User):
        """Test refresh token verification."""
        token = create_refresh_token(test_user.username, test_user.role)
        token_data = verify_token(token, expected_type="refresh")
        assert token_data.sub == test_user.username
        assert token_data.role == test_user.role
        assert token_data.token_type == "refresh"

    def test_access_token_as_refresh_fails(self, test_user: User):
        """Test that access token fails as refresh token."""
        token = create_access_token(test_user.username, test_user.role)
        with pytest.raises(HTTPException) as exc_info:
            verify_token(token, expected_type="refresh")
        assert exc_info.value.status_code == 401
        assert "Invalid token type" in exc_info.value.detail

    def test_invalid_token_fails(self):
        """Test that invalid token fails verification."""
        with pytest.raises(HTTPException) as exc_info:
            verify_token("invalid.token.here")
        assert exc_info.value.status_code == 401

    def test_token_with_custom_expiry(self, test_user: User):
        """Test token with custom expiry."""
        token = create_access_token(
            test_user.username,
            test_user.role,
            expires_delta=timedelta(hours=2),
        )
        token_data = verify_token(token)
        assert token_data.exp > datetime.now(timezone.utc) + timedelta(hours=1)


class TestTokenRevocation:
    """Tests for token revocation."""

    def test_revoke_token(self, test_user: User):
        """Test token revocation."""
        token = create_access_token(test_user.username, test_user.role)
        token_data = verify_token(token)

        assert is_token_revoked(token_data.jti) is False
        revoke_token(token_data.jti)
        assert is_token_revoked(token_data.jti) is True

    def test_revoked_token_fails_verification(self, test_user: User):
        """Test that revoked token fails verification."""
        token = create_access_token(test_user.username, test_user.role)
        token_data = verify_token(token)

        revoke_token(token_data.jti)

        with pytest.raises(HTTPException) as exc_info:
            verify_token(token)
        assert exc_info.value.status_code == 401
        assert "revoked" in exc_info.value.detail.lower()


class TestAPIKeys:
    """Tests for API key generation and validation."""

    def test_generate_api_key(self, test_user: User):
        """Test API key generation."""
        api_key, key_id = generate_api_key(
            test_user.username,
            test_user.role,
            name="test-key",
        )
        assert api_key.startswith("llk_")
        assert len(key_id) > 0

    def test_verify_api_key(self, test_user: User):
        """Test API key verification."""
        api_key, _ = generate_api_key(test_user.username, test_user.role)
        username, role = verify_api_key(api_key)
        assert username == test_user.username
        assert role == test_user.role

    def test_invalid_api_key_fails(self):
        """Test that invalid API key fails verification."""
        with pytest.raises(HTTPException) as exc_info:
            verify_api_key("llk_invalid_key")
        assert exc_info.value.status_code == 401

    def test_list_api_keys(self, test_user: User):
        """Test listing API keys."""
        generate_api_key(test_user.username, test_user.role, name="key1")
        generate_api_key(test_user.username, test_user.role, name="key2")

        keys = list_api_keys(test_user.username)
        assert len(keys) == 2
        assert any(k.name == "key1" for k in keys)
        assert any(k.name == "key2" for k in keys)

    def test_revoke_api_key(self, test_user: User):
        """Test API key revocation."""
        api_key, key_id = generate_api_key(test_user.username, test_user.role)

        # Key works before revocation
        verify_api_key(api_key)

        # Revoke the key
        assert revoke_api_key(key_id) is True

        # Key fails after revocation
        with pytest.raises(HTTPException):
            verify_api_key(api_key)

    def test_revoke_nonexistent_key(self):
        """Test revoking nonexistent key."""
        assert revoke_api_key("nonexistent") is False

    def test_rotate_api_key(self, test_user: User):
        """Test API key rotation."""
        old_key, old_id = generate_api_key(
            test_user.username,
            test_user.role,
            name="original",
        )

        result = rotate_api_key(old_id, name="rotated")
        assert result is not None
        new_key, new_id = result

        # Old key is revoked
        with pytest.raises(HTTPException):
            verify_api_key(old_key)

        # New key works
        username, role = verify_api_key(new_key)
        assert username == test_user.username

    def test_rotate_nonexistent_key(self):
        """Test rotating nonexistent key."""
        assert rotate_api_key("nonexistent") is None


class TestUserManagement:
    """Tests for user management."""

    def test_create_user(self):
        """Test user creation."""
        user = create_user("newuser", "password123", Role.VIEWER)
        assert user.username == "newuser"
        assert user.role == Role.VIEWER
        assert user.disabled is False

    def test_create_duplicate_user_fails(self, test_user: User):
        """Test that duplicate user creation fails."""
        with pytest.raises(ValueError, match="already exists"):
            create_user(test_user.username, "password123")

    def test_create_user_short_password_fails(self):
        """Test that short password fails."""
        with pytest.raises(ValueError, match="at least"):
            create_user("newuser", "short")

    def test_get_user(self, test_user: User):
        """Test getting user by username."""
        user = get_user(test_user.username)
        assert user is not None
        assert user.username == test_user.username

    def test_get_nonexistent_user(self):
        """Test getting nonexistent user."""
        user = get_user("nonexistent")
        assert user is None

    def test_authenticate_user_success(self, test_user: User):
        """Test successful user authentication."""
        user = authenticate_user(test_user.username, "password123")
        assert user is not None
        assert user.username == test_user.username

    def test_authenticate_user_wrong_password(self, test_user: User):
        """Test authentication with wrong password."""
        user = authenticate_user(test_user.username, "wrongpassword")
        assert user is None

    def test_authenticate_nonexistent_user(self):
        """Test authentication of nonexistent user."""
        user = authenticate_user("nonexistent", "password123")
        assert user is None

    def test_delete_user(self, test_user: User):
        """Test user deletion."""
        assert delete_user(test_user.username) is True
        assert get_user(test_user.username) is None

    def test_delete_nonexistent_user(self):
        """Test deleting nonexistent user."""
        assert delete_user("nonexistent") is False


class TestRoles:
    """Tests for role-based access control."""

    def test_admin_role_permissions(self):
        """Test admin role has all permissions."""
        perms = Role.ADMIN.permissions
        assert "read:projects" in perms
        assert "write:projects" in perms
        assert "write:rollback" in perms
        assert "manage:users" in perms
        assert "manage:api_keys" in perms

    def test_operator_role_permissions(self):
        """Test operator role permissions."""
        perms = Role.OPERATOR.permissions
        assert "read:projects" in perms
        assert "write:rollback" in perms
        assert "write:projects" not in perms
        assert "manage:users" not in perms

    def test_viewer_role_permissions(self):
        """Test viewer role permissions."""
        perms = Role.VIEWER.permissions
        assert "read:projects" in perms
        assert "read:health" in perms
        assert "write:rollback" not in perms
        assert "write:projects" not in perms


class TestAuthRoutes:
    """Tests for authentication routes."""

    def test_login_success(self, client: TestClient, test_user: User):
        """Test successful login."""
        response = client.post(
            "/api/v1/auth/token",
            data={"username": test_user.username, "password": TEST_PASSWORD},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client: TestClient, test_user: User):
        """Test login with wrong password."""
        response = client.post(
            "/api/v1/auth/token",
            data={"username": test_user.username, "password": "wrongpassword"},
        )
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client: TestClient):
        """Test login with nonexistent user."""
        response = client.post(
            "/api/v1/auth/token",
            data={"username": "nonexistent", "password": TEST_PASSWORD},
        )
        assert response.status_code == 401

    def test_refresh_token(self, client: TestClient, test_user: User):
        """Test token refresh."""
        # First login to get tokens
        login_response = client.post(
            "/api/v1/auth/token",
            data={"username": test_user.username, "password": TEST_PASSWORD},
        )
        refresh_token = login_response.json()["refresh_token"]

        # Use refresh token
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    def test_get_me_with_token(self, client: TestClient, test_user: User):
        """Test getting current user info with token."""
        login_response = client.post(
            "/api/v1/auth/token",
            data={"username": test_user.username, "password": TEST_PASSWORD},
        )
        access_token = login_response.json()["access_token"]

        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == test_user.username
        assert data["role"] == test_user.role.value

    def test_get_me_with_api_key(self, client: TestClient, test_user: User):
        """Test getting current user info with API key."""
        api_key, _ = generate_api_key(test_user.username, test_user.role)

        response = client.get(
            "/api/v1/auth/me",
            headers={"X-API-Key": api_key},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == test_user.username

    def test_get_me_unauthenticated(self, client: TestClient):
        """Test getting current user without authentication."""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401

    def test_create_api_key_admin_only(self, client: TestClient, admin_user: User, test_user: User):
        """Test that only admins can create API keys."""
        # Admin can create
        admin_token = create_access_token(admin_user.username, admin_user.role)
        response = client.post(
            "/api/v1/auth/api-keys",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"name": "test-key", "role": "viewer"},
        )
        assert response.status_code == 200

        # Viewer cannot create
        viewer_token = create_access_token(test_user.username, test_user.role)
        response = client.post(
            "/api/v1/auth/api-keys",
            headers={"Authorization": f"Bearer {viewer_token}"},
            json={"name": "test-key", "role": "viewer"},
        )
        assert response.status_code == 403

    def test_list_api_keys(self, client: TestClient, admin_user: User):
        """Test listing API keys."""
        admin_token = create_access_token(admin_user.username, admin_user.role)

        # Create some keys first
        client.post(
            "/api/v1/auth/api-keys",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"name": "key1"},
        )
        client.post(
            "/api/v1/auth/api-keys",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"name": "key2"},
        )

        # List keys
        response = client.get(
            "/api/v1/auth/api-keys",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        keys = response.json()
        assert len(keys) == 2

    def test_revoke_token_admin_only(self, client: TestClient, admin_user: User, test_user: User):
        """Test that only admins can revoke tokens."""
        admin_token = create_access_token(admin_user.username, admin_user.role)
        viewer_token = create_access_token(test_user.username, test_user.role)

        # Get JTI from viewer token
        viewer_data = verify_token(viewer_token)

        # Admin can revoke
        response = client.post(
            "/api/v1/auth/revoke",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"token_jti": viewer_data.jti},
        )
        assert response.status_code == 200

        # Viewer cannot revoke
        new_viewer_token = create_access_token(test_user.username, test_user.role)
        new_viewer_data = verify_token(new_viewer_token)
        response = client.post(
            "/api/v1/auth/revoke",
            headers={"Authorization": f"Bearer {new_viewer_token}"},
            json={"token_jti": new_viewer_data.jti},
        )
        assert response.status_code == 403


class TestRoleBasedAccess:
    """Tests for role-based access control dependencies."""

    @pytest.fixture
    def protected_app(self) -> FastAPI:
        """Create app with role-protected endpoints."""
        from typing import Annotated

        from fastapi import Depends

        app = FastAPI()
        app.include_router(auth_router, prefix="/api/v1")

        @app.get("/admin-only")
        async def admin_only(user: Annotated[TokenData, Depends(require_roles(Role.ADMIN))]):
            return {"message": "admin access granted", "user": user.sub}

        @app.get("/operator-access")
        async def operator_access(
            user: Annotated[TokenData, Depends(require_roles(Role.ADMIN, Role.OPERATOR))]
        ):
            return {"message": "operator access granted", "user": user.sub}

        @app.get("/viewer-access")
        async def viewer_access(
            user: Annotated[
                TokenData, Depends(require_roles(Role.ADMIN, Role.OPERATOR, Role.VIEWER))
            ]
        ):
            return {"message": "viewer access granted", "user": user.sub}

        return app

    @pytest.fixture
    def protected_client(self, protected_app: FastAPI) -> TestClient:
        """Create test client for protected app."""
        return TestClient(protected_app)

    def test_admin_can_access_admin_endpoint(self, protected_client: TestClient, admin_user: User):
        """Test admin can access admin-only endpoint."""
        token = create_access_token(admin_user.username, admin_user.role)
        response = protected_client.get(
            "/admin-only",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200

    def test_operator_cannot_access_admin_endpoint(
        self, protected_client: TestClient, operator_user: User
    ):
        """Test operator cannot access admin-only endpoint."""
        token = create_access_token(operator_user.username, operator_user.role)
        response = protected_client.get(
            "/admin-only",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403

    def test_viewer_cannot_access_admin_endpoint(
        self, protected_client: TestClient, test_user: User
    ):
        """Test viewer cannot access admin-only endpoint."""
        token = create_access_token(test_user.username, test_user.role)
        response = protected_client.get(
            "/admin-only",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403

    def test_operator_can_access_operator_endpoint(
        self, protected_client: TestClient, operator_user: User
    ):
        """Test operator can access operator endpoint."""
        token = create_access_token(operator_user.username, operator_user.role)
        response = protected_client.get(
            "/operator-access",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200

    def test_viewer_can_access_viewer_endpoint(self, protected_client: TestClient, test_user: User):
        """Test viewer can access viewer endpoint."""
        token = create_access_token(test_user.username, test_user.role)
        response = protected_client.get(
            "/viewer-access",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200

    def test_api_key_auth_works_for_protected_endpoints(
        self, protected_client: TestClient, admin_user: User
    ):
        """Test API key authentication works for protected endpoints."""
        api_key, _ = generate_api_key(admin_user.username, admin_user.role)
        response = protected_client.get(
            "/admin-only",
            headers={"X-API-Key": api_key},
        )
        assert response.status_code == 200
