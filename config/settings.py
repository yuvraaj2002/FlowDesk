"""Root application settings."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict

from config.llm_settings import LlmSettings


class Settings(BaseSettings):
    """Top-level settings loaded from env / `.env`."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )

    llm: LlmSettings = LlmSettings()
