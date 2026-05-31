"""Load the Romanized Nepali RAG evaluation query dataset."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

from ragbench.schemas import EvaluationQuery
from ragbench.utils.text import normalize_whitespace


QUERY_ALIASES = ("query", "query_romanized")
CATEGORY_ALIASES = ("category", "query_type")
EXPECTED_DOCUMENT_ALIASES = ("expected_document", "expected_doc", "required_docs")
EXPECTED_TOPIC_ALIASES = ("expected_topic", "topic")
OPTIONAL_METADATA_COLUMNS = ("topic", "query_type", "language_style")


def load_evaluation_queries(path: Path, limit: int | None = None) -> list[EvaluationQuery]:
    """Read and validate evaluation queries from CSV."""

    if not path.exists():
        raise FileNotFoundError(
            f"Evaluation dataset CSV not found: {path}. "
            "Place romanized_nepali_rag_eval_queries_300.csv under data/eval/queries/."
        )
    if not path.is_file():
        raise FileNotFoundError(f"Evaluation dataset path is not a file: {path}")

    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            fieldnames = reader.fieldnames or []
            _validate_columns(fieldnames)
            queries = [_parse_row(row, row_number=index + 2) for index, row in enumerate(reader)]
    except csv.Error as exc:
        raise ValueError(f"Malformed evaluation CSV {path}: {exc}") from exc
    except UnicodeDecodeError as exc:
        raise ValueError(f"Evaluation CSV must be UTF-8 encoded: {path}") from exc

    if limit and limit > 0:
        queries = queries[:limit]

    return queries


def _validate_columns(fieldnames: list[str]) -> None:
    missing = [column for column in ("query_id", "company", "difficulty") if column not in fieldnames]
    if not _first_existing(fieldnames, QUERY_ALIASES):
        missing.append("query or query_romanized")
    if not _first_existing(fieldnames, CATEGORY_ALIASES):
        missing.append("category or query_type")
    if missing:
        raise ValueError(f"Evaluation CSV is missing required columns: {missing}")


def _parse_row(row: dict[str, str | None], row_number: int) -> EvaluationQuery:
    query_id = _required_value(row, "query_id", row_number)
    company = _required_value(row, "company", row_number)
    difficulty = _required_value(row, "difficulty", row_number)
    query_column = _first_existing(row.keys(), QUERY_ALIASES)
    category_column = _first_existing(row.keys(), CATEGORY_ALIASES)
    if query_column is None or category_column is None:
        raise ValueError(f"Row {row_number} is missing required query/category columns.")

    query = _required_value(row, query_column, row_number)
    category = _required_value(row, category_column, row_number)
    expected_document = _optional_alias_value(row, EXPECTED_DOCUMENT_ALIASES)
    expected_topic = _optional_alias_value(row, EXPECTED_TOPIC_ALIASES)
    metadata = {
        column: normalize_whitespace(str(row[column]))
        for column in OPTIONAL_METADATA_COLUMNS
        if column in row and row[column] not in (None, "")
    }

    return EvaluationQuery(
        query_id=query_id,
        company=company,
        query=query,
        difficulty=difficulty,
        category=category,
        expected_document=expected_document,
        expected_topic=expected_topic,
        metadata=metadata,
    )


def _required_value(row: dict[str, str | None], column: str, row_number: int) -> str:
    value = normalize_whitespace(str(row.get(column) or ""))
    if not value:
        raise ValueError(f"Row {row_number} has an empty required value for column '{column}'.")
    return value


def _optional_alias_value(row: dict[str, str | None], aliases: Iterable[str]) -> str | None:
    column = _first_existing(row.keys(), aliases)
    if column is None:
        return None
    value = normalize_whitespace(str(row.get(column) or ""))
    return value or None


def _first_existing(columns: Iterable[str], aliases: Iterable[str]) -> str | None:
    column_set = set(columns)
    for alias in aliases:
        if alias in column_set:
            return alias
    return None
