"""Health HTTP routes."""

from __future__ import annotations

from fastapi import APIRouter

from app.vectorstore.qdrant import QdrantStore


class HealthRouter:
    """Liveness / dependency probe endpoints."""

    def __init__(self, qdrant_store: QdrantStore | None = None) -> None:
        self._qdrant = qdrant_store
        self._router = APIRouter(tags=["health"])
        self._register_routes()

    @property
    def router(self) -> APIRouter:
        return self._router

    def _register_routes(self) -> None:
        self._router.add_api_route("/healthz", self.healthz, methods=["GET"])

    async def healthz(self) -> dict[str, object]:
        qdrant_status = "unconfigured"
        if self._qdrant is not None:
            try:
                self._qdrant.ping()
                qdrant_status = "ok"
            except Exception:  # noqa: BLE001 — probe must never raise
                qdrant_status = "down"

        return {
            "status": "ok",
            "dependencies": {
                "qdrant": qdrant_status,
            },
        }
