import os
import secrets
from typing import Optional
from pydantic import BaseModel, Field, SecretStr, field_validator
from lattice_lock.exceptions import SecurityConfigurationError

class AuthConfig(BaseModel):
    """Authentication configuration."""
    
    secret_key: SecretStr = Field(..., description="Secret key for JWT signing")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    api_key_prefix: str = "llk_"
    password_min_length: int = 8

    @field_validator("access_token_expire_minutes")
    @classmethod
    def validate_access_token_expiry(cls, v: int) -> int:
        if v < 1:
            raise ValueError("Access token expiry must be at least 1 minute")
        return v
    
    @classmethod
    def load(cls) -> "AuthConfig":
        env = os.environ.get("LATTICE_ENV", "dev")
        secret_val = os.environ.get("LATTICE_LOCK_SECRET_KEY")
        
        # Enforce production security
        if env == "production":
            if not secret_val:
                raise SecurityConfigurationError("LATTICE_LOCK_SECRET_KEY must be set in production environment")
            if len(secret_val) < 32:
                 raise SecurityConfigurationError("LATTICE_LOCK_SECRET_KEY must be at least 32 characters in production")
        
        if not secret_val:
             if env == "dev":
                 secret_val = "dev-secret-do-not-use-in-production"
             else:
                 # Generate a random one if not provided in non-prod? 
                 # Or just use a placeholder to pass validation. 
                 # The original used secrets.token_urlsafe(32) as default_factory
                 secret_val = secrets.token_urlsafe(32)

        return cls(
            secret_key=SecretStr(secret_val),
            algorithm=os.environ.get("AUTH_ALGORITHM", "HS256"),
            access_token_expire_minutes=int(os.environ.get("TOKEN_EXPIRY_MINUTES", "30")),
            refresh_token_expire_days=int(os.environ.get("REFRESH_TOKEN_EXPIRE_DAYS", "7")),
            api_key_prefix=os.environ.get("API_KEY_PREFIX", "llk_"),
            password_min_length=int(os.environ.get("PASSWORD_MIN_LENGTH", "8"))
        )

# Global configuration instance
_config: Optional[AuthConfig] = None

def get_config() -> AuthConfig:
    global _config
    if _config is None:
        _config = AuthConfig.load()
    return _config
