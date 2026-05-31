"""Create a compact CSV summary across architecture evaluation outputs."""

from __future__ import annotations

import csv
import json
from pathlib import Path


SUMMARY_COLUMNS = [
    "architecture",
    "output_path",
    "total_queries",
    "successful_queries",
    "failed_queries",
    "average_latency_ms",
    "average_retrieved_chunks",
]


def write_evaluation_summary(result_paths: dict[str, Path], output_path: Path) -> list[dict[str, str]]:
    rows = [_summarize_architecture(architecture, path) for architecture, path in result_paths.items()]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=SUMMARY_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return rows


def _summarize_architecture(architecture: str, path: Path) -> dict[str, str]:
    if not path.exists():
        return {
            "architecture": architecture,
            "output_path": path.as_posix(),
            "total_queries": "0",
            "successful_queries": "0",
            "failed_queries": "0",
            "average_latency_ms": "0.0",
            "average_retrieved_chunks": "0.0",
        }

    total = 0
    failed = 0
    latency_sum = 0
    retrieved_sum = 0
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Malformed JSONL in {path} at line {line_number}: {exc}") from exc
            total += 1
            if payload.get("error"):
                failed += 1
            latency_sum += int(payload.get("latency_ms") or 0)
            retrieved_sum += len(payload.get("retrieved_chunks") or [])

    successful = total - failed
    average_latency = latency_sum / total if total else 0.0
    average_retrieved = retrieved_sum / total if total else 0.0
    return {
        "architecture": architecture,
        "output_path": path.as_posix(),
        "total_queries": str(total),
        "successful_queries": str(successful),
        "failed_queries": str(failed),
        "average_latency_ms": f"{average_latency:.1f}",
        "average_retrieved_chunks": f"{average_retrieved:.1f}",
    }
