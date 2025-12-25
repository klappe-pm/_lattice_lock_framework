"""
Central Application Configuration.
Aggregates specific configs from Auth, Analysis, and Execution modules.
"""
import os
import re
from typing import Optional


class AppConfig:
    def __init__(self):
        self.env = os.environ.get("LATTICE_ENV", "dev")
        
        # Analyzer Configuration
        self.analyzer_cache_size: int = self._parse_int("ANALYZER_CACHE_SIZE", 1024)
        
        # Executor Configuration
        self.max_function_calls: int = self._parse_int("MAX_FUNCTION_CALLS", 10)
        self.background_task_timeout: float = float(os.environ.get("BACKGROUND_TASK_TIMEOUT", "5.0"))
        
        # Auth Configuration
        self.token_expiry_minutes: int = self._parse_int("TOKEN_EXPIRY_MINUTES", 30)
        
        # Security Configuration
        self.jwt_algorithm = "HS256"
        self.secret_key = os.environ.get("LATTICE_LOCK_SECRET_KEY")

        # Validation logic for production security
        if self.env == "production" and not self.secret_key:
             raise ValueError("LATTICE_LOCK_SECRET_KEY must be set in production")

    def _parse_int(self, var: str, default: int) -> int:
        """Safely parse integer environment variables."""
        value = os.environ.get(var)
        if value is not None:
            if re.match(r"^\d+$", value):
                return int(value)
            raise ValueError(f"Environment variable {var} must be an integer, got: {value}")
        return default

    @classmethod
    def load(cls) -> "AppConfig":
        """Load configuration from environment."""
        return cls()

