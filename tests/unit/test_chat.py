"""Smoke tests for the chat API."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from app.guardrails.models import InjectionScanResult
from app.main import app, application
from app.rag.service import RagService
from app.retrieval.models import RetrievalHit, RetrievalResult
from app.router.models import ScopeDecision, ScopeRouteResult
from app.schemas.answer_status import AnswerStatus
from app.schemas.chat_response import ChatResponse
from app.schemas.citation import Citation
from config.settings import Settings


def _in_scope_router() -> MagicMock:
    router = MagicMock()
    router.enabled = True
    router.route = AsyncMock(
        return_value=ScopeRouteResult(
            decision=ScopeDecision.IN_SCOPE,
            confidence=0.8,
            probabilities={"in_scope": 0.9, "out_of_scope": 0.1},
            model="tev1:0.8b",
        )
    )
    return router


def _safe_guard() -> MagicMock:
    guard = MagicMock()
    guard.enabled = True
    guard.scan.return_value = InjectionScanResult(
        flagged=False,
        label="SAFE",
        score=0.01,
        model="protectai/deberta-v3-base-prompt-injection-v2",
    )
    guard.filter_hits.side_effect = lambda hits: list(hits)
    return guard


class TestChatApi:
    """HTTP smoke coverage for health + chat + session routes."""

    client = TestClient(app)

    def test_healthz(self) -> None:
        response = self.client.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "qdrant" in data["dependencies"]

    def test_create_session_returns_id(self) -> None:
        response = self.client.get("/sessions/new")
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"].startswith("sess_")
        assert len(data["session_id"]) == 21

    def test_chat_returns_rag_answer(self) -> None:
        fake = ChatResponse(
            session_id="sess_test_1",
            answer_markdown="Use a Delay step between the two email actions. [1]",
            status=AnswerStatus.ANSWERED,
            block_reason=None,
            citations=[
                Citation(
                    n=1,
                    doc_id="workflows/delay-steps",
                    source_type="help_doc",
                    scope="workflows",
                )
            ],
        )
        with patch.object(
            application._rag,
            "answer",
            new=AsyncMock(return_value=fake),
        ) as mock_answer:
            response = self.client.post(
                "/chat",
                json={
                    "session_id": "sess_test_1",
                    "message": "How do I set up a delay step?",
                    "account_id": "acc_1042",
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "sess_test_1"
        assert data["status"] == "answered"
        assert data["block_reason"] is None
        assert data["trace_id"].startswith("tr_")
        assert "Delay step" in data["answer_markdown"]
        assert "confidence" not in data
        assert "guardrail_flags" not in data
        assert data["citations"][0]["doc_id"] == "workflows/delay-steps"
        mock_answer.assert_awaited_once()
        kwargs = mock_answer.await_args.kwargs
        assert kwargs["account_id"] == "acc_1042"
        assert "delay step" in kwargs["message"].lower()

    def test_chat_rejects_empty_message(self) -> None:
        response = self.client.post(
            "/chat",
            json={"session_id": "sess_test_1", "message": ""},
        )
        assert response.status_code == 422

    def test_session_stub_is_empty(self) -> None:
        response = self.client.get("/sessions/sess_test_1")
        assert response.status_code == 200
        assert response.json() == {"session_id": "sess_test_1", "messages": []}


class TestRagService:
    def test_answer_grounds_on_retrieved_evidence(self) -> None:
        hits = [
            RetrievalHit(
                chunk_id="chk_1",
                score=0.9,
                text="Insert a Delay step between the two email actions.",
                metadata={
                    "doc_id": "workflows/delay-steps",
                    "source_type": "help_doc",
                    "version": "v3",
                    "area": "workflows",
                },
            )
        ]
        retriever = MagicMock()
        retriever.retrieve.return_value = RetrievalResult(
            query="delay step",
            top_k=8,
            hits=hits,
        )
        ollama = MagicMock()
        ollama.complete = AsyncMock(return_value="Use a Delay step. [1]")

        service = RagService(
            settings=Settings(),
            retriever=retriever,
            ollama_client=ollama,
            scope_router=_in_scope_router(),
            prompt_guard=_safe_guard(),
        )
        result = asyncio.run(
            service.answer(
                session_id="sess_1",
                message="How do delay steps work?",
                account_id="acc_1042",
            )
        )

        assert result.status == AnswerStatus.ANSWERED
        assert result.block_reason is None
        assert result.citations[0].doc_id == "workflows/delay-steps"
        assert result.citations[0].scope == "workflows"
        kwargs = ollama.complete.await_args.kwargs
        assert "Evidence" in kwargs["system_prompt"]
        assert "Delay step" in kwargs["system_prompt"]
        assert kwargs["user_message"] == "How do delay steps work?"

    def test_answer_escalates_when_no_hits(self) -> None:
        retriever = MagicMock()
        retriever.retrieve.return_value = RetrievalResult(
            query="salesforce cpq",
            top_k=8,
            hits=[],
        )
        ollama = MagicMock()
        ollama.complete = AsyncMock()

        service = RagService(
            settings=Settings(),
            retriever=retriever,
            ollama_client=ollama,
            scope_router=_in_scope_router(),
            prompt_guard=_safe_guard(),
        )
        result = asyncio.run(
            service.answer(
                session_id="sess_1",
                message="Does FlowDesk integrate with Salesforce CPQ?",
            )
        )

        assert result.status == AnswerStatus.ESCALATE
        assert result.block_reason is None
        ollama.complete.assert_not_awaited()
