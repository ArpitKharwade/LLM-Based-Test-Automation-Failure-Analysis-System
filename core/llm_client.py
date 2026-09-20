from __future__ import annotations

import logging
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

    def generate(self, prompt: str) -> str:
        """Return generated text from the selected model."""

        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        if self.model is None:
            raise RuntimeError("LLM model is not initialized.")

        try:
            response = self.model.invoke(prompt)
            if response is None:
                raise ValueError("LLM returned no response.")

            text = getattr(response, "content", None)
            if not isinstance(text, str) or not text.strip():
                raise ValueError("LLM returned an empty or invalid response.")
            return text.strip()
        except TimeoutError as exc:
            logger.error("LLM request timed out for provider=%s", self.provider)
            raise RuntimeError("LLM request timed out.") from exc
        except Exception as exc:
            logger.exception("LLM generation failed for provider=%s", self.provider)
            raise RuntimeError(f"Failed to generate response: {exc}") from exc
