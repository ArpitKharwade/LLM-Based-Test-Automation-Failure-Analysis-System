from __future__ import annotations

import logging
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, ValidationError

logger = logging.getLogger("llm_test_automation")


class FailureCategory(str, Enum):
    ASSERTION_FAILURE = "Assertion Failure"
    RUNTIME_ERROR = "Runtime Error"
    TYPE_ERROR = "Type Error"
    VALUE_ERROR = "Value Error"
    IMPORT_ERROR = "Import Error"
    CONFIGURATION_ERROR = "Configuration Error"
    TEST_GENERATION_ERROR = "Test Generation Error"
    UNKNOWN = "Unknown"


class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Priority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class FailureTriageResult(BaseModel):
    """A structured classification of a failure."""

    model_config = ConfigDict(extra="forbid")

    category: FailureCategory
    severity: Severity
    priority: Priority
    summary: str = Field(default="")


class FailureTriageAgent:
    """Classify failures into practical triage categories."""

    def __init__(self, llm_client=None):
        self.llm_client = llm_client

    def triage(self, error_type: str, error_message: str, stdout: str, stderr: str) -> FailureTriageResult:
        """Classify a failure sources using a deterministic mapping."""

        combined_text = f"{error_type} {error_message} {stdout} {stderr}".lower()

        if "assert" in combined_text:
            category = FailureCategory.ASSERTION_FAILURE
            severity = Severity.MEDIUM
            priority = Priority.MEDIUM
        elif "typeerror" in combined_text:
            category = FailureCategory.TYPE_ERROR
            severity = Severity.HIGH
            priority = Priority.HIGH
        elif "valueerror" in combined_text:
            category = FailureCategory.VALUE_ERROR
            severity = Severity.MEDIUM
            priority = Priority.MEDIUM
        elif "importerror" in combined_text or "modulenotfounderror" in combined_text:
            category = FailureCategory.IMPORT_ERROR
            severity = Severity.HIGH
            priority = Priority.HIGH
        elif "config" in combined_text or "environment" in combined_text or "key" in combined_text:
            category = FailureCategory.CONFIGURATION_ERROR
            severity = Severity.HIGH
            priority = Priority.HIGH
        elif "json" in combined_text or "validation" in combined_text or "schema" in combined_text:
            category = FailureCategory.TEST_GENERATION_ERROR
            severity = Severity.MEDIUM
            priority = Priority.MEDIUM
        elif "runtimeerror" in combined_text or "zerodivisionerror" in combined_text or "file" in combined_text:
            category = FailureCategory.RUNTIME_ERROR
            severity = Severity.HIGH
            priority = Priority.HIGH
        else:
            category = FailureCategory.UNKNOWN
            severity = Severity.LOW
            priority = Priority.LOW

        summary = (
            f"Failure classified as {category.value} with {severity.value} severity and {priority.value} priority."
        )

        try:
            result = FailureTriageResult(category=category, severity=severity, priority=priority, summary=summary)
            logger.info("Failure triaged as %s (%s)", category.value, severity.value)
            return result
        except ValidationError as exc:
            logger.exception("Failure triage result was invalid")
            raise ValueError(f"Failure triage validation failed: {exc}") from exc
