from __future__ import annotations

import json
import logging
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger("llm_test_automation")


class EvaluationResult(BaseModel):
    """Heuristic evaluation of AI-generated outputs.

    These scores are simple project-level checks rather than scientific benchmark metrics.
    """

    model_config = ConfigDict(extra="forbid")

    schema_valid: bool = Field(default=False)
    completeness: float = Field(default=0.0)
    consistency: float = Field(default=0.0)
    unsupported_claims: list[str] = Field(default_factory=list)
    issues: list[str] = Field(default_factory=list)


class LLMOutputEvaluator:
    """Perform lightweight checks on generated LLM output."""

    def evaluate(self, payload: Any, original_source: str, logs: str) -> EvaluationResult:
        """Apply heuristic checks for schema validity and groundedness."""

        issues: list[str] = []
        unsupported_claims: list[str] = []

        schema_valid = True
        try:
            if isinstance(payload, dict):
                json.dumps(payload)
            else:
                json.dumps(payload)
        except (TypeError, ValueError) as exc:
            schema_valid = False
            issues.append(f"JSON serialization failed: {exc}")

        completeness = 0.0
        consistency = 0.0

        if isinstance(payload, dict):
            if isinstance(payload.get("tests"), list) or isinstance(payload.get("error_type"), str):
                completeness = 1.0
            elif isinstance(payload.get("title"), str):
                completeness = 1.0
            else:
                completeness = 0.5

            if isinstance(original_source, str) and original_source.strip():
                if "function" in original_source.lower() or "return" in original_source.lower():
                    consistency = 0.8
                else:
                    consistency = 0.6
            else:
                consistency = 0.0

        if "api key" in logs.lower() or "secret" in logs.lower():
            unsupported_claims.append("Sensitive credential information should not be included in generated output.")

        if not isinstance(payload, dict):
            issues.append("Output was not a JSON-like dictionary.")
            schema_valid = False

        logger.info("LLM evaluation complete: schema_valid=%s, completeness=%s, consistency=%s", schema_valid, completeness, consistency)

        return EvaluationResult(
            schema_valid=schema_valid,
            completeness=completeness,
            consistency=consistency,
            unsupported_claims=unsupported_claims,
            issues=issues,
        )
