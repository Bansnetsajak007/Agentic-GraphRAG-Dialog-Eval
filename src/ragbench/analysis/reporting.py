"""Research-grade Markdown report generation."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def write_research_grade_report(
    output_path: Path,
    validation: dict[str, Any],
    descriptive_rows: list[dict[str, Any]],
    pairwise_rows: list[dict[str, Any]],
    company_rows: list[dict[str, Any]],
    difficulty_rows: list[dict[str, Any]],
    retrieval_rows: list[dict[str, Any]],
    tradeoff_rows: list[dict[str, Any]],
    failure_rows: list[dict[str, Any]],
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    overall = [row for row in descriptive_rows if row["metric"] == "overall_score"]
    latency = [row for row in descriptive_rows if row["metric"] == "latency_ms"]
    highest = _max_row(overall, "mean")
    fastest = _min_row(latency, "mean")
    simple_best = _best_stratum(difficulty_rows, "simple")
    complex_best = _best_stratum(difficulty_rows, "complex")
    graph_vs_traditional = _find_comparison(pairwise_rows, "agentic_graph_rag", "traditional_rag")
    graph_vs_agentic = _find_comparison(pairwise_rows, "agentic_graph_rag", "agentic_rag")
    best_tradeoff = _tradeoff_value(tradeoff_rows, "best_quality_latency_tradeoff")

    lines = [
        "# Research-Grade Evaluation of Three RAG Architectures for Romanized Nepali Customer Support",
        "",
        "## Abstract",
        "",
        _abstract(highest, graph_vs_traditional),
        "",
        "## Experimental Setup",
        "",
        "This analysis uses the existing `rag_metrics_detailed.jsonl` files as the source of truth. No RAG systems and no LLM judge calls are rerun by this analysis stage.",
        "",
        "## Dataset Description",
        "",
        "- 300 Romanized Nepali and code-mixed Nepali-English support queries.",
        "- 3 synthetic company domains with 100 queries each.",
        "- Difficulty labels include simple, medium, and complex.",
        "- Query category/intent labels are used for stratified analysis.",
        "",
        "## Architectures Compared",
        "",
        "- `traditional_rag`",
        "- `agentic_rag`",
        "- `agentic_graph_rag`",
        "",
        "## Evaluation Metrics",
        "",
        "The analysis normalizes available metrics from the detailed JSONL files, including retrieval metrics, judged generation metrics, Romanized Nepali robustness metrics, operational latency, and computed per-query `overall_score`.",
        "",
        "## LLM-as-Judge Configuration",
        "",
        _judge_config(validation),
        "",
        "## Statistical Testing Methodology",
        "",
        "Because each architecture is evaluated on the same 300 query IDs, pairwise comparisons use paired tests. The report includes paired bootstrap confidence intervals, paired permutation tests, optional Wilcoxon signed-rank p-values when SciPy is available, Cohen's dz, Cliff's delta, and Holm-Bonferroni adjusted p-values.",
        "",
        "## Overall Results",
        "",
        _table(overall, ["architecture", "n", "mean", "median", "std", "ci95_low", "ci95_high"]),
        "",
        "## Per-Company Results",
        "",
        _table(company_rows, ["company", "architecture", "n", "mean_overall_score", "ci95_low", "ci95_high", "mean_latency_ms", "best_architecture_for_group"]),
        "",
        "## Per-Difficulty Results",
        "",
        _table(difficulty_rows, ["difficulty", "architecture", "n", "mean_overall_score", "ci95_low", "ci95_high", "mean_latency_ms", "best_architecture_for_group"]),
        "",
        "## Retrieval Quality Analysis",
        "",
        _table(retrieval_rows, ["architecture", "mean_context_precision", "mean_context_recall", "hit_rate_at_k", "mrr_at_k", "ndcg_at_k", "average_retrieved_chunks", "missing_context_rate", "cross_company_contamination_rate", "retrieval_answer_correlation"]),
        "",
        "Retrieval scores are effectively tied across architectures when they use the same underlying retrieval output pattern. Any claimed advantage should therefore come from downstream reasoning/generation metrics, not retrieval alone.",
        "",
        "## Latency and Efficiency Analysis",
        "",
        _table(tradeoff_rows, ["architecture", "mean_quality_score", "mean_latency_ms", "p95_latency_ms", "quality_gain_over_traditional_rag", "latency_overhead_ms_over_traditional_rag", "quality_gain_per_extra_second"]),
        "",
        "## Failure Analysis",
        "",
        _table(failure_rows, ["architecture", "failure_type", "count", "rate"]),
        "",
        "## Statistical Significance Results",
        "",
        _table(pairwise_rows, ["comparison", "mean_difference_a_minus_b", "bootstrap_ci_low", "bootstrap_ci_high", "permutation_p_value", "holm_adjusted_p_value", "wilcoxon_p_value", "cohens_dz", "cliffs_delta", "conclusion"]),
        "",
        "## Practical Interpretation",
        "",
        _practical_interpretation(highest, fastest, best_tradeoff, graph_vs_traditional, graph_vs_agentic),
        "",
        "## Threats to Validity",
        "",
        "- The benchmark uses synthetic companies and synthetic queries, so external validity depends on future real-world data.",
        "- LLM-as-judge scores can encode model-specific preferences.",
        "- The current architectures appear to share much of the retrieval surface, reducing the chance of observing large retrieval differences.",
        "- Per-query overall score is a normalized composite; different metric weighting could change the final ordering.",
        "",
        "## Limitations",
        "",
        "- Token usage, agent steps, and tool-call counts are unavailable in the current detailed result files.",
        "- Gold answer points and expected source documents are sparse or absent, so judge metrics carry more weight for generation quality.",
        "- Statistical significance does not imply product relevance when effect sizes are tiny.",
        "",
        "## Final Conclusion",
        "",
        _final_conclusion(highest, graph_vs_traditional, fastest, simple_best, complex_best, best_tradeoff),
        "",
        "## Recommendations for Next Experiment",
        "",
        "- Add human-authored gold answer points and expected source documents for every query.",
        "- Add true agent-step and tool-call telemetry for agentic systems.",
        "- Evaluate on a larger and more realistic query set with adversarial Romanized Nepali spelling variants.",
        "- Run cost-aware evaluation that includes input/output tokens and infrastructure overhead.",
        "- Include human evaluation for a stratified sample to calibrate LLM-as-judge scores.",
        "",
        "## Validation Summary",
        "",
        f"- Overall validation status: `{validation.get('valid')}`",
        f"- Query alignment valid: `{validation.get('query_id_alignment', {}).get('valid')}`",
        f"- Field alignment valid: `{validation.get('field_alignment', {}).get('valid')}`",
    ]
    output_path.write_text("\n".join(lines), encoding="utf-8")


def _abstract(highest: dict[str, Any] | None, comparison: dict[str, Any] | None) -> str:
    if not highest:
        return "No valid overall scores were available."
    significance = "not tested"
    if comparison:
        significance = "statistically significant" if comparison.get("statistically_significant") else "not statistically significant"
    return (
        f"The highest mean overall score is achieved by `{highest['architecture']}` "
        f"(mean={_fmt(highest['mean'])}). Pairwise testing indicates that the main graph-vs-traditional comparison is {significance}. "
        "The interpretation emphasizes effect size and latency trade-offs rather than ranking by small mean differences alone."
    )


def _judge_config(validation: dict[str, Any]) -> str:
    arch_info = validation.get("architectures", {})
    models = sorted({str(info.get("judge_model")) for info in arch_info.values() if info.get("judge_model")})
    if not models:
        return "Judge metadata was not available in the validation summary."
    return f"Detailed metric files report judge model(s): {', '.join(models)}."


def _practical_interpretation(
    highest: dict[str, Any] | None,
    fastest: dict[str, Any] | None,
    best_tradeoff: str | None,
    graph_vs_traditional: dict[str, Any] | None,
    graph_vs_agentic: dict[str, Any] | None,
) -> str:
    parts = []
    if highest:
        parts.append(f"Best mean quality: `{highest['architecture']}`.")
    if fastest:
        parts.append(f"Fastest mean latency: `{fastest['architecture']}`.")
    if best_tradeoff:
        parts.append(f"Best quality-latency trade-off: `{best_tradeoff}`.")
    for comparison in [graph_vs_traditional, graph_vs_agentic]:
        if comparison:
            parts.append(
                f"`{comparison['architecture_a']}` vs `{comparison['architecture_b']}`: "
                f"{comparison['conclusion']} with mean difference {_fmt(comparison['mean_difference_a_minus_b'])}."
            )
    return " ".join(parts)


def _final_conclusion(
    highest: dict[str, Any] | None,
    graph_vs_traditional: dict[str, Any] | None,
    fastest: dict[str, Any] | None,
    simple_best: str | None,
    complex_best: str | None,
    best_tradeoff: str | None,
) -> str:
    lines = []
    lines.append(f"- Highest mean score: `{highest['architecture']}`." if highest else "- Highest mean score: unavailable.")
    if graph_vs_traditional:
        lines.append(
            "- Is `agentic_graph_rag` significantly better than `traditional_rag`? "
            f"{'Yes' if graph_vs_traditional.get('statistically_significant') else 'No'} "
            f"({graph_vs_traditional['conclusion']})."
        )
        lines.append(
            "- Is the advantage practically meaningful? "
            f"{'Yes' if graph_vs_traditional.get('practically_meaningful') else 'No'}."
        )
    lines.append(f"- Fastest architecture: `{fastest['architecture']}`." if fastest else "- Fastest architecture: unavailable.")
    lines.append(f"- Best for simple queries: `{simple_best}`." if simple_best else "- Best for simple queries: unavailable.")
    lines.append(f"- Best for complex queries: `{complex_best}`." if complex_best else "- Best for complex queries: unavailable.")
    lines.append(f"- Most production-ready: `{best_tradeoff or (fastest['architecture'] if fastest else 'unavailable')}` based on current quality-latency evidence.")
    lines.append("- Final research claim: report the systems as closely matched unless the adjusted paired tests show a clear and practically meaningful effect.")
    return "\n".join(lines)


def _find_comparison(rows: list[dict[str, Any]], a: str, b: str) -> dict[str, Any] | None:
    for row in rows:
        if row.get("architecture_a") == a and row.get("architecture_b") == b:
            return row
        if row.get("architecture_a") == b and row.get("architecture_b") == a:
            reversed_row = dict(row)
            reversed_row["mean_difference_a_minus_b"] = -float(row["mean_difference_a_minus_b"])
            reversed_row["bootstrap_ci_low"] = -float(row["bootstrap_ci_high"])
            reversed_row["bootstrap_ci_high"] = -float(row["bootstrap_ci_low"])
            reversed_row["architecture_a"] = a
            reversed_row["architecture_b"] = b
            return reversed_row
    return None


def _max_row(rows: list[dict[str, Any]], key: str) -> dict[str, Any] | None:
    valid = [row for row in rows if row.get(key) is not None]
    return max(valid, key=lambda row: float(row[key])) if valid else None


def _min_row(rows: list[dict[str, Any]], key: str) -> dict[str, Any] | None:
    valid = [row for row in rows if row.get(key) is not None]
    return min(valid, key=lambda row: float(row[key])) if valid else None


def _best_stratum(rows: list[dict[str, Any]], difficulty: str) -> str | None:
    matches = [row for row in rows if str(row.get("difficulty")).lower() == difficulty and row.get("mean_overall_score") is not None]
    return max(matches, key=lambda row: float(row["mean_overall_score"]))["architecture"] if matches else None


def _tradeoff_value(rows: list[dict[str, Any]], key: str) -> str | None:
    for row in rows:
        if row.get(key):
            return str(row[key])
    return None


def _table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    if not rows:
        return "_No rows available._"
    header = "| " + " | ".join(columns) + " |"
    sep = "| " + " | ".join("---" for _ in columns) + " |"
    body = ["| " + " | ".join(_fmt(row.get(column)) for column in columns) + " |" for row in rows]
    return "\n".join([header, sep, *body])


def _fmt(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)
