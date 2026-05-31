"""Shared constants and aliases for research-grade RAG analysis."""

from __future__ import annotations


ARCHITECTURES = ("traditional_rag", "agentic_rag", "agentic_graph_rag")

METRIC_ALIASES: dict[str, str] = {
    "overall": "overall_score",
    "overall_score": "overall_score",
    "faithfulness": "faithfulness",
    "groundedness": "faithfulness",
    "answer_relevance": "answer_relevancy",
    "answer_relevancy": "answer_relevancy",
    "context_relevance": "context_relevancy",
    "context_relevancy": "context_relevancy",
    "context_precision": "context_precision",
    "context_recall": "context_recall",
    "completeness": "answer_completeness",
    "answer_completeness": "answer_completeness",
    "correctness": "answer_correctness",
    "answer_correctness": "answer_correctness",
    "safety": "policy_compliance",
    "policy_compliance": "policy_compliance",
    "latency_ms": "latency_ms",
    "retrieved_chunks": "average_retrieved_chunks",
    "average_retrieved_chunks": "average_retrieved_chunks",
    "hit_rate_at_k": "hit_rate_at_k",
    "mrr_at_k": "mrr_at_k",
    "ndcg_at_k": "ndcg_at_k",
    "hallucination_rate": "hallucination_rate",
    "romanized_query_understanding": "romanized_query_understanding",
    "code_mixed_handling": "code_mixed_handling",
    "intent_classification_accuracy": "intent_classification_accuracy",
    "company_domain_accuracy": "company_domain_accuracy",
    "escalation_correctness": "escalation_correctness",
    "tone_appropriateness": "tone_appropriateness",
    "success": "success",
    "failure": "failure",
    "token_usage": "token_usage",
    "agent_steps": "agent_steps",
    "tool_calls": "tool_calls",
}

SCORE_METRICS = {
    "overall_score",
    "faithfulness",
    "answer_relevancy",
    "context_relevancy",
    "context_precision",
    "context_recall",
    "answer_completeness",
    "answer_correctness",
    "policy_compliance",
    "hit_rate_at_k",
    "mrr_at_k",
    "ndcg_at_k",
    "hallucination_rate",
    "romanized_query_understanding",
    "code_mixed_handling",
    "intent_classification_accuracy",
    "company_domain_accuracy",
    "escalation_correctness",
    "tone_appropriateness",
    "success",
    "failure",
}

RETRIEVAL_METRICS = [
    "context_precision",
    "context_recall",
    "context_relevancy",
    "hit_rate_at_k",
    "mrr_at_k",
    "ndcg_at_k",
]

GENERATION_METRICS = [
    "faithfulness",
    "answer_relevancy",
    "answer_correctness",
    "answer_completeness",
    "policy_compliance",
    "hallucination_rate",
]

ROMANIZED_METRICS = [
    "romanized_query_understanding",
    "code_mixed_handling",
    "intent_classification_accuracy",
    "company_domain_accuracy",
    "escalation_correctness",
    "tone_appropriateness",
]

LATENCY_METRICS = {"latency_ms"}
COUNT_METRICS = {"average_retrieved_chunks", "token_usage", "agent_steps", "tool_calls"}

PREFERRED_METRICS = [
    "overall_score",
    *RETRIEVAL_METRICS,
    "average_retrieved_chunks",
    *GENERATION_METRICS,
    *ROMANIZED_METRICS,
    "latency_ms",
    "token_usage",
    "agent_steps",
    "tool_calls",
    "success",
    "failure",
]

