"""CLI: print a query and the top-k retrieval hits."""

from __future__ import annotations

import argparse
import json
import sys

from app.retrieval.retriever import DenseRetriever


class RetrievalCli:
    """Parse args, run dense retrieval, print input + ranked hits."""

    def build_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            description="Embed a query and retrieve top-k chunks from Qdrant.",
        )
        parser.add_argument(
            "--query",
            "-q",
            required=True,
            help="Natural-language search query.",
        )
        parser.add_argument(
            "--top-k",
            "-k",
            type=int,
            default=None,
            help="Number of hits to return (default: RETRIEVAL__TOP_K / 8).",
        )
        parser.add_argument(
            "--json",
            action="store_true",
            help="Emit a single JSON object instead of a human-readable dump.",
        )
        return parser

    def run(self, argv: list[str] | None = None) -> int:
        args = self.build_parser().parse_args(argv)
        print("Loading embedding model...", file=sys.stderr)
        result = DenseRetriever().retrieve(args.query, top_k=args.top_k)

        if args.json:
            print(result.model_dump_json(indent=2))
            return 0

        print("=" * 72)
        print("INPUT")
        print("=" * 72)
        print(f"query: {result.query}")
        print(f"top_k: {result.top_k}")
        print(f"hits:  {len(result.hits)}")
        print()

        if not result.hits:
            print("No results. Is Qdrant up and has ingest been run?")
            return 0

        print("=" * 72)
        print("OUTPUT")
        print("=" * 72)
        for index, hit in enumerate(result.hits, start=1):
            print(f"\n--- [{index}] score={hit.score:.4f}  chunk_id={hit.chunk_id}")
            print("text:")
            print(hit.text)
            print("metadata:")
            print(json.dumps(hit.metadata, indent=2, default=str))
        return 0
