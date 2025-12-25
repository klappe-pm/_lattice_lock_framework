"""
Central Application Configuration.
Aggregates specific configs from Auth, Analysis, and Execution modules.
"""
import os
from typing import Optional

class AppConfig:
    def __init__(self):
        self.env = os.environ.get("LATTICE_ENV", "dev")
        
        # Analyzer Configuration
        self.analyzer_cache_size: int = int(os.environ.get("ANALYZER_CACHE_SIZE", 1024))
        
        # Executor Configuration
        self.max_function_calls: int = int(os.environ.get("MAX_FUNCTION_CALLS", 10))
        self.background_task_timeout: float = float(os.environ.get("BACKGROUND_TASK_TIMEOUT", "5.0"))
        
        # Auth Configuration
        self.token_expiry_minutes: int = int(os.environ.get("TOKEN_EXPIRY_MINUTES", 30))
        
        # Security Configuration
        self.jwt_algorithm = "HS256"
        self.secret_key = os.environ.get("LATTICE_LOCK_SECRET_KEY")

        # Validation logic for production security
        if self.env == "production" and not self.secret_key:
             raise ValueError("LATTICE_LOCK_SECRET_KEY must be set in production")

    @classmethod
    def load(cls) -> "AppConfig":
        """Load configuration from environment."""
        return cls()
