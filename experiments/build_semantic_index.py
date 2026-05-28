"""Build the Phase 1 semantic Chroma index."""

from __future__ import annotations

import argparse
import os
import sys

from rich.console import Console

from ragbench.config import get_settings
from ragbench.indexing.chroma_index import build_chroma_index
from ragbench.loaders.document_loader import load_document_chunks


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Chroma index for ChitoMart business documents.")
    parser.add_argument("--rebuild", action="store_true", help="Delete and rebuild the semantic index.")
    parser.add_argument("--chunk-size", type=int, default=700, help="Character chunk size.")
    parser.add_argument("--overlap", type=int, default=100, help="Character overlap between chunks.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    settings = get_settings()
    console = Console()

    try:
        chunks = load_document_chunks(settings.business_docs_dir, chunk_size=args.chunk_size, overlap=args.overlap)
        indexed_count = build_chroma_index(
            chunks,
            persist_dir=settings.chroma_dir,
            collection_name=settings.collection_name,
            embedding_model_name=settings.embedding_model,
            rebuild=args.rebuild,
        )
    except Exception as exc:
        console.print(f"[red]Index build failed:[/red] {exc}")
        return 1

    console.print(f"[green]Loaded {len(chunks)} chunks from business docs[/green]")
    console.print(f"Indexed new chunks: {indexed_count}")
    console.print(f"Chroma path: {settings.chroma_dir}")
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(exit_code)
