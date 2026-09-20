from pathlib import Path
import os

import pytest

from config.settings import Settings, load_settings


def test_settings_validates_provider(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("GOOGLE_API_KEY", "")
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("MODEL_NAME", "gpt-4o-mini")

    settings = load_settings()

    assert settings.LLM_PROVIDER == "openai"
    assert settings.OPENAI_API_KEY == "test-key"


def test_missing_openai_key_raises(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "")
    monkeypatch.setenv("GOOGLE_API_KEY", "")
    monkeypatch.setenv("LLM_PROVIDER", "openai")

    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        load_settings()


def test_invalid_provider_raises(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("GOOGLE_API_KEY", "")
    monkeypatch.setenv("LLM_PROVIDER", "other")

    with pytest.raises(ValueError, match="LLM_PROVIDER"):
        load_settings()
