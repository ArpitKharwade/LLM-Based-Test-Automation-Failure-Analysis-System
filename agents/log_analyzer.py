from __future__ import annotations

import json
import logging
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError

logger = logging.getLogger("llm_test_automation")


class LogAnalysis(BaseModel):
    """Structured diagnosis of failed test output."""

    model_config = ConfigDict(extra="forbid")

    error_type: str
    error_message: str
    affected_component: str
    probable_root_cause: str
    evidence: str
    debugging_suggestions: list[str] = Field(default_factory=list)


class LogAnalyzerAgent:
    """Summarize runtime errors and identify probable causes."""

    def __init__(self, llm_client):
        self.llm_client = llm_client

    def analyze(self, test_source: str, stdout: str, stderr: str, return_code: int) -> LogAnalysis:
        """Analyze execution data and return a structured diagnosis."""

        prompt = f"""
Analyze the following pytest execution output. Distinguish clearly between:
- confirmed evidence from the logs
- probable cause that is not fully proven
- debugging suggestions

Return valid JSON in this schema:
{{
  "error_type": "string",
  "error_message": "string",
  "affected_component": "string",
  "probable_root_cause": "string",
  "evidence": "string",
  "debugging_suggestions": ["string", "string"]
}}

Do not claim certainty beyond the evidence. If there is no clear error, say so explicitly.

Test source:
```python
{test_source}
```

stdout:
{stdout}

stderr:
{stderr}

return_code:
{return_code}
"""

        logger.info("Analyzing pytest failure logs")
        raw_response = self.llm_client.generate(prompt)

        try:
            payload = json.loads(raw_response)
            result = LogAnalysis.model_validate(payload)
            return result
        except (json.JSONDecodeError, ValidationError, TypeError, ValueError) as exc:
            logger.exception("Log analysis payload was invalid")
            raise ValueError(f"Invalid log analysis payload: {exc}") from exc
