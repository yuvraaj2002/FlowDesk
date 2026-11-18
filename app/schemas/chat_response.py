"""Chat response for a grounded RAG turn."""

from __future__ import annotations

from uuid import uuid4

from pydantic import BaseModel, Field

from app.schemas.answer_status import AnswerStatus
from app.schemas.block_reason import BlockReason
from app.schemas.citation import Citation


class ChatResponse(BaseModel):
    session_id: str
    answer_markdown: str
    status: AnswerStatus = AnswerStatus.ANSWERED
    block_reason: BlockReason | None = None
    citations: list[Citation] = Field(default_factory=list)
    trace_id: str = Field(default_factory=lambda: f"tr_{uuid4().hex}")
