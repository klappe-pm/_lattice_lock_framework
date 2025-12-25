"""
Authentication service functions for login and token refresh.
"""
import logging
from datetime import timedelta

from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from .config import AuthConfig, get_config
from .models import Role, TokenResponse
from .tokens import create_access_token, create_refresh_token, verify_token
from .users import authenticate_user

logger = logging.getLogger("lattice_lock.admin.auth.service")

# Global config reference for configure()
_global_config = None

def configure(config: AuthConfig) -> None:
    """
    Set the global authentication configuration.
    
    Args:
        config: AuthConfig instance to use globally
    """
    global _global_config
    import lattice_lock.admin.auth.config as config_module
    config_module._config = config
    logger.info("Authentication configuration updated")


async def login_for_access_token(form_data: OAuth2PasswordRequestForm) -> TokenResponse:
    """
    Authenticate user and return access/refresh tokens.
    
    Args:
        form_data: OAuth2 password request form with username and password
        
    Returns:
        TokenResponse with access_token, refresh_token, and expiry info
        
    Raises:
        HTTPException 401: If credentials are invalid
    """
    user = authenticate_user(form_data.username, form_data.password)
    
    if not user:
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
        token_type="bearer",
        expires_in=config.access_token_expire_minutes * 60,
    )


async def refresh_access_token(refresh_token: str) -> TokenResponse:
    """
    Exchange a valid refresh token for a new access token.
    
    Args:
        refresh_token: Valid refresh token
        
    Returns:
        TokenResponse with new access_token
        
    Raises:
        HTTPException 401: If refresh token is invalid or expired
    """
    try:
        token_data = verify_token(refresh_token, expected_type="refresh")
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    config = get_config()
    access_token = create_access_token(token_data.sub, token_data.role)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=None,  # Don't issue new refresh token
        token_type="bearer",
        expires_in=config.access_token_expire_minutes * 60,
    )
