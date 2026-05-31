"""Quality-latency trade-off analysis."""

from __future__ import annotations

from typing import Any

import pandas as pd


def latency_quality_tradeoff(frame: pd.DataFrame) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    summaries: dict[str, dict[str, Any]] = {}
    for architecture, group in frame.groupby("architecture"):
        latencies = sorted(float(value) for value in group["latency_ms"].dropna().tolist())
        summaries[architecture] = {
            "architecture": architecture,
            "mean_quality_score": _mean(group["overall_score"]),
            "mean_latency_ms": _mean(group["latency_ms"]),
            "p95_latency_ms": _quantile(latencies, 0.95),
        }
    baseline = summaries.get("traditional_rag")
    for architecture, row in sorted(summaries.items()):
        if baseline:
            quality_gain = row["mean_quality_score"] - baseline["mean_quality_score"]
            latency_overhead = row["mean_latency_ms"] - baseline["mean_latency_ms"]
            row["quality_gain_over_traditional_rag"] = quality_gain
            row["latency_overhead_ms_over_traditional_rag"] = latency_overhead
            row["quality_gain_per_extra_second"] = (
                quality_gain / (latency_overhead / 1000.0) if latency_overhead and latency_overhead > 0 else None
            )
        else:
            row["quality_gain_over_traditional_rag"] = None
            row["latency_overhead_ms_over_traditional_rag"] = None
            row["quality_gain_per_extra_second"] = None
        rows.append(row)
    best_quality = max(rows, key=lambda row: row["mean_quality_score"] if row["mean_quality_score"] is not None else -1)
    fastest = min(rows, key=lambda row: row["mean_latency_ms"] if row["mean_latency_ms"] is not None else float("inf"))
    best_tradeoff = max(
        rows,
        key=lambda row: (
            row["mean_quality_score"] / (row["mean_latency_ms"] / 1000.0)
            if row["mean_quality_score"] is not None and row["mean_latency_ms"]
            else -1
        ),
    )
    for row in rows:
        row["best_quality_architecture"] = best_quality["architecture"]
        row["fastest_architecture"] = fastest["architecture"]
        row["best_quality_latency_tradeoff"] = best_tradeoff["architecture"]
    return rows


def _mean(series: pd.Series) -> float | None:
    values = [float(value) for value in series.dropna().tolist()]
    return sum(values) / len(values) if values else None


def _quantile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    if len(values) == 1:
        return values[0]
    rank = q * (len(values) - 1)
    lower = int(rank)
    upper = min(lower + 1, len(values) - 1)
    weight = rank - lower
    return values[lower] * (1 - weight) + values[upper] * weight

