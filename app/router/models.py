"""Typed result from the front-door scope router."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class ScopeDecision(StrEnum):
    IN_SCOPE = "in_scope"
    OUT_OF_SCOPE = "out_of_scope"


class ScopeRouteResult(BaseModel):
    decision: ScopeDecision
    confidence: float = Field(ge=0.0, le=1.0)
    probabilities: dict[str, float] = Field(default_factory=dict)
    model: str
