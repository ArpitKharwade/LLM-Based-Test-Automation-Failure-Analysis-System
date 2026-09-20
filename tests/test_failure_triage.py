from agents.failure_triage import FailureTriageAgent


def test_failure_triage_classifies_assertion_error():
    agent = FailureTriageAgent()
    result = agent.triage(
        error_type="AssertionError",
        error_message="assert 3.3333333333333335 == 2.5",
        stdout="",
        stderr="assert 3.3333333333333335 == 2.5",
    )

    assert result.category.value == "Assertion Failure"
    assert result.severity.value in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
    assert result.priority.value in {"LOW", "MEDIUM", "HIGH"}


def test_failure_triage_classifies_type_error():
    agent = FailureTriageAgent()
    result = agent.triage(
        error_type="TypeError",
        error_message="unsupported operand type(s) for +: 'int' and 'str'",
        stdout="",
        stderr="TypeError: unsupported operand type(s) for +: 'int' and 'str'",
    )

    assert result.category.value == "Type Error"
    assert result.priority.value == "HIGH"
