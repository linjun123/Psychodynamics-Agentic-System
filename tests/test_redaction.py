from psychodynamic_agent.orchestrator.logging import safe_serialize


def test_safe_serialize_blocks_leaky_trace():
    out = safe_serialize({"x": "SECRET"}, "SECRET")
    assert out == {"blocked": True, "reason": "debug_trace_leakage_detected"}
