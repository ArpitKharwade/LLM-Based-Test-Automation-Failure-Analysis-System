from types import SimpleNamespace

from core.llm_client import LLMClient


def test_llm_client_extracts_text_from_structured_content(monkeypatch):
    class FakeModel:
        def invoke(self, prompt):
            return SimpleNamespace(content=[{"type": "text", "text": "Hello from Gemini."}])

    client = LLMClient.__new__(LLMClient)
    client.provider = "gemini"
    client.model_name = "gemini-3.8-flash"
    client.api_key = "test-key"
    client.model = FakeModel()

    assert client.generate("Say hello") == "Hello from Gemini."
