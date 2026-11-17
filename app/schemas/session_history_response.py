"""Response for fetching conversation history."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SessionHistoryResponse(BaseModel):
    session_id: str
    messages: list[dict[str, Any]] = Field(default_factory=list)
