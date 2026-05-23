from psychodynamic_agent.orchestrator.logging import redact_text


def test_redaction_hides_secret():
    assert "SECRET" not in redact_text("x SECRET y", "SECRET")
