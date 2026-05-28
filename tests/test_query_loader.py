from pathlib import Path

import pandas as pd
import pytest

from ragbench.loaders.query_loader import load_eval_queries, prepare_eval_queries


def test_prepare_eval_queries_creates_expected_columns(tmp_path: Path) -> None:
    raw_path = tmp_path / "raw.csv"
    output_path = tmp_path / "eval.csv"
    pd.DataFrame(
        {
            "Input": [
                "delivery charge kati ho?",
                "delivery charge kati ho?",
                "payment failed vayo but paisa katyo",
            ],
            "Output": ["Inquiry", "Inquiry", "Complaint"],
            "Noise": ["x", "y", "z"],
        }
    ).to_csv(raw_path, index=False)

    prepared = prepare_eval_queries(raw_path, output_path)

    assert output_path.exists()
    assert list(prepared["id"]) == ["Q0001", "Q0002"]
    assert list(prepared["intent"]) == ["Inquiry", "Complaint"]
    assert prepared.loc[0, "language_type"] == "code_mixed"
    assert prepared.loc[1, "query_type"] == "complaint"


def test_prepare_eval_queries_missing_raw_file_has_clear_error(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Raw Crowpeaks CSV not found"):
        prepare_eval_queries(tmp_path / "missing.csv", tmp_path / "out.csv")


def test_load_eval_queries_reads_schema(tmp_path: Path) -> None:
    csv_path = tmp_path / "eval.csv"
    pd.DataFrame(
        [
            {
                "id": "Q0001",
                "query": "refund huncha?",
                "intent": "Inquiry",
                "language_type": "romanized_nepali",
                "query_type": "policy_payment",
                "requires_clarification": False,
                "difficulty": "easy",
                "expected_answer": "",
                "required_docs": "",
                "required_facts": "",
                "notes": "",
            }
        ]
    ).to_csv(csv_path, index=False)

    queries = load_eval_queries(csv_path)

    assert len(queries) == 1
    assert queries[0].id == "Q0001"
    assert queries[0].query == "refund huncha?"
