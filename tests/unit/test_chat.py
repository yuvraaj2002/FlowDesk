"""Smoke tests for the chat API."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app


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

    def test_chat_returns_ollama_answer(self) -> None:
        with patch(
            "app.api.chat.OllamaClient.complete",
            new=AsyncMock(return_value="Use a Delay step between the two email actions."),
        ) as mock_complete:
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
        assert data["trace_id"].startswith("tr_")
        assert "Delay step" in data["answer_markdown"]
        assert "ollama_direct" in data["guardrail_flags"]
        assert "citations" not in data
        assert "proposed_actions" not in data
        mock_complete.assert_awaited_once()
        kwargs = mock_complete.await_args.kwargs
        assert kwargs["account_id"] == "acc_1042"
        assert "delay step" in kwargs["user_message"].lower()
        assert "FlowDesk Support Copilot" in kwargs["system_prompt"]

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
