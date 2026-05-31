"""Optional LLM-as-judge scoring for generation and language robustness metrics."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any

from ragbench.evaluators.metric_schemas import EvaluationDatasetItem, RAGResultItem
from ragbench.llms.chat import ChatConfig, ProviderChat


JUDGED_METRICS = [
    "faithfulness",
    "answer_relevancy",
    "answer_correctness",
    "answer_completeness",
    "policy_compliance",
    "romanized_query_understanding",
    "tone_appropriateness",
]


@dataclass(frozen=True)
class JudgeConfig:
    provider: str = "none"
    model: str = ""
    api_key: str | None = None
    base_url: str = ""
    api_keys: tuple[str, ...] = ()

    @property
    def enabled(self) -> bool:
        return self.provider not in {"", "none", "disabled"} and bool(self.api_key or self.api_keys)


class RAGJudge:
    def __init__(self, config: JudgeConfig):
        self.config = config
        self.chat_model = (
            ProviderChat(
                ChatConfig(
                    provider=config.provider,
                    model=config.model,
                    api_key=config.api_key,
                    base_url=config.base_url,
                    api_keys=config.api_keys,
                    temperature=0.0,
                )
            )
            if config.enabled
            else None
        )

    @classmethod
    def from_env(cls, provider_override: str | None = None, model_override: str | None = None) -> "RAGJudge":
        return cls(build_judge_config(provider_override=provider_override, model_override=model_override))

    @property
    def enabled(self) -> bool:
        return self.chat_model is not None

    def score(
        self,
        dataset_item: EvaluationDatasetItem,
        result: RAGResultItem,
    ) -> tuple[dict[str, float | None], dict[str, Any]]:
        if not self.chat_model:
            return {}, {"enabled": False, "reason": "Judge LLM is not configured."}

        prompt = _build_judge_prompt(dataset_item, result)
        try:
            raw_response = self.chat_model.complete(_system_prompt(), prompt)
            payload = _extract_json(raw_response)
            scores = {
                metric: _clamp_score(payload.get(metric))
                for metric in JUDGED_METRICS
            }
            if scores.get("faithfulness") is not None:
                scores["hallucination_rate"] = 1.0 - float(scores["faithfulness"])
            return scores, {
                "enabled": True,
                "provider": self.config.provider,
                "model": self.config.model,
                "rationale": str(payload.get("rationale") or "")[:1000],
            }
        except Exception as exc:
            return {}, {
                "enabled": True,
                "provider": self.config.provider,
                "model": self.config.model,
                "error": f"{type(exc).__name__}: {exc}",
            }


def build_judge_config(provider_override: str | None = None, model_override: str | None = None) -> JudgeConfig:
    provider = (provider_override or os.getenv("JUDGE_LLM_PROVIDER", "none")).lower()
    if provider == "auto":
        provider = _auto_provider()
    if provider in {"", "none", "disabled"}:
        return JudgeConfig(provider="none")
    if provider == "openai":
        return JudgeConfig(
            provider="openai",
            model=model_override or os.getenv("JUDGE_MODEL") or os.getenv("JUDGE_OPENAI_MODEL", "gpt-4o-mini"),
            api_key=os.getenv("JUDGE_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("JUDGE_OPENAI_BASE_URL") or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        )
    if provider == "gemini":
        primary_key = os.getenv("JUDGE_GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
        extra_keys = _parse_env_list("JUDGE_GEMINI_API_KEYS") or _parse_env_list("GEMINI_API_KEYS")
        return JudgeConfig(
            provider="gemini",
            model=model_override or os.getenv("JUDGE_MODEL") or os.getenv("JUDGE_GEMINI_MODEL", "gemini-2.5-flash"),
            api_key=primary_key,
            api_keys=tuple(key for key in [primary_key, *extra_keys] if key),
            base_url=os.getenv("JUDGE_GEMINI_BASE_URL") or os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta"),
        )
    if provider == "nvidia":
        return JudgeConfig(
            provider="nvidia",
            model=model_override or os.getenv("JUDGE_MODEL") or os.getenv("JUDGE_NVIDIA_MODEL", "meta/llama-3.1-8b-instruct"),
            api_key=os.getenv("JUDGE_NVIDIA_API_KEY") or os.getenv("NVIDIA_API_KEY"),
            base_url=os.getenv("JUDGE_NVIDIA_BASE_URL") or os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1"),
        )
    raise ValueError("JUDGE_LLM_PROVIDER must be 'none', 'auto', 'openai', 'gemini', or 'nvidia'.")


def _auto_provider() -> str:
    if os.getenv("JUDGE_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY"):
        return "openai"
    if os.getenv("JUDGE_GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY") or os.getenv("JUDGE_GEMINI_API_KEYS") or os.getenv("GEMINI_API_KEYS"):
        return "gemini"
    if os.getenv("JUDGE_NVIDIA_API_KEY") or os.getenv("NVIDIA_API_KEY"):
        return "nvidia"
    return "none"


def _system_prompt() -> str:
    return (
        "You are a strict RAG evaluation judge for Romanized Nepali customer-support answers. "
        "Return only valid JSON. Score each requested metric from 0.0 to 1.0."
    )


def _build_judge_prompt(dataset_item: EvaluationDatasetItem, result: RAGResultItem) -> str:
    context = "\n\n".join(
        f"[{chunk.get('chunk_id') or ''} | {chunk.get('source') or ''}]\n{str(chunk.get('content') or '')[:1200]}"
        for chunk in result.retrieved_chunks[:6]
    )
    expected_points = "\n".join(f"- {point}" for point in dataset_item.expected_answer_points) or "Not provided."
    return f"""Evaluate the answer for this customer-support RAG result.

Architecture: {result.architecture}
Company: {dataset_item.company}
Query category: {dataset_item.category}
Difficulty: {dataset_item.difficulty}
Expected topic: {dataset_item.expected_topic or result.expected_topic or "Not provided."}
Expected source doc: {dataset_item.expected_source_doc or result.expected_document or "Not provided."}
Expected answer points:
{expected_points}

Customer query:
{dataset_item.query}

Generated answer:
{result.answer}

Retrieved context:
{context or "No retrieved context."}

Return JSON with exactly these numeric fields:
faithfulness, answer_relevancy, answer_correctness, answer_completeness, policy_compliance,
romanized_query_understanding, tone_appropriateness.

Use this guidance:
- faithfulness: answer is supported by retrieved context.
- answer_relevancy: answer addresses the user query.
- answer_correctness: answer matches expected topic/source/answer points when provided.
- answer_completeness: answer covers all necessary customer-support information.
- policy_compliance: answer avoids unsupported promises and follows policy constraints.
- romanized_query_understanding: answer shows correct understanding of Romanized Nepali/code-mixed wording.
- tone_appropriateness: answer is polite, concise, and support-oriented.

Also include one short "rationale" string. Return JSON only."""


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            raise
        payload = json.loads(match.group(0))
    if not isinstance(payload, dict):
        raise ValueError("Judge response JSON must be an object.")
    return payload


def _clamp_score(value: Any) -> float | None:
    if value is None:
        return None
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    return max(0.0, min(1.0, numeric))


def _parse_env_list(name: str) -> list[str]:
    return [item.strip() for item in os.getenv(name, "").split(",") if item.strip()]
