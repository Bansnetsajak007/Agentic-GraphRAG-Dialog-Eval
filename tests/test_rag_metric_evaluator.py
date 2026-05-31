import json
from pathlib import Path

from ragbench.evaluators.aggregation import summarize_by_architecture
from ragbench.evaluators.data_io import load_dataset, load_results
from ragbench.evaluators.deterministic_metrics import score_deterministic_metrics


def test_load_dataset_supports_csv_and_expected_fields(tmp_path: Path) -> None:
    dataset_path = tmp_path / "queries.csv"
    dataset_path.write_text(
        "\n".join(
            [
                "query_id,company,topic,difficulty,query_type,query_romanized,expected_source_doc,expected_answer_points",
                "Q1,QuickCommerce / E-commerce Company,delivery_order_status,simple,fact_lookup,mero order kata pugyo?,delivery_policy.md,Ask for order ID|Check delivery status",
            ]
        ),
        encoding="utf-8",
    )

    dataset = load_dataset(dataset_path)

    assert dataset["Q1"].expected_topic == "delivery_order_status"
    assert dataset["Q1"].expected_source_doc == "delivery_policy.md"
    assert dataset["Q1"].expected_answer_points == ["Ask for order ID", "Check delivery status"]


def test_load_results_reads_eval_jsonl(tmp_path: Path) -> None:
    result_path = tmp_path / "eval_results.jsonl"
    result_path.write_text(
        json.dumps(
            {
                "query_id": "Q1",
                "architecture": "traditional_rag",
                "company": "QuickCommerce / E-commerce Company",
                "company_key": "chitomart",
                "query": "mero order kata pugyo?",
                "difficulty": "simple",
                "category": "fact_lookup",
                "answer": "Order ID share garnuhos.",
                "retrieved_chunks": [],
                "source_documents": [],
                "latency_ms": 10,
                "token_usage": None,
                "error": None,
                "metadata": {},
            }
        )
        + "\n",
        encoding="utf-8",
    )

    results = load_results(result_path)

    assert len(results) == 1
    assert results[0].architecture == "traditional_rag"


def test_deterministic_retrieval_metrics_use_expected_topic() -> None:
    dataset = load_dataset_row()
    result = load_result_row()

    metrics, evidence = score_deterministic_metrics(
        dataset,
        result,
        company_map={"QuickCommerce / E-commerce Company": "chitomart"},
    )

    assert metrics["hit_rate_at_k"] == 1.0
    assert metrics["mrr_at_k"] == 1.0
    assert metrics["company_domain_accuracy"] == 1.0
    assert metrics["intent_classification_accuracy"] == 1.0
    assert evidence["relevant_chunk_count"] == 1


def test_summary_computes_latency_and_success_rates() -> None:
    dataset = load_dataset_row()
    result = load_result_row()
    metrics, _evidence = score_deterministic_metrics(
        dataset,
        result,
        company_map={"QuickCommerce / E-commerce Company": "chitomart"},
    )
    from ragbench.evaluators.metric_schemas import PerQueryMetricResult

    record = PerQueryMetricResult(
        query_id="Q1",
        architecture="traditional_rag",
        company=dataset.company,
        company_key="chitomart",
        difficulty=dataset.difficulty,
        category=dataset.category,
        query=dataset.query,
        answer=result.answer,
        metrics=metrics,
    )

    rows = summarize_by_architecture([record])

    assert rows[0]["total_queries"] == 1
    assert rows[0]["success_rate"] == 1.0
    assert rows[0]["average_latency_ms"] == 10.0


def load_dataset_row():
    from ragbench.evaluators.metric_schemas import EvaluationDatasetItem

    return EvaluationDatasetItem(
        query_id="Q1",
        company="QuickCommerce / E-commerce Company",
        query="mero order kata pugyo?",
        difficulty="simple",
        category="fact_lookup",
        expected_topic="delivery_order_status",
    )


def load_result_row():
    from ragbench.evaluators.metric_schemas import RAGResultItem

    return RAGResultItem(
        query_id="Q1",
        architecture="traditional_rag",
        company="QuickCommerce / E-commerce Company",
        company_key="chitomart",
        query="mero order kata pugyo?",
        difficulty="simple",
        category="fact_lookup",
        answer="Order ID share garnuhos, ma delivery status check garera update dinchu.",
        retrieved_chunks=[
            {
                "chunk_id": "chitomart__delivery_policy-001",
                "source": "chitomart/delivery_policy.md",
                "content": "Delivery status check garna order ID chaincha.",
                "score": 0.1,
                "metadata": {"company": "chitomart"},
            }
        ],
        source_documents=["chitomart/delivery_policy.md"],
        latency_ms=10,
        token_usage=None,
        error=None,
        metadata={},
    )
