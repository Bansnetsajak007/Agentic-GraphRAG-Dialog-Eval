"""CLI for research-grade statistical analysis of existing RAG metric outputs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd
from rich.console import Console

from ragbench.analysis.failures import build_failure_taxonomy, write_representative_failures
from ragbench.analysis.loading import load_analysis_data
from ragbench.analysis.reporting import write_research_grade_report
from ragbench.analysis.retrieval import retrieval_quality_summary
from ragbench.analysis.schemas import ARCHITECTURES
from ragbench.analysis.stats import descriptive_stats, latency_stats, pairwise_tests
from ragbench.analysis.stratified import category_summary, stratified_summary
from ragbench.analysis.tradeoff import latency_quality_tradeoff
from ragbench.analysis.visualizations import generate_figures


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Research-grade analysis of existing RAG evaluation metrics.")
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    parser.add_argument("--output-dir", type=Path, default=Path("results/analysis"))
    parser.add_argument("--bootstrap-samples", type=int, default=10000)
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--practical-threshold", type=float, default=0.01)
    parser.add_argument("--skip-figures", action="store_true", help="Skip PNG figure generation.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    console = Console()
    try:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        data = load_analysis_data(args.results_dir, architectures=ARCHITECTURES)
        _write_json(data.validation_summary, args.output_dir / "validation_summary.json")

        desc_rows = descriptive_stats(
            data.frame,
            data.available_metrics,
            bootstrap_samples=args.bootstrap_samples,
            alpha=args.alpha,
        )
        latency_rows = latency_stats(data.frame)
        desc_rows = _merge_latency_rows(desc_rows, latency_rows)
        _write_csv(desc_rows, args.output_dir / "descriptive_stats.csv")
        _write_csv(
            [
                {
                    "architecture": row["architecture"],
                    "metric": row["metric"],
                    "n": row["n"],
                    "mean": row["mean"],
                    "ci95_low": row["ci95_low"],
                    "ci95_high": row["ci95_high"],
                }
                for row in desc_rows
            ],
            args.output_dir / "bootstrap_confidence_intervals.csv",
        )

        pairwise_rows = pairwise_tests(
            data.frame,
            metric="overall_score",
            bootstrap_samples=args.bootstrap_samples,
            alpha=args.alpha,
            practical_threshold=args.practical_threshold,
        )
        _write_csv(pairwise_rows, args.output_dir / "pairwise_significance_tests.csv")

        company_rows = stratified_summary(data.frame, ["company"], bootstrap_samples=args.bootstrap_samples, alpha=args.alpha)
        difficulty_rows = stratified_summary(data.frame, ["difficulty"], bootstrap_samples=args.bootstrap_samples, alpha=args.alpha)
        company_difficulty_rows = stratified_summary(
            data.frame,
            ["company", "difficulty"],
            bootstrap_samples=args.bootstrap_samples,
            alpha=args.alpha,
        )
        category_rows = category_summary(data.frame, bootstrap_samples=args.bootstrap_samples, alpha=args.alpha)
        _write_csv(company_rows, args.output_dir / "by_company_analysis.csv")
        _write_csv(difficulty_rows, args.output_dir / "by_difficulty_analysis.csv")
        _write_csv(company_difficulty_rows, args.output_dir / "by_company_difficulty_analysis.csv")
        _write_csv(category_rows, args.output_dir / "by_category_analysis.csv")

        retrieval_rows = retrieval_quality_summary(data.frame)
        _write_csv(retrieval_rows, args.output_dir / "retrieval_quality_analysis.csv")

        tradeoff_rows = latency_quality_tradeoff(data.frame)
        _write_csv(tradeoff_rows, args.output_dir / "latency_quality_tradeoff.csv")

        failure_rows, representative_failures = build_failure_taxonomy(data.frame)
        _write_csv(failure_rows, args.output_dir / "failure_taxonomy.csv")
        write_representative_failures(args.output_dir / "representative_failures.jsonl", representative_failures)

        figure_paths: list[Path] = []
        if not args.skip_figures:
            figure_paths = generate_figures(
                frame=data.frame,
                descriptive_rows=desc_rows,
                company_rows=company_rows,
                difficulty_rows=difficulty_rows,
                pairwise_rows=pairwise_rows,
                failure_rows=failure_rows,
                output_dir=args.output_dir / "figures",
            )

        write_research_grade_report(
            output_path=args.output_dir / "research_grade_rag_evaluation_report.md",
            validation=data.validation_summary,
            descriptive_rows=desc_rows,
            pairwise_rows=pairwise_rows,
            company_rows=company_rows,
            difficulty_rows=difficulty_rows,
            retrieval_rows=retrieval_rows,
            tradeoff_rows=tradeoff_rows,
            failure_rows=failure_rows,
        )
    except Exception as exc:
        console.print(f"[red]Research-grade analysis failed:[/red] {exc}")
        return 1

    summary = _summary(pairwise_rows, desc_rows, tradeoff_rows, difficulty_rows)
    console.print("[green]Research-grade analysis complete.[/green]")
    console.print(f"Output directory: {args.output_dir}")
    console.print(f"Generated figures: {len(figure_paths)}")
    console.print(f"Highest mean score: {summary['highest_mean_score']}")
    console.print(f"agentic_graph_rag vs traditional_rag: {summary['graph_vs_traditional']}")
    console.print(f"Fastest architecture: {summary['fastest_architecture']}")
    console.print(f"Best complex-query architecture: {summary['best_complex_architecture']}")
    return 0


def _merge_latency_rows(desc_rows: list[dict[str, Any]], latency_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    latency_by_arch = {row["architecture"]: row for row in latency_rows}
    for row in desc_rows:
        if row["metric"] == "latency_ms":
            row.update(latency_by_arch.get(row["architecture"], {}))
    return desc_rows


def _summary(
    pairwise_rows: list[dict[str, Any]],
    desc_rows: list[dict[str, Any]],
    tradeoff_rows: list[dict[str, Any]],
    difficulty_rows: list[dict[str, Any]],
) -> dict[str, str]:
    overall_rows = [row for row in desc_rows if row["metric"] == "overall_score"]
    best = max(overall_rows, key=lambda row: row["mean"])
    fastest = min([row for row in desc_rows if row["metric"] == "latency_ms"], key=lambda row: row["mean"])
    graph_vs_traditional = next(
        (
            row
            for row in pairwise_rows
            if {row["architecture_a"], row["architecture_b"]} == {"agentic_graph_rag", "traditional_rag"}
        ),
        None,
    )
    complex_rows = [row for row in difficulty_rows if str(row.get("difficulty")).lower() == "complex"]
    best_complex = max(complex_rows, key=lambda row: row["mean_overall_score"]) if complex_rows else None
    return {
        "highest_mean_score": f"{best['architecture']} ({best['mean']:.4f})",
        "graph_vs_traditional": graph_vs_traditional["conclusion"] if graph_vs_traditional else "not available",
        "fastest_architecture": fastest["architecture"],
        "best_complex_architecture": best_complex["architecture"] if best_complex else "not available",
        "best_tradeoff": tradeoff_rows[0].get("best_quality_latency_tradeoff", "not available") if tradeoff_rows else "not available",
    }


def _write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(path, index=False)


def _write_json(payload: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())

