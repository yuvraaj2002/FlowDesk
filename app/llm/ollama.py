"""Ollama chat client."""

from __future__ import annotations

import httpx

from config.llm_settings import LlmSettings
from config.settings import Settings


class OllamaClient:
    """Minimal async client for local Ollama `/api/chat`."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or Settings()
        self._llm: LlmSettings = self._settings.llm

    async def complete(
        self,
        *,
        system_prompt: str,
        user_message: str,
        account_id: str | None = None,
    ) -> str:
        """Return assistant text for one turn."""
        content = user_message
        if account_id:
            content = f"[account_id={account_id}]\n{user_message}"

        payload = {
            "model": self._llm.model,
            "stream": False,
            "options": {"temperature": self._llm.temperature},
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content},
            ],
        }

        url = f"{self._llm.base_url.rstrip('/')}/api/chat"
        timeout = httpx.Timeout(self._llm.timeout_seconds)

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

        message = data.get("message") or {}
        text = (message.get("content") or "").strip()
        if not text:
            raise RuntimeError("Ollama returned an empty assistant message")
        return text
