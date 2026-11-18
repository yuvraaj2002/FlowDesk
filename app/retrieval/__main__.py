"""CLI: `uv run python -m app.retrieval --query "..."` or `make retrieve`."""

from __future__ import annotations

from app.retrieval.cli import RetrievalCli


def main() -> None:
    raise SystemExit(RetrievalCli().run())


if __name__ == "__main__":
    main()
