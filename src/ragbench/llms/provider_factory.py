"""Provider selection for configured LLM backends."""

from __future__ import annotations

from typing import Any

from ragbench.llms.chat import ChatConfig, ProviderChat


def resolve_llm_provider(settings: Any) -> str:
    """Pick an LLM provider from explicit config or available API keys."""

    provider = settings.llm_provider.lower()
    if provider in {"openai", "gemini", "nvidia"}:
        return provider
    if provider != "auto":
        raise ValueError("LLM_PROVIDER must be 'auto', 'openai', 'gemini', or 'nvidia'.")
    if settings.openai_api_key:
        return "openai"
    if settings.gemini_api_key or settings.gemini_api_keys:
        return "gemini"
    if settings.nvidia_api_key:
        return "nvidia"
    return "gemini"


def build_chat_model(settings: Any) -> ProviderChat:
    provider = resolve_llm_provider(settings)
    if provider == "openai":
        return ProviderChat(
            ChatConfig(
                provider="openai",
                model=settings.openai_model,
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
                temperature=0.0,
            )
        )
    if provider == "gemini":
        gemini_keys = tuple(
            key
            for key in [settings.gemini_api_key, *settings.gemini_api_keys]
            if key
        )
        return ProviderChat(
            ChatConfig(
                provider="gemini",
                model=settings.gemini_model,
                api_key=settings.gemini_api_key,
                base_url=settings.gemini_base_url,
                api_keys=gemini_keys,
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
