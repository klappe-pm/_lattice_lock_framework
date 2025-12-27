import secrets
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, status

from .config import get_config
from .models import Role, TokenData
from .storage import MemoryAuthStorage


def create_access_token(username: str, role: Role, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token."""
    config = get_config()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=config.access_token_expire_minutes)

    jti = secrets.token_urlsafe(16)
    payload = {
        "sub": username,
        "role": role.value,
        "exp": int(expire.timestamp()),
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "jti": jti,
        "token_type": "access",
    }

    return jwt.encode(payload, config.secret_key.get_secret_value(), algorithm=config.algorithm)


def create_refresh_token(username: str, role: Role, expires_delta: timedelta | None = None) -> str:
    """Create a JWT refresh token."""
    config = get_config()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=config.refresh_token_expire_days)

    jti = secrets.token_urlsafe(16)
    payload = {
        "sub": username,
        "role": role.value,
        "exp": int(expire.timestamp()),
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "jti": jti,
        "token_type": "refresh",
    }

    return jwt.encode(payload, config.secret_key.get_secret_value(), algorithm=config.algorithm)


def verify_token(token: str, expected_type: str = "access") -> TokenData:
    """Verify and decode a JWT token."""
    config = get_config()
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # PyJWT decode
        payload = jwt.decode(
            token, config.secret_key.get_secret_value(), algorithms=[config.algorithm]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception

        jti: str = payload.get("jti", "")
        if MemoryAuthStorage.is_token_revoked(jti):
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
    except jwt.PyJWTError:
        raise credentials_exception


def revoke_token(jti: str) -> None:
    """Revoke a token by its JTI."""
    MemoryAuthStorage.revoke_token(jti)


def is_token_revoked(jti: str) -> bool:
    """Check if token is revoked."""
    return MemoryAuthStorage.is_token_revoked(jti)


def clear_revoked_tokens() -> None:
    """Clear revoked tokens (test utility)."""
    MemoryAuthStorage._revoked_tokens.clear()
