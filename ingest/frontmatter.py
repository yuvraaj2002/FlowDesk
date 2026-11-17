"""Minimal YAML frontmatter parser for markdown files."""

from __future__ import annotations

from typing import Any

import yaml


class FrontmatterParser:
    """Split `---`-delimited frontmatter from markdown body."""

    def parse(self, raw: str) -> tuple[dict[str, Any], str]:
        text = raw.lstrip("\ufeff")
        if not text.startswith("---"):
            return {}, text.strip()

        parts = text.split("---", 2)
        if len(parts) < 3:
            return {}, text.strip()

        meta = yaml.safe_load(parts[1]) or {}
        if not isinstance(meta, dict):
            meta = {}
        body = parts[2].strip()
        return meta, body
