from memory_distortion_helpers import activation, decision, trace

from psychodynamic_agent.memory.condensation import (
    build_condensation_groups,
    build_condensation_record,
    build_condensed_memory_cue,
)


def test_condensation_groups_and_builds_safe_cue() -> None:
    traces = [trace(trace_id="a"), trace(trace_id="b", private_core_summary="PRIVATE hidden b")]
    activations = [
        activation(trace_id="a", activation_rank=1),
        activation(trace_id="b", activation_rank=2),
    ]
    decisions = [
        decision(trace_id="a", activation_rank=1),
        decision(trace_id="b", activation_rank=2),
    ]
    groups = build_condensation_groups(activations=activations, traces=traces, decisions=decisions)
    assert groups == [["a", "b"]]
    cue = build_condensed_memory_cue(
        group_trace_ids=groups[0], activations=activations, traces=traces, decisions=decisions
    )
    record = build_condensation_record(group_trace_ids=groups[0], traces=traces, cue=cue)
    assert cue.cue_type == "condensed_memory"
    assert set(cue.source_trace_ids) == {"a", "b"}
    assert "PRIVATE" not in cue.public_summary
    assert record.mechanism == "condensation"
