"""Load, normalize, and validate detailed RAG metric JSONL files."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from ragbench.analysis.schemas import (
    ARCHITECTURES,
    COUNT_METRICS,
    GENERATION_METRICS,
    LATENCY_METRICS,
    METRIC_ALIASES,
    PREFERRED_METRICS,
    RETRIEVAL_METRICS,
    ROMANIZED_METRICS,
    SCORE_METRICS,
)


@dataclass(frozen=True)
class LoadedAnalysisData:
    frame: pd.DataFrame
    validation_summary: dict[str, Any]
    available_metrics: list[str]
    unavailable_metrics: list[str]


def load_analysis_data(results_dir: Path, architectures: tuple[str, ...] = ARCHITECTURES) -> LoadedAnalysisData:
    rows: list[dict[str, Any]] = []
    raw_by_arch: dict[str, list[dict[str, Any]]] = {}
    for architecture in architectures:
        path = results_dir / architecture / "rag_metrics_detailed.jsonl"
        raw_rows = _load_jsonl(path)
        raw_by_arch[architecture] = raw_rows
        for payload in raw_rows:
            rows.append(_normalize_payload(payload, architecture))

    frame = pd.DataFrame(rows)
    available_metrics = [metric for metric in PREFERRED_METRICS if metric in frame.columns and frame[metric].notna().any()]
    unavailable_metrics = [metric for metric in PREFERRED_METRICS if metric not in available_metrics]
    validation = validate_alignment(raw_by_arch, frame, architectures)
    validation["available_metrics"] = available_metrics
    validation["unavailable_metrics"] = unavailable_metrics
    return LoadedAnalysisData(
        frame=frame,
        validation_summary=validation,
        available_metrics=available_metrics,
        unavailable_metrics=unavailable_metrics,
    )


def validate_alignment(
    raw_by_arch: dict[str, list[dict[str, Any]]],
    frame: pd.DataFrame,
    architectures: tuple[str, ...] = ARCHITECTURES,
) -> dict[str, Any]:
    validation: dict[str, Any] = {
        "architectures": {},
        "query_id_alignment": {"valid": True, "mismatches": []},
        "field_alignment": {"valid": True, "mismatches": []},
        "metric_validation": {"malformed_scores": [], "missing_counts": {}},
        "valid": True,
    }

    query_sets: dict[str, set[str]] = {}
    for architecture in architectures:
        rows = raw_by_arch.get(architecture, [])
        query_ids = [str(row.get("query_id") or "") for row in rows]
        duplicate_query_ids = sorted({query_id for query_id in query_ids if query_ids.count(query_id) > 1})
        judge_errors = sum(1 for row in rows if (row.get("judge") or {}).get("error"))
        judge_models = sorted({str((row.get("judge") or {}).get("model")) for row in rows if (row.get("judge") or {}).get("model")})
        validation["architectures"][architecture] = {
            "row_count": len(rows),
            "expected_row_count": 300,
            "row_count_valid": len(rows) == 300,
            "duplicate_query_ids": duplicate_query_ids,
            "judge_error_count": judge_errors,
            "judge_error_rate": judge_errors / len(rows) if rows else None,
            "judge_model": ", ".join(judge_models) if judge_models else None,
        }
        if len(rows) != 300 or duplicate_query_ids:
            validation["valid"] = False
        query_sets[architecture] = set(query_ids)

    if query_sets:
        reference_arch = architectures[0]
        reference = query_sets.get(reference_arch, set())
        for architecture, query_set in query_sets.items():
            if query_set != reference:
                validation["query_id_alignment"]["valid"] = False
                validation["query_id_alignment"]["mismatches"].append(
                    {
                        "architecture": architecture,
                        "missing_from_architecture": sorted(reference - query_set)[:20],
                        "extra_in_architecture": sorted(query_set - reference)[:20],
                    }
                )
                validation["valid"] = False

    alignment_fields = ["company", "difficulty", "query", "category"]
    if all(query_sets.get(architecture) == query_sets.get(architectures[0]) for architecture in architectures):
        for query_id in sorted(query_sets.get(architectures[0], set())):
            per_arch = frame[frame["query_id"] == query_id]
            for field in alignment_fields:
                values = sorted({str(value) for value in per_arch[field].dropna().tolist()})
                if len(values) > 1:
                    validation["field_alignment"]["valid"] = False
                    validation["field_alignment"]["mismatches"].append(
                        {"query_id": query_id, "field": field, "values": values}
                    )
                    validation["valid"] = False

    for metric in [column for column in frame.columns if column in SCORE_METRICS | LATENCY_METRICS | COUNT_METRICS]:
        missing_count = int(frame[metric].isna().sum())
        if missing_count:
            validation["metric_validation"]["missing_counts"][metric] = missing_count
        if metric in SCORE_METRICS:
            bad = frame[frame[metric].notna() & ((frame[metric] < 0.0) | (frame[metric] > 1.0))]
            if not bad.empty:
                validation["metric_validation"]["malformed_scores"].append(
                    {"metric": metric, "count": int(len(bad)), "query_ids": bad["query_id"].head(20).tolist()}
                )
                validation["valid"] = False
    return validation


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Detailed metric file not found: {path}")
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Malformed JSONL in {path} at line {line_number}: {exc}") from exc
            if not isinstance(payload, dict):
                raise ValueError(f"Expected JSON object in {path} at line {line_number}.")
            rows.append(payload)
    return rows


def _normalize_payload(payload: dict[str, Any], architecture: str) -> dict[str, Any]:
    row: dict[str, Any] = {
        "architecture": str(payload.get("architecture") or architecture),
        "query_id": str(payload.get("query_id") or ""),
        "company": str(payload.get("company") or ""),
        "company_key": payload.get("company_key"),
        "difficulty": str(payload.get("difficulty") or ""),
        "category": str(payload.get("category") or ""),
        "query": str(payload.get("query") or ""),
        "answer": str(payload.get("answer") or ""),
        "error": payload.get("error"),
        "judge_error": (payload.get("judge") or {}).get("error"),
        "judge_enabled": bool((payload.get("judge") or {}).get("enabled")),
        "judge_model": (payload.get("judge") or {}).get("model"),
        "expected_topic": payload.get("expected_topic"),
        "expected_source_doc": payload.get("expected_source_doc"),
        "retrieved_chunk_ids": payload.get("retrieved_chunk_ids") or [],
        "source_documents": payload.get("source_documents") or [],
    }
    metrics = payload.get("metrics") or {}
    if not isinstance(metrics, dict):
        raise ValueError(f"Record {row['query_id']} has non-object metrics.")
    for raw_name, value in metrics.items():
        canonical = METRIC_ALIASES.get(str(raw_name), str(raw_name))
        row[canonical] = _numeric_or_none(value)
    row["retrieved_chunk_count"] = len(row["retrieved_chunk_ids"])
    row["source_document_count"] = len(row["source_documents"])
    if "average_retrieved_chunks" not in row or row["average_retrieved_chunks"] is None:
        row["average_retrieved_chunks"] = float(row["retrieved_chunk_count"])
    row["overall_score"] = _compute_overall_score(row)
    return row


def _numeric_or_none(value: Any) -> float | None:
    if value is None:
        return None
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    return numeric if math.isfinite(numeric) else None


def _compute_overall_score(row: dict[str, Any]) -> float | None:
    if row.get("overall_score") is not None:
        return row["overall_score"]
    retrieval = _mean(row.get(metric) for metric in RETRIEVAL_METRICS)
    generation_values = []
    for metric in GENERATION_METRICS:
        value = row.get(metric)
        if value is None:
            continue
        generation_values.append(1.0 - value if metric == "hallucination_rate" else value)
    generation = _mean(generation_values)
    romanized = _mean(row.get(metric) for metric in ROMANIZED_METRICS)
    operational = row.get("success")
    return _mean([retrieval, generation, romanized, operational])


def _mean(values: Any) -> float | None:
    numeric = [float(value) for value in values if value is not None and not pd.isna(value)]
    return sum(numeric) / len(numeric) if numeric else None
