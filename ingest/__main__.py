"""CLI: `uv run python -m ingest` or `make ingest`."""

from __future__ import annotations

import argparse
import json
import sys

from ingest.runner import IngestRunner


class IngestCli:
    """Parse args and run knowledge-base ingest."""

    def build_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            description="Chunk, embed, and upsert FlowDesk knowledge into Qdrant.",
        )
        parser.add_argument(
            "--source",
            action="append",
            choices=["docs", "changelog", "tickets", "all"],
            help="Source to ingest (repeatable). Default: all.",
        )
        return parser

    def run(self, argv: list[str] | None = None) -> int:
        args = self.build_parser().parse_args(argv)
        sources = args.source or ["all"]
        if "all" in sources:
            selected = ["docs", "changelog", "tickets"]
        else:
            selected = sources

        print(f"Ingesting sources: {', '.join(selected)}")
        print("Loading embedding model (first run may download from Hugging Face)...")
        print("Device: auto-detect (cuda → mps → cpu)")
        result = IngestRunner().run(sources=selected)
        print(json.dumps(result, indent=2))
        return 0


def main() -> None:
    raise SystemExit(IngestCli().run())


if __name__ == "__main__":
    main()
