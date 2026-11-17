"""Smoke tests for the static /chat stub."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_healthz() -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_chat_returns_static_answer() -> None:
    response = client.post(
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
    assert "static stub" in data["answer_markdown"].lower()
    assert data["citations"][0]["doc_id"] == "meta/static-stub"
    assert "static_stub" in data["guardrail_flags"]


def test_chat_rejects_empty_message() -> None:
    response = client.post(
        "/chat",
        json={"session_id": "sess_test_1", "message": ""},
    )
    assert response.status_code == 422


def test_session_stub_is_empty() -> None:
    response = client.get("/sessions/sess_test_1")
    assert response.status_code == 200
    assert response.json() == {"session_id": "sess_test_1", "messages": []}
