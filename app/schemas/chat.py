"""Chat request/response contracts (PRD §4.6, §7.1)."""

from __future__ import annotations

from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class AnswerStatus(StrEnum):
    ANSWERED = "answered"
    PARTIAL = "partial"
    REFUSED = "refused"
    ESCALATE = "escalate"


class Confidence(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Citation(BaseModel):
    n: int
    chunk_id: str
    doc_id: str
    version: str | None = None


class ProposedAction(BaseModel):
    tool_name: str
    args: dict[str, Any]
    args_hash: str
    approval_id: str | None = None
    rationale: str | None = None


class Answer(BaseModel):
    answer_markdown: str
    citations: list[Citation] = Field(default_factory=list)
    conflict_notes: list[str] = Field(default_factory=list)
    status: AnswerStatus = AnswerStatus.ANSWERED
    confidence: Confidence = Confidence.HIGH
    proposed_actions: list[ProposedAction] = Field(default_factory=list)
    guardrail_flags: list[str] = Field(default_factory=list)


class ChatRequest(BaseModel):
    session_id: str
    message: str = Field(min_length=1)
    account_id: str | None = None
    stream: bool = False


class ChatResponse(Answer):
    """Answer payload plus request-level identifiers."""

    trace_id: str = Field(default_factory=lambda: f"tr_{uuid4().hex}")
    session_id: str
