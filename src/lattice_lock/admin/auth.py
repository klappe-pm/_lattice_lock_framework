"""
Lattice Lock Admin API Authentication

Provides JWT and API key authentication for the Admin API with role-based
access control. Supports OAuth2 password flow and bearer token authentication.

Security Notes:
    - Tokens and keys are never logged
    - All sensitive data is redacted in error messages
    - Token revocation is tracked in memory (use Redis/DB for production)
"""

import logging
import os
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Annotated

import bcrypt
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel, Field

logger = logging.getLogger("lattice_lock.admin.auth")


class Role(str, Enum):
    """User roles for role-based access control.

    Roles define what actions a user can perform:
        - admin: Full access to all endpoints and operations
        - operator: Can view data and trigger rollbacks
        - viewer: Read-only access to project status and errors
    """

    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"

    @property
    def permissions(self) -> set[str]:
        """Get permissions associated with this role."""
        base_permissions = {"read:health", "read:projects", "read:errors"}

        if self == Role.ADMIN:
            return base_permissions | {
                "write:projects",
                "write:rollback",
                "write:config",
                "manage:users",
                "manage:api_keys",
            }
        elif self == Role.OPERATOR:
            return base_permissions | {"write:rollback"}
        else:  # VIEWER
            return base_permissions


@dataclass
class AuthConfig:
    """Configuration for authentication settings.

    Attributes:
        secret_key: Secret key for JWT signing (required)
        algorithm: JWT algorithm to use (default: HS256)
        access_token_expire_minutes: Access token validity period
        refresh_token_expire_days: Refresh token validity period
        api_key_prefix: Prefix for API keys (for identification)
        password_min_length: Minimum password length
    """

    secret_key: str = field(
        default_factory=lambda: os.environ.get("LATTICE_LOCK_SECRET_KEY", secrets.token_urlsafe(32))
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    api_key_prefix: str = "llk_"
    password_min_length: int = 8

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if len(self.secret_key) < 32:
            raise ValueError("Secret key must be at least 32 characters")
        if self.access_token_expire_minutes < 1:
            raise ValueError("Access token expiry must be at least 1 minute")
        if self.refresh_token_expire_days < 1:
            raise ValueError("Refresh token expiry must be at least 1 day")


# Global configuration - can be overridden via configure()
_config: AuthConfig | None = None


def get_config() -> AuthConfig:
    """Get the current authentication configuration."""
    global _config
    if _config is None:
        _config = AuthConfig()
    return _config


def configure(config: AuthConfig) -> None:
    """Set the authentication configuration.

    Args:
        config: New authentication configuration to use
    """
    global _config
    _config = config


# Bcrypt configuration
# Using bcrypt directly instead of passlib for compatibility with bcrypt 4.x/5.x
# which strictly enforces the 72-byte password limit
_BCRYPT_ROUNDS = 12  # Cost factor for bcrypt hashing


class TokenData(BaseModel):
    """Data contained in a JWT token.

    Attributes:
        sub: Subject (username or user ID)
        role: User's role
        exp: Expiration timestamp
        iat: Issued at timestamp
        jti: JWT ID (for revocation tracking)
        token_type: Type of token (access or refresh)
    """

    sub: str
    role: Role
    exp: datetime
    iat: datetime
    jti: str = Field(default_factory=lambda: secrets.token_urlsafe(16))
    token_type: str = "access"


class User(BaseModel):
    """User model for authentication.

    Attributes:
        username: Unique username
        hashed_password: Bcrypt-hashed password
        role: User's role
        disabled: Whether the user is disabled
        api_keys: List of API key hashes (not the actual keys)
    """

    username: str
    hashed_password: str
    role: Role = Role.VIEWER
    disabled: bool = False
    api_keys: list[str] = Field(default_factory=list)


class TokenResponse(BaseModel):
    """Response model for token endpoints.

    Attributes:
        access_token: JWT access token
        refresh_token: JWT refresh token (optional)
        token_type: Token type (always "bearer")
        expires_in: Seconds until access token expires
    """

    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
    expires_in: int


class APIKeyInfo(BaseModel):
    """Information about an API key.

    Attributes:
        key_id: Unique identifier for the key
        created_at: When the key was created
        last_used: When the key was last used (optional)
        name: Human-readable name for the key
    """

    key_id: str
    created_at: datetime
    last_used: datetime | None = None
    name: str = ""


# OAuth2 scheme for bearer token authentication
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/token",
    auto_error=False,
)

# API key header scheme
api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False,
)


# In-memory storage for revoked tokens and API keys
# In production, use Redis or a database
_revoked_tokens: set[str] = set()
_api_keys: dict[str, tuple[str, Role, str]] = {}  # hash -> (user, role, key_id)
_api_key_metadata: dict[str, APIKeyInfo] = {}  # key_id -> metadata


def hash_password(password: str) -> str:
    """Hash a password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Bcrypt hash of the password
    """
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=_BCRYPT_ROUNDS)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Bcrypt hash to verify against

    Returns:
        True if password matches, False otherwise
    """
    try:
        password_bytes = plain_password.encode("utf-8")
        hashed_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except (ValueError, TypeError):
        return False


def create_access_token(
    username: str,
    role: Role,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a JWT access token.

    Args:
        username: User's username
        role: User's role
        expires_delta: Custom expiration time (optional)

    Returns:
        Encoded JWT access token
    """
    config = get_config()

    if expires_delta is None:
        expires_delta = timedelta(minutes=config.access_token_expire_minutes)

    now = datetime.now(timezone.utc)
    expire = now + expires_delta
    jti = secrets.token_urlsafe(16)

    # JWT claims must use Unix timestamps for exp and iat
    payload = {
        "sub": username,
        "role": role.value,
        "exp": int(expire.timestamp()),
        "iat": int(now.timestamp()),
        "jti": jti,
        "token_type": "access",
    }

    return jwt.encode(
        payload,
        config.secret_key,
        algorithm=config.algorithm,
    )


def create_refresh_token(
    username: str,
    role: Role,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a JWT refresh token.

    Refresh tokens have longer validity and can be used to obtain
    new access tokens without re-authentication.

    Args:
        username: User's username
        role: User's role
        expires_delta: Custom expiration time (optional)

    Returns:
        Encoded JWT refresh token
    """
    config = get_config()

    if expires_delta is None:
        expires_delta = timedelta(days=config.refresh_token_expire_days)

    now = datetime.now(timezone.utc)
    expire = now + expires_delta
    jti = secrets.token_urlsafe(16)

    # JWT claims must use Unix timestamps for exp and iat
    payload = {
        "sub": username,
        "role": role.value,
        "exp": int(expire.timestamp()),
        "iat": int(now.timestamp()),
        "jti": jti,
        "token_type": "refresh",
    }

    return jwt.encode(
        payload,
        config.secret_key,
        algorithm=config.algorithm,
    )


def verify_token(token: str, expected_type: str = "access") -> TokenData:
    """Verify and decode a JWT token.

    Args:
        token: JWT token to verify
        expected_type: Expected token type ("access" or "refresh")

    Returns:
        Decoded token data

    Raises:
        HTTPException: If token is invalid, expired, or revoked
    """
    config = get_config()

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            config.secret_key,
            algorithms=[config.algorithm],
        )

        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception

        jti: str = payload.get("jti", "")
        if is_token_revoked(jti):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token_type: str = payload.get("token_type", "access")
        if token_type != expected_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token type: expected {expected_type}",
                headers={"WWW-Authenticate": "Bearer"},
            )

        role_str = payload.get("role")
        try:
            role = Role(role_str)
        except ValueError:
            raise credentials_exception

        return TokenData(
            sub=username,
            role=role,
            exp=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
            iat=datetime.fromtimestamp(payload["iat"], tz=timezone.utc),
            jti=jti,
            token_type=token_type,
        )

    except JWTError:
        raise credentials_exception


def revoke_token(jti: str) -> None:
    """Revoke a token by its JTI (JWT ID).

    Revoked tokens will be rejected even if otherwise valid.

    Args:
        jti: JWT ID to revoke
    """
    _revoked_tokens.add(jti)
    logger.info("Token revoked: %s", jti[:8] + "...")


def is_token_revoked(jti: str) -> bool:
    """Check if a token has been revoked.

    Args:
        jti: JWT ID to check

    Returns:
        True if token is revoked, False otherwise
    """
    return jti in _revoked_tokens


def clear_revoked_tokens() -> None:
    """Clear all revoked tokens (useful for testing)."""
    _revoked_tokens.clear()


def generate_api_key(
    username: str,
    role: Role,
    name: str = "",
) -> tuple[str, str]:
    """Generate a new API key for a user.

    Args:
        username: User the key belongs to
        role: Role to assign to the key
        name: Human-readable name for the key

    Returns:
        Tuple of (api_key, key_id)

    Note:
        The API key is only returned once. Store it securely.
        Only the hash is stored for verification.
    """
    config = get_config()

    key_id = secrets.token_urlsafe(8)
    key_secret = secrets.token_urlsafe(32)
    api_key = f"{config.api_key_prefix}{key_secret}"

    api_key_hash = bcrypt.hashpw(api_key.encode(), bcrypt.gensalt()).decode()

    _api_keys[api_key_hash] = (username, role, key_id)
    _api_key_metadata[key_id] = APIKeyInfo(
        key_id=key_id,
        created_at=datetime.now(timezone.utc),
        name=name,
    )

    logger.info("API key generated: %s", key_id)

    return api_key, key_id


def verify_api_key(api_key: str) -> tuple[str, Role]:
    """Verify an API key and return associated user info.

    Args:
        api_key: API key to verify

    Returns:
        Tuple of (username, role)

    Raises:
        HTTPException: If API key is invalid
    """
    for stored_hash, (username, role, key_id) in _api_keys.items():
        try:
            if bcrypt.checkpw(api_key.encode(), stored_hash.encode()):
                if key_id in _api_key_metadata:
                    _api_key_metadata[key_id].last_used = datetime.now(timezone.utc)
                return username, role
        except ValueError:
            # Skip any entries with invalid hash format
            continue

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API key",
    )


def revoke_api_key(key_id: str) -> bool:
    """Revoke an API key by its ID.

    Args:
        key_id: ID of the key to revoke

    Returns:
        True if key was revoked, False if not found
    """
    keys_to_remove = [key_hash for key_hash, (_, _, kid) in _api_keys.items() if kid == key_id]

    if not keys_to_remove:
        return False

    for key_hash in keys_to_remove:
        del _api_keys[key_hash]

    if key_id in _api_key_metadata:
        del _api_key_metadata[key_id]

    logger.info("API key revoked: %s", key_id)
    return True


def list_api_keys(username: str) -> list[APIKeyInfo]:
    """List all API keys for a user.

    Args:
        username: User to list keys for

    Returns:
        List of API key metadata (not the actual keys)
    """
    key_ids = [key_id for key_hash, (user, _, key_id) in _api_keys.items() if user == username]

    return [_api_key_metadata[key_id] for key_id in key_ids if key_id in _api_key_metadata]


def rotate_api_key(key_id: str, name: str = "") -> tuple[str, str] | None:
    """Rotate an API key, revoking the old one and creating a new one.

    Args:
        key_id: ID of the key to rotate
        name: Name for the new key (optional)

    Returns:
        Tuple of (new_api_key, new_key_id) or None if key not found
    """
    key_info = None
    username = None
    role = None

    for key_hash, (user, r, kid) in _api_keys.items():
        if kid == key_id:
            username = user
            role = r
            key_info = _api_key_metadata.get(key_id)
            break

    if username is None or role is None:
        return None

    revoke_api_key(key_id)

    key_name = name or (key_info.name if key_info else "")
    return generate_api_key(username, role, key_name)


def clear_api_keys() -> None:
    """Clear all API keys (useful for testing)."""
    _api_keys.clear()
    _api_key_metadata.clear()


async def get_current_user(
    token: Annotated[str | None, Depends(oauth2_scheme)] = None,
    api_key: Annotated[str | None, Security(api_key_header)] = None,
) -> TokenData:
    """Get the current authenticated user from token or API key.

    This is a FastAPI dependency that extracts and validates credentials
    from either a Bearer token or X-API-Key header.

    Args:
        token: JWT bearer token (optional)
        api_key: API key from header (optional)

    Returns:
        Token data representing the authenticated user

    Raises:
        HTTPException: If no valid credentials provided
    """
    if token:
        return verify_token(token)

    if api_key:
        username, role = verify_api_key(api_key)
        return TokenData(
            sub=username,
            role=role,
            exp=datetime.now(timezone.utc) + timedelta(hours=1),
            iat=datetime.now(timezone.utc),
            token_type="api_key",
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )


def require_roles(*allowed_roles: Role):
    """Create a dependency that requires specific roles.

    Args:
        *allowed_roles: Roles that are allowed to access the endpoint

    Returns:
        FastAPI dependency function

    Example:
        @router.post("/rollback", dependencies=[Depends(require_roles(Role.ADMIN, Role.OPERATOR))])
        async def trigger_rollback():
            ...
    """

    async def role_checker(
        current_user: Annotated[TokenData, Depends(get_current_user)],
    ) -> TokenData:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {[r.value for r in allowed_roles]}",
            )
        return current_user

    return role_checker


def require_permission(permission: str):
    """Create a dependency that requires a specific permission.

    Args:
        permission: Permission string required (e.g., "write:rollback")

    Returns:
        FastAPI dependency function
    """

    async def permission_checker(
        current_user: Annotated[TokenData, Depends(get_current_user)],
    ) -> TokenData:
        if permission not in current_user.role.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission: {permission}",
            )
        return current_user

    return permission_checker


# Convenience dependencies for common role requirements
require_admin = require_roles(Role.ADMIN)
require_operator = require_roles(Role.ADMIN, Role.OPERATOR)
require_viewer = require_roles(Role.ADMIN, Role.OPERATOR, Role.VIEWER)


# User storage (in-memory for now, use database in production)
_users: dict[str, User] = {}


def create_user(
    username: str,
    password: str,
    role: Role = Role.VIEWER,
) -> User:
    """Create a new user.

    Args:
        username: Unique username
        password: Plain text password (will be hashed)
        role: User's role

    Returns:
        Created user object

    Raises:
        ValueError: If username already exists or password too short
    """
    config = get_config()

    if username in _users:
        raise ValueError(f"User {username} already exists")

    if len(password) < config.password_min_length:
        raise ValueError(f"Password must be at least {config.password_min_length} characters")

    user = User(
        username=username,
        hashed_password=hash_password(password),
        role=role,
    )

    _users[username] = user
    logger.info("User created: %s with role %s", username, role.value)

    return user


def get_user(username: str) -> User | None:
    """Get a user by username.

    Args:
        username: Username to look up

    Returns:
        User object or None if not found
    """
    return _users.get(username)


def authenticate_user(username: str, password: str) -> User | None:
    """Authenticate a user with username and password.

    Uses constant-time comparison to prevent timing attacks that could
    enumerate valid usernames. Always performs a password hash comparison
    even when the user doesn't exist.

    Args:
        username: Username to authenticate
        password: Plain text password

    Returns:
        User object if authentication successful, None otherwise
    """
    user = get_user(username)

    # Always perform password verification to prevent timing attacks
    # that could enumerate valid usernames. Use a dummy hash when user
    # doesn't exist to ensure constant-time behavior.
    # This dummy hash is a valid bcrypt hash that will never match any password
    dummy_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYA/pWrKJKUu"

    if user is None:
        # Perform dummy verification to maintain constant time
        verify_password(password, dummy_hash)
        return None

    if user.disabled:
        # Still perform verification for disabled users to maintain constant time
        verify_password(password, user.hashed_password)
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user


def delete_user(username: str) -> bool:
    """Delete a user.

    Args:
        username: Username to delete

    Returns:
        True if user was deleted, False if not found
    """
    if username in _users:
        del _users[username]
        logger.info("User deleted: %s", username)
        return True
    return False


def clear_users() -> None:
    """Clear all users (useful for testing)."""
    _users.clear()


async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm,
) -> TokenResponse:
    """OAuth2 password flow endpoint handler.

    This function handles the OAuth2 password grant type, validating
    user credentials and returning access and refresh tokens.

    Args:
        form_data: OAuth2 form with username and password

    Returns:
        Token response with access and refresh tokens

    Raises:
        HTTPException: If authentication fails
    """
    user = authenticate_user(form_data.username, form_data.password)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    config = get_config()

    access_token = create_access_token(user.username, user.role)
    refresh_token = create_refresh_token(user.username, user.role)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=config.access_token_expire_minutes * 60,
    )


async def refresh_access_token(refresh_token: str) -> TokenResponse:
    """Refresh an access token using a refresh token.

    Args:
        refresh_token: Valid refresh token

    Returns:
        New token response with fresh access token

    Raises:
        HTTPException: If refresh token is invalid
    """
    token_data = verify_token(refresh_token, expected_type="refresh")
    config = get_config()

    user = get_user(token_data.sub)
    if user is None or user.disabled:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or disabled",
        )

    access_token = create_access_token(user.username, user.role)

    return TokenResponse(
        access_token=access_token,
        refresh_token=None,
        expires_in=config.access_token_expire_minutes * 60,
    )
