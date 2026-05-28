"""Prepare Phase 1 evaluation queries from the raw Crowpeaks CSV."""

from __future__ import annotations

import argparse

from rich.console import Console

from ragbench.config import get_settings
from ragbench.loaders.query_loader import prepare_eval_queries


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare eval_queries_v1.csv from raw customer messages.")
    parser.add_argument("--limit", type=int, default=None, help="Maximum number of queries to prepare.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    settings = get_settings()
    console = Console()

    try:
        df = prepare_eval_queries(settings.raw_csv_path, settings.processed_queries_path, limit=args.limit)
    except FileNotFoundError as exc:
        console.print(f"[red]Dataset preparation failed:[/red] {exc}")
        console.print("[yellow]See docs/dataset_notes.md for expected dataset placement.[/yellow]")
        return 1
    except Exception as exc:
        console.print(f"[red]Dataset preparation failed:[/red] {exc}")
        return 1

    console.print(f"[green]Prepared {len(df)} queries[/green]")
    console.print(f"Output: {settings.processed_queries_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
