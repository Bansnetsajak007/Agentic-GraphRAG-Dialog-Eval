"""Descriptive and paired statistical tests for RAG architecture comparison."""

from __future__ import annotations

import math
import random
from itertools import combinations
from typing import Any, Iterable

import pandas as pd

from ragbench.analysis.schemas import ARCHITECTURES


def bootstrap_ci(
    values: Iterable[float],
    samples: int = 10000,
    alpha: float = 0.05,
    seed: int = 1337,
) -> tuple[float | None, float | None]:
    numeric = [float(value) for value in values if value is not None and not pd.isna(value)]
    if not numeric:
        return None, None
    rng = random.Random(seed)
    n = len(numeric)
    means = []
    for _ in range(samples):
        means.append(sum(numeric[rng.randrange(n)] for _ in range(n)) / n)
    means.sort()
    return _quantile(means, alpha / 2), _quantile(means, 1 - alpha / 2)


def paired_bootstrap_diff_ci(
    left: list[float],
    right: list[float],
    samples: int = 10000,
    alpha: float = 0.05,
    seed: int = 1337,
) -> tuple[float, float]:
    diffs = [a - b for a, b in zip(left, right) if not pd.isna(a) and not pd.isna(b)]
    if not diffs:
        return math.nan, math.nan
    rng = random.Random(seed)
    n = len(diffs)
    means = []
    for _ in range(samples):
        means.append(sum(diffs[rng.randrange(n)] for _ in range(n)) / n)
    means.sort()
    return float(_quantile(means, alpha / 2)), float(_quantile(means, 1 - alpha / 2))


def paired_permutation_test(
    left: list[float],
    right: list[float],
    samples: int = 10000,
    seed: int = 1337,
) -> float:
    diffs = [a - b for a, b in zip(left, right) if not pd.isna(a) and not pd.isna(b)]
    if not diffs:
        return math.nan
    observed = abs(sum(diffs) / len(diffs))
    if observed == 0:
        return 1.0
    rng = random.Random(seed)
    extreme = 0
    for _ in range(samples):
        permuted_mean = sum(diff if rng.random() < 0.5 else -diff for diff in diffs) / len(diffs)
        if abs(permuted_mean) >= observed:
            extreme += 1
    return (extreme + 1) / (samples + 1)


def cohens_dz(left: list[float], right: list[float]) -> float | None:
    diffs = [a - b for a, b in zip(left, right) if not pd.isna(a) and not pd.isna(b)]
    if len(diffs) < 2:
        return None
    mean_diff = sum(diffs) / len(diffs)
    std_diff = _sample_std(diffs)
    if std_diff == 0:
        return 0.0 if mean_diff == 0 else math.copysign(math.inf, mean_diff)
    return mean_diff / std_diff


def cliffs_delta(left: list[float], right: list[float]) -> float | None:
    pairs = [(a, b) for a, b in zip(left, right) if not pd.isna(a) and not pd.isna(b)]
    if not pairs:
        return None
    wins = sum(1 for a, b in pairs if a > b)
    losses = sum(1 for a, b in pairs if a < b)
    return (wins - losses) / len(pairs)


def wilcoxon_p_value(left: list[float], right: list[float]) -> float | None:
    try:
        from scipy.stats import wilcoxon
    except Exception:
        return None
    pairs = [(a, b) for a, b in zip(left, right) if not pd.isna(a) and not pd.isna(b)]
    if not pairs:
        return None
    diffs = [a - b for a, b in pairs]
    if all(diff == 0 for diff in diffs):
        return 1.0
    try:
        return float(wilcoxon([a for a, _b in pairs], [b for _a, b in pairs], zero_method="wilcox").pvalue)
    except Exception:
        return None


def holm_bonferroni(p_values: dict[str, float], alpha: float = 0.05) -> dict[str, dict[str, float | bool]]:
    valid_items = [(key, value) for key, value in p_values.items() if value is not None and not math.isnan(value)]
    sorted_items = sorted(valid_items, key=lambda item: item[1])
    m = len(sorted_items)
    adjusted_raw: dict[str, float] = {}
    for rank, (key, p_value) in enumerate(sorted_items, start=1):
        adjusted_raw[key] = min(1.0, p_value * (m - rank + 1))
    adjusted: dict[str, float] = {}
    running_max = 0.0
    for key, _p_value in sorted_items:
        running_max = max(running_max, adjusted_raw[key])
        adjusted[key] = min(1.0, running_max)
    return {key: {"adjusted_p_value": adjusted[key], "significant": adjusted[key] < alpha} for key, _ in sorted_items}


def descriptive_stats(
    frame: pd.DataFrame,
    metrics: list[str],
    bootstrap_samples: int,
    alpha: float,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for architecture, group in frame.groupby("architecture"):
        for metric in metrics:
            if metric not in group:
                continue
            values = [float(value) for value in group[metric].dropna().tolist()]
            if not values:
                continue
            ci_low, ci_high = bootstrap_ci(values, samples=bootstrap_samples, alpha=alpha)
            rows.append(
                {
                    "architecture": architecture,
                    "metric": metric,
                    "n": len(values),
                    "mean": sum(values) / len(values),
                    "median": _quantile(sorted(values), 0.5),
                    "std": _sample_std(values),
                    "min": min(values),
                    "max": max(values),
                    "p25": _quantile(sorted(values), 0.25),
                    "p75": _quantile(sorted(values), 0.75),
                    "ci95_low": ci_low,
                    "ci95_high": ci_high,
                }
            )
    return rows


def latency_stats(frame: pd.DataFrame) -> list[dict[str, Any]]:
    rows = []
    for architecture, group in frame.groupby("architecture"):
        values = sorted(float(value) for value in group["latency_ms"].dropna().tolist())
        if not values:
            continue
        rows.append(
            {
                "architecture": architecture,
                "latency_mean": sum(values) / len(values),
                "latency_median": _quantile(values, 0.5),
                "latency_p95": _quantile(values, 0.95),
                "latency_p99": _quantile(values, 0.99),
            }
        )
    return rows


def pairwise_tests(
    frame: pd.DataFrame,
    metric: str = "overall_score",
    bootstrap_samples: int = 10000,
    alpha: float = 0.05,
    practical_threshold: float = 0.01,
) -> list[dict[str, Any]]:
    pivot = frame.pivot(index="query_id", columns="architecture", values=metric)
    rows: list[dict[str, Any]] = []
    p_values: dict[str, float] = {}
    for left, right in combinations(ARCHITECTURES, 2):
        if left not in pivot or right not in pivot:
            continue
        left_values = pivot[left].tolist()
        right_values = pivot[right].tolist()
        diffs = [a - b for a, b in zip(left_values, right_values) if not pd.isna(a) and not pd.isna(b)]
        if not diffs:
            continue
        comparison = f"{left}_vs_{right}"
        p_value = paired_permutation_test(left_values, right_values, samples=bootstrap_samples)
        p_values[comparison] = p_value
        ci_low, ci_high = paired_bootstrap_diff_ci(left_values, right_values, samples=bootstrap_samples, alpha=alpha)
        mean_diff = sum(diffs) / len(diffs)
        rows.append(
            {
                "comparison": comparison,
                "architecture_a": left,
                "architecture_b": right,
                "metric": metric,
                "n": len(diffs),
                "mean_a": _mean(left_values),
                "mean_b": _mean(right_values),
                "mean_difference_a_minus_b": mean_diff,
                "bootstrap_ci_low": ci_low,
                "bootstrap_ci_high": ci_high,
                "permutation_p_value": p_value,
                "wilcoxon_p_value": wilcoxon_p_value(left_values, right_values),
                "cohens_dz": cohens_dz(left_values, right_values),
                "cliffs_delta": cliffs_delta(left_values, right_values),
                "practically_meaningful": abs(mean_diff) >= practical_threshold,
            }
        )
    corrections = holm_bonferroni(p_values, alpha=alpha)
    for row in rows:
        correction = corrections.get(row["comparison"], {})
        row["holm_adjusted_p_value"] = correction.get("adjusted_p_value")
        row["statistically_significant"] = bool(correction.get("significant", False))
        row["conclusion"] = _comparison_conclusion(row)
    return rows


def _comparison_conclusion(row: dict[str, Any]) -> str:
    if not row["statistically_significant"]:
        return "not statistically significant"
    if not row["practically_meaningful"]:
        return "statistically significant but practically small"
    return "statistically significant and practically meaningful"


def _sample_std(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    return math.sqrt(sum((value - mean) ** 2 for value in values) / (len(values) - 1))


def _mean(values: list[float]) -> float | None:
    numeric = [float(value) for value in values if not pd.isna(value)]
    return sum(numeric) / len(numeric) if numeric else None


def _quantile(sorted_values: list[float], q: float) -> float:
    if not sorted_values:
        return math.nan
    if len(sorted_values) == 1:
        return sorted_values[0]
    rank = q * (len(sorted_values) - 1)
    lower = math.floor(rank)
    upper = math.ceil(rank)
    if lower == upper:
        return sorted_values[lower]
    weight = rank - lower
    return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight

