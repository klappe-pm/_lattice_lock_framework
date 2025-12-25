"""Logging configuration and standards."""
import logging
import re

LOG_LEVELS = {
    "cache_hit": logging.DEBUG,
    "model_selection": logging.INFO,
    "provider_failover": logging.WARNING,
    "security_violation": logging.CRITICAL,
    "billing_integrity": logging.CRITICAL,
}

# Patterns to redact from logs
REDACT_PATTERNS = [
    re.compile(r"(api[_-]?key[\"']?\s*[:=]\s*[\"']?)([^\"'\s]+)", re.I),
    re.compile(r"(secret[_-]?key[\"']?\s*[:=]\s*[\"']?)([^\"'\s]+)", re.I),
    re.compile(r"(bearer\s+)([^\s]+)", re.I),
    re.compile(r"(password[\"']?\s*[:=]\s*[\"']?)([^\"'\s]+)", re.I),
    re.compile(r"(token[\"']?\s*[:=]\s*[\"']?)([^\"'\s]+)", re.I),
]


def redact_sensitive(message: str) -> str:
    """Redact sensitive data from log messages."""
    for pattern in REDACT_PATTERNS:
        message = pattern.sub(r"\1[REDACTED]", message)
    return message


class RedactingFormatter(logging.Formatter):
    """Formatter that automatically redacts sensitive data."""
    
    def format(self, record: logging.LogRecord) -> str:
        original = super().format(record)
        return redact_sensitive(original)


def configure_logging(level: int = logging.INFO) -> None:
    """Configure logging with redaction for the framework."""
    handler = logging.StreamHandler()
    handler.setFormatter(RedactingFormatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ))
    
    root_logger = logging.getLogger("lattice_lock")
    root_logger.setLevel(level)
    root_logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with standard configuration."""
    return logging.getLogger(name)

