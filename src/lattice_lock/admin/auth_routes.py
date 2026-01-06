"""
Lattice Lock Admin API Authentication Routes

Provides FastAPI routes for authentication operations including:
- OAuth2 password flow token generation
- Token refresh
- API key management
- Token revocation

All routes are prefixed with /api/v1/auth when included in the main app.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field

from lattice_lock.admin.auth import (
    APIKeyInfo,
    Role,
    TokenData,
    TokenResponse,
    generate_api_key,
    get_current_user,
    list_api_keys,
    login_for_access_token,
    refresh_access_token,
    require_roles,
    revoke_api_key,
    revoke_token,
    rotate_api_key,
)

router = APIRouter(prefix="/auth", tags=["authentication"])


class RefreshTokenRequest(BaseModel):
    """Request body for token refresh endpoint."""

    refresh_token: str = Field(..., description="Valid refresh token")


class APIKeyCreateRequest(BaseModel):
    """Request body for API key creation."""

    name: str = Field("", description="Human-readable name for the key")
    role: Role = Field(Role.VIEWER, description="Role to assign to the key")


class APIKeyCreateResponse(BaseModel):
    """Response for API key creation.

    Note: The api_key is only returned once. Store it securely.
    """

    api_key: str = Field(..., description="The API key (only shown once)")
    key_id: str = Field(..., description="Unique identifier for the key")
    name: str = Field("", description="Human-readable name")
    role: Role = Field(..., description="Role assigned to the key")


class APIKeyRotateRequest(BaseModel):
    """Request body for API key rotation."""

    name: str = Field("", description="Name for the new key (optional)")


class RevokeTokenRequest(BaseModel):
    """Request body for token revocation."""

    token_jti: str = Field(..., description="JTI of the token to revoke")


class MessageResponse(BaseModel):
    """Simple message response."""

    message: str


class UserInfoResponse(BaseModel):
    """Response containing current user information."""

    username: str
    role: Role
    token_type: str


@router.post(
    "/token",
    response_model=TokenResponse,
    summary="Login and get access token",
    description="OAuth2 password flow. Returns access and refresh tokens.",
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> TokenResponse:
    """Authenticate with username and password to get JWT tokens.

    This endpoint implements the OAuth2 password grant type.
    Use the returned access_token as a Bearer token for authenticated requests.
    Use the refresh_token to obtain new access tokens without re-authenticating.

    Args:
        form_data: OAuth2 password request form with username and password

    Returns:
        TokenResponse with access_token, refresh_token, and expiry info

    Raises:
        401 Unauthorized: If credentials are invalid
    """
    return await login_for_access_token(form_data)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Exchange a valid refresh token for a new access token.",
)
async def refresh(request: RefreshTokenRequest) -> TokenResponse:
    """Refresh an expired access token using a valid refresh token.

    Args:
        request: Request containing the refresh token

    Returns:
        TokenResponse with new access_token

    Raises:
        401 Unauthorized: If refresh token is invalid or expired
    """
    return await refresh_access_token(request.refresh_token)


@router.get(
    "/me",
    response_model=UserInfoResponse,
    summary="Get current user info",
    description="Returns information about the currently authenticated user.",
)
async def get_me(
    current_user: Annotated[TokenData, Depends(get_current_user)],
) -> UserInfoResponse:
    """Get information about the currently authenticated user.

    Args:
        current_user: Injected by authentication dependency

    Returns:
        Current user's username, role, and authentication method
    """
    return UserInfoResponse(
        username=current_user.sub,
        role=current_user.role,
        token_type=current_user.token_type,
    )


@router.post(
    "/revoke",
    response_model=MessageResponse,
    summary="Revoke a token",
    description="Revoke a token by its JTI. Requires admin role.",
    dependencies=[Depends(require_roles(Role.ADMIN))],
)
async def revoke(request: RevokeTokenRequest) -> MessageResponse:
    """Revoke a JWT token by its JTI (JWT ID).

    Once revoked, the token will be rejected even if otherwise valid.
    This is useful for logging out users or invalidating compromised tokens.

    Note: Only admins can revoke tokens.

    Args:
        request: Request containing the JTI to revoke

    Returns:
        Confirmation message
    """
    revoke_token(request.token_jti)
    return MessageResponse(message="Token revoked successfully")


@router.post(
    "/api-keys",
    response_model=APIKeyCreateResponse,
    summary="Create API key",
    description="Generate a new API key. Requires admin role.",
    dependencies=[Depends(require_roles(Role.ADMIN))],
)
async def create_api_key(
    request: APIKeyCreateRequest,
    current_user: Annotated[TokenData, Depends(get_current_user)],
) -> APIKeyCreateResponse:
    """Create a new API key.

    The API key is returned only once in this response.
    Store it securely - it cannot be retrieved again.

    Note: Only admins can create API keys.

    Args:
        request: API key creation request with optional name and role
        current_user: Current authenticated user (admin)

    Returns:
        The new API key and its metadata
    """
    api_key, key_id = generate_api_key(
        username=current_user.sub,
        role=request.role,
        name=request.name,
    )

    return APIKeyCreateResponse(
        api_key=api_key,
        key_id=key_id,
        name=request.name,
        role=request.role,
    )


@router.get(
    "/api-keys",
    response_model=list[APIKeyInfo],
    summary="List API keys",
    description="List all API keys for the current user.",
)
async def get_api_keys(
    current_user: Annotated[TokenData, Depends(get_current_user)],
) -> list[APIKeyInfo]:
    """List all API keys belonging to the current user.

    Returns metadata only - the actual keys cannot be retrieved.

    Args:
        current_user: Current authenticated user

    Returns:
        List of API key metadata
    """
    return list_api_keys(current_user.sub)


@router.delete(
    "/api-keys/{key_id}",
    response_model=MessageResponse,
    summary="Revoke API key",
    description="Revoke an API key by its ID.",
)
async def delete_api_key(
    key_id: str,
    current_user: Annotated[TokenData, Depends(get_current_user)],
) -> MessageResponse:
    """Revoke an API key.

    Users can revoke their own keys. Admins can revoke any key.

    Args:
        key_id: ID of the key to revoke
        current_user: Current authenticated user

    Returns:
        Confirmation message

    Raises:
        404 Not Found: If key doesn't exist
        403 Forbidden: If user doesn't own the key and isn't admin
    """
    keys = list_api_keys(current_user.sub)
    owns_key = any(k.key_id == key_id for k in keys)

    if not owns_key and current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot revoke keys you don't own",
        )

    if not revoke_api_key(key_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    return MessageResponse(message="API key revoked successfully")


@router.post(
    "/api-keys/{key_id}/rotate",
    response_model=APIKeyCreateResponse,
    summary="Rotate API key",
    description="Revoke an existing key and create a new one.",
)
async def rotate_key(
    key_id: str,
    request: APIKeyRotateRequest,
    current_user: Annotated[TokenData, Depends(get_current_user)],
) -> APIKeyCreateResponse:
    """Rotate an API key.

    This revokes the existing key and creates a new one with the same
    role. The new key is returned only once - store it securely.

    Args:
        key_id: ID of the key to rotate
        request: Optional new name for the key
        current_user: Current authenticated user

    Returns:
        The new API key and its metadata

    Raises:
        404 Not Found: If key doesn't exist
        403 Forbidden: If user doesn't own the key and isn't admin
    """
    keys = list_api_keys(current_user.sub)
    owns_key = any(k.key_id == key_id for k in keys)

    if not owns_key and current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot rotate keys you don't own",
        )

    result = rotate_api_key(key_id, request.name)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    api_key, new_key_id = result

    key_info = list_api_keys(current_user.sub)
    new_key_info = next((k for k in key_info if k.key_id == new_key_id), None)

    return APIKeyCreateResponse(
        api_key=api_key,
        key_id=new_key_id,
        name=request.name or (new_key_info.name if new_key_info else ""),
        role=current_user.role,
    )
