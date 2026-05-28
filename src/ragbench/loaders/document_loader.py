"""Load and chunk ChitoMart Markdown business documents."""

from __future__ import annotations

from pathlib import Path

from ragbench.schemas import DocumentChunk
from ragbench.utils.text import deterministic_chunks


def load_markdown_documents(docs_dir: Path) -> list[tuple[str, str]]:
    if not docs_dir.exists():
        raise FileNotFoundError(f"Business docs directory does not exist: {docs_dir}")

    markdown_files = sorted(docs_dir.glob("*.md"))
    if not markdown_files:
        raise FileNotFoundError(f"No Markdown business documents found in: {docs_dir}")

    documents: list[tuple[str, str]] = []
    for path in markdown_files:
        text = path.read_text(encoding="utf-8").strip()
        if text:
            documents.append((path.name, text))

    if not documents:
        raise ValueError(f"Markdown business documents are empty in: {docs_dir}")

    return documents


def load_document_chunks(
    docs_dir: Path,
    chunk_size: int = 700,
    overlap: int = 100,
) -> list[DocumentChunk]:
    documents = load_markdown_documents(docs_dir)
    chunks: list[DocumentChunk] = []

    for source, text in documents:
        for index, content in enumerate(deterministic_chunks(text, chunk_size=chunk_size, overlap=overlap), start=1):
            stem = Path(source).stem
            chunks.append(
                DocumentChunk(
                    chunk_id=f"{stem}-{index:03d}",
                    source=source,
                    content=content,
                    metadata={"source": source, "chunk_index": index},
                )
            )

    return chunks
