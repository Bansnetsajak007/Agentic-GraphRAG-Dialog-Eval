"""Write architecture evaluation results to JSONL."""

from __future__ import annotations

import json
from pathlib import Path

from ragbench.schemas import EvaluationResult


class EvaluationJsonlWriter:
    def __init__(self, output_path: Path, append: bool = False):
        self.output_path = output_path
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        mode = "a" if append else "w"
        self.handle = self.output_path.open(mode, encoding="utf-8")
        self.count = 0

    def write(self, result: EvaluationResult) -> None:
        self.handle.write(json.dumps(result.model_dump(mode="json"), ensure_ascii=False) + "\n")
        self.handle.flush()
        self.count += 1

    def close(self) -> None:
        self.handle.close()

    def __enter__(self) -> "EvaluationJsonlWriter":
        return self

    def __exit__(self, *_exc_info) -> None:
        self.close()
