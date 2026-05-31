"""Stratified RAG evaluation summaries."""

from __future__ import annotations

from typing import Any

import pandas as pd

from ragbench.analysis.stats import bootstrap_ci


def stratified_summary(
    frame: pd.DataFrame,
    group_fields: list[str],
    metric: str = "overall_score",
    bootstrap_samples: int = 10000,
    alpha: float = 0.05,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    grouped = frame.groupby([*group_fields, "architecture"], dropna=False)
    intermediate: list[dict[str, Any]] = []
    for keys, group in grouped:
        if not isinstance(keys, tuple):
            keys = (keys,)
        group_values = dict(zip([*group_fields, "architecture"], keys))
        values = [float(value) for value in group[metric].dropna().tolist()]
        ci_low, ci_high = bootstrap_ci(values, samples=bootstrap_samples, alpha=alpha) if values else (None, None)
        intermediate.append(
            {
                **group_values,
                "n": len(group),
                "mean_overall_score": sum(values) / len(values) if values else None,
                "ci95_low": ci_low,
                "ci95_high": ci_high,
                "mean_latency_ms": _mean(group.get("latency_ms")),
                "p95_latency_ms": _quantile(group.get("latency_ms"), 0.95),
                "judge_error_count": int(group["judge_error"].notna().sum()) if "judge_error" in group else 0,
            }
        )

    by_group: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    for row in intermediate:
        key = tuple(row[field] for field in group_fields)
        by_group.setdefault(key, []).append(row)
    for key_rows in by_group.values():
        best = max(
            key_rows,
            key=lambda row: float(row["mean_overall_score"]) if row["mean_overall_score"] is not None else -1.0,
        )
        for row in key_rows:
            row["best_architecture_for_group"] = best["architecture"]
            row["practical_interpretation"] = _interpret_group_row(row, best)
            rows.append(row)
    return rows


def category_summary(
    frame: pd.DataFrame,
    bootstrap_samples: int,
    alpha: float,
) -> list[dict[str, Any]]:
    return stratified_summary(frame, ["category"], bootstrap_samples=bootstrap_samples, alpha=alpha)


def _interpret_group_row(row: dict[str, Any], best: dict[str, Any]) -> str:
    if row["architecture"] == best["architecture"]:
        return "best mean score in this stratum"
    if row["mean_overall_score"] is None or best["mean_overall_score"] is None:
        return "insufficient metric data"
    gap = best["mean_overall_score"] - row["mean_overall_score"]
    if gap < 0.01:
        return "performance is practically tied with best architecture"
    return f"trails best architecture by {gap:.4f} mean score"


def _mean(series: pd.Series | None) -> float | None:
    if series is None:
        return None
    values = [float(value) for value in series.dropna().tolist()]
    return sum(values) / len(values) if values else None


def _quantile(series: pd.Series | None, q: float) -> float | None:
    if series is None:
        return None
    values = sorted(float(value) for value in series.dropna().tolist())
    if not values:
        return None
    if len(values) == 1:
        return values[0]
    rank = q * (len(values) - 1)
    lower = int(rank)
    upper = min(lower + 1, len(values) - 1)
    weight = rank - lower
    return values[lower] * (1 - weight) + values[upper] * weight

