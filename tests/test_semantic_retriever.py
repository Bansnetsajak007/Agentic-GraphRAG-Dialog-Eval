from pathlib import Path

from ragbench.retrievers import semantic_retriever
from ragbench.retrievers.semantic_retriever import SemanticRetriever


class FakeCollection:
    def query(self, query_embeddings, n_results, include):
        return {
            "ids": [["delivery_policy-001"]],
            "documents": [["Inside Kathmandu Ring Road, delivery charge is NPR 60."]],
            "metadatas": [[{"source": "delivery_policy.md", "chunk_id": "delivery_policy-001"}]],
            "distances": [[0.12]],
        }


class FakeEmbedder:
    def __init__(self, model_name: str):
        self.model_name = model_name

    def encode(self, texts: list[str]) -> list[list[float]]:
        return [[0.1, 0.2, 0.3] for _ in texts]

    def encode_query(self, text: str) -> list[float]:
        return [0.1, 0.2, 0.3]


def test_semantic_retriever_returns_expected_structure(monkeypatch) -> None:
    monkeypatch.setattr(semantic_retriever, "get_or_create_collection", lambda *_args, **_kwargs: FakeCollection())
    monkeypatch.setattr(semantic_retriever, "SentenceTransformerEmbedding", FakeEmbedder)

    retriever = SemanticRetriever(
        persist_dir=Path(".chroma/test"),
        collection_name="test",
        embedding_model_name="fake-model",
    )
    results = retriever.retrieve("delivery charge kati ho?", top_k=1)

    assert len(results) == 1
    assert results[0].chunk_id == "delivery_policy-001"
    assert results[0].source == "delivery_policy.md"
    assert results[0].score == 0.12
    assert "delivery charge" in results[0].content
