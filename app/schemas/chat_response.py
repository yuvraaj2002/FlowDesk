"""Chat response for the current Ollama-backed turn."""

from __future__ import annotations

from uuid import uuid4

from pydantic import BaseModel, Field

from app.schemas.answer_status import AnswerStatus
from app.schemas.confidence import Confidence


class ChatResponse(BaseModel):
    session_id: str
    answer_markdown: str
    status: AnswerStatus = AnswerStatus.ANSWERED
    confidence: Confidence = Confidence.MEDIUM
    guardrail_flags: list[str] = Field(default_factory=list)
    trace_id: str = Field(default_factory=lambda: f"tr_{uuid4().hex}")
