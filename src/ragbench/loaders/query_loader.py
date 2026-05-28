"""Prepare and load evaluation queries."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from ragbench.schemas import EvalQuery
from ragbench.utils.text import normalize_whitespace


OUTPUT_COLUMNS = [
    "id",
    "query",
    "intent",
    "language_type",
    "query_type",
    "requires_clarification",
    "difficulty",
    "expected_answer",
    "required_docs",
    "required_facts",
    "notes",
]


def normalize_label(label: object) -> str:
    text = normalize_whitespace(str(label or "Other"))
    if not text:
        return "Other"
    return " ".join(part.capitalize() for part in text.replace("_", " ").split())


def infer_language_type(query: str) -> str:
    lowered = query.lower()
    nepali_markers = ["cha", "chha", "xa", "ho", "huncha", "garne", "kati", "mero", "paisa", "vayo"]
    english_markers = ["order", "delivery", "refund", "payment", "support", "item"]
    has_nepali = any(marker in lowered for marker in nepali_markers)
    has_english = any(marker in lowered for marker in english_markers)
    if has_nepali and has_english:
        return "code_mixed"
    if has_nepali:
        return "romanized_nepali"
    return "english_or_other"


def infer_query_type(query: str, intent: str) -> str:
    lowered = f"{query} {intent}".lower()
    if any(word in lowered for word in ["complaint", "wrong", "damaged", "missing", "rude", "bad"]):
        return "complaint"
    if any(word in lowered for word in ["refund", "payment", "paid", "paisa", "esewa", "khalti"]):
        return "policy_payment"
    if any(word in lowered for word in ["delivery", "charge", "location", "kati"]):
        return "policy_delivery"
    return "general_support"


def infer_requires_clarification(query: str) -> bool:
    lowered = query.lower()
    ambiguous_terms = ["help", "problem", "issue", "bigriyo", "garne", "support"]
    has_specific_detail = any(term in lowered for term in ["order", "id", "payment", "delivery", "refund", "item"])
    return any(term in lowered for term in ambiguous_terms) and not has_specific_detail


def infer_difficulty(query: str) -> str:
    word_count = len(query.split())
    if word_count <= 5:
        return "easy"
    if word_count <= 14:
        return "medium"
    return "hard"


def prepare_eval_queries(raw_csv_path: Path, output_path: Path, limit: int | None = None) -> pd.DataFrame:
    if not raw_csv_path.exists():
        raise FileNotFoundError(
            "Raw Crowpeaks CSV not found. Expected file at "
            f"{raw_csv_path}. Add the dataset there before preparing evaluation queries."
        )

    df = pd.read_csv(raw_csv_path)
    missing = {"Input", "Output"} - set(df.columns)
    if missing:
        raise ValueError(f"Raw CSV is missing required columns: {sorted(missing)}")

    prepared = (
        df[["Input", "Output"]]
        .rename(columns={"Input": "query", "Output": "intent"})
        .dropna(subset=["query"])
        .copy()
    )
    prepared["query"] = prepared["query"].astype(str).map(normalize_whitespace)
    prepared = prepared[prepared["query"] != ""]
    prepared = prepared.drop_duplicates(subset=["query"], keep="first")
    prepared["intent"] = prepared["intent"].map(normalize_label)

    if limit and limit > 0 and len(prepared) > limit:
        per_label = max(1, limit // max(1, prepared["intent"].nunique()))
        sampled = (
            prepared.groupby("intent", group_keys=False)
            .apply(lambda group: group.head(per_label), include_groups=False)
            .reset_index(drop=False)
        )
        if "intent" not in sampled.columns:
            sampled["intent"] = prepared.groupby("intent").head(per_label)["intent"].to_list()
        if len(sampled) < limit:
            remainder = prepared[~prepared["query"].isin(sampled["query"])].head(limit - len(sampled))
            sampled = pd.concat([sampled[["query", "intent"]], remainder[["query", "intent"]]], ignore_index=True)
        prepared = sampled[["query", "intent"]].head(limit)

    prepared = prepared.reset_index(drop=True)
    prepared.insert(0, "id", [f"Q{i:04d}" for i in range(1, len(prepared) + 1)])
    prepared["language_type"] = prepared["query"].map(infer_language_type)
    prepared["query_type"] = [infer_query_type(query, intent) for query, intent in zip(prepared["query"], prepared["intent"])]
    prepared["requires_clarification"] = prepared["query"].map(infer_requires_clarification)
    prepared["difficulty"] = prepared["query"].map(infer_difficulty)
    prepared["expected_answer"] = ""
    prepared["required_docs"] = ""
    prepared["required_facts"] = ""
    prepared["notes"] = ""
    prepared = prepared[OUTPUT_COLUMNS]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    prepared.to_csv(output_path, index=False)
    return prepared


def load_eval_queries(path: Path, limit: int | None = None) -> list[EvalQuery]:
    if not path.exists():
        raise FileNotFoundError(
            f"Processed eval query CSV not found: {path}. Run experiments/prepare_eval_queries.py first."
        )

    df = pd.read_csv(path, keep_default_na=False)
    missing = set(OUTPUT_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Processed query CSV is missing required columns: {sorted(missing)}")

    if limit and limit > 0:
        df = df.head(limit)

    return [EvalQuery(**row) for row in df.to_dict(orient="records")]
