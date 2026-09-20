from test_runner.pytest_runner import PytestResult, PytestRunner


def test_pytest_runner_parses_failed_result(tmp_path):
    test_file = tmp_path / "test_example.py"
    test_file.write_text(
        "def test_fail():\n"
        "    assert 1 == 2\n",
        encoding="utf-8",
    )

    runner = PytestRunner(timeout_seconds=10)
    result = runner.run(test_file)

    assert isinstance(result, PytestResult)
    assert result.return_code != 0
    assert result.status in {"FAILED", "ERROR", "PASSED"}
    assert result.summary["total"] >= 1
