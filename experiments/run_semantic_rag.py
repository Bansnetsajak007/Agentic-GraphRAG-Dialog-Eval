"""Run the Phase 1 Traditional Semantic RAG baseline."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

from rich.console import Console

from ragbench.config import get_settings
from ragbench.evaluators.prediction_writer import PredictionJsonlWriter
from ragbench.llms.chat import GENERATION_SKIPPED_MESSAGE
from ragbench.llms.provider_factory import build_chat_model
from ragbench.loaders.query_loader import load_eval_queries
from ragbench.pipelines.semantic_rag import SemanticRAGPipeline
from ragbench.retrievers.semantic_retriever import SemanticRetriever


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Traditional Semantic RAG predictions.")
    parser.add_argument("--limit", type=int, default=None, help="Maximum number of queries to run.")
    parser.add_argument("--top-k", type=int, default=4, help="Number of chunks to retrieve.")
    parser.add_argument("--company", default=None, help="Company-specific index to query, e.g. chitomart.")
    parser.add_argument("--delay-seconds", type=float, default=0.0, help="Delay between LLM calls for rate-limited providers.")
    parser.add_argument("--resume", action="store_true", help="Append to existing predictions and skip already processed IDs.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    settings = get_settings()
    console = Console()

    try:
        eval_queries = load_eval_queries(settings.processed_queries_path, limit=args.limit)
        completed_ids: set[str] = set()
        if args.resume and settings.predictions_path.exists():
            with settings.predictions_path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    if line.strip():
                        completed_ids.add(str(json.loads(line)["id"]))
            eval_queries = [query for query in eval_queries if query.id not in completed_ids]
        retriever = SemanticRetriever(
            persist_dir=settings.chroma_dir,
            collection_name=settings.collection_name,
            embedding_model_name=settings.embedding_model,
            top_k=args.top_k,
            company=args.company,
        )
        chat_model = build_chat_model(settings)
        pipeline = SemanticRAGPipeline(
            retriever=retriever,
            chat_model=chat_model,
            embedding_model_name=settings.embedding_model,
            top_k=args.top_k,
        )
        predictions = []
        with PredictionJsonlWriter(settings.predictions_path, append=args.resume) as writer:
            for index, query in enumerate(eval_queries):
                prediction = pipeline.run(query.id, query.query, intent=query.intent)
                writer.write(prediction)
                predictions.append(prediction)
                if args.delay_seconds > 0 and index < len(eval_queries) - 1:
                    time.sleep(args.delay_seconds)
    except Exception as exc:
        console.print(f"[red]Semantic RAG run failed:[/red] {exc}")
        return 1

    average_latency = sum(prediction.latency_ms for prediction in predictions) / len(predictions) if predictions else 0
    skipped = sum(1 for prediction in predictions if prediction.answer == GENERATION_SKIPPED_MESSAGE)
    generated = len(predictions) - skipped

    if args.resume:
        console.print(f"Previously completed queries skipped: {len(completed_ids)}")
    console.print(f"[green]Processed queries this run:[/green] {len(predictions)}")
    console.print(f"Output path: {settings.predictions_path}")
    console.print(f"Average latency ms: {average_latency:.1f}")
    console.print(f"Answers generated: {generated}")
    console.print(f"Generation skipped outputs: {skipped}")
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(exit_code)
