"""
Logging Configuration and Standards.

This module provides the standard logging configuration interface
as specified in the refactoring plan. It re-exports from the main
logging_config module for convenience.

For full logging functionality, see lattice_lock.logging_config.
"""

import logging
import re
from typing import Dict

# Re-export main logging utilities
from lattice_lock.logging_config import (
    get_logger,
    setup_logging,
    configure_from_environment,
    get_trace_id,
    set_trace_id,
    generate_trace_id,
)

# Log level mappings for different event types
LOG_LEVELS: Dict[str, int] = {
    "cache_hit": logging.DEBUG,
    "model_selection": logging.INFO,
    "provider_failover": logging.WARNING,
    "security_violation": logging.CRITICAL,
    "billing_integrity": logging.CRITICAL,
}

# Patterns to redact from logs
REDACT_PATTERNS = [
    re.compile(r"(api[_-]?key[\"\']?\s*[:=]\s*[\"\']?)([^\"\'\s]+)", re.I),
    re.compile(r"(secret[_-]?key[\"\']?\s*[:=]\s*[\"\']?)([^\"\'\s]+)", re.I),
    re.compile(r"(bearer\s+)([^\s]+)", re.I),
]


def redact_sensitive(message: str) -> str:
    """Redact sensitive data from log messages.
    
    Args:
        message: The log message to redact.
        
    Returns:
        Message with sensitive values replaced with [REDACTED].
    """
    for pattern in REDACT_PATTERNS:
        message = pattern.sub(r"\1[REDACTED]", message)
    return message


__all__ = [
    "get_logger",
    "setup_logging",
    "configure_from_environment",
    "get_trace_id",
    "set_trace_id",
    "generate_trace_id",
    "LOG_LEVELS",
    "REDACT_PATTERNS",
    "redact_sensitive",
]
