from types import SimpleNamespace

import pytest

from ragbench.llms.provider_factory import build_chat_model, resolve_llm_provider


def make_settings(**overrides):
    defaults = {
        "llm_provider": "auto",
        "openai_api_key": None,
        "openai_base_url": "https://api.openai.com/v1",
        "openai_model": "gpt-4o-mini",
        "gemini_api_key": None,
        "gemini_api_keys": [],
        "gemini_base_url": "https://generativelanguage.googleapis.com/v1beta",
        "gemini_model": "gemini-2.5-flash",
        "nvidia_api_key": None,
        "nvidia_base_url": "https://integrate.api.nvidia.com/v1",
        "nvidia_model": "meta/llama-3.1-8b-instruct",
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def test_auto_provider_prefers_openai_when_key_exists() -> None:
    settings = make_settings(openai_api_key="openai-key", gemini_api_key="gemini-key", nvidia_api_key="nvidia-key")

    assert resolve_llm_provider(settings) == "openai"


def test_auto_provider_uses_gemini_when_no_openai_key_exists() -> None:
    settings = make_settings(gemini_api_key="gemini-key", nvidia_api_key="nvidia-key")

    assert resolve_llm_provider(settings) == "gemini"


def test_auto_provider_uses_gemini_when_key_list_exists() -> None:
    settings = make_settings(gemini_api_keys=["gemini-key-1", "gemini-key-2"])

    assert resolve_llm_provider(settings) == "gemini"


def test_auto_provider_uses_nvidia_when_only_nvidia_key_exists() -> None:
    settings = make_settings(nvidia_api_key="nvidia-key")

    assert resolve_llm_provider(settings) == "nvidia"


def test_auto_provider_defaults_to_gemini_for_retrieval_only() -> None:
    settings = make_settings()
    chat = build_chat_model(settings)

    assert chat.provider == "gemini"
    assert chat.generation_enabled is False


def test_build_chat_model_supports_openai() -> None:
    settings = make_settings(openai_api_key="openai-key")
    chat = build_chat_model(settings)

    assert chat.provider == "openai"
    assert chat.model == "gpt-4o-mini"
    assert chat.generation_enabled is True


def test_build_chat_model_combines_single_and_list_gemini_keys() -> None:
    settings = make_settings(gemini_api_key="gemini-key-1", gemini_api_keys=["gemini-key-2"])
    chat = build_chat_model(settings)

    assert chat.api_keys == ("gemini-key-1", "gemini-key-2")


def test_explicit_provider_overrides_available_key() -> None:
    settings = make_settings(llm_provider="nvidia", gemini_api_key="gemini-key", nvidia_api_key=None)
    chat = build_chat_model(settings)

    assert chat.provider == "nvidia"
    assert chat.generation_enabled is False


def test_invalid_provider_raises() -> None:
    settings = make_settings(llm_provider="bad")

    with pytest.raises(ValueError, match="LLM_PROVIDER"):
        resolve_llm_provider(settings)
