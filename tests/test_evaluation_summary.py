import json
from pathlib import Path

from ragbench.evaluators.summary_report import write_evaluation_summary


def test_write_evaluation_summary_counts_successes_and_failures(tmp_path: Path) -> None:
    result_path = tmp_path / "traditional_rag" / "eval_results.jsonl"
    result_path.parent.mkdir(parents=True)
    result_path.write_text(
        "\n".join(
            [
                json.dumps({"query_id": "Q1", "latency_ms": 100, "retrieved_chunks": [{"chunk_id": "c1"}]}),
                json.dumps({"query_id": "Q2", "latency_ms": 300, "retrieved_chunks": [], "error": "boom"}),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    summary_path = tmp_path / "summary" / "evaluation_summary.csv"

    rows = write_evaluation_summary({"traditional_rag": result_path}, summary_path)

    assert summary_path.exists()
    assert rows[0]["total_queries"] == "2"
    assert rows[0]["successful_queries"] == "1"
    assert rows[0]["failed_queries"] == "1"
    assert rows[0]["average_latency_ms"] == "200.0"
    assert rows[0]["average_retrieved_chunks"] == "0.5"
