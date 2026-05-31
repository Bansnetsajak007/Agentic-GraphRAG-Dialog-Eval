"""Typed structures for post-hoc RAG evaluation metrics."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


ARCHITECTURES = ("traditional_rag", "agentic_rag", "agentic_graph_rag")

RETRIEVAL_METRICS = [
    "context_precision",
    "context_recall",
    "context_relevancy",
    "hit_rate_at_k",
    "mrr_at_k",
    "ndcg_at_k",
    "average_retrieved_chunks",
]

GENERATION_METRICS = [
    "faithfulness",
    "answer_relevancy",
    "answer_correctness",
    "answer_completeness",
    "hallucination_rate",
    "policy_compliance",
]

ROMANIZED_METRICS = [
    "romanized_query_understanding",
    "code_mixed_handling",
    "intent_classification_accuracy",
    "company_domain_accuracy",
    "escalation_correctness",
    "tone_appropriateness",
]

OPERATIONAL_METRICS = [
    "success_rate",
    "failure_rate",
    "average_latency_ms",
    "p50_latency_ms",
    "p95_latency_ms",
    "average_token_usage",
    "average_agent_steps",
    "average_tool_calls",
]

PER_QUERY_METRICS = RETRIEVAL_METRICS + GENERATION_METRICS + ROMANIZED_METRICS + [
    "latency_ms",
    "token_usage",
    "agent_steps",
    "tool_calls",
    "success",
    "failure",
]

SUMMARY_METRICS = RETRIEVAL_METRICS + GENERATION_METRICS + ROMANIZED_METRICS + OPERATIONAL_METRICS


class EvaluationDatasetItem(BaseModel):
    model_config = ConfigDict(coerce_numbers_to_str=False)

    query_id: str
    company: str
    query: str
    difficulty: str
    category: str
    expected_topic: str | None = None
    expected_source_doc: str | None = None
    expected_answer_points: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class RAGResultItem(BaseModel):
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
    retrieved_chunks: list[dict[str, Any]] = Field(default_factory=list)
    source_documents: list[str] = Field(default_factory=list)
    latency_ms: int = 0
    token_usage: dict[str, Any] | int | float | None = None
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class PerQueryMetricResult(BaseModel):
    model_config = ConfigDict(coerce_numbers_to_str=False)

    query_id: str
    architecture: str
    company: str
    company_key: str | None = None
    difficulty: str
    category: str
    query: str
    answer: str
    metrics: dict[str, float | None]
    expected_topic: str | None = None
    expected_source_doc: str | None = None
    expected_answer_points: list[str] = Field(default_factory=list)
    retrieved_chunk_ids: list[str] = Field(default_factory=list)
    source_documents: list[str] = Field(default_factory=list)
    judge: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
