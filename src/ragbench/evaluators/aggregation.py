"""Aggregate per-query RAG metric records into research summaries."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable

from ragbench.evaluators.metric_schemas import (
    GENERATION_METRICS,
    OPERATIONAL_METRICS,
    PER_QUERY_METRICS,
    RETRIEVAL_METRICS,
    ROMANIZED_METRICS,
    SUMMARY_METRICS,
    PerQueryMetricResult,
)


BASE_SUMMARY_FIELDS = [
    "architecture",
    "company",
    "difficulty",
    "total_queries",
    "successful_queries",
    "failed_queries",
]

COMPOSITE_FIELDS = [
    "retrieval_quality_score",
    "generation_quality_score",
    "romanized_robustness_score",
    "operational_quality_score",
    "overall_score",
]

SUMMARY_FIELDS = BASE_SUMMARY_FIELDS + SUMMARY_METRICS + COMPOSITE_FIELDS


def summarize_by_architecture(records: list[PerQueryMetricResult]) -> list[dict[str, Any]]:
    return _summarize_grouped(records, keys=("architecture",))


def summarize_by_company(records: list[PerQueryMetricResult]) -> list[dict[str, Any]]:
    return _summarize_grouped(records, keys=("architecture", "company"))


def summarize_by_difficulty(records: list[PerQueryMetricResult]) -> list[dict[str, Any]]:
    return _summarize_grouped(records, keys=("architecture", "difficulty"))


def _summarize_grouped(records: list[PerQueryMetricResult], keys: tuple[str, ...]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, ...], list[PerQueryMetricResult]] = defaultdict(list)
    for record in records:
        grouped[tuple(str(getattr(record, key)) for key in keys)].append(record)

    rows: list[dict[str, Any]] = []
    for group_values, group_records in sorted(grouped.items()):
        row = _summarize_records(group_records)
        for key, value in zip(keys, group_values):
            row[key] = value
        for field in ("architecture", "company", "difficulty"):
            row.setdefault(field, "ALL")
        rows.append(row)
    return rows


def _summarize_records(records: list[PerQueryMetricResult]) -> dict[str, Any]:
    total = len(records)
    failed = sum(1 for record in records if record.error)
    successful = total - failed
    row: dict[str, Any] = {
        "total_queries": total,
        "successful_queries": successful,
        "failed_queries": failed,
        "success_rate": successful / total if total else None,
        "failure_rate": failed / total if total else None,
    }
    latencies = [_metric(record, "latency_ms") for record in records]
    latency_values = [value for value in latencies if value is not None]
    row["average_latency_ms"] = _mean(latency_values)
    row["p50_latency_ms"] = _percentile(latency_values, 50)
    row["p95_latency_ms"] = _percentile(latency_values, 95)
    row["average_token_usage"] = _mean_metric(records, "token_usage")
    row["average_agent_steps"] = _mean_metric(records, "agent_steps")
    row["average_tool_calls"] = _mean_metric(records, "tool_calls")

    for metric in SUMMARY_METRICS:
        if metric in OPERATIONAL_METRICS:
            continue
        row[metric] = _mean_metric(records, metric)

    row["retrieval_quality_score"] = _category_score(row, RETRIEVAL_METRICS, invert=())
    row["generation_quality_score"] = _category_score(row, GENERATION_METRICS, invert=("hallucination_rate",))
    row["romanized_robustness_score"] = _category_score(row, ROMANIZED_METRICS, invert=())
    row["operational_quality_score"] = row.get("success_rate")
    row["overall_score"] = _mean(
        [
            row.get("retrieval_quality_score"),
            row.get("generation_quality_score"),
            row.get("romanized_robustness_score"),
            row.get("operational_quality_score"),
        ]
    )
    return row


def error_analysis(records: list[PerQueryMetricResult]) -> dict[str, Any]:
    failure_count = sum(1 for record in records if record.error)
    no_retrieval = sum(1 for record in records if (record.metrics.get("average_retrieved_chunks") or 0) == 0)
    low_hit_rate = sum(1 for record in records if _low(record.metrics.get("hit_rate_at_k")))
    low_faithfulness = sum(1 for record in records if _low(record.metrics.get("faithfulness")))
    low_answer_relevancy = sum(1 for record in records if _low(record.metrics.get("answer_relevancy")))
    low_tone = sum(1 for record in records if _low(record.metrics.get("tone_appropriateness")))
    return {
        "total_records": len(records),
        "failure_count": failure_count,
        "no_retrieval_count": no_retrieval,
        "low_hit_rate_count": low_hit_rate,
        "low_faithfulness_count": low_faithfulness,
        "low_answer_relevancy_count": low_answer_relevancy,
        "low_tone_appropriateness_count": low_tone,
    }


def metric_fieldnames(include_group_fields: tuple[str, ...]) -> list[str]:
    fields = ["architecture", *[field for field in include_group_fields if field != "architecture"]]
    fields.extend(field for field in SUMMARY_FIELDS if field not in fields)
    return fields


def _mean_metric(records: Iterable[PerQueryMetricResult], metric: str) -> float | None:
    return _mean([_metric(record, metric) for record in records])


def _metric(record: PerQueryMetricResult, metric: str) -> float | None:
    value = record.metrics.get(metric)
    if value is None:
        return None
    return float(value)


def _mean(values: Iterable[float | None]) -> float | None:
    numeric = [float(value) for value in values if value is not None]
    return sum(numeric) / len(numeric) if numeric else None


def _percentile(values: list[float], percentile: int) -> float | None:
    if not values:
        return None
    sorted_values = sorted(values)
    if len(sorted_values) == 1:
        return sorted_values[0]
    rank = (percentile / 100) * (len(sorted_values) - 1)
    lower = int(rank)
    upper = min(lower + 1, len(sorted_values) - 1)
    weight = rank - lower
    return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight


def _category_score(row: dict[str, Any], metrics: list[str], invert: tuple[str, ...]) -> float | None:
    values: list[float | None] = []
    for metric in metrics:
        if metric == "average_retrieved_chunks":
            continue
        value = row.get(metric)
        if value is None:
            continue
        values.append(1.0 - float(value) if metric in invert else float(value))
    return _mean(values)


def _low(value: float | None, threshold: float = 0.5) -> bool:
    return value is not None and value < threshold
