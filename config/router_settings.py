"""Front-door scope router (Ollama decision model)."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class RouterSettings(BaseSettings):
    """tev1-style System One gate before RAG."""

    model_config = SettingsConfigDict(env_prefix="ROUTER__", extra="ignore")

    enabled: bool = True
    model: str = "tev1:0.8b"
    # Reuse the Ollama host; override if the decision model is elsewhere.
    base_url: str = "http://localhost:11434"
    timeout_seconds: float = 30.0
    # If confidence is below this, fall through to RAG instead of hard-refusing.
    min_confidence: float = 0.35
