"""
Centralized Logging Configuration for Lattice Lock Framework.

Provides consistent logging setup across all modules with support for:
- Console and file handlers
- JSON formatting for production environments
- Trace ID propagation for request tracking
- Sensitive data redaction
"""

import json
import logging
import os
import sys
import uuid
from contextvars import ContextVar
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

# Context variable for trace ID propagation
trace_id_var: ContextVar[str] = ContextVar("trace_id", default="")


def generate_trace_id() -> str:
    """Generate a new trace ID for request tracking."""
    return str(uuid.uuid4())[:8]


def get_trace_id() -> str:
    """Get the current trace ID from context."""
    return trace_id_var.get() or "unknown"


def set_trace_id(trace_id: str | None = None) -> str:
    """Set the trace ID in context. Generates a new one if not provided."""
    if trace_id is None:
        trace_id = generate_trace_id()
    trace_id_var.set(trace_id)
    return trace_id


class TraceIdFilter(logging.Filter):
    """Filter that adds trace_id to log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.trace_id = get_trace_id()
        return True


class SensitiveDataFilter(logging.Filter):
    """Filter that redacts sensitive data from log messages."""

    SENSITIVE_PATTERNS = {
        "password",
        "secret",
        "token",
        "api_key",
        "apikey",
        "authorization",
        "auth",
        "credential",
        "private_key",
        "bearer",
    }

    def filter(self, record: logging.LogRecord) -> bool:
        if hasattr(record, "msg") and isinstance(record.msg, str):
            record.msg = self._redact_message(record.msg)
        return True

    def _redact_message(self, message: str) -> str:
        """Redact sensitive patterns from message."""
        lower_msg = message.lower()
        for pattern in self.SENSITIVE_PATTERNS:
            if pattern in lower_msg:
                # Simple redaction - replace values after sensitive keys
                import re

                # Match patterns like key=value, key: value, "key": "value"
                for sep in ["=", ":", ": "]:
                    regex = rf'({pattern}){sep}([^\s,}}\]"\']+)'
                    message = re.sub(regex, rf"\1{sep}[REDACTED]", message, flags=re.IGNORECASE)
        return message


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging in production environments."""

    def format(self, record: logging.LogRecord) -> str:
        log_data: dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "trace_id": getattr(record, "trace_id", "unknown"),
        }

        # Add location info
        if record.pathname:
            log_data["location"] = {
                "file": record.pathname,
                "line": record.lineno,
                "function": record.funcName,
            }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        extra_fields = {
            k: v
            for k, v in record.__dict__.items()
            if k
            not in {
                "name",
                "msg",
                "args",
                "created",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "stack_info",
                "exc_info",
                "exc_text",
                "thread",
                "threadName",
                "trace_id",
                "message",
                "taskName",
            }
        }
        if extra_fields:
            log_data["extra"] = extra_fields

        return json.dumps(log_data)


class ConsoleFormatter(logging.Formatter):
    """Human-readable formatter for console output."""

    def __init__(self, include_trace_id: bool = True) -> None:
        self.include_trace_id = include_trace_id
        if include_trace_id:
            fmt = "%(asctime)s - %(name)s - %(levelname)s - [%(trace_id)s] %(message)s"
        else:
            fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        super().__init__(fmt=fmt, datefmt="%Y-%m-%d %H:%M:%S")


class SimpleFormatter(logging.Formatter):
    """Simple formatter for CLI output (message only)."""

    def __init__(self) -> None:
        super().__init__(fmt="%(message)s")


def setup_logging(
    level: int | str = logging.INFO,
    json_format: bool = False,
    log_file: str | None = None,
    log_file_max_bytes: int = 10 * 1024 * 1024,  # 10MB
    log_file_backup_count: int = 5,
    include_trace_id: bool = True,
    simple_format: bool = False,
) -> logging.Logger:
    """
    Configure logging for the Lattice Lock framework.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: Use JSON formatting for structured logging
        log_file: Optional file path for file logging
        log_file_max_bytes: Maximum size of log file before rotation
        log_file_backup_count: Number of backup files to keep
        include_trace_id: Include trace ID in log messages
        simple_format: Use simple message-only format (for CLI)

    Returns:
        The root lattice_lock logger
    """
    # Convert string level to int if needed
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)

    # Get the root logger for lattice_lock
    root_logger = logging.getLogger("lattice_lock")
    root_logger.setLevel(level)

    # Clear existing handlers
    root_logger.handlers.clear()

    # Create filters
    trace_filter = TraceIdFilter()
    sensitive_filter = SensitiveDataFilter()

    # Console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(level)

    if simple_format:
        console_handler.setFormatter(SimpleFormatter())
    elif json_format:
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(ConsoleFormatter(include_trace_id=include_trace_id))

    console_handler.addFilter(trace_filter)
    console_handler.addFilter(sensitive_filter)
    root_logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        # Ensure the log directory exists
        log_dir = Path(log_file).parent
        if log_dir != Path(".") and not log_dir.exists():
            log_dir.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=log_file_max_bytes,
            backupCount=log_file_backup_count,
        )
        file_handler.setLevel(level)

        # Always use JSON format for file logging
        file_handler.setFormatter(JSONFormatter())
        file_handler.addFilter(trace_filter)
        file_handler.addFilter(sensitive_filter)
        root_logger.addHandler(file_handler)

    # Prevent propagation to root logger
    root_logger.propagate = False

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the lattice_lock namespace.

    Args:
        name: Logger name (will be prefixed with 'lattice_lock.')

    Returns:
        Configured logger instance
    """
    if not name.startswith("lattice_lock"):
        name = f"lattice_lock.{name}"
    return logging.getLogger(name)


# Environment-based configuration
def configure_from_environment() -> logging.Logger:
    """
    Configure logging based on environment variables.

    Environment variables:
        LATTICE_LOG_LEVEL: Logging level (default: INFO)
        LATTICE_LOG_JSON: Enable JSON format (default: false)
        LATTICE_LOG_FILE: Log file path (optional)
        LATTICE_LOG_SIMPLE: Use simple format for CLI (default: false)
    """
    level = os.environ.get("LATTICE_LOG_LEVEL", "INFO")
    json_format = os.environ.get("LATTICE_LOG_JSON", "").lower() in ("true", "1", "yes")
    log_file = os.environ.get("LATTICE_LOG_FILE")
    simple_format = os.environ.get("LATTICE_LOG_SIMPLE", "").lower() in ("true", "1", "yes")

    return setup_logging(
        level=level,
        json_format=json_format,
        log_file=log_file,
        simple_format=simple_format,
    )


def cleanup_old_logs(
    log_dir: str | Path,
    max_age_days: int = 3,
    pattern: str = "*.log*",
) -> int:
    """
    Delete log files older than the specified number of days.

    This function scans the specified directory for log files matching the pattern
    and deletes any that are older than max_age_days based on their modification time.

    Args:
        log_dir: Directory containing log files to clean up
        max_age_days: Maximum age in days before a log file is deleted (default: 3)
        pattern: Glob pattern to match log files (default: "*.log*" to catch
                 rotated logs like app.log, app.log.1, app.log.2, etc.)

    Returns:
        Number of files deleted

    Example:
        >>> from lattice_lock.logging_config import cleanup_old_logs
        >>> deleted = cleanup_old_logs("/var/log/lattice_lock", max_age_days=3)
        >>> print(f"Deleted {deleted} old log files")
    """
    log_path = Path(log_dir)
    if not log_path.exists():
        return 0

    if not log_path.is_dir():
        raise ValueError(f"log_dir must be a directory, got: {log_dir}")

    cutoff_time = datetime.now() - timedelta(days=max_age_days)
    deleted_count = 0
    logger = logging.getLogger("lattice_lock.log_cleanup")

    for log_file in log_path.glob(pattern):
        if not log_file.is_file():
            continue

        try:
            file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            if file_mtime < cutoff_time:
                log_file.unlink()
                deleted_count += 1
                logger.debug(f"Deleted old log file: {log_file}")
        except OSError as e:
            logger.warning(f"Failed to delete log file {log_file}: {e}")

    if deleted_count > 0:
        logger.info(f"Cleaned up {deleted_count} log files older than {max_age_days} days")

    return deleted_count
