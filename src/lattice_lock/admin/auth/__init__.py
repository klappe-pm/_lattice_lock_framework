from .config import AuthConfig, get_config, reset_config
from .models import Role, TokenData, User, APIKeyInfo, TokenResponse
from .passwords import get_password_hash, verify_password
from .tokens import (
    create_access_token, 
    create_refresh_token, 
    verify_token, 
    revoke_token, 
    is_token_revoked, 
    clear_revoked_tokens
)
from .api_keys import (
    generate_api_key, 
    verify_api_key, 
    revoke_api_key, 
    rotate_api_key, 
    list_api_keys, 
    clear_api_keys
)
from .users import (
    create_user, 
    get_user, 
    delete_user, 
    clear_users, 
    authenticate_user
)
from .dependencies import (
    get_current_user, 
    require_roles,
    require_permission,
    require_admin, 
    require_operator, 
    require_viewer,
    oauth2_scheme,
    api_key_header
)
from .service import (
    configure,
    login_for_access_token,
    refresh_access_token,
)

# Backward compatibility alias
hash_password = get_password_hash

__all__ = [
    # Config
    "AuthConfig", "get_config", "reset_config", "configure",
    # Models
    "Role", "TokenData", "User", "APIKeyInfo", "TokenResponse",
    # Passwords
    "get_password_hash", "verify_password", "hash_password",
    # Tokens
    "create_access_token", "create_refresh_token", "verify_token", 
    "revoke_token", "is_token_revoked", "clear_revoked_tokens",
    # API Keys
    "generate_api_key", "verify_api_key", "revoke_api_key", 
    "rotate_api_key", "list_api_keys", "clear_api_keys",
    # Users
    "create_user", "get_user", "delete_user", "clear_users", "authenticate_user",
    # Dependencies
    "get_current_user", "require_roles", "require_permission",
    "require_admin", "require_operator", "require_viewer",
    "oauth2_scheme", "api_key_header",
    # Service
    "login_for_access_token", "refresh_access_token",
]
