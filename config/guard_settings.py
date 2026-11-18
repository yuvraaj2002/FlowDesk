"""L1 input injection / jailbreak classifier settings."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class GuardSettings(BaseSettings):
    """Local HF classifier that runs before the scope router."""

    model_config = SettingsConfigDict(env_prefix="GUARD__", extra="ignore")

    enabled: bool = True
    # Prompt-Guard-86M is gated on Hugging Face; protectai works without approval.
    # Set GUARD__MODEL=meta-llama/Prompt-Guard-86M once HF access is granted.
    model: str = "protectai/deberta-v3-base-prompt-injection-v2"
    device: str = "auto"
    # Block when the malicious-class score is at or above this value.
    jailbreak_threshold: float = 0.85
