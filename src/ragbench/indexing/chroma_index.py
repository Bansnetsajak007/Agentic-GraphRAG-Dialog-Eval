"""Persistent Chroma indexing for Phase 1 semantic RAG."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any
from typing import Iterable

from ragbench.schemas import DocumentChunk


class SentenceTransformerEmbedding:
    def __init__(self, model_name: str, fallback_dim: int = 384):
        self.model_name = model_name
        self.fallback_dim = fallback_dim
        self.backend = "auto"

    def encode(self, texts: list[str]) -> list[list[float]]:
        backend = os.getenv("RAGBENCH_EMBEDDING_BACKEND", "auto").lower()
        if backend == "hash" or self.backend in {"hash", "hash_fallback"}:
            self.backend = "hash"
            return [hash_embedding(text, dim=self.fallback_dim) for text in texts]

        try:
            vectors = encode_with_sentence_transformers_worker(
                texts,
                self.model_name,
                timeout_seconds=float(os.getenv("RAGBENCH_ST_TIMEOUT_SECONDS", "20")),
            )
            self.backend = "sentence-transformers"
            return vectors
        except Exception:
            self.backend = "hash_fallback"
            return [hash_embedding(text, dim=self.fallback_dim) for text in texts]


def hash_embedding(text: str, dim: int = 384) -> list[float]:
    """Deterministic local embedding fallback for constrained environments."""

    tokens = re.findall(r"[a-z0-9]+", text.lower())
    if not tokens:
        tokens = [text.lower()]

    vector = [0.0] * dim
    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
        index = int(digest[:8], 16) % dim
        sign = 1.0 if int(digest[8:10], 16) % 2 else -1.0
        vector[index] += sign

    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [value / norm for value in vector]


def encode_with_sentence_transformers_worker(
    texts: list[str],
    model_name: str,
    timeout_seconds: float,
) -> list[list[float]]:
    resolved_name = model_name.removeprefix("sentence-transformers/")
    worker_code = """
import json
import sys

from sentence_transformers import SentenceTransformer

payload = json.loads(sys.stdin.read())
model = SentenceTransformer(payload["model_name"])
vectors = model.encode(payload["texts"], normalize_embeddings=True, show_progress_bar=False)
print(json.dumps(vectors.tolist()))
"""
    completed = subprocess.run(
        [sys.executable, "-c", worker_code],
        input=json.dumps({"model_name": resolved_name, "texts": texts}),
        text=True,
        capture_output=True,
        timeout=timeout_seconds,
        check=True,
    )
    return json.loads(completed.stdout)


def get_chroma_client(persist_dir: Path) -> Any:
    import chromadb

    persist_dir.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(persist_dir))


def get_or_create_collection(persist_dir: Path, collection_name: str) -> Any:
    client = get_chroma_client(persist_dir)
    return client.get_or_create_collection(name=collection_name, metadata={"hnsw:space": "cosine"})


def rebuild_collection(persist_dir: Path, collection_name: str) -> Any:
    if persist_dir.exists():
        shutil.rmtree(persist_dir)
    return get_or_create_collection(persist_dir, collection_name)


def build_chroma_index(
    chunks: Iterable[DocumentChunk],
    persist_dir: Path,
    collection_name: str,
    embedding_model_name: str,
    rebuild: bool = False,
) -> int:
    collection = rebuild_collection(persist_dir, collection_name) if rebuild else get_or_create_collection(persist_dir, collection_name)
    embedder = SentenceTransformerEmbedding(embedding_model_name)
    chunk_list = list(chunks)
    if not chunk_list:
        raise ValueError("No document chunks were provided for indexing.")

    existing_ids: set[str] = set()
    if not rebuild:
        current = collection.get(include=[])
        existing_ids = set(current.get("ids", []))

    new_chunks = [chunk for chunk in chunk_list if chunk.chunk_id not in existing_ids]
    if not new_chunks:
        return 0

    embeddings = embedder.encode([chunk.content for chunk in new_chunks])
    collection.add(
        ids=[chunk.chunk_id for chunk in new_chunks],
        documents=[chunk.content for chunk in new_chunks],
        metadatas=[
            {
                "source": chunk.source,
                "chunk_id": chunk.chunk_id,
                **{key: value for key, value in chunk.metadata.items() if isinstance(value, str | int | float | bool)},
            }
            for chunk in new_chunks
        ],
        embeddings=embeddings,
    )
    return len(new_chunks)
