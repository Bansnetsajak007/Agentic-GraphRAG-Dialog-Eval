"""Gemini and NVIDIA chat clients for answer generation."""

from __future__ import annotations

from dataclasses import dataclass
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
    temperature: float = 0.0
    timeout_seconds: float = 60.0
    max_retries: int = 5


class ProviderChat:
    """Small HTTP wrapper for Gemini and NVIDIA chat generation."""

    def __init__(self, config: ChatConfig):
        self.provider = config.provider.lower()
        self.model = config.model
        self.api_key = config.api_key
        self.base_url = config.base_url.rstrip("/")
        self.temperature = config.temperature
        self.timeout_seconds = config.timeout_seconds
        self.max_retries = config.max_retries

    @property
    def generation_enabled(self) -> bool:
        return bool(self.api_key)

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        if not self.api_key:
            return GENERATION_SKIPPED_MESSAGE
        if self.provider == "gemini":
            return self._complete_gemini(system_prompt, user_prompt)
        if self.provider == "nvidia":
            return self._complete_nvidia(system_prompt, user_prompt)
        raise ValueError(f"Unsupported LLM_PROVIDER '{self.provider}'. Use 'gemini' or 'nvidia'.")

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
                "x-goog-api-key": self.api_key,
                "Content-Type": "application/json",
            },
            json=payload,
        )
        data = response.json()
        parts = data["candidates"][0]["content"].get("parts", [])
        return "".join(str(part.get("text", "")) for part in parts).strip()

    def _post_json_with_retries(
        self,
        url: str,
        headers: dict[str, str],
        json: dict[str, Any],
    ) -> httpx.Response:
        retryable_statuses = {429, 500, 502, 503, 504}
        last_error: Exception | None = None

        for attempt in range(self.max_retries + 1):
            try:
                response = httpx.post(
                    url,
                    headers=headers,
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
                sleep_seconds = self._retry_sleep_seconds(exc, attempt)
                time.sleep(sleep_seconds)

        if last_error:
            raise last_error
        raise RuntimeError("Provider request failed without a response.")

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
