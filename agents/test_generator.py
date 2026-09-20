from __future__ import annotations

import json
import logging
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError

logger = logging.getLogger("llm_test_automation")


class GeneratedTestCase(BaseModel):
    """Single generated test case."""

    model_config = ConfigDict(extra="forbid")

    name: str
    description: str
    input: str
    expected_output: str
    category: str = Field(default="normal")


class GeneratedTestSuite(BaseModel):
    """Structured test generation response."""

    model_config = ConfigDict(extra="forbid")

    tests: list[GeneratedTestCase]


class TestGeneratorAgent:
    """Generate structured Python test cases from source code."""

    def __init__(self, llm_client):
        self.llm_client = llm_client

    def generate_tests(self, source_code: str, max_tests: int = 5) -> list[GeneratedTestCase]:
        """Ask the LLM for a list of test case objects derived from the source code."""

        prompt = f"""
You are generating tests for a Python module.
Use only the code provided below. Do not invent functions, classes, or behavior not present in the source.
Return valid JSON in the exact schema:
{{
  "tests": [
    {{
      "name": "string",
      "description": "string",
      "input": "string",
      "expected_output": "string",
      "category": "normal|edge_case|boundary|invalid_input"
    }}
  ]
}}

Rules:
- Generate between 3 and {max_tests} useful test cases.
- Include normal, edge, boundary, and invalid-input cases when relevant.
- Prefer realistic values and avoid destructive operations.
- Keep test cases grounded in the actual source code.
- Do not hallucinate missing functions or outputs.

Source code:
```python
{source_code}
```
"""

        logger.info("Generating structured test cases with LLM")
        raw_response = self.llm_client.generate(prompt)

        try:
            parsed = json.loads(raw_response)
            result = GeneratedTestSuite.model_validate(parsed)
            logger.info("Generated %s tests from source code", len(result.tests))
            return result.tests
        except (json.JSONDecodeError, ValidationError, TypeError, ValueError) as exc:
            logger.exception("Test generation response could not be validated")
            raise ValueError(f"Invalid test generation payload: {exc}") from exc
