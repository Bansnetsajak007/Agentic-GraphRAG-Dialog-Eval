from pathlib import Path

import pytest

from ragbench.loaders.eval_dataset_loader import load_evaluation_queries


def test_load_evaluation_queries_maps_dataset_columns(tmp_path: Path) -> None:
    dataset_path = tmp_path / "queries.csv"
    dataset_path.write_text(
        "\n".join(
            [
                "query_id,company,topic,difficulty,query_type,language_style,query_romanized",
                "QC001,QuickCommerce / E-commerce Company,delivery_order_status,simple,fact_lookup,romanized,mero order kata pugyo?",
            ]
        ),
        encoding="utf-8",
    )

    queries = load_evaluation_queries(dataset_path)

    assert len(queries) == 1
    assert queries[0].query_id == "QC001"
    assert queries[0].query == "mero order kata pugyo?"
    assert queries[0].category == "fact_lookup"
    assert queries[0].expected_topic == "delivery_order_status"
    assert queries[0].metadata["language_style"] == "romanized"


def test_load_evaluation_queries_missing_file_has_clear_error(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Place romanized_nepali_rag_eval_queries_300.csv"):
        load_evaluation_queries(tmp_path / "missing.csv")


def test_load_evaluation_queries_rejects_missing_required_columns(tmp_path: Path) -> None:
    dataset_path = tmp_path / "queries.csv"
    dataset_path.write_text("query_id,company,query_romanized\nQ1,chitomart,hello\n", encoding="utf-8")

    with pytest.raises(ValueError, match="missing required columns"):
        load_evaluation_queries(dataset_path)


def test_load_evaluation_queries_rejects_empty_required_values(tmp_path: Path) -> None:
    dataset_path = tmp_path / "queries.csv"
    dataset_path.write_text(
        "\n".join(
            [
                "query_id,company,difficulty,category,query",
                "Q1,chitomart,simple,fact_lookup,",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Row 2 has an empty required value"):
        load_evaluation_queries(dataset_path)
