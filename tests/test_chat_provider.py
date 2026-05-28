from ragbench.llms.chat import GENERATION_SKIPPED_MESSAGE, ChatConfig, ProviderChat


def test_provider_chat_skips_generation_without_key() -> None:
    chat = ProviderChat(
        ChatConfig(
            provider="gemini",
            model="gemini-2.5-flash",
            api_key=None,
            base_url="https://generativelanguage.googleapis.com/v1beta",
        )
    )

    assert chat.generation_enabled is False
    assert chat.complete("system", "user") == GENERATION_SKIPPED_MESSAGE


def test_provider_chat_rejects_unsupported_provider_with_key() -> None:
    chat = ProviderChat(
        ChatConfig(
            provider="other",
            model="fake",
            api_key="test-key",
            base_url="https://example.test",
        )
    )

    try:
        chat.complete("system", "user")
    except ValueError as exc:
        assert "Unsupported LLM_PROVIDER" in str(exc)
    else:
        raise AssertionError("Expected unsupported provider to raise ValueError")
