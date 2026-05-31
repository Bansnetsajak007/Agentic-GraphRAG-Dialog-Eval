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


def test_provider_chat_dedupes_multiple_keys() -> None:
    chat = ProviderChat(
        ChatConfig(
            provider="gemini",
            model="gemini-2.5-flash",
            api_key="key-a",
            base_url="https://generativelanguage.googleapis.com/v1beta",
            api_keys=("key-a", "key-b", "key-b"),
        )
    )

    assert chat.api_keys == ("key-a", "key-b")
    assert chat.api_key == "key-a"


def test_provider_chat_rotates_key() -> None:
    chat = ProviderChat(
        ChatConfig(
            provider="gemini",
            model="gemini-2.5-flash",
            api_key=None,
            base_url="https://generativelanguage.googleapis.com/v1beta",
            api_keys=("key-a", "key-b"),
        )
    )

    chat._rotate_key()

    assert chat.api_key == "key-b"


def test_provider_chat_selects_random_key(monkeypatch) -> None:
    chat = ProviderChat(
        ChatConfig(
            provider="gemini",
            model="gemini-2.5-flash",
            api_key=None,
            base_url="https://generativelanguage.googleapis.com/v1beta",
            api_keys=("key-a", "key-b", "key-c"),
        )
    )
    monkeypatch.setattr("ragbench.llms.chat.random.choice", lambda choices: choices[-1])

    chat._select_random_key()

    assert chat.api_key == "key-c"


def test_provider_chat_avoids_disabled_random_key(monkeypatch) -> None:
    chat = ProviderChat(
        ChatConfig(
            provider="gemini",
            model="gemini-2.5-flash",
            api_key=None,
            base_url="https://generativelanguage.googleapis.com/v1beta",
            api_keys=("key-a", "key-b", "key-c"),
        )
    )
    chat.disabled_key_indices.add(2)
    monkeypatch.setattr("ragbench.llms.chat.random.choice", lambda choices: choices[-1])

    chat._select_random_key()

    assert chat.api_key == "key-b"


def test_provider_chat_selects_different_key(monkeypatch) -> None:
    chat = ProviderChat(
        ChatConfig(
            provider="gemini",
            model="gemini-2.5-flash",
            api_key=None,
            base_url="https://generativelanguage.googleapis.com/v1beta",
            api_keys=("key-a", "key-b", "key-c"),
        )
    )
    monkeypatch.setattr("ragbench.llms.chat.random.choice", lambda choices: choices[-1])

    chat._select_different_key()

    assert chat.api_key == "key-c"
