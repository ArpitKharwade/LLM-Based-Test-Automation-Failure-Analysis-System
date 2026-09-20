from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field, field_validator


class Settings(BaseModel):
    """Application settings loaded from environment variables and .env."""

    model_config = ConfigDict(extra="ignore")

    OPENAI_API_KEY: str = Field(default="")
    GOOGLE_API_KEY: str = Field(default="")
    LLM_PROVIDER: str = Field(default="openai")
    MODEL_NAME: str = Field(default="gpt-4o-mini")

    @field_validator("LLM_PROVIDER")
    @classmethod
    def validate_provider(cls, value: str) -> str:
        normalized = (value or "").strip().lower()
        if normalized not in {"openai", "gemini"}:
            raise ValueError("LLM_PROVIDER must be either 'openai' or 'gemini'.")
        return normalized


def load_settings(env_file: str | Path = ".env") -> Settings:
    """Load configuration from the environment and .env file."""

    env_path = Path(env_file)
    if env_path.exists():
        load_dotenv(env_path, override=False)

    provider = (os.getenv("LLM_PROVIDER", "openai") or "openai").strip().lower()
    model_name = os.getenv("MODEL_NAME", "gpt-4o-mini") or "gpt-4o-mini"
    settings = Settings(
        OPENAI_API_KEY=os.getenv("OPENAI_API_KEY", "") or "",
        GOOGLE_API_KEY=os.getenv("GOOGLE_API_KEY", "") or "",
        LLM_PROVIDER=provider,
        MODEL_NAME=model_name,
    )

    if settings.LLM_PROVIDER == "openai" and not settings.OPENAI_API_KEY:
        raise ValueError(
            "OPENAI_API_KEY is missing. Add it to your .env file or set it in the environment."
        )

    if settings.LLM_PROVIDER == "gemini" and not settings.GOOGLE_API_KEY:
        raise ValueError(
            "GOOGLE_API_KEY is missing. Add it to your .env file or set it in the environment."
        )

    return settings
