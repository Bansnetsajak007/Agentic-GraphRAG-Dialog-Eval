"""Publication-oriented analysis figures."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from ragbench.analysis.schemas import ARCHITECTURES


def generate_figures(
    frame: pd.DataFrame,
    descriptive_rows: list[dict[str, Any]],
    company_rows: list[dict[str, Any]],
    difficulty_rows: list[dict[str, Any]],
    pairwise_rows: list[dict[str, Any]],
    failure_rows: list[dict[str, Any]],
    output_dir: Path,
) -> list[Path]:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as exc:
        raise RuntimeError("matplotlib is required to generate PNG figures. Run `uv sync` after adding dependencies.") from exc

    output_dir.mkdir(parents=True, exist_ok=True)
    generated: list[Path] = []
    generated.append(_overall_score_ci(plt, descriptive_rows, output_dir))
    generated.append(_score_boxplot(plt, frame, output_dir))
    generated.append(_latency_distribution(plt, frame, output_dir))
    generated.append(_grouped_bar(plt, pd.DataFrame(company_rows), "company", "score_by_company_architecture", output_dir))
    generated.append(_grouped_bar(plt, pd.DataFrame(difficulty_rows), "difficulty", "score_by_difficulty_architecture", output_dir))
    generated.append(_quality_latency_scatter(plt, frame, output_dir))
    generated.append(_pairwise_diff_plot(plt, pairwise_rows, output_dir))
    generated.append(_metric_radar(plt, frame, output_dir))
    generated.append(_failure_type_counts(plt, failure_rows, output_dir))
    return generated


def _overall_score_ci(plt: Any, descriptive_rows: list[dict[str, Any]], output_dir: Path) -> Path:
    data = pd.DataFrame([row for row in descriptive_rows if row["metric"] == "overall_score"])
    data.to_csv(output_dir / "overall_score_ci_data.csv", index=False)
    path = output_dir / "overall_score_by_architecture_ci.png"
    fig, ax = plt.subplots(figsize=(7, 4))
    errors = [
        [row["mean"] - row["ci95_low"] for _idx, row in data.iterrows()],
        [row["ci95_high"] - row["mean"] for _idx, row in data.iterrows()],
    ]
    ax.bar(data["architecture"], data["mean"], yerr=errors, capsize=5, color=["#4C78A8", "#F58518", "#54A24B"])
    ax.set_ylabel("Overall score")
    ax.set_title("Overall score by architecture with 95% bootstrap CI")
    ax.set_ylim(0, 1)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path


def _score_boxplot(plt: Any, frame: pd.DataFrame, output_dir: Path) -> Path:
    frame[["architecture", "overall_score"]].to_csv(output_dir / "score_distribution_boxplot_data.csv", index=False)
    path = output_dir / "score_distribution_boxplot_by_architecture.png"
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.boxplot([frame[frame["architecture"] == arch]["overall_score"].dropna() for arch in ARCHITECTURES], labels=ARCHITECTURES)
    ax.set_ylabel("Overall score")
    ax.set_title("Score distribution by architecture")
    ax.set_ylim(0, 1)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path


def _latency_distribution(plt: Any, frame: pd.DataFrame, output_dir: Path) -> Path:
    frame[["architecture", "latency_ms"]].to_csv(output_dir / "latency_distribution_data.csv", index=False)
    path = output_dir / "latency_distribution_by_architecture.png"
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.boxplot([frame[frame["architecture"] == arch]["latency_ms"].dropna() for arch in ARCHITECTURES], labels=ARCHITECTURES)
    ax.set_ylabel("Latency ms")
    ax.set_title("Latency distribution by architecture")
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path


def _grouped_bar(plt: Any, data: pd.DataFrame, group_field: str, name: str, output_dir: Path) -> Path:
    data.to_csv(output_dir / f"{name}_data.csv", index=False)
    path = output_dir / f"{name}.png"
    groups = sorted(data[group_field].dropna().unique())
    width = 0.24
    x = list(range(len(groups)))
    fig, ax = plt.subplots(figsize=(9, 4.8))
    for idx, architecture in enumerate(ARCHITECTURES):
        subset = data[data["architecture"] == architecture].set_index(group_field)
        values = [subset.loc[group]["mean_overall_score"] if group in subset.index else 0 for group in groups]
        ax.bar([value + (idx - 1) * width for value in x], values, width=width, label=architecture)
    ax.set_xticks(x)
    ax.set_xticklabels(groups, rotation=25, ha="right")
    ax.set_ylabel("Mean overall score")
    ax.set_title(f"Score by {group_field} and architecture")
    ax.set_ylim(0, 1)
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path


def _quality_latency_scatter(plt: Any, frame: pd.DataFrame, output_dir: Path) -> Path:
    data = frame[["architecture", "overall_score", "latency_ms", "difficulty"]]
    data.to_csv(output_dir / "quality_vs_latency_scatter_data.csv", index=False)
    path = output_dir / "quality_vs_latency_scatter.png"
    fig, ax = plt.subplots(figsize=(7, 4.8))
    for architecture in ARCHITECTURES:
        subset = data[data["architecture"] == architecture]
        ax.scatter(subset["latency_ms"], subset["overall_score"], s=12, alpha=0.5, label=architecture)
    ax.set_xlabel("Latency ms")
    ax.set_ylabel("Overall score")
    ax.set_title("Quality vs latency")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path


def _pairwise_diff_plot(plt: Any, pairwise_rows: list[dict[str, Any]], output_dir: Path) -> Path:
    data = pd.DataFrame(pairwise_rows)
    data.to_csv(output_dir / "pairwise_score_difference_data.csv", index=False)
    path = output_dir / "pairwise_score_difference_plot.png"
    fig, ax = plt.subplots(figsize=(8, 4))
    x = list(range(len(data)))
    ax.errorbar(
        x,
        data["mean_difference_a_minus_b"],
        yerr=[
            data["mean_difference_a_minus_b"] - data["bootstrap_ci_low"],
            data["bootstrap_ci_high"] - data["mean_difference_a_minus_b"],
        ],
        fmt="o",
        capsize=5,
    )
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(data["comparison"], rotation=25, ha="right")
    ax.set_ylabel("Mean paired score difference")
    ax.set_title("Pairwise overall-score differences with 95% CI")
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path


def _metric_radar(plt: Any, frame: pd.DataFrame, output_dir: Path) -> Path:
    import math

    metrics = ["context_recall", "faithfulness", "answer_relevancy", "policy_compliance", "tone_appropriateness", "success"]
    data = frame.groupby("architecture")[metrics].mean(numeric_only=True).reset_index()
    data.to_csv(output_dir / "metric_radar_data.csv", index=False)
    path = output_dir / "metric_radar_chart.png"
    angles = [idx / float(len(metrics)) * 2 * math.pi for idx in range(len(metrics))]
    angles += angles[:1]
    fig = plt.figure(figsize=(6, 6))
    ax = plt.subplot(111, polar=True)
    for _idx, row in data.iterrows():
        values = [row[metric] for metric in metrics]
        values += values[:1]
        ax.plot(angles, values, linewidth=1.5, label=row["architecture"])
        ax.fill(angles, values, alpha=0.08)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(metrics)
    ax.set_ylim(0, 1)
    ax.set_title("Metric radar chart")
    ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.1))
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path


def _failure_type_counts(plt: Any, failure_rows: list[dict[str, Any]], output_dir: Path) -> Path:
    data = pd.DataFrame(failure_rows)
    data.to_csv(output_dir / "failure_type_count_data.csv", index=False)
    path = output_dir / "failure_type_count_by_architecture.png"
    pivot = data.pivot_table(index="failure_type", columns="architecture", values="count", fill_value=0)
    fig, ax = plt.subplots(figsize=(10, 5))
    pivot.plot(kind="bar", ax=ax)
    ax.set_ylabel("Count")
    ax.set_title("Failure type count by architecture")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path

