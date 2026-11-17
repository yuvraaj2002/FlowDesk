"""LLM provider settings."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class LlmSettings(BaseSettings):
    """Ollama / Bedrock connection and generation knobs."""

    model_config = SettingsConfigDict(env_prefix="LLM__", extra="ignore")

    provider: str = "ollama"
    model: str = "LiquidAI/lfm2.5-1.2b-instruct:latest"
    base_url: str = "http://localhost:11434"
    temperature: float = 0.2
    timeout_seconds: float = 60.0
