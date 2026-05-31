"""Retrieval quality and evidence diagnostics."""

from __future__ import annotations

from typing import Any

import pandas as pd

from ragbench.analysis.schemas import RETRIEVAL_METRICS


def retrieval_quality_summary(frame: pd.DataFrame) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for architecture, group in frame.groupby("architecture"):
        rows.append(
            {
                "architecture": architecture,
                "mean_context_precision": _mean(group, "context_precision"),
                "mean_context_recall": _mean(group, "context_recall"),
                "mean_context_relevancy": _mean(group, "context_relevancy"),
                "hit_rate_at_k": _mean(group, "hit_rate_at_k"),
                "mrr_at_k": _mean(group, "mrr_at_k"),
                "ndcg_at_k": _mean(group, "ndcg_at_k"),
                "average_retrieved_chunks": _mean(group, "average_retrieved_chunks"),
                "missing_context_rate": float((group["average_retrieved_chunks"].fillna(0) == 0).mean()),
                "duplicate_chunk_rate": _duplicate_rate(group),
                "cross_company_contamination_rate": _cross_company_rate(group),
                "retrieval_answer_correlation": _correlation(
                    group[[metric for metric in RETRIEVAL_METRICS if metric in group]].mean(axis=1),
                    group["overall_score"],
                ),
                "context_recall_overall_correlation": _correlation(group.get("context_recall"), group["overall_score"]),
                "context_relevancy_overall_correlation": _correlation(group.get("context_relevancy"), group["overall_score"]),
            }
        )
    return rows


def annotate_retrieval_flags(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    frame["empty_retrieval"] = frame["average_retrieved_chunks"].fillna(0) == 0
    frame["over_retrieval"] = frame["average_retrieved_chunks"].fillna(0) > 6
    frame["retrieval_miss"] = frame["hit_rate_at_k"].fillna(1) < 0.5
    frame["irrelevant_retrieval"] = frame["context_relevancy"].fillna(1) < 0.03
    frame["duplicate_retrieval"] = frame["retrieved_chunk_ids"].map(lambda ids: len(ids) != len(set(ids)) if isinstance(ids, list) else False)
    frame["cross_company_contamination"] = frame.apply(_has_cross_company_source, axis=1)
    return frame


def _duplicate_rate(group: pd.DataFrame) -> float:
    flags = group["retrieved_chunk_ids"].map(lambda ids: len(ids) != len(set(ids)) if isinstance(ids, list) else False)
    return float(flags.mean()) if len(flags) else 0.0


def _cross_company_rate(group: pd.DataFrame) -> float:
    flags = group.apply(_has_cross_company_source, axis=1)
    return float(flags.mean()) if len(flags) else 0.0


def _has_cross_company_source(row: pd.Series) -> bool:
    company_key = str(row.get("company_key") or "").lower()
    source_documents = row.get("source_documents") or []
    if not company_key or not isinstance(source_documents, list):
        return False
    return any(str(source).split("/", 1)[0].lower() not in {"", company_key} for source in source_documents)


def _mean(group: pd.DataFrame, metric: str) -> float | None:
    if metric not in group:
        return None
    values = [float(value) for value in group[metric].dropna().tolist()]
    return sum(values) / len(values) if values else None


def _correlation(left: pd.Series | None, right: pd.Series | None) -> float | None:
    if left is None or right is None:
        return None
    pairs = [(float(a), float(b)) for a, b in zip(left.tolist(), right.tolist()) if pd.notna(a) and pd.notna(b)]
    if len(pairs) < 2:
        return None
    left_values = [a for a, _ in pairs]
    right_values = [b for _, b in pairs]
    left_mean = sum(left_values) / len(left_values)
    right_mean = sum(right_values) / len(right_values)
    numerator = sum((a - left_mean) * (b - right_mean) for a, b in pairs)
    left_denominator = sum((a - left_mean) ** 2 for a in left_values) ** 0.5
    right_denominator = sum((b - right_mean) ** 2 for b in right_values) ** 0.5
    if left_denominator == 0 or right_denominator == 0:
        return None
    return numerator / (left_denominator * right_denominator)

