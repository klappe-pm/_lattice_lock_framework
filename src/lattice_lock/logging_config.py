"""
Centralized Logging Configuration for Lattice Lock Framework.

Provides environment-based logging configuration with support for:
- JSON structured logging for production
- Human-readable format for development
- Log rotation and file handlers
- Consistent logger naming conventions
- Sensitive data redaction
"""

import json
import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging in production environments."""

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
    }

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "trace_id"):
            log_data["trace_id"] = record.trace_id

        if hasattr(record, "span_id"):
            log_data["span_id"] = record.span_id

        extra_fields = {}
        for key, value in record.__dict__.items():
            if key not in {
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
                "message",
                "trace_id",
                "span_id",
                "taskName",
            }:
                extra_fields[key] = self._redact_sensitive(key, value)

        if extra_fields:
            log_data["extra"] = extra_fields

        return json.dumps(log_data, default=str)

    def _redact_sensitive(self, key: str, value: Any) -> Any:
        """Redact sensitive values based on key names."""
        if isinstance(value, dict):
            return {k: self._redact_sensitive(k, v) for k, v in value.items()}

        key_lower = key.lower()
        if any(sensitive in key_lower for sensitive in self.SENSITIVE_KEYS):
            return "[REDACTED]"

        if isinstance(value, str) and len(value) > 500:
            return value[:500] + "...[truncated]"

        return value


class DevelopmentFormatter(logging.Formatter):
    """Human-readable formatter for development environments."""

    COLORS = {
        "DEBUG": "\033[36m",
        "INFO": "\033[32m",
        "WARNING": "\033[33m",
        "ERROR": "\033[31m",
        "CRITICAL": "\033[35m",
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, "")
        reset = self.RESET if color else ""

        trace_info = ""
        if hasattr(record, "trace_id"):
            trace_info = f" [trace:{record.trace_id[:8]}]"

        formatted = (
            f"{color}{record.levelname:<8}{reset} "
            f"{record.name}:{record.lineno}{trace_info} - {record.getMessage()}"
        )

        if record.exc_info:
            formatted += "\n" + self.formatException(record.exc_info)

        return formatted


def get_log_level() -> int:
    """Get log level from environment variable."""
    level_name = os.getenv("LATTICE_LOG_LEVEL", "INFO").upper()
    return getattr(logging, level_name, logging.INFO)


def get_log_format() -> str:
    """Get log format from environment variable."""
    return os.getenv("LATTICE_LOG_FORMAT", "development")


def get_log_file() -> str | None:
    """Get log file path from environment variable."""
    return os.getenv("LATTICE_LOG_FILE")


def configure_logging(
    level: int | None = None,
    format_type: str | None = None,
    log_file: str | None = None,
    enable_console: bool = True,
) -> None:
    """
    Configure logging for the Lattice Lock Framework.

    Args:
        level: Log level (default: from LATTICE_LOG_LEVEL env var or INFO)
        format_type: 'json' for structured logging, 'development' for human-readable
                    (default: from LATTICE_LOG_FORMAT env var or 'development')
        log_file: Path to log file (default: from LATTICE_LOG_FILE env var)
        enable_console: Whether to enable console output (default: True)
    """
    if level is None:
        level = get_log_level()

    if format_type is None:
        format_type = get_log_format()

    if log_file is None:
        log_file = get_log_file()

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    if format_type == "json":
        formatter = JSONFormatter()
    else:
        formatter = DevelopmentFormatter()

    if enable_console:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(file_handler)

    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the standard Lattice Lock naming convention.

    Args:
        name: Logger name (typically __name__ from the calling module)

    Returns:
        Configured logger instance
    """
    if not name.startswith("lattice_lock"):
        if name.startswith("src."):
            name = name[4:]

    return logging.getLogger(name)


class LoggerAdapter(logging.LoggerAdapter):
    """Logger adapter that adds trace context to log records."""

    def process(
        self, msg: str, kwargs: dict[str, Any]
    ) -> tuple[str, dict[str, Any]]:
        extra = kwargs.get("extra", {})

        if "trace_id" in self.extra:
            extra["trace_id"] = self.extra["trace_id"]
        if "span_id" in self.extra:
            extra["span_id"] = self.extra["span_id"]

        kwargs["extra"] = extra
        return msg, kwargs


def get_traced_logger(
    name: str, trace_id: str | None = None, span_id: str | None = None
) -> LoggerAdapter:
    """
    Get a logger with trace context attached.

    Args:
        name: Logger name
        trace_id: Optional trace ID for distributed tracing
        span_id: Optional span ID for distributed tracing

    Returns:
        LoggerAdapter with trace context
    """
    logger = get_logger(name)
    extra = {}
    if trace_id:
        extra["trace_id"] = trace_id
    if span_id:
        extra["span_id"] = span_id
    return LoggerAdapter(logger, extra)
