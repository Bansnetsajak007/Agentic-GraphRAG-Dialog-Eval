"""Persistent Chroma indexing for Phase 1 semantic RAG."""

from __future__ import annotations

import hashlib
import json
import math
import os
import random
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any
from typing import Iterable

import httpx

from ragbench.schemas import DocumentChunk


class SentenceTransformerEmbedding:
    def __init__(self, model_name: str, fallback_dim: int = 384):
        self.model_name = model_name
        self.fallback_dim = fallback_dim
        self.backend = "auto"
        self.provider = os.getenv("EMBEDDING_PROVIDER", "sentence-transformers").lower()
        self.gemini = GeminiEmbeddingClient.from_env(model_name, fallback_dim)

    def encode(self, texts: list[str]) -> list[list[float]]:
        return self.encode_documents(texts)

    def encode_documents(self, texts: list[str], titles: list[str] | None = None) -> list[list[float]]:
        if self.provider == "gemini" or self.model_name.startswith("gemini-"):
            self.backend = "gemini"
            return self.gemini.encode_documents(texts, titles=titles)
        return self._encode_local(texts)

    def encode_query(self, query: str) -> list[float]:
        if self.provider == "gemini" or self.model_name.startswith("gemini-"):
            self.backend = "gemini"
            return self.gemini.encode_query(query)
        return self._encode_local([query])[0]

    def _encode_local(self, texts: list[str]) -> list[list[float]]:
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


class GeminiEmbeddingClient:
    def __init__(
        self,
        model_name: str,
        api_keys: tuple[str, ...],
        base_url: str,
        output_dimensionality: int,
        timeout_seconds: float = 60.0,
        max_retries: int = 8,
    ):
        self.model_name = model_name
        self.api_keys = self._dedupe_keys(api_keys)
        self.api_key = self.api_keys[0] if self.api_keys else None
        self.key_index = 0
        self.base_url = base_url.rstrip("/")
        self.output_dimensionality = output_dimensionality
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries

    @classmethod
    def from_env(cls, model_name: str, output_dimensionality: int) -> "GeminiEmbeddingClient":
        keys = []
        primary = os.getenv("GEMINI_API_KEY")
        if primary:
            keys.append(primary)
        keys.extend(key.strip() for key in os.getenv("GEMINI_API_KEYS", "").split(",") if key.strip())
        return cls(
            model_name=model_name,
            api_keys=tuple(keys),
            base_url=os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta"),
            output_dimensionality=int(os.getenv("EMBEDDING_DIMENSIONS", str(output_dimensionality))),
        )

    def encode_documents(self, texts: list[str], titles: list[str] | None = None) -> list[list[float]]:
        titles = titles or ["" for _ in texts]
        return [
            self._embed(text=f"title: {title} | text: {text}", task_type="RETRIEVAL_DOCUMENT")
            for title, text in zip(titles, texts)
        ]

    def encode_query(self, query: str) -> list[float]:
        return self._embed(text=f"task: question answering | query: {query}", task_type="RETRIEVAL_QUERY")

    def _embed(self, text: str, task_type: str) -> list[float]:
        if not self.api_key:
            raise RuntimeError("Gemini embedding selected but GEMINI_API_KEY/GEMINI_API_KEYS is not set.")

        payload: dict[str, Any] = {
            "content": {"parts": [{"text": text}]},
            "taskType": task_type,
            "outputDimensionality": self.output_dimensionality,
        }
        url = f"{self.base_url}/models/{self.model_name}:embedContent"
        last_error: Exception | None = None

        for attempt in range(self.max_retries + 1):
            try:
                response = httpx.post(
                    url,
                    headers={
                        "x-goog-api-key": self.api_key,
                        "Content-Type": "application/json",
                    },
                    json=payload,
                    timeout=self.timeout_seconds,
                )
                if response.status_code not in {429, 500, 502, 503, 504}:
                    response.raise_for_status()
                    return list(response.json()["embedding"]["values"])
                response.raise_for_status()
            except (httpx.HTTPStatusError, httpx.TimeoutException, httpx.TransportError) as exc:
                last_error = exc
                if attempt >= self.max_retries:
                    raise
                self._select_different_key()
                time.sleep(self._retry_sleep_seconds(exc, attempt))

        if last_error:
            raise last_error
        raise RuntimeError("Gemini embedding request failed without a response.")

    def _select_different_key(self) -> bool:
        if len(self.api_keys) <= 1:
            return False
        current_index = self.key_index
        choices = [index for index in range(len(self.api_keys)) if index != current_index]
        self.key_index = random.choice(choices)
        self.api_key = self.api_keys[self.key_index]
        return True

    @staticmethod
    def _dedupe_keys(keys: tuple[str, ...]) -> tuple[str, ...]:
        deduped: list[str] = []
        seen: set[str] = set()
        for key in keys:
            clean_key = key.strip()
            if clean_key and clean_key not in seen:
                deduped.append(clean_key)
                seen.add(clean_key)
        return tuple(deduped)

    @staticmethod
    def _retry_sleep_seconds(exc: Exception, attempt: int) -> float:
        if isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code == 429:
            retry_after = exc.response.headers.get("retry-after")
            if retry_after:
                try:
                    return min(float(retry_after), 90.0)
                except ValueError:
                    pass
            return 60.0
        return float(min(2**attempt, 8))


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


def company_collection_name(base_name: str, company: str) -> str:
    clean_company = re.sub(r"[^a-z0-9_]+", "_", company.lower()).strip("_")
    return f"{base_name}_{clean_company}" if clean_company else base_name


def rebuild_collection(persist_dir: Path, collection_name: str) -> Any:
    client = get_chroma_client(persist_dir)
    try:
        client.delete_collection(collection_name)
    except Exception:
        pass
    return client.get_or_create_collection(name=collection_name, metadata={"hnsw:space": "cosine"})


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

    embeddings = embedder.encode_documents(
        [chunk.content for chunk in new_chunks],
        titles=[chunk.source for chunk in new_chunks],
    )
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
