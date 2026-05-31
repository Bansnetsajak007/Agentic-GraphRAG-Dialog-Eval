"""OpenAI-compatible, Gemini, and NVIDIA chat clients for answer generation."""

from __future__ import annotations

from dataclasses import dataclass
import random
import time
from typing import Any

import httpx


GENERATION_SKIPPED_MESSAGE = "LLM generation skipped because no supported provider API key is set."


@dataclass(frozen=True)
class ChatConfig:
    provider: str
    model: str
    api_key: str | None
    base_url: str
    api_keys: tuple[str, ...] = ()
    temperature: float = 0.0
    timeout_seconds: float = 60.0
    max_retries: int = 12


class ProviderChat:
    """Small HTTP wrapper for OpenAI-compatible, Gemini, and NVIDIA chat generation."""

    def __init__(self, config: ChatConfig):
        self.provider = config.provider.lower()
        self.model = config.model
        primary_key = () if config.api_key is None else (config.api_key,)
        self.api_keys = self._dedupe_keys(primary_key + config.api_keys)
        self.api_key = self.api_keys[0] if self.api_keys else None
        self.key_index = 0
        self.disabled_key_indices: set[int] = set()
        self.base_url = config.base_url.rstrip("/")
        self.temperature = config.temperature
        self.timeout_seconds = config.timeout_seconds
        self.max_retries = config.max_retries

    @property
    def generation_enabled(self) -> bool:
        return bool(self.api_keys)

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        if not self.api_key:
            return GENERATION_SKIPPED_MESSAGE
        if self.provider == "gemini":
            return self._complete_gemini(system_prompt, user_prompt)
        if self.provider == "openai":
            return self._complete_openai(system_prompt, user_prompt)
        if self.provider == "nvidia":
            return self._complete_nvidia(system_prompt, user_prompt)
        raise ValueError(f"Unsupported LLM_PROVIDER '{self.provider}'. Use 'openai', 'gemini', or 'nvidia'.")

    def _complete_openai(self, system_prompt: str, user_prompt: str) -> str:
        payload = {
            "model": self.model,
            "temperature": self.temperature,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        response = self._post_json_with_retries(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        data = response.json()
        return str(data["choices"][0]["message"].get("content") or "")

    def _complete_nvidia(self, system_prompt: str, user_prompt: str) -> str:
        payload = {
            "model": self.model,
            "temperature": self.temperature,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        response = self._post_json_with_retries(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        data = response.json()
        return str(data["choices"][0]["message"].get("content") or "")

    def _complete_gemini(self, system_prompt: str, user_prompt: str) -> str:
        payload: dict[str, Any] = {
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": user_prompt}],
                }
            ],
            "generationConfig": {"temperature": self.temperature},
        }
        response = self._post_json_with_retries(
            f"{self.base_url}/models/{self.model}:generateContent",
            headers={
                "x-goog-api-key": "{api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            rotate_keys=True,
            randomize_key=True,
        )
        data = response.json()
        parts = data["candidates"][0]["content"].get("parts", [])
        return "".join(str(part.get("text", "")) for part in parts).strip()

    def _post_json_with_retries(
        self,
        url: str,
        headers: dict[str, str],
        json: dict[str, Any],
        rotate_keys: bool = False,
        randomize_key: bool = False,
    ) -> httpx.Response:
        retryable_statuses = {429, 500, 502, 503, 504}
        last_error: Exception | None = None

        if randomize_key:
            self._select_random_key()

        for attempt in range(self.max_retries + 1):
            try:
                request_headers = self._headers_for_current_key(headers)
                response = httpx.post(
                    url,
                    headers=request_headers,
                    json=json,
                    timeout=self.timeout_seconds,
                )
                if response.status_code not in retryable_statuses:
                    response.raise_for_status()
                    return response
                response.raise_for_status()
            except (httpx.HTTPStatusError, httpx.TimeoutException, httpx.TransportError) as exc:
                last_error = exc
                if attempt >= self.max_retries:
                    raise
                if rotate_keys and self._should_disable_key(exc):
                    self.disabled_key_indices.add(self.key_index)
                rotated = rotate_keys and self._should_rotate_key(exc) and self._select_different_key()
                sleep_seconds = self._sleep_after_retry(exc, attempt, rotated)
                time.sleep(sleep_seconds)

        if last_error:
            raise last_error
        raise RuntimeError("Provider request failed without a response.")

    def _headers_for_current_key(self, headers: dict[str, str]) -> dict[str, str]:
        current_key = self.api_key or ""
        return {key: value.replace("{api_key}", current_key) for key, value in headers.items()}

    def _rotate_key(self) -> bool:
        if len(self.api_keys) <= 1:
            return False
        self.key_index = (self.key_index + 1) % len(self.api_keys)
        self.api_key = self.api_keys[self.key_index]
        return True

    def _select_random_key(self) -> bool:
        active_indices = self._active_key_indices()
        if len(active_indices) <= 1:
            return False
        self.key_index = random.choice(active_indices)
        self.api_key = self.api_keys[self.key_index]
        return True

    def _select_different_key(self) -> bool:
        active_indices = self._active_key_indices()
        if len(active_indices) <= 1:
            return False
        current_index = self.key_index
        choices = [index for index in active_indices if index != current_index]
        if not choices:
            return False
        self.key_index = random.choice(choices)
        self.api_key = self.api_keys[self.key_index]
        return True

    def _active_key_indices(self) -> list[int]:
        return [index for index in range(len(self.api_keys)) if index not in self.disabled_key_indices]

    @staticmethod
    def _should_rotate_key(exc: Exception) -> bool:
        return isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code in {403, 429, 503}

    @staticmethod
    def _should_disable_key(exc: Exception) -> bool:
        return isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code == 403

    @staticmethod
    def _dedupe_keys(keys: tuple[str, ...]) -> tuple[str, ...]:
        deduped: list[str] = []
        seen: set[str] = set()
        for key in keys:
            clean_key = key.strip()
            if clean_key and clean_key not in seen:
                deduped.append(clean_key)
                seen.add(clean_key)
        return tuple(deduped)

    @staticmethod
    def _retry_sleep_seconds(exc: Exception, attempt: int) -> float:
        if isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code == 429:
            retry_after = exc.response.headers.get("retry-after")
            if retry_after:
                try:
                    return min(float(retry_after), 90.0)
                except ValueError:
                    pass
            return 60.0
        return float(min(2**attempt, 8))

    def _sleep_after_retry(self, exc: Exception, attempt: int, rotated: bool) -> float:
        if isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code == 429:
            return self._retry_sleep_seconds(exc, attempt)
        if not rotated:
            return self._retry_sleep_seconds(exc, attempt)
        return 0.1
