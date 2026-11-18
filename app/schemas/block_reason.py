"""Why a chat turn was blocked before answering."""

from __future__ import annotations

from enum import StrEnum


class BlockReason(StrEnum):
    """Literal block causes surfaced on refused / escalated turns."""

    OUT_OF_SCOPE = "out_of_scope"
    PROMPT_INJECTION = "prompt_injection"
