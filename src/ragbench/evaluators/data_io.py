"""I/O helpers for post-hoc RAG metric evaluation."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from ragbench.evaluators.metric_schemas import EvaluationDatasetItem, RAGResultItem
from ragbench.utils.text import normalize_whitespace


QUERY_COLUMNS = ("query", "query_romanized", "question")
CATEGORY_COLUMNS = ("category", "query_type", "intent")
EXPECTED_TOPIC_COLUMNS = ("expected_topic", "topic")
EXPECTED_SOURCE_COLUMNS = (
    "expected_source_doc",
    "expected_source_document",
    "expected_document",
    "expected_doc",
    "source_doc",
    "source_document",
)
EXPECTED_POINTS_COLUMNS = (
    "expected_answer_points",
    "expected_answer",
    "expected_facts",
    "required_facts",
)


def load_dataset(path: Path) -> dict[str, EvaluationDatasetItem]:
    if not path.exists():
        raise FileNotFoundError(f"Evaluation dataset not found: {path}")
    if path.suffix.lower() == ".jsonl":
        rows = _read_jsonl(path)
    elif path.suffix.lower() == ".csv":
        rows = _read_csv(path)
    else:
        raise ValueError(f"Unsupported dataset format for {path}. Use .csv or .jsonl.")

    items: dict[str, EvaluationDatasetItem] = {}
    for row_number, row in enumerate(rows, start=1):
        item = _dataset_item_from_row(row, row_number=row_number)
        if item.query_id in items:
            raise ValueError(f"Duplicate query_id in evaluation dataset: {item.query_id}")
        items[item.query_id] = item
    return items


def load_results(path: Path) -> list[RAGResultItem]:
    if not path.exists():
        raise FileNotFoundError(f"Architecture result JSONL not found: {path}")
    results: list[RAGResultItem] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Malformed JSONL in {path} at line {line_number}: {exc}") from exc
            results.append(RAGResultItem(**payload))
    return results


def load_detailed_metrics(path: Path) -> list[Any]:
    if not path.exists():
        return []
    rows: list[Any] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Malformed detailed metric JSONL in {path} at line {line_number}: {exc}") from exc
    return rows


def write_jsonl(items: list[Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for item in items:
            if hasattr(item, "model_dump"):
                payload = item.model_dump(mode="json")
            else:
                payload = item
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def append_jsonl_item(item: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if hasattr(item, "model_dump"):
        payload = item.model_dump(mode="json")
    else:
        payload = item
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def write_csv(rows: list[dict[str, Any]], path: Path, fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: _csv_value(row.get(key)) for key in fieldnames})


def write_json(payload: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def result_path_for(results_dir: Path, architecture: str) -> Path:
    return results_dir / architecture / "eval_results.jsonl"


def detailed_metrics_path_for(results_dir: Path, architecture: str) -> Path:
    return results_dir / architecture / "rag_metrics_detailed.jsonl"


def _read_csv(path: Path) -> list[dict[str, Any]]:
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))
    except csv.Error as exc:
        raise ValueError(f"Malformed CSV dataset {path}: {exc}") from exc


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Malformed JSONL dataset {path} at line {line_number}: {exc}") from exc
    return rows


def _dataset_item_from_row(row: dict[str, Any], row_number: int) -> EvaluationDatasetItem:
    query_id = _required(row, "query_id", row_number)
    company = _required(row, "company", row_number)
    difficulty = _required(row, "difficulty", row_number)
    query = _required_alias(row, QUERY_COLUMNS, row_number)
    category = _required_alias(row, CATEGORY_COLUMNS, row_number)
    expected_topic = _optional_alias(row, EXPECTED_TOPIC_COLUMNS)
    expected_source_doc = _optional_alias(row, EXPECTED_SOURCE_COLUMNS)
    expected_answer_points = _parse_points(_optional_alias(row, EXPECTED_POINTS_COLUMNS))
    metadata = {
        key: value
        for key, value in row.items()
        if key
        and key
        not in {
            "query_id",
            "company",
            "difficulty",
            *QUERY_COLUMNS,
            *CATEGORY_COLUMNS,
            *EXPECTED_TOPIC_COLUMNS,
            *EXPECTED_SOURCE_COLUMNS,
            *EXPECTED_POINTS_COLUMNS,
        }
        and value not in (None, "")
    }
    return EvaluationDatasetItem(
        query_id=query_id,
        company=company,
        query=query,
        difficulty=difficulty,
        category=category,
        expected_topic=expected_topic,
        expected_source_doc=expected_source_doc,
        expected_answer_points=expected_answer_points,
        metadata=metadata,
    )


def _required(row: dict[str, Any], column: str, row_number: int) -> str:
    value = normalize_whitespace(str(row.get(column) or ""))
    if not value:
        raise ValueError(f"Dataset row {row_number} has empty required column '{column}'.")
    return value


def _required_alias(row: dict[str, Any], aliases: tuple[str, ...], row_number: int) -> str:
    value = _optional_alias(row, aliases)
    if value is None:
        raise ValueError(f"Dataset row {row_number} is missing one of required columns: {list(aliases)}")
    return value


def _optional_alias(row: dict[str, Any], aliases: tuple[str, ...]) -> str | None:
    for alias in aliases:
        value = normalize_whitespace(str(row.get(alias) or ""))
        if value:
            return value
    return None


def _parse_points(value: str | None) -> list[str]:
    if not value:
        return []
    stripped = value.strip()
    if stripped.startswith("["):
        try:
            decoded = json.loads(stripped)
            if isinstance(decoded, list):
                return [normalize_whitespace(str(item)) for item in decoded if normalize_whitespace(str(item))]
        except json.JSONDecodeError:
            pass
    separators = ["|", ";", "\n"]
    points = [stripped]
    for separator in separators:
        if separator in stripped:
            points = stripped.split(separator)
            break
    return [normalize_whitespace(point) for point in points if normalize_whitespace(point)]


def _csv_value(value: Any) -> str | int | float:
    if value is None:
        return ""
    if isinstance(value, float):
        return round(value, 4)
    if isinstance(value, int):
        return value
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)
