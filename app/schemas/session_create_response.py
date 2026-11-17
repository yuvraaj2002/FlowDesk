"""Response for creating a new chat session."""

from __future__ import annotations

from pydantic import BaseModel


class SessionCreateResponse(BaseModel):
    session_id: str
