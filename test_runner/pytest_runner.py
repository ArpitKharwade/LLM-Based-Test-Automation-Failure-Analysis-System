from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class PytestResult:
    """Outcome of a pytest run."""

    test_file: str
    command: list[str]
    stdout: str = ""
    stderr: str = ""
    return_code: int = 0
    duration_seconds: float = 0.0
    status: str = "UNKNOWN"
    summary: dict[str, int] = field(default_factory=lambda: {"passed": 0, "failed": 0, "errors": 0, "total": 0})


class PytestRunner:
    """Run generated tests via pytest in a subprocess."""

    def __init__(self, timeout_seconds: int = 30):
        self.timeout_seconds = timeout_seconds

    def run(self, test_file: str | Path) -> PytestResult:
        """Execute a pytest file and capture output."""

        file_path = Path(test_file)
        if not file_path.exists():
            raise FileNotFoundError(f"Test file not found: {file_path}")

        command = ["python", "-m", "pytest", str(file_path), "-q"]
        start = time.time()
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=self.timeout_seconds,
            check=False,
        )
        elapsed = time.time() - start

        stdout = completed.stdout or ""
        stderr = completed.stderr or ""
        return_code = completed.returncode

        if return_code == 0:
            status = "PASSED"
        elif "ERROR" in stdout.upper() or "ERROR" in stderr.upper():
            status = "ERROR"
        else:
            status = "FAILED"

        summary = {"passed": 0, "failed": 0, "errors": 0, "total": 0}
        if stdout:
            for line in stdout.splitlines():
                if " passed" in line.lower():
                    summary["passed"] += 1
                elif " failed" in line.lower():
                    summary["failed"] += 1
                elif " error" in line.lower():
                    summary["errors"] += 1

        summary["total"] = summary["passed"] + summary["failed"] + summary["errors"]

        return PytestResult(
            test_file=str(file_path),
            command=command,
            stdout=stdout,
            stderr=stderr,
            return_code=return_code,
            duration_seconds=elapsed,
            status=status,
            summary=summary,
        )
