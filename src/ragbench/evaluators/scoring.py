"""Per-query RAG metric scoring orchestration."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ragbench.evaluators.deterministic_metrics import score_deterministic_metrics
from ragbench.evaluators.judge import RAGJudge
from ragbench.evaluators.metric_schemas import EvaluationDatasetItem, PerQueryMetricResult, RAGResultItem


class RAGMetricScorer:
    def __init__(self, company_map: Mapping[str, str], judge: RAGJudge | None = None, top_k: int | None = None):
        self.company_map = company_map
        self.judge = judge or RAGJudge.from_env(provider_override="none")
        self.top_k = top_k

    def score(self, dataset_item: EvaluationDatasetItem, result: RAGResultItem) -> PerQueryMetricResult:
        metrics, evidence = score_deterministic_metrics(
            dataset_item=dataset_item,
            result=result,
            company_map=self.company_map,
            top_k=self.top_k,
        )
        judge_scores, judge_info = self.judge.score(dataset_item, result)
        for key, value in judge_scores.items():
            if value is not None:
                metrics[key] = value

        retrieved_chunk_ids = [str(chunk.get("chunk_id") or "") for chunk in result.retrieved_chunks if chunk.get("chunk_id")]
        source_documents = result.source_documents or evidence.get("source_documents", [])
        metadata: dict[str, Any] = {
            "deterministic_evidence": evidence,
            "result_metadata": result.metadata,
            "dataset_metadata": dataset_item.metadata,
        }
        return PerQueryMetricResult(
            query_id=result.query_id,
            architecture=result.architecture,
            company=dataset_item.company,
            company_key=result.company_key,
            difficulty=dataset_item.difficulty,
            category=dataset_item.category,
            query=dataset_item.query,
            answer=result.answer,
            metrics=metrics,
            expected_topic=dataset_item.expected_topic or result.expected_topic,
            expected_source_doc=dataset_item.expected_source_doc or result.expected_document,
            expected_answer_points=dataset_item.expected_answer_points,
            retrieved_chunk_ids=retrieved_chunk_ids,
            source_documents=source_documents,
            judge=judge_info,
            error=result.error,
            metadata=metadata,
        )
