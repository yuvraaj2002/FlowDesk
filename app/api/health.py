"""Health HTTP routes."""

from __future__ import annotations

from fastapi import APIRouter


class HealthRouter:
    """Liveness probe endpoints."""

    def __init__(self) -> None:
        self._router = APIRouter(tags=["health"])
        self._register_routes()

    @property
    def router(self) -> APIRouter:
        return self._router

    def _register_routes(self) -> None:
        self._router.add_api_route("/healthz", self.healthz, methods=["GET"])

    async def healthz(self) -> dict[str, str]:
        return {"status": "ok"}
