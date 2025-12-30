from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer

from .api_keys import verify_api_key
from .models import Role, TokenData
from .tokens import verify_token

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/token",
    auto_error=False,
)

api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False,
)


async def get_current_user(
    token: Annotated[str | None, Depends(oauth2_scheme)] = None,
    api_key: Annotated[str | None, Security(api_key_header)] = None,
) -> TokenData:
    """Get the current authenticated user from token or API key."""
    if token:
        return verify_token(token)

    if api_key:
        username, role = verify_api_key(api_key)
        return TokenData(
            sub=username,
            role=role,
            exp=datetime.now(timezone.utc) + timedelta(hours=1),
            iat=datetime.now(timezone.utc),
            jti="",
            token_type="api_key",
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )


def require_roles(*allowed_roles: Role):
    """Create a dependency that requires specific roles."""

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
    """Create a dependency that requires a specific permission."""

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


# Convenience dependencies
require_admin = require_roles(Role.ADMIN)
require_operator = require_roles(Role.ADMIN, Role.OPERATOR)
require_viewer = require_roles(Role.ADMIN, Role.OPERATOR, Role.VIEWER)
