"""Write benchmark predictions to JSONL."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from ragbench.schemas import Prediction


def write_predictions(predictions: Iterable[Prediction], output_path: Path) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with output_path.open("w", encoding="utf-8") as handle:
        for prediction in predictions:
            handle.write(json.dumps(prediction.model_dump(mode="json"), ensure_ascii=False) + "\n")
            count += 1
    return count


class PredictionJsonlWriter:
    def __init__(self, output_path: Path, append: bool = False):
        self.output_path = output_path
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        mode = "a" if append else "w"
        self.handle = self.output_path.open(mode, encoding="utf-8")
        self.count = 0

    def write(self, prediction: Prediction) -> None:
        self.handle.write(json.dumps(prediction.model_dump(mode="json"), ensure_ascii=False) + "\n")
        self.handle.flush()
        self.count += 1

    def close(self) -> None:
        self.handle.close()

    def __enter__(self) -> "PredictionJsonlWriter":
        return self

    def __exit__(self, *_exc_info) -> None:
        self.close()
