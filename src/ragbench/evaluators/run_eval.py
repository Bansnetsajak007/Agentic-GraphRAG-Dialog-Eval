"""Run architecture evaluation over the Romanized Nepali RAG query dataset."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from rich.console import Console

from ragbench.config import get_settings
from ragbench.evaluators.architectures import EvaluationArchitectureRunner, SUPPORTED_ARCHITECTURES
from ragbench.evaluators.evaluation_writer import EvaluationJsonlWriter
from ragbench.evaluators.summary_report import write_evaluation_summary
from ragbench.llms.provider_factory import build_chat_model
from ragbench.loaders.eval_dataset_loader import load_evaluation_queries


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run RAG architecture evaluation.")
    parser.add_argument(
        "--architecture",
        required=True,
        help=f"Architecture to evaluate: {', '.join(SUPPORTED_ARCHITECTURES)}.",
    )
    parser.add_argument("--dataset-path", type=Path, default=None, help="CSV evaluation dataset path.")
    parser.add_argument("--output-path", type=Path, default=None, help="Override JSONL output path.")
    parser.add_argument("--summary-path", type=Path, default=None, help="Override summary CSV output path.")
    parser.add_argument("--limit", type=int, default=None, help="Maximum number of queries to run.")
    parser.add_argument("--top-k", type=int, default=4, help="Number of chunks to retrieve.")
    parser.add_argument("--delay-seconds", type=float, default=0.0, help="Delay between queries for rate-limited providers.")
    parser.add_argument("--resume", action="store_true", help="Append to existing output and skip already processed query IDs.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    settings = get_settings()
    console = Console()

    if args.architecture not in SUPPORTED_ARCHITECTURES:
        console.print(
            f"[red]Unsupported architecture:[/red] {args.architecture}. "
            f"Supported values: {', '.join(SUPPORTED_ARCHITECTURES)}"
        )
        return 2

    dataset_path = args.dataset_path or settings.evaluation_dataset_path
    output_path = args.output_path or settings.architecture_results_paths[args.architecture]
    summary_path = args.summary_path or settings.evaluation_summary_path

    try:
        queries = load_evaluation_queries(dataset_path, limit=args.limit)
        completed_ids = _load_completed_ids(output_path) if args.resume else set()
        if completed_ids:
            queries = [query for query in queries if query.query_id not in completed_ids]

        architecture_runner = EvaluationArchitectureRunner(
            architecture=args.architecture,
            settings=settings,
            chat_model=build_chat_model(settings),
            top_k=args.top_k,
        )

        processed = 0
        failed = 0
        with EvaluationJsonlWriter(output_path, append=args.resume) as writer:
            for index, query in enumerate(queries):
                try:
                    result = architecture_runner.run(query)
                except Exception as exc:
                    result = architecture_runner.error_result(query, exc)
                    failed += 1
                writer.write(result)
                processed += 1
                if args.delay_seconds > 0 and index < len(queries) - 1:
                    time.sleep(args.delay_seconds)

        write_evaluation_summary(settings.architecture_results_paths, summary_path)
    except Exception as exc:
        console.print(f"[red]Evaluation run failed:[/red] {exc}")
        return 1

    if args.resume:
        console.print(f"Previously completed queries skipped: {len(completed_ids)}")
    console.print(f"[green]Architecture:[/green] {args.architecture}")
    console.print(f"Processed queries this run: {processed}")
    console.print(f"Per-query errors: {failed}")
    console.print(f"Output path: {output_path}")
    console.print(f"Summary path: {summary_path}")
    return 0


def _load_completed_ids(output_path: Path) -> set[str]:
    if not output_path.exists():
        return set()

    completed_ids: set[str] = set()
    with output_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                completed_ids.add(str(json.loads(line)["query_id"]))
            except (json.JSONDecodeError, KeyError) as exc:
                raise ValueError(f"Cannot resume from malformed JSONL {output_path} at line {line_number}: {exc}") from exc
    return completed_ids


if __name__ == "__main__":
    sys.exit(main())
