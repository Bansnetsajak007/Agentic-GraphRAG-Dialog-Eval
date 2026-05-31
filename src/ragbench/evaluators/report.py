"""Markdown report generation for RAG architecture evaluation."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def write_research_report(
    output_path: Path,
    dataset_path: Path,
    summary_rows: list[dict[str, Any]],
    company_rows: list[dict[str, Any]],
    difficulty_rows: list[dict[str, Any]],
    error_summary: dict[str, Any],
    judge_info: dict[str, Any],
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    best = _best_architecture(summary_rows)
    lines = [
        "# RAG Evaluation Report",
        "",
        "## Objective",
        "",
        "Evaluate Traditional RAG, Agentic RAG, and Agentic GraphRAG for a Romanized Nepali customer-support benchmark using retrieval, generation, language robustness, and operational metrics.",
        "",
        "## Dataset Description",
        "",
        f"- Dataset path: `{dataset_path.as_posix()}`",
        "- 300 Romanized Nepali/code-mixed customer-support queries.",
        "- 3 company domains: quick-commerce/e-commerce, hosting/cloud provider, and FinTech/digital wallet.",
        "- 100 queries per company with simple, medium, and complex/adversarial difficulty levels.",
        "- Current dataset provides expected topic/category metadata. Gold answer points and expected source docs are used automatically when present.",
        "",
        "## Architectures Compared",
        "",
        "- `traditional_rag`",
        "- `agentic_rag`",
        "- `agentic_graph_rag`",
        "",
        "## Metrics Used",
        "",
        "- Retrieval: context precision, context recall, context relevancy, hit rate@k, MRR@k, nDCG@k, retrieved chunk count.",
        "- Generation: faithfulness/groundedness, answer relevancy, correctness, completeness, hallucination rate, policy compliance.",
        "- Romanized Nepali support: query understanding, code-mixed handling, intent classification accuracy, company-domain accuracy, escalation correctness, tone appropriateness.",
        "- Operational: success/failure rate, average/p50/p95 latency, token usage, agent steps, tool calls when available.",
        "",
        _judge_section(judge_info),
        "",
        "## Overall Comparison Table",
        "",
        _table(
            summary_rows,
            [
                "architecture",
                "total_queries",
                "success_rate",
                "overall_score",
                "retrieval_quality_score",
                "generation_quality_score",
                "romanized_robustness_score",
                "average_latency_ms",
                "p95_latency_ms",
            ],
        ),
        "",
        "## Company-Wise Comparison",
        "",
        _table(
            company_rows,
            [
                "architecture",
                "company",
                "success_rate",
                "overall_score",
                "context_recall",
                "hit_rate_at_k",
                "answer_relevancy",
                "average_latency_ms",
            ],
        ),
        "",
        "## Difficulty-Wise Comparison",
        "",
        _table(
            difficulty_rows,
            [
                "architecture",
                "difficulty",
                "success_rate",
                "overall_score",
                "context_recall",
                "answer_relevancy",
                "escalation_correctness",
                "average_latency_ms",
            ],
        ),
        "",
        "## Latency and Efficiency Comparison",
        "",
        _table(summary_rows, ["architecture", "average_latency_ms", "p50_latency_ms", "p95_latency_ms", "average_token_usage", "average_agent_steps", "average_tool_calls"]),
        "",
        "## Retrieval-Quality Comparison",
        "",
        _table(summary_rows, ["architecture", "context_precision", "context_recall", "context_relevancy", "hit_rate_at_k", "mrr_at_k", "ndcg_at_k", "average_retrieved_chunks"]),
        "",
        "## Generation-Quality Comparison",
        "",
        _table(summary_rows, ["architecture", "faithfulness", "answer_relevancy", "answer_correctness", "answer_completeness", "hallucination_rate", "policy_compliance"]),
        "",
        "## Romanized Nepali Robustness Comparison",
        "",
        _table(summary_rows, ["architecture", "romanized_query_understanding", "code_mixed_handling", "intent_classification_accuracy", "company_domain_accuracy", "escalation_correctness", "tone_appropriateness"]),
        "",
        "## Error Analysis",
        "",
        _error_lines(error_summary),
        "",
        "## Final Conclusion",
        "",
        _conclusion(best, summary_rows),
        "",
    ]
    output_path.write_text("\n".join(lines), encoding="utf-8")


def _judge_section(judge_info: dict[str, Any]) -> str:
    if not judge_info.get("enabled"):
        return (
            "Judge status: LLM judge was not configured. Deterministic metrics were computed, "
            "and judge-dependent metrics remain blank unless a heuristic fallback was available."
        )
    return f"Judge status: LLM judge enabled with `{judge_info.get('provider')}` model `{judge_info.get('model')}`."


def _best_architecture(summary_rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    scored = [row for row in summary_rows if row.get("overall_score") is not None]
    if not scored:
        return None
    return max(scored, key=lambda row: float(row["overall_score"]))


def _conclusion(best: dict[str, Any] | None, summary_rows: list[dict[str, Any]]) -> str:
    if best is None:
        return "No architecture can be selected because no comparable overall scores were available."
    architecture = best["architecture"]
    return (
        f"`{architecture}` has the highest computed overall score in this run. "
        "The conclusion is based on the available deterministic metrics and any configured judge metrics. "
        "If judge metrics were disabled, treat generation-quality conclusions as provisional and rerun with `JUDGE_LLM_PROVIDER` configured for stronger answer-quality assessment."
    )


def _error_lines(error_summary: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"- Total evaluated records: {error_summary.get('total_records', 0)}",
            f"- Failed records: {error_summary.get('failure_count', 0)}",
            f"- Records with no retrieved chunks: {error_summary.get('no_retrieval_count', 0)}",
            f"- Records below hit-rate threshold: {error_summary.get('low_hit_rate_count', 0)}",
            f"- Records below faithfulness threshold: {error_summary.get('low_faithfulness_count', 0)}",
            f"- Records below answer-relevancy threshold: {error_summary.get('low_answer_relevancy_count', 0)}",
            f"- Records below tone-appropriateness threshold: {error_summary.get('low_tone_appropriateness_count', 0)}",
        ]
    )


def _table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    if not rows:
        return "_No rows available._"
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join("---" for _ in columns) + " |"
    body = ["| " + " | ".join(_format_value(row.get(column)) for column in columns) + " |" for row in rows]
    return "\n".join([header, separator, *body])


def _format_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)
