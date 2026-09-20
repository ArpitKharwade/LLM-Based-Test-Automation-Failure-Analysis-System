from __future__ import annotations

import sys
from pathlib import Path

from config.settings import load_settings
from core.workflow import Workflow
from utils.logger import configure_logger


def main() -> int:
    """Run the complete LLM-based test automation workflow."""

    logger = configure_logger("logs", "workflow.log")
    print("==================================================")
    print("LLM TEST AUTOMATION SYSTEM")
    print("==================================================")

    try:
        settings = load_settings(Path(".env"))
    except ValueError as exc:
        logger.error("Configuration error: %s", exc)
        print(f"Configuration error: {exc}")
        print("Create a .env file from .env.example and add your API key.")
        return 1

    provider = settings.LLM_PROVIDER.upper()
    print(f"Provider: {provider}")
    logger.info("Application configuration loaded for provider=%s", settings.LLM_PROVIDER)

    workflow = Workflow(settings)

    source_path = Path("sample_project/calculator.py")
    if not source_path.exists():
        logger.error("Sample source file not found: %s", source_path)
        print(f"Sample source file not found: {source_path}")
        return 1

    source_code = source_path.read_text(encoding="utf-8")

    steps = [
        "Generating test cases...",
        "Creating executable tests...",
        "Running tests...",
        "Analyzing logs...",
        "Triaging failure...",
        "Generating bug report...",
        "Evaluating output...",
    ]

    for index, step in enumerate(steps, start=1):
        print(f"[{index}/{len(steps)}] {step}")
        logger.info("Workflow step %s/%s: %s", index, len(steps), step)

    final_report = workflow.run(source_code)

    execution = final_report.get("execution", {})
    triage = final_report.get("failure_triage", {})
    bug_report = final_report.get("bug_report", {})

    print("==================================================")
    print("WORKFLOW COMPLETE")
    print("==================================================")
    print(f"Tests generated: {final_report.get('generated_test_count', 0)}")
    print(f"Tests passed: {execution.get('summary', {}).get('passed', 0)}")
    print(f"Tests failed: {execution.get('summary', {}).get('failed', 0)}")
    print(f"Severity: {triage.get('severity', 'UNKNOWN')}")
    print(f"Category: {triage.get('category', 'Unknown')}")
    print("Bug report:")
    print(bug_report.get("title", "No bug report available"))
    print("Final report:")
    print("output/final_report.json")
    logger.info("Workflow finished successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
