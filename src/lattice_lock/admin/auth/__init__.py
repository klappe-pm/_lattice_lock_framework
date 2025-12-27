from .api_keys import (
    clear_api_keys,
    generate_api_key,
    list_api_keys,
    revoke_api_key,
    rotate_api_key,
    verify_api_key,
)
from .config import AuthConfig, get_config, reset_config
from .dependencies import (
    api_key_header,
    get_current_user,
    oauth2_scheme,
    require_admin,
    require_operator,
    require_permission,
    require_roles,
    require_viewer,
)
from .models import APIKeyInfo, Role, TokenData, TokenResponse, User
from .passwords import get_password_hash, verify_password
from .service import configure, login_for_access_token, refresh_access_token
from .tokens import (
    clear_revoked_tokens,
    create_access_token,
    create_refresh_token,
    is_token_revoked,
    revoke_token,
    verify_token,
)
from .users import authenticate_user, clear_users, create_user, delete_user, get_user

# Backward compatibility alias
hash_password = get_password_hash

__all__ = [
    # Config
    "AuthConfig",
    "get_config",
    "reset_config",
    "configure",
    # Models
    "Role",
    "TokenData",
    "User",
    "APIKeyInfo",
    "TokenResponse",
    # Passwords
    "get_password_hash",
    "verify_password",
    "hash_password",
    # Tokens
    "create_access_token",
    "create_refresh_token",
    "verify_token",
    "revoke_token",
    "is_token_revoked",
    "clear_revoked_tokens",
    # API Keys
    "generate_api_key",
    "verify_api_key",
    "revoke_api_key",
    "rotate_api_key",
    "list_api_keys",
    "clear_api_keys",
    # Users
    "create_user",
    "get_user",
    "delete_user",
    "clear_users",
    "authenticate_user",
    # Dependencies
    "get_current_user",
    "require_roles",
    "require_permission",
    "require_admin",
    "require_operator",
    "require_viewer",
    "oauth2_scheme",
    "api_key_header",
    # Service
    "login_for_access_token",
    "refresh_access_token",
]
