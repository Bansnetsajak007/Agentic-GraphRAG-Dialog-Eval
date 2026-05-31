"""Run post-hoc RAG metric evaluation across all architecture outputs."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rich.console import Console

from ragbench.config import get_settings
from ragbench.evaluators.aggregation import (
    SUMMARY_FIELDS,
    error_analysis,
    metric_fieldnames,
    summarize_by_architecture,
    summarize_by_company,
    summarize_by_difficulty,
)
from ragbench.evaluators.data_io import (
    append_jsonl_item,
    detailed_metrics_path_for,
    load_detailed_metrics,
    load_dataset,
    load_results,
    result_path_for,
    write_csv,
    write_json,
)
from ragbench.evaluators.judge import RAGJudge
from ragbench.evaluators.metric_schemas import ARCHITECTURES, PerQueryMetricResult
from ragbench.evaluators.report import write_research_report
from ragbench.evaluators.scoring import RAGMetricScorer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compute research-grade RAG evaluation metrics.")
    parser.add_argument(
        "--dataset",
        type=Path,
        default=None,
        help="Evaluation dataset CSV/JSONL path. Defaults to data/eval/romanized_nepali_rag_eval_queries_300.csv.",
    )
    parser.add_argument("--results-dir", type=Path, default=Path("results"), help="Directory containing architecture result folders.")
    parser.add_argument(
        "--architectures",
        nargs="+",
        default=list(ARCHITECTURES),
        help=f"Architectures to evaluate. Defaults to: {', '.join(ARCHITECTURES)}.",
    )
    parser.add_argument("--top-k", type=int, default=None, help="Evaluate retrieval metrics over the first k chunks only.")
    parser.add_argument("--limit", type=int, default=None, help="Optional per-architecture query limit for debugging.")
    parser.add_argument(
        "--resume-detailed",
        action="store_true",
        help="Append to existing detailed metric JSONL files and skip already scored query IDs.",
    )
    parser.add_argument("--progress-every", type=int, default=25, help="Print progress every N newly scored queries.")
    parser.add_argument(
        "--judge-provider",
        default=None,
        help="Optional judge provider: none, auto, openai, gemini, or nvidia. Defaults to JUDGE_LLM_PROVIDER or none.",
    )
    parser.add_argument("--judge-model", default=None, help="Optional judge model override.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    settings = get_settings()
    console = Console()
    dataset_path = args.dataset or _default_dataset_path(settings.project_root)
    results_dir = args.results_dir

    try:
        _validate_architectures(args.architectures)
        dataset = load_dataset(dataset_path)
        judge = RAGJudge.from_env(provider_override=args.judge_provider, model_override=args.judge_model)
        scorer = RAGMetricScorer(company_map=settings.company_knowledge_base_map, judge=judge, top_k=args.top_k)

        all_records: list[PerQueryMetricResult] = []
        for architecture in args.architectures:
            result_path = result_path_for(results_dir, architecture)
            result_rows = load_results(result_path)
            if args.limit and args.limit > 0:
                result_rows = result_rows[: args.limit]
            detailed_path = detailed_metrics_path_for(results_dir, architecture)
            existing_payloads = load_detailed_metrics(detailed_path) if args.resume_detailed else []
            existing_records = [PerQueryMetricResult(**payload) for payload in existing_payloads]
            completed_ids = {record.query_id for record in existing_records}
            if not args.resume_detailed:
                detailed_path.parent.mkdir(parents=True, exist_ok=True)
                detailed_path.write_text("", encoding="utf-8")

            newly_scored = 0
            for result in result_rows:
                if result.query_id in completed_ids:
                    continue
                dataset_item = dataset.get(result.query_id)
                if dataset_item is None:
                    raise ValueError(f"Result {result_path} contains query_id not found in dataset: {result.query_id}")
                metric_record = scorer.score(dataset_item, result)
                append_jsonl_item(metric_record, detailed_path)
                newly_scored += 1
                if args.progress_every > 0 and newly_scored % args.progress_every == 0:
                    console.print(f"{architecture}: scored {newly_scored} new records")

            detailed_records = [PerQueryMetricResult(**payload) for payload in load_detailed_metrics(detailed_path)]
            all_records.extend(detailed_records)
            console.print(
                f"{architecture}: total detailed records {len(detailed_records)} "
                f"({newly_scored} newly scored, {len(completed_ids)} skipped)"
            )

        summary_rows = summarize_by_architecture(all_records)
        company_rows = summarize_by_company(all_records)
        difficulty_rows = summarize_by_difficulty(all_records)
        errors = error_analysis(all_records)
        judge_info = {
            "enabled": judge.enabled,
            "provider": judge.config.provider,
            "model": judge.config.model,
        }

        write_csv(summary_rows, results_dir / "rag_evaluation_summary.csv", SUMMARY_FIELDS)
        write_json(
            {
                "dataset_path": dataset_path.as_posix(),
                "judge": judge_info,
                "summary": summary_rows,
                "by_company": company_rows,
                "by_difficulty": difficulty_rows,
                "error_analysis": errors,
            },
            results_dir / "rag_evaluation_summary.json",
        )
        write_csv(company_rows, results_dir / "rag_evaluation_by_company.csv", metric_fieldnames(("architecture", "company")))
        write_csv(difficulty_rows, results_dir / "rag_evaluation_by_difficulty.csv", metric_fieldnames(("architecture", "difficulty")))
        write_research_report(
            output_path=results_dir / "rag_evaluation_report.md",
            dataset_path=dataset_path,
            summary_rows=summary_rows,
            company_rows=company_rows,
            difficulty_rows=difficulty_rows,
            error_summary=errors,
            judge_info=judge_info,
        )
    except Exception as exc:
        console.print(f"[red]RAG metric evaluation failed:[/red] {exc}")
        return 1

    console.print(f"[green]Wrote RAG metric summary:[/green] {results_dir / 'rag_evaluation_summary.csv'}")
    console.print(f"[green]Wrote research report:[/green] {results_dir / 'rag_evaluation_report.md'}")
    if not judge.enabled:
        console.print("Judge LLM not configured; judge-dependent metrics were left blank or filled only by deterministic fallback.")
    return 0


def _default_dataset_path(project_root: Path) -> Path:
    direct_path = project_root / "data/eval/romanized_nepali_rag_eval_queries_300.csv"
    if direct_path.exists():
        return direct_path
    jsonl_path = project_root / "data/eval/romanized_nepali_rag_eval_queries_300.jsonl"
    if jsonl_path.exists():
        return jsonl_path
    return project_root / "data/eval/queries/romanized_nepali_rag_eval_queries_300.csv"


def _validate_architectures(architectures: list[str]) -> None:
    unsupported = sorted(set(architectures) - set(ARCHITECTURES))
    if unsupported:
        raise ValueError(f"Unsupported architectures: {unsupported}. Supported: {list(ARCHITECTURES)}")


if __name__ == "__main__":
    sys.exit(main())
