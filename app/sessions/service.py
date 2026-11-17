"""Session id creation."""

from __future__ import annotations

from uuid import uuid4


class SessionService:
    """Issues opaque session identifiers for the chat UI."""

    def create_session_id(self) -> str:
        return f"sess_{uuid4().hex[:16]}"
