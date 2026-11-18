"""Root application settings."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict

from config.embed_settings import EmbedSettings
from config.guard_settings import GuardSettings
from config.llm_settings import LlmSettings
from config.qdrant_settings import QdrantSettings
from config.retrieval_settings import RetrievalSettings
from config.router_settings import RouterSettings


class Settings(BaseSettings):
    """Top-level settings loaded from env / `.env`."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )

    llm: LlmSettings = LlmSettings()
    qdrant: QdrantSettings = QdrantSettings()
    embed: EmbedSettings = EmbedSettings()
    retrieval: RetrievalSettings = RetrievalSettings()
    router: RouterSettings = RouterSettings()
    guard: GuardSettings = GuardSettings()
