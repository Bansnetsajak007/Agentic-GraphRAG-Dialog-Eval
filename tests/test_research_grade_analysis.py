import json
from pathlib import Path

from ragbench.analysis.loading import load_analysis_data
from ragbench.analysis.reporting import write_research_grade_report
from ragbench.analysis.stats import bootstrap_ci, cohens_dz, paired_permutation_test


def test_load_analysis_data_aligns_architectures(tmp_path: Path) -> None:
    for architecture in ("traditional_rag", "agentic_rag", "agentic_graph_rag"):
        path = tmp_path / architecture / "rag_metrics_detailed.jsonl"
        path.parent.mkdir(parents=True)
        path.write_text(
            json.dumps(_record("Q1", architecture, 0.8)) + "\n",
            encoding="utf-8",
        )

    loaded = load_analysis_data(tmp_path)

    assert len(loaded.frame) == 3
    assert loaded.validation_summary["query_id_alignment"]["valid"] is True
    assert loaded.validation_summary["field_alignment"]["valid"] is True
    assert "overall_score" in loaded.available_metrics


def test_bootstrap_ci_contains_mean() -> None:
    values = [0.1, 0.2, 0.3, 0.4]
    low, high = bootstrap_ci(values, samples=200, seed=1)
    mean = sum(values) / len(values)

    assert low <= mean <= high


def test_paired_permutation_test_detects_large_consistent_difference() -> None:
    left = [0.9] * 20
    right = [0.1] * 20

    p_value = paired_permutation_test(left, right, samples=500, seed=1)

    assert p_value < 0.01


def test_cohens_dz_for_paired_samples() -> None:
    left = [0.4, 0.5, 0.6]
    right = [0.3, 0.3, 0.3]

    effect = cohens_dz(left, right)

    assert effect is not None
    assert effect > 0


def test_research_report_generation_smoke(tmp_path: Path) -> None:
    output_path = tmp_path / "report.md"
    descriptive = [
        {"architecture": "traditional_rag", "metric": "overall_score", "n": 1, "mean": 0.7, "median": 0.7, "std": 0.0, "ci95_low": 0.7, "ci95_high": 0.7},
        {"architecture": "agentic_graph_rag", "metric": "overall_score", "n": 1, "mean": 0.8, "median": 0.8, "std": 0.0, "ci95_low": 0.8, "ci95_high": 0.8},
        {"architecture": "traditional_rag", "metric": "latency_ms", "n": 1, "mean": 10.0, "median": 10.0, "std": 0.0, "ci95_low": 10.0, "ci95_high": 10.0},
    ]

    write_research_grade_report(
        output_path=output_path,
        validation={"valid": True, "query_id_alignment": {"valid": True}, "field_alignment": {"valid": True}, "architectures": {"traditional_rag": {"judge_model": "gpt-5.2"}}},
        descriptive_rows=descriptive,
        pairwise_rows=[],
        company_rows=[],
        difficulty_rows=[],
        retrieval_rows=[],
        tradeoff_rows=[],
        failure_rows=[],
    )

    assert output_path.exists()
    assert "Research-Grade Evaluation" in output_path.read_text(encoding="utf-8")


def _record(query_id: str, architecture: str, score: float) -> dict:
    return {
        "query_id": query_id,
        "architecture": architecture,
        "company": "QuickCommerce / E-commerce Company",
        "company_key": "chitomart",
        "difficulty": "simple",
        "category": "fact_lookup",
        "query": "mero order kata pugyo?",
        "answer": "Order ID share garnuhos.",
        "retrieved_chunk_ids": ["c1"],
        "source_documents": ["chitomart/delivery_policy.md"],
        "judge": {"enabled": True, "model": "gpt-5.2"},
        "metrics": {
            "faithfulness": score,
            "answer_relevancy": score,
            "context_recall": score,
            "context_precision": score,
            "context_relevancy": score,
            "hit_rate_at_k": score,
            "mrr_at_k": score,
            "ndcg_at_k": score,
            "policy_compliance": score,
            "tone_appropriateness": score,
            "success": 1.0,
            "latency_ms": 10,
            "average_retrieved_chunks": 1,
        },
    }
