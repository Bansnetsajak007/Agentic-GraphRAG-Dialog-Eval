"""Traditional semantic vector retriever."""

from __future__ import annotations

from pathlib import Path

from ragbench.indexing.chroma_index import SentenceTransformerEmbedding, get_or_create_collection
from ragbench.schemas import RetrievedChunk


class SemanticRetriever:
    def __init__(
        self,
        persist_dir: Path,
        collection_name: str,
        embedding_model_name: str,
        top_k: int = 4,
    ):
        self.collection = get_or_create_collection(persist_dir, collection_name)
        self.embedder = SentenceTransformerEmbedding(embedding_model_name)
        self.top_k = top_k

    def retrieve(self, query: str, top_k: int | None = None) -> list[RetrievedChunk]:
        k = top_k or self.top_k
        query_embedding = self.embedder.encode([query])[0]
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            include=["documents", "metadatas", "distances"],
        )

        ids = results.get("ids", [[]])[0]
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        retrieved: list[RetrievedChunk] = []
        for chunk_id, content, metadata, distance in zip(ids, documents, metadatas, distances):
            metadata = metadata or {}
            retrieved.append(
                RetrievedChunk(
                    chunk_id=str(metadata.get("chunk_id") or chunk_id),
                    source=str(metadata.get("source") or ""),
                    content=content or "",
                    score=float(distance) if distance is not None else None,
                    metadata=dict(metadata),
                )
            )
        return retrieved
