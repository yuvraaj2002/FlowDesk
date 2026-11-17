"""Chat endpoints — static stub until retrieval / agents land."""

from __future__ import annotations

from fastapi import APIRouter

from app.schemas.chat import (
    AnswerStatus,
    ChatRequest,
    ChatResponse,
    Citation,
    Confidence,
)

router = APIRouter(tags=["chat"])

_STATIC_ANSWER = (
    "This is a **static stub** from the FlowDesk Support Copilot API. "
    "Retrieval, tools, and the LangGraph orchestrator are not wired yet. "
    "Your message was received and a real answer will replace this soon."
)


@router.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest) -> ChatResponse:
    """Run one turn. Returns a fixed Answer-shaped payload for now."""
    return ChatResponse(
        session_id=body.session_id,
        answer_markdown=_STATIC_ANSWER,
        citations=[
            Citation(
                n=1,
                chunk_id="stub_chunk_0001",
                doc_id="meta/static-stub",
                version="v0",
            )
        ],
        conflict_notes=[],
        status=AnswerStatus.ANSWERED,
        confidence=Confidence.LOW,
        proposed_actions=[],
        guardrail_flags=["static_stub"],
    )


@router.get("/sessions/{session_id}")
async def get_session(session_id: str) -> dict:
    """Conversation history stub — empty until session store exists."""
    return {"session_id": session_id, "messages": []}
