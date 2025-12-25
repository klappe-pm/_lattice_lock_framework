"""
Central Application Configuration.

Aggregates specific configs from Auth, Analysis, and Execution modules.
Provides environment-based validation for production deployments.
"""

import os
from typing import Optional


class AppConfig:
    """Central configuration for the Lattice Lock Framework.
    
    Loads configuration from environment variables with sensible defaults.
    Enforces security requirements in production environments.
    
    Attributes:
        env: Current environment (dev, staging, production)
        analyzer_cache_size: Maximum entries in task analyzer cache
        max_function_calls: Maximum function calls per conversation
        background_task_timeout: Timeout for background tasks in seconds
        token_expiry_minutes: JWT token expiry time
        jwt_algorithm: Algorithm for JWT encoding
        secret_key: Secret key for JWT signing (required in production)
    """
    
    def __init__(self) -> None:
        self.env = os.environ.get("LATTICE_ENV", "dev")
        
        # Analyzer Configuration
        self.analyzer_cache_size: int = int(
            os.environ.get("ANALYZER_CACHE_SIZE", "1024")
        )
        
        # Executor Configuration
        self.max_function_calls: int = int(
            os.environ.get("MAX_FUNCTION_CALLS", "10")
        )
        self.background_task_timeout: float = float(
            os.environ.get("BACKGROUND_TASK_TIMEOUT", "5.0")
        )
        
        # Auth Configuration
        self.token_expiry_minutes: int = int(
            os.environ.get("TOKEN_EXPIRY_MINUTES", "30")
        )
        
        # Security Configuration
        self.jwt_algorithm = "HS256"
        self.secret_key: Optional[str] = os.environ.get("LATTICE_LOCK_SECRET_KEY")
        
        # Validation logic for production security
        if self.env == "production" and not self.secret_key:
            from lattice_lock.errors.types import ConfigurationError
            raise ConfigurationError(
                "LATTICE_LOCK_SECRET_KEY must be set in production",
                config_key="LATTICE_LOCK_SECRET_KEY",
                error_code="LL-501"
            )
    
    @classmethod
    def load(cls) -> "AppConfig":
        """Load configuration from environment.
        
        Returns:
            AppConfig instance with values loaded from environment.
        """
        return cls()
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.env == "production"
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.env == "dev"
