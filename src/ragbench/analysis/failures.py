"""Automatic failure taxonomy for low-scoring RAG outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from ragbench.analysis.retrieval import annotate_retrieval_flags


FAILURE_TYPES = [
    "retrieval miss",
    "irrelevant retrieval",
    "partial answer",
    "hallucinated policy",
    "wrong company policy",
    "wrong action recommendation",
    "poor handling of complex Romanized Nepali",
    "ambiguity not clarified",
    "over-answering",
    "under-answering",
    "latency overhead without quality gain",
]


def build_failure_taxonomy(frame: pd.DataFrame) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    flagged = annotate_retrieval_flags(frame)
    latency_threshold = flagged["latency_ms"].quantile(0.95) if "latency_ms" in flagged else None
    rows: list[dict[str, Any]] = []
    representatives: list[dict[str, Any]] = []
    for architecture, group in flagged.groupby("architecture"):
        type_to_examples: dict[str, list[pd.Series]] = {failure_type: [] for failure_type in FAILURE_TYPES}
        for _idx, row in group.iterrows():
            failure_types = classify_failure(row, latency_threshold=latency_threshold)
            for failure_type in failure_types:
                type_to_examples[failure_type].append(row)
        for failure_type, examples in type_to_examples.items():
            rows.append(
                {
                    "architecture": architecture,
                    "failure_type": failure_type,
                    "count": len(examples),
                    "rate": len(examples) / len(group) if len(group) else 0.0,
                }
            )
            for example in sorted(examples, key=lambda item: float(item.get("overall_score") or 1.0))[:3]:
                representatives.append(_representative_payload(example, failure_type))
    return rows, representatives


def write_representative_failures(path: Path, representatives: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for item in representatives:
            handle.write(json.dumps(item, ensure_ascii=False) + "\n")


def classify_failure(row: pd.Series, latency_threshold: float | None) -> list[str]:
    failures: list[str] = []
    if float(row.get("overall_score") or 0.0) < 0.6:
        if bool(row.get("retrieval_miss")):
            failures.append("retrieval miss")
        if bool(row.get("irrelevant_retrieval")):
            failures.append("irrelevant retrieval")
        if _low(row.get("answer_completeness")):
            failures.append("partial answer")
        if _high(row.get("hallucination_rate")) or _low(row.get("faithfulness")):
            failures.append("hallucinated policy")
        if _low(row.get("company_domain_accuracy")) or bool(row.get("cross_company_contamination")):
            failures.append("wrong company policy")
        if _low(row.get("policy_compliance")):
            failures.append("wrong action recommendation")
        if str(row.get("difficulty") or "").lower() == "complex" and _low(row.get("romanized_query_understanding")):
            failures.append("poor handling of complex Romanized Nepali")
        if _low(row.get("answer_relevancy")):
            failures.append("ambiguity not clarified")
        if len(str(row.get("answer") or "").split()) > 120 and _low(row.get("answer_relevancy"), threshold=0.7):
            failures.append("over-answering")
        if len(str(row.get("answer") or "").split()) < 12 and _low(row.get("answer_completeness"), threshold=0.7):
            failures.append("under-answering")
    if latency_threshold is not None and float(row.get("latency_ms") or 0.0) >= latency_threshold:
        if str(row.get("architecture")) != "traditional_rag" and float(row.get("overall_score") or 0.0) < 0.75:
            failures.append("latency overhead without quality gain")
    return sorted(set(failures))


def underperformance_rows(frame: pd.DataFrame) -> pd.DataFrame:
    pivot = frame.pivot(index="query_id", columns="architecture", values="overall_score")
    underperforming_ids = set()
    for architecture in ("agentic_rag", "agentic_graph_rag"):
        if architecture in pivot and "traditional_rag" in pivot:
            ids = pivot[pivot[architecture] < pivot["traditional_rag"]]["query_id"] if "query_id" in pivot else []
            underperforming_ids.update(ids)
    return frame[frame["query_id"].isin(underperforming_ids)]


def _representative_payload(row: pd.Series, failure_type: str) -> dict[str, Any]:
    return {
        "architecture": row.get("architecture"),
        "query_id": row.get("query_id"),
        "company": row.get("company"),
        "difficulty": row.get("difficulty"),
        "category": row.get("category"),
        "failure_type": failure_type,
        "overall_score": row.get("overall_score"),
        "faithfulness": row.get("faithfulness"),
        "answer_relevancy": row.get("answer_relevancy"),
        "context_relevancy": row.get("context_relevancy"),
        "latency_ms": row.get("latency_ms"),
        "query": row.get("query"),
        "answer_excerpt": str(row.get("answer") or "")[:500],
        "source_documents": row.get("source_documents"),
    }


def _low(value: Any, threshold: float = 0.5) -> bool:
    return value is not None and pd.notna(value) and float(value) < threshold


def _high(value: Any, threshold: float = 0.5) -> bool:
    return value is not None and pd.notna(value) and float(value) > threshold

