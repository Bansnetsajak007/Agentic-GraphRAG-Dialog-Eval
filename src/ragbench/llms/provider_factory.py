"""Provider selection for configured LLM backends."""

from __future__ import annotations

from typing import Any

from ragbench.llms.chat import ChatConfig, ProviderChat


def resolve_llm_provider(settings: Any) -> str:
    """Pick an LLM provider from explicit config or available API keys."""

    provider = settings.llm_provider.lower()
    if provider in {"gemini", "nvidia"}:
        return provider
    if provider != "auto":
        raise ValueError("LLM_PROVIDER must be 'auto', 'gemini', or 'nvidia'.")
    if settings.gemini_api_key:
        return "gemini"
    if settings.nvidia_api_key:
        return "nvidia"
    return "gemini"


def build_chat_model(settings: Any) -> ProviderChat:
    provider = resolve_llm_provider(settings)
    if provider == "gemini":
        return ProviderChat(
            ChatConfig(
                provider="gemini",
                model=settings.gemini_model,
                api_key=settings.gemini_api_key,
                base_url=settings.gemini_base_url,
                temperature=0.0,
            )
        )
    return ProviderChat(
        ChatConfig(
            provider="nvidia",
            model=settings.nvidia_model,
            api_key=settings.nvidia_api_key,
            base_url=settings.nvidia_base_url,
            temperature=0.0,
        )
    )
