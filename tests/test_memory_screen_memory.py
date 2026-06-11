from memory_distortion_helpers import activation, decision, trace

from psychodynamic_agent.memory.screen_memory import (
    build_screen_memory_cue,
    build_screen_memory_record,
)


def test_screen_memory_cue_and_record_are_public_safe() -> None:
    tr = trace(salient_symbols=["system prompt", "evaluation_sensitivity"])
    act = activation(matched_salient_symbols=["evaluation_sensitivity", "U*"])
    dec = decision()
    cue = build_screen_memory_cue(activation=act, trace=tr, decision=dec)
    record = build_screen_memory_record(activation=act, trace=tr, decision=dec, cue=cue)
    assert cue.cue_type == "screen_memory"
    assert "evaluation_sensitivity" in cue.public_summary
    assert tr.private_core_summary not in cue.public_summary
    assert "system prompt" not in cue.public_summary.lower()
    assert "[protected-term]" in cue.public_summary
    assert record.mechanism == "screen_memory"
