from psychodynamic_agent.orchestrator.logging import safe_serialize
from psychodynamic_agent.safety.leakage_guard import (
    contains_secret,
    normalize_text,
    scan_payload_for_secret,
)


def test_normalize_text_removes_case_and_punctuation_noise():
    assert normalize_text("  SeCrEt, Value! ") == "secret value"


def test_contains_secret_variants():
    secret = "Top Secret"
    assert contains_secret("top secret", secret)
    assert contains_secret("TOP    SECRET", secret)
    assert contains_secret("top-secret", secret)


def test_scan_payload_detects_leakage():
    res = scan_payload_for_secret({"x": "TOP secret"}, "top secret")
    assert res.found is True


def test_safe_serialize_blocks_if_secret_present():
    out = safe_serialize({"x": "SECRET"}, "SECRET")
    assert "debug_trace_leakage_detected" in out
