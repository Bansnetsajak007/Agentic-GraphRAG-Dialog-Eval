"""Load and chunk ChitoMart Markdown business documents."""

from __future__ import annotations

from pathlib import Path

from ragbench.schemas import DocumentChunk
from ragbench.utils.text import deterministic_chunks


def source_to_chunk_prefix(source: str) -> str:
    return Path(source).with_suffix("").as_posix().replace("/", "__")


def source_to_company(source: str) -> str:
    parts = Path(source).parts
    return parts[0] if len(parts) > 1 else ""


def load_markdown_documents(docs_dir: Path) -> list[tuple[str, str]]:
    if not docs_dir.exists():
        raise FileNotFoundError(f"Business docs directory does not exist: {docs_dir}")

    markdown_files = sorted(docs_dir.rglob("*.md"))
    if not markdown_files:
        raise FileNotFoundError(f"No Markdown business documents found in: {docs_dir}")

    documents: list[tuple[str, str]] = []
    for path in markdown_files:
        text = path.read_text(encoding="utf-8").strip()
        if text:
            documents.append((path.relative_to(docs_dir).as_posix(), text))

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
            chunk_prefix = source_to_chunk_prefix(source)
            company = source_to_company(source)
            chunks.append(
                DocumentChunk(
                    chunk_id=f"{chunk_prefix}-{index:03d}",
                    source=source,
                    content=content,
                    metadata={"source": source, "chunk_index": index, "company": company},
                )
            )

    return chunks
