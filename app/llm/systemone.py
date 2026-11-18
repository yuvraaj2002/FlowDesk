"""Ollama System One (/v1/systemone) client for decision models."""

from __future__ import annotations

from typing import Any

import httpx

from config.router_settings import RouterSettings
from config.settings import Settings


class SystemOneClient:
    """Async client for Ollama decision models (tev1 / nimble / jev-style)."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or Settings()
        self._router: RouterSettings = self._settings.router

    async def decide(
        self,
        *,
        state: str | dict[str, Any],
        questions: dict[str, Any],
        model: str | None = None,
    ) -> dict[str, Any]:
        payload = {
            "model": model or self._router.model,
            "state": state,
            "questions": questions,
        }
        url = f"{self._router.base_url.rstrip('/')}/v1/systemone"
        timeout = httpx.Timeout(self._router.timeout_seconds)

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

        if not isinstance(data, dict) or "answers" not in data:
            raise RuntimeError("System One returned an invalid response")
        return data
