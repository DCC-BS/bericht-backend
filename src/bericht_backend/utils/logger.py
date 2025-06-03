import logging
import os
import time
import uuid
from collections.abc import Mapping
from datetime import datetime
from typing import Any

import structlog
import structlog.processors
from structlog.processors import CallsiteParameter
from structlog.stdlib import BoundLogger
from structlog.types import EventDict, Processor


# In-memory log storage with maximum size
class InMemoryLogHandler(logging.Handler):
    """A logging handler that keeps logs in memory for retrieval via API."""

    # Singleton instance
    _instance = None  # Type: Optional["InMemoryLogHandler"]
    
    def __init__(self, capacity: int = 1000):
        """Initialize the handler with a maximum capacity for logs.
        
        Args:
            capacity: Maximum number of log entries to store
        """
        super().__init__()
        self.logs: list[dict[str, Any]] = []
        self.capacity = capacity
    
    def emit(self, record: logging.LogRecord) -> None:
        """Store the log record in memory.
        
        Args:
            record: The log record to store
        """
        # Convert the log record to a dict for storage
        log_entry = self.format(record)
        
        # Check if it's a JSON-formatted log (from structlog)
        if log_entry.startswith('{') and log_entry.endswith('}'):
            import json
            try:
                # Try to parse as JSON
                log_dict = json.loads(log_entry)
                self.logs.append(log_dict)
            except json.JSONDecodeError:
                # If it's not valid JSON, store as plain text
                self.logs.append({"message": log_entry, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z")})
        else:
            # For non-JSON logs, create a simple dict
            self.logs.append({"message": log_entry, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z")})
        
        # Maintain the maximum capacity
        if len(self.logs) > self.capacity:
            self.logs.pop(0)
    
    @classmethod
    def get_instance(cls, capacity: int = 1000) -> "InMemoryLogHandler":
        """Get or create the singleton instance of InMemoryLogHandler.
        
        Args:
            capacity: Maximum number of log entries to store
            
        Returns:
            The singleton instance of InMemoryLogHandler
        """
        if cls._instance is None:
            cls._instance = InMemoryLogHandler(capacity)
        return cls._instance
    
    def get_logs(
        self,
        level: str | None = None,
        from_time: datetime | None = None,
        to_time: datetime | None = None,
        limit: int = 100,
        request_id: str | None = None
    ) -> list[dict[str, Any]]:
        """Get logs with optional filtering.
        
        Args:
            level: Filter by log level (e.g., "INFO", "ERROR")
            from_time: Filter logs from this time
            to_time: Filter logs until this time
            limit: Maximum number of logs to return
            request_id: Filter by specific request ID
            
        Returns:
            A list of log entries matching the filter criteria
        """
        # Start with all logs
        filtered_logs = self.logs.copy()
        
        # Apply filters
        if level:
            filtered_logs = [log for log in filtered_logs if log.get("level", "").upper() == level.upper()]
        
        if from_time:
            filtered_logs = [
                log for log in filtered_logs
                if "timestamp" in log and datetime.fromisoformat(log["timestamp"].replace("Z", "+00:00")) >= from_time
            ]
        
        if to_time:
            filtered_logs = [
                log for log in filtered_logs
                if "timestamp" in log and datetime.fromisoformat(log["timestamp"].replace("Z", "+00:00")) <= to_time
            ]
        
        if request_id:
            filtered_logs = [log for log in filtered_logs if log.get("request_id") == request_id]
        
        # Sort by timestamp (most recent first)
        filtered_logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        # Apply limit
        return filtered_logs[:limit]


# Standard library logging setup
def setup_stdlib_logging() -> None:
    """Configure standard library logging to work with structlog."""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, log_level, logging.INFO)

    # Create a handler for console output
    handler = logging.StreamHandler()

    # Add in-memory handler for API access
    memory_handler = InMemoryLogHandler.get_instance()
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(handler)
    root_logger.addHandler(memory_handler)

    # Disable propagation for libraries that are too verbose
    for logger_name in ["uvicorn.access"]:
        lib_logger = logging.getLogger(logger_name)
        lib_logger.propagate = False


def add_request_id(logger: BoundLogger, method_name: str, event_dict: EventDict) -> Mapping[str, Any]: # pyright: ignore[reportUnusedParameter]
    """
    Add a request ID to the log context if it doesn't exist.

    Args:
        logger: The logger instance
        method_name: The name of the logging method
        event_dict: The event dictionary

    Returns:
        The updated event dictionary
    """
    if "request_id" not in event_dict:
        event_dict["request_id"] = str(uuid.uuid4())
    return event_dict


def add_timestamp(logger: BoundLogger, method_name: str, event_dict: EventDict) -> Mapping[str, Any]:  # pyright: ignore[reportUnusedParameter]
    """
    Add an ISO-8601 timestamp to the log entry.

    Args:
        logger: The logger instance
        method_name: The name of the logging method
        event_dict: The event dictionary

    Returns:
        The updated event dictionary
    """
    event_dict["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    return event_dict


def init_logger() -> None:
    """
    Initialize the logger configuration based on environment.
    Uses JSON renderer in production environment for compatibility with fluentbit.
    Adds the module name as context to the logger.
    """
    # Set up standard library logging first
    setup_stdlib_logging()

    # Define processors list for structlog
    processors: list[Processor] = [
        structlog.stdlib.filter_by_level,  # Filter logs by configured level
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        add_timestamp,
        add_request_id,
        structlog.processors.CallsiteParameterAdder(
            parameters=[
                CallsiteParameter.MODULE,
                CallsiteParameter.FUNC_NAME,
                CallsiteParameter.LINENO,
            ]  # Using enum values for structlog 25.2.0
        ),
        structlog.processors.format_exc_info,  # Format exception info if present
        structlog.processors.UnicodeDecoder(),  # Handle non-unicode characters
    ]

    # Use different renderers for development vs production
    if os.getenv("PROD"):
        # JSON renderer for production to be fluentbit compatible
        processors.append(structlog.processors.JSONRenderer())
    else:
        # For development, use a colored console renderer
        processors.append(structlog.dev.ConsoleRenderer(colors=True))

    # Configure structlog
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None) -> BoundLogger:
    """
    Get a structured logger instance.

    Args:
        name: Optional name for the logger, typically the module name

    Returns:
        A bound logger instance for structured logging
    """
    if name:
        return structlog.get_logger(name)  # pyright: ignore[reportAny]
    return structlog.get_logger()  # pyright: ignore[reportAny]
