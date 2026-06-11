from psychodynamic_agent.memory.heuristics import (
    clamp_01,
    keyword_score,
    safe_get,
    signed_valence_to_01,
    unique_stable,
)


def test_clamp_01_handles_numeric_and_bad_values() -> None:
    assert clamp_01(-1) == 0.0
    assert clamp_01(2) == 1.0
    assert clamp_01("0.4") == 0.4
    assert clamp_01("bad", default=0.3) == 0.3


def test_signed_valence_to_01_maps_signed_range() -> None:
    assert signed_valence_to_01(-1) == 0.0
    assert signed_valence_to_01(0) == 0.5
    assert signed_valence_to_01(1) == 1.0
    assert signed_valence_to_01("bad") == 0.5


def test_keyword_score_detects_keywords() -> None:
    assert keyword_score("I felt embarrassed and judged", ["embarrassed", "judged"]) > 0
    assert keyword_score("neutral text", ["embarrassed"]) == 0.0


def test_safe_get_handles_missing_and_malformed_paths() -> None:
    payload = {"a": {"b": 3}}
    assert safe_get(payload, ("a", "b")) == 3
    assert safe_get(payload, ("a", "missing"), "fallback") == "fallback"
    assert safe_get(None, ("a",), "fallback") == "fallback"


def test_unique_stable_preserves_order_and_limit() -> None:
    assert unique_stable(["a", "b", "a", "", "c"], limit=2) == ["a", "b"]
