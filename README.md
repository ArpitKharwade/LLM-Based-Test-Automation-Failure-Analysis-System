# LLM-Based Test Automation & Failure Analysis System

<<<<<<< HEAD
## Overview

This project is an AI-assisted software testing and debugging workflow built in Python. It analyzes a Python module, asks an LLM to generate relevant tests, executes them with pytest, captures failures, and then uses LLM-based reasoning to classify the issue, identify likely root causes, and produce a structured bug report.

This is a portfolio and academic project designed to demonstrate practical LLM orchestration and debugging workflows. It does not claim production-grade reliability or benchmark performance.

## Features

- LLM-based test generation
- Automated pytest execution
- Log analysis and failure diagnosis
- Failure triage and severity assignment
- Root-cause analysis with clear evidence labeling
- Structured bug report generation
- LLM output evaluation using lightweight heuristics
- Prompt-driven workflow orchestration with LangChain
- OpenAI and Google Gemini support
- Logging and JSON output for observability

## Architecture

```text
SOURCE CODE
    |
    v
TEST GENERATOR
    |
    v
GENERATED TEST CASES
    |
    v
TEST CODE GENERATOR
    |
    v
PYTEST RUNNER
    |
    v
EXECUTION LOGS
    |
    v
LOG ANALYZER
    |
    v
FAILURE TRIAGE
    |
    v
BUG REPORTER
    |
    v
LLM EVALUATOR
    |
    v
FINAL JSON REPORT
```

## Tech Stack

- Python 3.10+
- LangChain
- OpenAI API
- Google Gemini API
- Pytest
- Pydantic
- python-dotenv
- JSON and logging
- pathlib and subprocess

## Project Structure

- `config/` – environment configuration and validation
- `core/` – LLM client and workflow orchestration
- `agents/` – test generation, log analysis, triage, reporting, and evaluation
- `test_runner/` – pytest execution wrapper
- `utils/` – JSON writing, filesystem helpers, and logging
- `sample_project/` – example source code and tests used for demonstration
- `data/` – sample logs and supporting data
- `output/` – generated reports and execution results
- `logs/` – runtime workflow logs

## Installation

On Windows, create and activate a virtual environment:

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create a local environment file from the example:

```powershell
copy .env.example .env
```

Then add your API key values to `.env`.

## Configuration

Set the provider and model in `.env`:

```env
OPENAI_API_KEY=your_key_here
GOOGLE_API_KEY=
LLM_PROVIDER=openai
MODEL_NAME=gpt-4o-mini
```

For Gemini, use:

```env
OPENAI_API_KEY=
GOOGLE_API_KEY=your_key_here
LLM_PROVIDER=gemini
MODEL_NAME=gemini-1.5-flash
```

The application validates the selected provider and raises an explicit error if the matching key is missing.

## Running

```powershell
python main.py
```

## Example Workflow

1. Load configuration from `.env`.
2. Initialize the selected LLM provider.
3. Read the sample source code from `sample_project/calculator.py`.
4. Ask the LLM to generate structured tests.
5. Save generated tests in `output/generated_tests/`.
6. Run pytest with a timeout.
7. Capture stdout, stderr, return code, and timing.
8. Feed execution logs to the log analyzer.
9. Classify the failure with the triage module.
10. Generate a structured bug report.
11. Evaluate the output quality using simple heuristics.
12. Save the final report to `output/final_report.json`.

## Sample Output

Example output shape (illustrative only):

```json
{
  "generated_test_count": 5,
  "execution": {
    "status": "FAILED",
    "summary": {
      "passed": 4,
      "failed": 1,
      "errors": 0,
      "total": 5
    }
  },
  "failure_triage": {
    "category": "Assertion Failure",
    "severity": "MEDIUM",
    "priority": "MEDIUM"
  }
}
```

This is an example structure, not a measured benchmark.

## Limitations

- LLM outputs may contain incorrect or incomplete reasoning.
- Root-cause analysis is probabilistic and should be reviewed.
- Generated tests should be manually checked before production use.
- API access is required for real LLM execution.
- This is a portfolio and academic implementation, not an enterprise-ready system.

## Future Improvements

- CI/CD integration
- Web dashboard for reports
- Persistent test history
- Regression tracking across versions
- Human-in-the-loop validation
- Additional provider integrations

## Notes

- `.env` is intentionally excluded from Git.
- API keys are never printed in logs or terminal output.
- The project is designed to be readable and interview-friendly.
=======
An AI-powered test automation and failure analysis system built with Python and LLM APIs. The system automates test case generation, analyzes execution logs, performs failure triage, and generates structured bug reports to streamline debugging.

## Key Features

- Automated test case generation using LLMs
- Execution log analysis and error identification
- Automated failure triage and categorization
- Structured bug report generation
- Prompt engineering and LLM evaluation
- Logging and monitoring for workflow observability
- Support for OpenAI and Gemini APIs
- LangChain-based LLM workflow orchestration
>>>>>>> 8a426f75e209135befd4ab56980fc3fe3388a08b
