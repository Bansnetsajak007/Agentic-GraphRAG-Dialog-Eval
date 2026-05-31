"""Deterministic metric scoring for RAG evaluation outputs."""

from __future__ import annotations

import math
import re
from collections.abc import Mapping
from typing import Any

from ragbench.evaluators.architectures import safe_resolve_company_key
from ragbench.evaluators.metric_schemas import EvaluationDatasetItem, RAGResultItem


STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "is",
    "are",
    "to",
    "for",
    "of",
    "in",
    "on",
    "with",
    "mero",
    "ma",
    "ko",
    "ka",
    "ki",
    "ra",
    "yo",
    "k",
    "ke",
    "cha",
    "chha",
    "ho",
    "huncha",
    "garne",
    "kasari",
    "kata",
}

ROMANIZED_MARKERS = {
    "mero",
    "tapai",
    "tapaiko",
    "kasari",
    "kati",
    "kina",
    "kata",
    "cha",
    "chha",
    "huncha",
    "garna",
    "garne",
    "bhayo",
    "vayo",
    "paisa",
    "milcha",
    "parcha",
}

ENGLISH_SUPPORT_MARKERS = {
    "order",
    "refund",
    "payment",
    "delivery",
    "server",
    "domain",
    "ssl",
    "wallet",
    "account",
    "ticket",
    "support",
}

ESCALATION_TOPIC_MARKERS = {
    "complaint",
    "fraud",
    "abuse",
    "security",
    "incident",
    "chargeback",
    "unauthorized",
    "sla",
    "downtime",
    "legal",
    "risk",
}

ESCALATION_ANSWER_MARKERS = {
    "escalate",
    "ticket",
    "support team",
    "operations team",
    "security team",
    "review",
    "investigate",
    "case",
    "incident",
    "complaint",
}


def score_deterministic_metrics(
    dataset_item: EvaluationDatasetItem,
    result: RAGResultItem,
    company_map: Mapping[str, str],
    top_k: int | None = None,
) -> tuple[dict[str, float | None], dict[str, Any]]:
    chunks = result.retrieved_chunks[:top_k] if top_k else result.retrieved_chunks
    relevance = [_is_relevant_chunk(chunk, dataset_item, result) for chunk in chunks]
    has_relevance_target = _has_relevance_target(dataset_item, result)
    retrieved_count = len(chunks)
    source_documents = result.source_documents or [
        str(chunk.get("source") or "") for chunk in chunks if str(chunk.get("source") or "")
    ]

    metrics: dict[str, float | None] = {
        "context_precision": _context_precision(relevance, retrieved_count) if has_relevance_target else None,
        "context_recall": _context_recall(relevance, dataset_item, result) if has_relevance_target else None,
        "context_relevancy": _context_relevancy(dataset_item.query, dataset_item.expected_topic, chunks),
        "hit_rate_at_k": 1.0 if has_relevance_target and any(relevance) else (0.0 if has_relevance_target else None),
        "mrr_at_k": _mrr(relevance) if has_relevance_target else None,
        "ndcg_at_k": _ndcg(relevance) if has_relevance_target else None,
        "average_retrieved_chunks": float(retrieved_count),
        "faithfulness": _lexical_faithfulness(result.answer, chunks),
        "answer_relevancy": _lexical_overlap_score(dataset_item.query, result.answer),
        "answer_correctness": _answer_point_coverage(result.answer, dataset_item.expected_answer_points),
        "answer_completeness": _answer_point_coverage(result.answer, dataset_item.expected_answer_points),
        "hallucination_rate": None,
        "policy_compliance": None,
        "romanized_query_understanding": None,
        "code_mixed_handling": _code_mixed_handling(dataset_item, result),
        "intent_classification_accuracy": _intent_accuracy(dataset_item, result),
        "company_domain_accuracy": _company_domain_accuracy(dataset_item, result, company_map),
        "escalation_correctness": _escalation_correctness(dataset_item, result),
        "tone_appropriateness": None,
        "latency_ms": float(result.latency_ms or 0),
        "token_usage": _token_usage_value(result.token_usage),
        "agent_steps": _metadata_numeric(result.metadata, ("agent_steps", "steps", "num_agent_steps")),
        "tool_calls": _metadata_numeric(result.metadata, ("tool_calls", "num_tool_calls", "tools_called")),
        "success": 0.0 if result.error else 1.0,
        "failure": 1.0 if result.error else 0.0,
    }
    if metrics["faithfulness"] is not None:
        metrics["hallucination_rate"] = 1.0 - metrics["faithfulness"]

    evidence = {
        "has_relevance_target": has_relevance_target,
        "relevant_chunk_count": sum(1 for value in relevance if value),
        "retrieved_chunk_count": retrieved_count,
        "source_documents": sorted(set(source_documents)),
        "expected_topic": dataset_item.expected_topic or result.expected_topic,
        "expected_source_doc": dataset_item.expected_source_doc or result.expected_document,
    }
    return metrics, evidence


def _has_relevance_target(dataset_item: EvaluationDatasetItem, result: RAGResultItem) -> bool:
    return bool(dataset_item.expected_source_doc or result.expected_document or dataset_item.expected_topic or result.expected_topic)


def _is_relevant_chunk(
    chunk: dict[str, Any],
    dataset_item: EvaluationDatasetItem,
    result: RAGResultItem,
) -> bool:
    source = str(chunk.get("source") or "")
    chunk_id = str(chunk.get("chunk_id") or "")
    content = str(chunk.get("content") or "")
    metadata = chunk.get("metadata") if isinstance(chunk.get("metadata"), dict) else {}
    haystack = " ".join(
        [
            source,
            chunk_id,
            content[:1500],
            " ".join(str(value) for value in metadata.values()),
        ]
    ).lower()

    expected_source = (dataset_item.expected_source_doc or result.expected_document or "").lower()
    if expected_source:
        expected_source_clean = expected_source.replace("\\", "/")
        if expected_source_clean in source.lower() or expected_source_clean in chunk_id.lower():
            return True
        expected_tokens = _tokens(expected_source)
        source_tokens = _tokens(f"{source} {chunk_id}")
        if expected_tokens and len(expected_tokens & source_tokens) / len(expected_tokens) >= 0.6:
            return True

    expected_topic = dataset_item.expected_topic or result.expected_topic or ""
    topic_tokens = _tokens(expected_topic)
    if topic_tokens:
        source_tokens = _tokens(f"{source} {chunk_id} {' '.join(str(v) for v in metadata.values())}")
        content_tokens = _tokens(content[:1500])
        if topic_tokens & source_tokens:
            return True
        return len(topic_tokens & content_tokens) / len(topic_tokens) >= 0.5

    return False


def _context_precision(relevance: list[bool], retrieved_count: int) -> float | None:
    if retrieved_count == 0:
        return 0.0
    return sum(1 for value in relevance if value) / retrieved_count


def _context_recall(relevance: list[bool], dataset_item: EvaluationDatasetItem, result: RAGResultItem) -> float:
    expected_source = dataset_item.expected_source_doc or result.expected_document
    if expected_source:
        expected_count = max(1, len(_split_expected_sources(expected_source)))
        return min(1.0, sum(1 for value in relevance if value) / expected_count)
    return 1.0 if any(relevance) else 0.0


def _split_expected_sources(value: str) -> list[str]:
    return [item.strip() for item in re.split(r"[|;,]", value) if item.strip()]


def _context_relevancy(query: str, expected_topic: str | None, chunks: list[dict[str, Any]]) -> float | None:
    if not chunks:
        return 0.0
    target_tokens = _tokens(f"{query} {expected_topic or ''}")
    if not target_tokens:
        return None
    scores = []
    for chunk in chunks:
        chunk_tokens = _tokens(
            f"{chunk.get('source') or ''} {chunk.get('chunk_id') or ''} {str(chunk.get('content') or '')[:1500]}"
        )
        scores.append(_jaccard(target_tokens, chunk_tokens))
    return sum(scores) / len(scores) if scores else None


def _mrr(relevance: list[bool]) -> float:
    for index, is_relevant in enumerate(relevance, start=1):
        if is_relevant:
            return 1.0 / index
    return 0.0


def _ndcg(relevance: list[bool]) -> float:
    if not relevance:
        return 0.0
    gains = [1.0 if value else 0.0 for value in relevance]
    dcg = sum(gain / math.log2(index + 2) for index, gain in enumerate(gains))
    ideal = sorted(gains, reverse=True)
    idcg = sum(gain / math.log2(index + 2) for index, gain in enumerate(ideal))
    return dcg / idcg if idcg > 0 else 0.0


def _lexical_faithfulness(answer: str, chunks: list[dict[str, Any]]) -> float | None:
    answer_tokens = _tokens(answer)
    if not answer_tokens:
        return 0.0
    context_tokens = _tokens(" ".join(str(chunk.get("content") or "") for chunk in chunks))
    if not context_tokens:
        return None
    return min(1.0, len(answer_tokens & context_tokens) / max(1, len(answer_tokens)))


def _lexical_overlap_score(reference: str, answer: str) -> float | None:
    reference_tokens = _tokens(reference)
    answer_tokens = _tokens(answer)
    if not reference_tokens or not answer_tokens:
        return 0.0 if reference_tokens else None
    return min(1.0, len(reference_tokens & answer_tokens) / len(reference_tokens))


def _answer_point_coverage(answer: str, points: list[str]) -> float | None:
    if not points:
        return None
    answer_tokens = _tokens(answer)
    if not answer_tokens:
        return 0.0
    covered = 0
    for point in points:
        point_tokens = _tokens(point)
        if point_tokens and len(point_tokens & answer_tokens) / len(point_tokens) >= 0.5:
            covered += 1
    return covered / len(points)


def _code_mixed_handling(dataset_item: EvaluationDatasetItem, result: RAGResultItem) -> float | None:
    language_style = str(dataset_item.metadata.get("language_style") or result.metadata.get("language_style") or "").lower()
    query_tokens = _tokens(dataset_item.query)
    is_code_mixed = "mixed" in language_style or bool(query_tokens & ROMANIZED_MARKERS) and bool(query_tokens & ENGLISH_SUPPORT_MARKERS)
    if not is_code_mixed:
        return None
    return 0.0 if result.error or not result.answer.strip() else 1.0


def _intent_accuracy(dataset_item: EvaluationDatasetItem, result: RAGResultItem) -> float:
    return 1.0 if _normalize_label(dataset_item.category) == _normalize_label(result.category) else 0.0


def _company_domain_accuracy(
    dataset_item: EvaluationDatasetItem,
    result: RAGResultItem,
    company_map: Mapping[str, str],
) -> float:
    expected_company_key = safe_resolve_company_key(dataset_item.company, dict(company_map))
    if not expected_company_key:
        return 1.0 if _normalize_label(dataset_item.company) == _normalize_label(result.company) else 0.0
    return 1.0 if expected_company_key == result.company_key else 0.0


def _escalation_correctness(dataset_item: EvaluationDatasetItem, result: RAGResultItem) -> float | None:
    topic_query = f"{dataset_item.expected_topic or ''} {dataset_item.category} {dataset_item.query}".lower()
    answer = result.answer.lower()
    escalation_needed = any(marker in topic_query for marker in ESCALATION_TOPIC_MARKERS)
    has_escalation = any(marker in answer for marker in ESCALATION_ANSWER_MARKERS)
    if escalation_needed:
        return 1.0 if has_escalation else 0.0
    return 1.0 if not has_escalation else 0.5


def _token_usage_value(token_usage: dict[str, Any] | int | float | None) -> float | None:
    if token_usage is None:
        return None
    if isinstance(token_usage, int | float):
        return float(token_usage)
    for key in ("total_tokens", "total", "tokens"):
        value = token_usage.get(key)
        if isinstance(value, int | float):
            return float(value)
    numeric_values = [float(value) for value in token_usage.values() if isinstance(value, int | float)]
    return sum(numeric_values) if numeric_values else None


def _metadata_numeric(metadata: dict[str, Any], keys: tuple[str, ...]) -> float | None:
    for key in keys:
        value = metadata.get(key)
        if isinstance(value, int | float):
            return float(value)
    return None


def _tokens(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9]+", text.lower().replace("_", " ")) if token not in STOPWORDS}


def _jaccard(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def _normalize_label(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()
