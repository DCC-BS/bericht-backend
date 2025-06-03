"""Model for log response."""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class LogEntry(BaseModel):
    """A single log entry."""

    level: str = Field(description="Log level (INFO, WARNING, ERROR, etc.)")
    timestamp: str = Field(description="ISO-8601 timestamp of the log entry")
    message: str = Field(description="Log message content")
    module: str | None = Field(None, description="Source module that generated the log")
    function: str | None = Field(None, description="Source function that generated the log")
    line_number: int | None = Field(None, description="Source line number that generated the log")
    request_id: str | None = Field(None, description="Request ID associated with the log entry")
    extra: dict[str, Any] = Field(default_factory=dict, description="Additional log context data")


class LogResponse(BaseModel):
    """Response model for log retrieval endpoints."""

    logs: list[LogEntry] = Field(default_factory=list, description="List of log entries")
    count: int = Field(description="Total number of log entries returned")
    from_timestamp: datetime | None = Field(None, description="Starting timestamp for filtered logs")
    to_timestamp: datetime | None = Field(None, description="Ending timestamp for filtered logs")
    level_filter: str | None = Field(None, description="Log level filter that was applied")
