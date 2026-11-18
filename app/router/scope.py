"""Scope gate: FlowDesk support vs random out-of-domain questions."""

from __future__ import annotations

from app.llm.systemone import SystemOneClient
from app.router.models import ScopeDecision, ScopeRouteResult
from config.router_settings import RouterSettings
from config.settings import Settings

_SCOPE_QUESTION = {
    "type": "choice",
    "instructions": (
        "Decide if the user message is a FlowDesk support question or unrelated. "
        "FlowDesk is a SaaS CRM. In-scope covers product how-tos, docs, changelogs, "
        "workflows, messaging/SMS/email limits, billing/plan limits, tickets, "
        "integrations, webhooks, delays, and account/workflow diagnosis for agents."
    ),
    "criteria": {
        "in_scope": (
            "About FlowDesk product support, docs, workflows, messaging, billing, "
            "tickets, integrations, or account behavior"
        ),
        "out_of_scope": (
            "Random chatter, jokes, general knowledge, coding homework, or anything "
            "unrelated to FlowDesk support"
        ),
    },
}


class ScopeRouter:
    """Front-door router powered by a local Ollama decision model."""

    def __init__(
        self,
        settings: Settings | None = None,
        client: SystemOneClient | None = None,
    ) -> None:
        self._settings = settings or Settings()
        self._router: RouterSettings = self._settings.router
        self._client = client or SystemOneClient(self._settings)

    @property
    def enabled(self) -> bool:
        return self._router.enabled

    async def route(self, message: str) -> ScopeRouteResult:
        data = await self._client.decide(
            state=message.strip(),
            questions={"scope": _SCOPE_QUESTION},
            model=self._router.model,
        )
        answer = (data.get("answers") or {}).get("scope") or {}
        choice = str(answer.get("choice") or ScopeDecision.IN_SCOPE)
        if choice not in {ScopeDecision.IN_SCOPE, ScopeDecision.OUT_OF_SCOPE}:
            choice = ScopeDecision.IN_SCOPE

        probabilities = {
            str(key): float(value)
            for key, value in dict(answer.get("probabilities") or {}).items()
        }
        confidence = float(answer.get("confidence") or 0.0)
        return ScopeRouteResult(
            decision=ScopeDecision(choice),
            confidence=confidence,
            probabilities=probabilities,
            model=str(data.get("model") or self._router.model),
        )
