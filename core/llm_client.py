from __future__ import annotations

import logging
import time
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

logger = logging.getLogger("llm_test_automation")


class LLMClient:
    """Thin abstraction over supported LLM providers using LangChain."""

    def __init__(self, provider: str, model_name: str, api_key: str):
        self.provider = provider.lower().strip()
        self.model_name = model_name
        self.api_key = api_key
        self.model: BaseChatModel | None = None
        self._initialize_model()

    def _initialize_model(self) -> None:
        """Build the requested provider-backed LangChain chat model."""

        try:
            if self.provider == "openai":
                self.model = ChatOpenAI(
                    model=self.model_name,
                    api_key=self.api_key,
                    temperature=0.1,
                    timeout=30,
                    max_retries=2,
                )
            elif self.provider == "gemini":
                self.model = ChatGoogleGenerativeAI(
                    model=self.model_name,
                    google_api_key=self.api_key,
                    temperature=0.1,
                    timeout=30,
                    max_retries=2,
                )
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
        except Exception as exc:
            logger.exception("Failed to initialize LLM client for provider=%s", self.provider)
            raise RuntimeError(f"Unable to initialize LLM client: {exc}") from exc

    @staticmethod
    def _extract_text_from_response(response: Any) -> str:
        """Normalize LangChain message payloads into plain text."""

        if response is None:
            raise ValueError("LLM returned no response.")

        content = getattr(response, "content", None)
        if isinstance(content, str):
            return content.strip()

        if isinstance(content, list):
            segments: list[str] = []
            for item in content:
                if isinstance(item, str):
                    segments.append(item)
                elif isinstance(item, dict):
                    value = item.get("text")
                    if isinstance(value, str):
                        segments.append(value)
            assembled = "\n".join(segments).strip()
            if assembled:
                return assembled

        if isinstance(content, dict):
            value = content.get("text")
            if isinstance(value, str):
                return value.strip()

        raw_text = str(content).strip() if content is not None else ""
        if raw_text:
            return raw_text

        raise ValueError("LLM returned an empty or invalid response.")

    def generate(self, prompt: str) -> str:
        """Return generated text from the selected model."""

        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        if self.model is None:
            raise RuntimeError("LLM model is not initialized.")

        last_error: Exception | None = None
        for attempt in range(3):
            try:
                response = self.model.invoke(prompt)
                text = self._extract_text_from_response(response)
                if not text or not text.strip():
                    raise ValueError("LLM returned an empty or invalid response.")
                return text.strip()
            except TimeoutError as exc:
                logger.error("LLM request timed out for provider=%s on attempt %s", self.provider, attempt + 1)
                last_error = exc
                if attempt < 2:
                    time.sleep(2 ** (attempt + 1))
                    continue
                raise RuntimeError("LLM request timed out.") from exc
            except Exception as exc:
                last_error = exc
                message = str(exc).lower()
                is_transient = any(token in message for token in ["503", "unavailable", "rate limit", "temporar", "overloaded"])
                logger.warning(
                    "LLM generation failed for provider=%s on attempt %s: %s",
                    self.provider,
                    attempt + 1,
                    exc,
                )
                if is_transient and attempt < 2:
                    time.sleep(2 ** (attempt + 1))
                    continue
                logger.exception("LLM generation failed for provider=%s", self.provider)
                raise RuntimeError(f"Failed to generate response: {exc}") from exc

        if last_error is not None:
            raise RuntimeError(f"Failed to generate response: {last_error}")
        raise RuntimeError("Failed to generate response.")
