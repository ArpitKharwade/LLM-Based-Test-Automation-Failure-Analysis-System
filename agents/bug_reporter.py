from __future__ import annotations

import json
import logging
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError

logger = logging.getLogger("llm_test_automation")


class BugReport(BaseModel):
    """Structured bug report generated after failure analysis."""

    model_config = ConfigDict(extra="forbid")

    title: str
    severity: str
    priority: str
    description: str
    error: str
    root_cause: str
    evidence: str
    affected_component: str
    reproduction_steps: list[str] = Field(default_factory=list)
    recommended_fix: str


class BugReporterAgent:
    """Assemble the final structured bug report."""

    def __init__(self, llm_client):
        self.llm_client = llm_client

    def generate_report(
        self,
        source_code: str,
        test_execution_result: dict[str, Any],
        log_analysis: dict[str, Any],
        triage: dict[str, Any],
    ) -> BugReport:
        """Create a human-readable bug report from the pipeline data."""

        prompt = f"""
Using the data below, create a concise but structured bug report. Distinguish between:
- evidence from logs and source code
- the likely root cause
- recommended remediation

Return valid JSON with this schema:
{{
  "title": "string",
  "severity": "string",
  "priority": "string",
  "description": "string",
  "error": "string",
  "root_cause": "string",
  "evidence": "string",
  "affected_component": "string",
  "reproduction_steps": ["string"],
  "recommended_fix": "string"
}}

Source code:
```python
{source_code}
```

Test execution result:
{json.dumps(test_execution_result, indent=2, sort_keys=True)}

Log analysis:
{json.dumps(log_analysis, indent=2, sort_keys=True)}

Failure triage:
{json.dumps(triage, indent=2, sort_keys=True)}
"""

        logger.info("Generating structured bug report")
        raw_response = self.llm_client.generate(prompt)

        try:
            payload = json.loads(raw_response)
            result = BugReport.model_validate(payload)
            return result
        except (json.JSONDecodeError, ValidationError, TypeError, ValueError) as exc:
            logger.exception("Bug report payload was invalid")
            raise ValueError(f"Invalid bug report payload: {exc}") from exc
