"""Typed data structures shared by the Phase 1 baseline."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class DocumentChunk(BaseModel):
    chunk_id: str
    source: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class RetrievedChunk(BaseModel):
    chunk_id: str
    source: str
    content: str
    score: float | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvalQuery(BaseModel):
    id: str
    query: str
    intent: str = ""
    language_type: str = ""
    query_type: str = ""
    requires_clarification: bool = False
    difficulty: str = ""
    expected_answer: str = ""
    required_docs: str = ""
    required_facts: str = ""
    notes: str = ""


class EvaluationQuery(BaseModel):
    """Normalized query row from the Romanized Nepali RAG evaluation dataset."""

    query_id: str
    company: str
    query: str
    difficulty: str
    category: str
    expected_document: str | None = None
    expected_topic: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class Prediction(BaseModel):
    model_config = ConfigDict(coerce_numbers_to_str=False)

    id: str
    system: str = "semantic_rag"
    query: str
    intent: str = ""
    retrieved_context: list[RetrievedChunk]
    answer: str
    latency_ms: int
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvaluationResult(BaseModel):
    """JSONL output record for architecture evaluation runs."""

    model_config = ConfigDict(coerce_numbers_to_str=False)

    query_id: str
    architecture: str
    company: str
    company_key: str | None = None
    query: str
    difficulty: str
    category: str
    expected_document: str | None = None
    expected_topic: str | None = None
    answer: str = ""
    retrieved_chunks: list[RetrievedChunk] = Field(default_factory=list)
    source_documents: list[str] = Field(default_factory=list)
    latency_ms: int = 0
    token_usage: dict[str, int] | None = None
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
