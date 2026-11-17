"""FastAPI application entrypoint."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import ChatRouter
from app.api.health import HealthRouter


class Application:
    """Builds and configures the FlowDesk Support Copilot API."""

    def __init__(self) -> None:
        self.app = FastAPI(
            title="FlowDesk Support Copilot",
            version="0.1.0",
            description="RAG support copilot API — chat, approvals, traces, evals.",
        )
        self._configure_cors()
        self._register_routes()

    def _configure_cors(self) -> None:
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "http://localhost:5173",
                "http://127.0.0.1:5173",
            ],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def _register_routes(self) -> None:
        self.app.include_router(HealthRouter().router)
        self.app.include_router(ChatRouter().router)


application = Application()
app = application.app
