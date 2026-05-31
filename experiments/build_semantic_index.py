"""Build the Phase 1 semantic Chroma index."""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from collections import defaultdict

from rich.console import Console

from ragbench.config import get_settings
from ragbench.indexing.chroma_index import build_chroma_index, company_collection_name
from ragbench.loaders.document_loader import load_document_chunks


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Chroma index for ChitoMart business documents.")
    parser.add_argument("--rebuild", action="store_true", help="Delete and rebuild the semantic index.")
    parser.add_argument("--chunk-size", type=int, default=700, help="Character chunk size.")
    parser.add_argument("--overlap", type=int, default=100, help="Character overlap between chunks.")
    parser.add_argument("--company", default=None, help="Optional company folder to index, e.g. chitomart, cloudsewa, paysathi.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    settings = get_settings()
    console = Console()

    try:
        if args.rebuild and settings.chroma_dir.exists():
            shutil.rmtree(settings.chroma_dir)

        chunks = load_document_chunks(settings.business_docs_dir, chunk_size=args.chunk_size, overlap=args.overlap)
        if args.company:
            chunks = [chunk for chunk in chunks if chunk.metadata.get("company") == args.company]
        if not chunks:
            raise ValueError(f"No document chunks found for company={args.company!r}.")

        chunks_by_company = defaultdict(list)
        for chunk in chunks:
            chunks_by_company[str(chunk.metadata.get("company") or "default")].append(chunk)

        indexed_count = 0
        for company, company_chunks in sorted(chunks_by_company.items()):
            collection_name = company_collection_name(settings.collection_name, company)
            count = build_chroma_index(
                company_chunks,
                persist_dir=settings.chroma_dir,
                collection_name=collection_name,
                embedding_model_name=settings.embedding_model,
                rebuild=False,
            )
            indexed_count += count
            console.print(f"Company: {company} | Collection: {collection_name} | Indexed chunks: {count}")
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
