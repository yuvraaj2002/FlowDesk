"""Stable content-hash ids for idempotent upserts."""

from __future__ import annotations

import hashlib


class ChunkIdFactory:
    """Build sha256 chunk ids from source key + text."""

    def build(self, *parts: str) -> str:
        material = "\n".join(parts)
        return hashlib.sha256(material.encode("utf-8")).hexdigest()
