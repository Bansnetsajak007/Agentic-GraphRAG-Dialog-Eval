from pathlib import Path

from ragbench.loaders.document_loader import load_document_chunks, load_markdown_documents
from ragbench.utils.text import deterministic_chunks


def test_load_markdown_documents(tmp_path: Path) -> None:
    docs_dir = tmp_path / "business_docs"
    docs_dir.mkdir()
    (docs_dir / "policy.md").write_text("# Policy\n\nDelivery charge is NPR 60.", encoding="utf-8")

    documents = load_markdown_documents(docs_dir)

    assert documents == [("policy.md", "# Policy\n\nDelivery charge is NPR 60.")]


def test_load_document_chunks_adds_source_and_chunk_ids(tmp_path: Path) -> None:
    docs_dir = tmp_path / "business_docs"
    docs_dir.mkdir()
    (docs_dir / "policy.md").write_text("A" * 900, encoding="utf-8")

    chunks = load_document_chunks(docs_dir, chunk_size=500, overlap=100)

    assert len(chunks) == 2
    assert chunks[0].chunk_id == "policy-001"
    assert chunks[0].source == "policy.md"
    assert chunks[0].metadata["chunk_index"] == 1


def test_deterministic_chunks_overlap() -> None:
    chunks = deterministic_chunks("abcdefghij", chunk_size=6, overlap=2)

    assert chunks == ["abcdef", "efghij"]
