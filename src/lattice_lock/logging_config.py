"""
Centralized logging configuration for Lattice Lock.
Supports development, production, and test environments.
"""

import logging
import logging.config
import os
from typing import Any

LOGGING_CONFIG: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"},
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
        },
    },
    "filters": {
        "redact_sensitive": {
            "()": "lattice_lock.logging_config.SensitiveDataFilter",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "standard",
            "filters": ["redact_sensitive"],
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/lattice_lock.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "level": "DEBUG",
            "formatter": "json",
            "filters": ["redact_sensitive"],
        },
        "errors_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/errors.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "level": "ERROR",
            "formatter": "json",
            "filters": ["redact_sensitive"],
        },
    },
    "loggers": {
        "lattice_lock": {
            "level": os.getenv("LATTICE_LOCK_LOG_LEVEL", "INFO"),
            "handlers": ["console", "file"],
            "propagate": False,
        },
        "lattice_lock.errors": {
            "level": "DEBUG",
            "handlers": ["console", "errors_file"],
            "propagate": False,
        },
        "lattice_lock.admin": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False,
        },
    },
    "root": {
        "level": "WARNING",
        "handlers": ["console"],
    },
}


class SensitiveDataFilter(logging.Filter):
    """Filter to redact sensitive information from logs."""

    SENSITIVE_KEYS = {
        "password",
        "secret",
        "token",
        "api_key",
        "apikey",
        "authorization",
        "auth",
        "credential",
        "private_key",
        "access_token",
        "refresh_token",
        "session_id",
    }

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter log record to redact sensitive data."""
        if hasattr(record, "msg"):
            record.msg = self._redact_message(record.msg)
        return True

    @classmethod
    def _redact_message(cls, msg: Any) -> Any:
        """Recursively redact sensitive values."""
        if isinstance(msg, dict):
            return {
                k: (
                    "[REDACTED]"
                    if any(s in k.lower() for s in cls.SENSITIVE_KEYS)
                    else cls._redact_message(v)
                )
                for k, v in msg.items()
            }
        elif isinstance(msg, (list, tuple)):
            return type(msg)(cls._redact_message(item) for item in msg)
        return msg


def setup_logging(environment: str = "development") -> None:
    """
    Set up logging configuration for the application.

    Args:
        environment: One of 'development', 'production', 'testing'
    """
    if environment == "production":
        LOGGING_CONFIG["handlers"]["console"]["formatter"] = "json"
        LOGGING_CONFIG["loggers"]["lattice_lock"]["level"] = "INFO"
    elif environment == "testing":
        LOGGING_CONFIG["handlers"]["console"]["level"] = "WARNING"
        LOGGING_CONFIG["loggers"]["lattice_lock"]["level"] = "WARNING"

    logging.config.dictConfig(LOGGING_CONFIG)


if __name__ == "__main__":
    setup_logging("development")
    logger = logging.getLogger("lattice_lock")
    logger.info("Logging configured successfully")
