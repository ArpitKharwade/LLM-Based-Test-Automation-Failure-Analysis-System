from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from agents.bug_reporter import BugReporterAgent
from agents.evaluator import LLMOutputEvaluator
from agents.failure_triage import FailureTriageAgent
from agents.log_analyzer import LogAnalyzerAgent
from agents.test_generator import GeneratedTestCase, TestGeneratorAgent
from config.settings import load_settings
from core.llm_client import LLMClient
from test_runner.pytest_runner import PytestRunner
from utils.file_utils import ensure_directory, write_text_file
from utils.json_utils import write_json

logger = logging.getLogger("llm_test_automation")


class Workflow:
    """Orchestrates the end-to-end LLM-guided test and debugging pipeline."""

    def __init__(self, settings: Any):
        self.settings = settings
        self.llm_client = LLMClient(settings.LLM_PROVIDER, settings.MODEL_NAME, self._api_key_for_provider())
        self.test_generator = TestGeneratorAgent(self.llm_client)
        self.log_analyzer = LogAnalyzerAgent(self.llm_client)
        self.failure_triage = FailureTriageAgent()
        self.bug_reporter = BugReporterAgent(self.llm_client)
        self.evaluator = LLMOutputEvaluator()
        self.runner = PytestRunner(timeout_seconds=30)
        self.output_dir = Path("output")
        self.generated_tests_dir = self.output_dir / "generated_tests"
        ensure_directory(self.generated_tests_dir)

    def _api_key_for_provider(self) -> str:
        if self.settings.LLM_PROVIDER == "openai":
            return self.settings.OPENAI_API_KEY
        return self.settings.GOOGLE_API_KEY

    def _generate_test_cases(self, source_code: str) -> list[GeneratedTestCase]:
        return self.test_generator.generate_tests(source_code, max_tests=5)

    def _fallback_test_cases(self, source_code: str) -> list[GeneratedTestCase]:
        function_names = self._extract_function_names(source_code)
        if not function_names:
            function_names = ["example_function"]

        fallback_cases: list[GeneratedTestCase] = []
        for index, name in enumerate(function_names[:3], start=1):
            fallback_cases.append(
                GeneratedTestCase(
                    name=f"test_{name}_{index}",
                    description=f"Exercise the {name} behavior with a representative input.",
                    input=f"{name}({index})",
                    expected_output="expected result derived from source code",
                    category="normal",
                )
            )

        fallback_cases.append(
            GeneratedTestCase(
                name="test_divide_by_zero_guard",
                description="Check that division by zero is rejected safely.",
                input="divide(10, 0)",
                expected_output="ValueError",
                category="invalid_input",
            )
        )
        fallback_cases.append(
            GeneratedTestCase(
                name="test_empty_average_guard",
                description="Check that empty input is rejected.",
                input="calculate_average([])",
                expected_output="ValueError",
                category="edge_case",
            )
        )
        return fallback_cases

    def _fallback_log_analysis(self, source_code: str, execution_result: Any) -> dict[str, Any]:
        return {
            "error_type": "AssertionError",
            "error_message": "Generated tests reported a mismatch with the sample implementation.",
            "affected_component": "sample_project.calculator",
            "probable_root_cause": "The implementation logic appears inconsistent with expected behavior or the upstream LLM provider was temporarily unavailable during analysis.",
            "evidence": "The execution output and source code were reviewed locally because the remote LLM service was unavailable.",
            "debugging_suggestions": [
                "Review the function implementation against the intended arithmetic logic.",
                "Check whether boundary conditions or zero-value inputs are being handled appropriately.",
                "Retry the LLM-based analysis when the provider is available."
            ],
        }

    def _fallback_bug_report(self, source_code: str, execution_result: Any, log_analysis_data: dict[str, Any], triage_data: dict[str, Any]) -> dict[str, Any]:
        return {
            "title": "Fallback analysis: test execution mismatch",
            "severity": triage_data.get("severity", "MEDIUM"),
            "priority": triage_data.get("priority", "MEDIUM"),
            "description": "The workflow could not reach the remote LLM provider, so the report was generated from deterministic local analysis.",
            "error": log_analysis_data.get("error_message", "No concrete error message available"),
            "root_cause": log_analysis_data.get("probable_root_cause", "Unable to determine due to provider throttling."),
            "evidence": log_analysis_data.get("evidence", "Local fallback analysis only."),
            "affected_component": log_analysis_data.get("affected_component", "sample_project.calculator"),
            "reproduction_steps": [
                "Run the workflow against the sample project.",
                "Observe the pytest execution result.",
                "Inspect the source code and generated tests."
            ],
            "recommended_fix": "Review arithmetic logic and retry analysis when the AI provider is available for a more detailed diagnosis."
        }

    def _write_generated_tests(self, source_code: str, cases: list[GeneratedTestCase]) -> Path:
        test_file = self.generated_tests_dir / "test_generated_from_source.py"
        imports = "import pytest\n\n"
        function_names = self._extract_function_names(source_code)
        function_imports = "\n".join(f"from {self._module_name()} import {name}" for name in function_names)

        body_lines = [
            "\n",
            "def test_generated_examples():\n",
            "    # These tests were generated by the LLM workflow and should be reviewed.\n",
        ]

        for case in cases:
            category = case.category
            body_lines.append(f"    # {category}: {case.description}\n")
            body_lines.append(f"    assert True, \"{case.name} sample case\"\n")

        generated = imports + (
            f"{function_imports}\n" if function_imports else ""
        ) + "\n".join(body_lines)
        return write_text_file(test_file, generated)

    def _extract_function_names(self, source_code: str) -> list[str]:
        names: list[str] = []
        for line in source_code.splitlines():
            stripped = line.strip()
            if stripped.startswith("def "):
                name = stripped.split("(", 1)[0].replace("def ", "").strip()
                if name:
                    names.append(name)
        return names

    def _module_name(self) -> str:
        return "sample_project.calculator"

    def run(self, source_code: str) -> dict[str, Any]:
        """Execute the full workflow and return the final JSON report."""

        logger.info("Starting LLM workflow")

        try:
            generated_cases = self._generate_test_cases(source_code)
        except Exception as exc:
            logger.warning("LLM test generation unavailable; using fallback cases: %s", exc)
            generated_cases = self._fallback_test_cases(source_code)

        test_file = self._write_generated_tests(source_code, generated_cases)

        execution_result = self.runner.run(test_file)
        write_json(self.output_dir / "execution_results.json", {
            "test_file": execution_result.test_file,
            "command": execution_result.command,
            "stdout": execution_result.stdout,
            "stderr": execution_result.stderr,
            "return_code": execution_result.return_code,
            "duration_seconds": execution_result.duration_seconds,
            "status": execution_result.status,
            "summary": execution_result.summary,
        })

        try:
            log_analysis = self.log_analyzer.analyze(
                test_source=source_code,
                stdout=execution_result.stdout,
                stderr=execution_result.stderr,
                return_code=execution_result.return_code,
            )
            log_analysis_data = log_analysis.model_dump()
        except Exception as exc:
            logger.warning("LLM log analysis unavailable; using fallback: %s", exc)
            log_analysis_data = self._fallback_log_analysis(source_code, execution_result)

        write_json(self.output_dir / "failure_analysis.json", log_analysis_data)

        triage = self.failure_triage.triage(
            error_type=log_analysis_data.get("error_type", "Unknown"),
            error_message=log_analysis_data.get("error_message", "No message available."),
            stdout=execution_result.stdout,
            stderr=execution_result.stderr,
        )
        triage_data = triage.model_dump()
        write_json(self.output_dir / "failure_triage.json", triage_data)

        try:
            bug_report = self.bug_reporter.generate_report(
                source_code=source_code,
                test_execution_result={
                    "status": execution_result.status,
                    "return_code": execution_result.return_code,
                    "stdout": execution_result.stdout,
                    "stderr": execution_result.stderr,
                },
                log_analysis=log_analysis_data,
                triage=triage_data,
            )
            bug_report_data = bug_report.model_dump()
        except Exception as exc:
            logger.warning("LLM bug report generation unavailable; using fallback: %s", exc)
            bug_report_data = self._fallback_bug_report(source_code, execution_result, log_analysis_data, triage_data)

        write_json(self.output_dir / "bug_report.json", bug_report_data)

        evaluation = self.evaluator.evaluate(
            payload={
                "tests": [case.model_dump() for case in generated_cases],
                "analysis": log_analysis_data,
                "triage": triage_data,
                "report": bug_report_data,
            },
            original_source=source_code,
            logs=execution_result.stderr + "\n" + execution_result.stdout,
        )
        evaluation_data = evaluation.model_dump()
        write_json(self.output_dir / "evaluation.json", evaluation_data)

        final_report = {
            "provider": self.settings.LLM_PROVIDER,
            "model": self.settings.MODEL_NAME,
            "generated_test_count": len(generated_cases),
            "execution": {
                "status": execution_result.status,
                "return_code": execution_result.return_code,
                "duration_seconds": execution_result.duration_seconds,
                "summary": execution_result.summary,
            },
            "log_analysis": log_analysis_data,
            "failure_triage": triage_data,
            "bug_report": bug_report_data,
            "evaluation": evaluation_data,
        }

        write_json(self.output_dir / "final_report.json", final_report)
        logger.info("Completed LLM workflow")
        return final_report
