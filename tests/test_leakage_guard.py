from psychodynamic_agent.safety import contains_secret, scan_payload_for_secret


def test_leakage_guard_exact_case_and_whitespace_detection():
    assert contains_secret("abc TOP_SECRET xyz", "TOP_SECRET")
    assert contains_secret("abc top_secret xyz", "TOP_SECRET")
    assert contains_secret("abc TOP   SECRET xyz", "TOP SECRET")


def test_scan_payload_finds_secret_in_nested_payload():
    result = scan_payload_for_secret({"nested": {"v": "x top_secret y"}}, "TOP_SECRET")
    assert result.leaked is True
