"""Typed result from the L1 input classifier."""

from __future__ import annotations

from pydantic import BaseModel, Field


class InjectionScanResult(BaseModel):
    flagged: bool
    label: str
    score: float = Field(ge=0.0, le=1.0)
    model: str
