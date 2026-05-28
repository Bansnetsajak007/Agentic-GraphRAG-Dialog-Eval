"""Traditional Semantic RAG baseline pipeline."""

from __future__ import annotations

import time

from ragbench.llms.chat import ProviderChat
from ragbench.retrievers.semantic_retriever import SemanticRetriever
from ragbench.schemas import Prediction


SYSTEM_PROMPT = """You are ChitoMart customer support.
Answer using only the retrieved ChitoMart policy context.
Be concise, helpful, and grounded.
Romanized Nepali and English mixed style is allowed when natural.
If required information is missing from context, say so and ask for the needed detail.
Do not invent policy, order status, coupons, rider names, or compensation."""


def build_user_prompt(query: str, context_blocks: list[str]) -> str:
    context = "\n\n".join(context_blocks) if context_blocks else "No retrieved context."
    return f"""Customer query:
{query}

Retrieved context:
{context}

Write the support answer."""


class SemanticRAGPipeline:
    def __init__(
        self,
        retriever: SemanticRetriever,
        chat_model: ProviderChat,
        embedding_model_name: str,
        top_k: int = 4,
    ):
        self.retriever = retriever
        self.chat_model = chat_model
        self.embedding_model_name = embedding_model_name
        self.top_k = top_k

    def run(self, query_id: str, query: str, intent: str = "") -> Prediction:
        started = time.perf_counter()
        retrieved = self.retriever.retrieve(query, top_k=self.top_k)
        context_blocks = [
            f"[{chunk.chunk_id} | {chunk.source}]\n{chunk.content}"
            for chunk in retrieved
        ]
        answer = self.chat_model.complete(SYSTEM_PROMPT, build_user_prompt(query, context_blocks))
        latency_ms = int((time.perf_counter() - started) * 1000)
        return Prediction(
            id=query_id,
            query=query,
            intent=intent,
            retrieved_context=retrieved,
            answer=answer,
            latency_ms=latency_ms,
            metadata={
                "top_k": self.top_k,
                "embedding_model": self.embedding_model_name,
                "embedding_backend": self.retriever.embedder.backend,
                "llm_model": self.chat_model.model,
                "llm_provider": self.chat_model.provider,
                "generation_enabled": self.chat_model.generation_enabled,
            },
        )
