"""Architecture adapters used by the evaluation runner."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ragbench.llms.chat import ProviderChat
from ragbench.pipelines.semantic_rag import SemanticRAGPipeline
from ragbench.retrievers.semantic_retriever import SemanticRetriever
from ragbench.schemas import EvaluationQuery, EvaluationResult


SUPPORTED_ARCHITECTURES = ("traditional_rag", "agentic_rag", "agentic_graph_rag")


ARCHITECTURE_IMPLEMENTATION_NOTES = {
    "traditional_rag": "Traditional semantic RAG baseline.",
    "agentic_rag": "Evaluation slot for Agentic RAG; currently uses the controlled semantic RAG adapter.",
    "agentic_graph_rag": "Evaluation slot for Agentic GraphRAG; currently uses the controlled semantic RAG adapter.",
}


class EvaluationArchitectureRunner:
    """Run one named architecture against company-specific semantic indexes."""

    def __init__(
        self,
        architecture: str,
        settings: Any,
        chat_model: ProviderChat,
        top_k: int = 4,
    ):
        if architecture not in SUPPORTED_ARCHITECTURES:
            raise ValueError(
                f"Unsupported architecture '{architecture}'. "
                f"Supported values: {', '.join(SUPPORTED_ARCHITECTURES)}"
            )
        self.architecture = architecture
        self.settings = settings
        self.chat_model = chat_model
        self.top_k = top_k
        self._pipelines: dict[str, SemanticRAGPipeline] = {}

    def run(self, query: EvaluationQuery) -> EvaluationResult:
        company_key = resolve_company_key(query.company, self.settings.company_knowledge_base_map)
        self._validate_company_docs(company_key)
        pipeline = self._pipeline_for_company(company_key)
        prediction = pipeline.run(query.query_id, query.query, intent=query.category)
        source_documents = sorted({chunk.source for chunk in prediction.retrieved_context if chunk.source})

        return EvaluationResult(
            query_id=query.query_id,
            architecture=self.architecture,
            company=query.company,
            company_key=company_key,
            query=query.query,
            difficulty=query.difficulty,
            category=query.category,
            expected_document=query.expected_document,
            expected_topic=query.expected_topic,
            answer=prediction.answer,
            retrieved_chunks=prediction.retrieved_context,
            source_documents=source_documents,
            latency_ms=prediction.latency_ms,
            token_usage=None,
            metadata={
                **query.metadata,
                **prediction.metadata,
                "architecture_note": ARCHITECTURE_IMPLEMENTATION_NOTES[self.architecture],
            },
        )

    def error_result(self, query: EvaluationQuery, exc: Exception) -> EvaluationResult:
        company_key = safe_resolve_company_key(query.company, self.settings.company_knowledge_base_map)
        return EvaluationResult(
            query_id=query.query_id,
            architecture=self.architecture,
            company=query.company,
            company_key=company_key,
            query=query.query,
            difficulty=query.difficulty,
            category=query.category,
            expected_document=query.expected_document,
            expected_topic=query.expected_topic,
            error=f"{type(exc).__name__}: {exc}",
            metadata={**query.metadata, "architecture_note": ARCHITECTURE_IMPLEMENTATION_NOTES[self.architecture]},
        )

    def _pipeline_for_company(self, company_key: str) -> SemanticRAGPipeline:
        if company_key not in self._pipelines:
            retriever = SemanticRetriever(
                persist_dir=self.settings.chroma_dir,
                collection_name=self.settings.collection_name,
                embedding_model_name=self.settings.embedding_model,
                top_k=self.top_k,
                company=company_key,
            )
            self._pipelines[company_key] = SemanticRAGPipeline(
                retriever=retriever,
                chat_model=self.chat_model,
                embedding_model_name=self.settings.embedding_model,
                top_k=self.top_k,
            )
        return self._pipelines[company_key]

    def _validate_company_docs(self, company_key: str) -> None:
        docs_dir = Path(self.settings.business_docs_dir) / company_key
        if not docs_dir.exists():
            raise FileNotFoundError(f"Knowledge base directory does not exist for company '{company_key}': {docs_dir}")


def resolve_company_key(company: str, company_map: dict[str, str]) -> str:
    if company in company_map:
        return company_map[company]
    normalized_company = _normalize_company_label(company)
    for label, company_key in company_map.items():
        if _normalize_company_label(label) == normalized_company:
            return company_key
    raise ValueError(f"No knowledge base mapping configured for company '{company}'.")


def safe_resolve_company_key(company: str, company_map: dict[str, str]) -> str | None:
    try:
        return resolve_company_key(company, company_map)
    except ValueError:
        return None


def _normalize_company_label(company: str) -> str:
    return " ".join(company.lower().replace("/", " ").replace("-", " ").split())
