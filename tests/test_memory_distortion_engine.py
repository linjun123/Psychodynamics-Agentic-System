from copy import deepcopy

from memory_distortion_helpers import activation, decision, trace

from psychodynamic_agent.memory.distortion_engine import MemoryDistortionEngine


def test_engine_builds_all_distortion_artifacts_without_mutation() -> None:
    traces = [
        trace(trace_id="screen", object_targets=[]),
        trace(trace_id="disp", object_targets=["boss"], accessibility="direct"),
        trace(trace_id="c1", object_targets=["task"], accessibility="direct", defense_level=0.1),
        trace(trace_id="c2", object_targets=["task"], accessibility="direct", defense_level=0.1),
        trace(
            trace_id="latest",
            created_turn=5,
            object_targets=["task"],
            accessibility="direct",
            defense_level=0.1,
        ),
    ]
    activations = [
        activation(trace_id="screen", activation_rank=1),
        activation(trace_id="disp", activation_rank=2),
        activation(trace_id="c1", activation_rank=3),
        activation(trace_id="c2", activation_rank=4),
    ]
    decisions = [
        decision(trace_id="screen", activation_rank=1),
        decision(
            trace_id="disp",
            activation_rank=2,
            original_accessibility="direct",
            decided_accessibility="direct",
            conscious_access="direct",
            mechanism="direct",
            defense_pressure=0.8,
        ),
        decision(
            trace_id="c1",
            activation_rank=3,
            original_accessibility="direct",
            decided_accessibility="direct",
            conscious_access="direct",
            mechanism="direct",
            defense_pressure=0.2,
        ),
        decision(
            trace_id="c2",
            activation_rank=4,
            original_accessibility="direct",
            decided_accessibility="direct",
            conscious_access="direct",
            mechanism="direct",
            defense_pressure=0.2,
        ),
    ]
    before = deepcopy([item.model_dump() for item in traces])
    result = MemoryDistortionEngine().build_distortion_result(
        activations=activations, traces=traces, decisions=decisions, latest_trace=traces[-1]
    )
    modes = {item.mode for item in result.distortion_decisions}
    assert {"screen_memory", "displacement", "condensation", "deferred_action"} <= modes
    assert any(cue.cue_type == "screen_memory" for cue in result.distorted_cues)
    assert any(cue.cue_type == "displaced_memory" for cue in result.distorted_cues)
    assert any(cue.cue_type == "condensed_memory" for cue in result.distorted_cues)
    assert {"c1", "c2"} <= set(result.suppressed_trace_ids)
    assert result.deferred_action_updates
    assert before == [item.model_dump() for item in traces]
    for cue in result.distorted_cues:
        assert "PRIVATE" not in cue.public_summary


def test_engine_does_not_displace_blocked_action_only_trace() -> None:
    blocked_trace = trace(
        trace_id="blocked",
        object_targets=["boss"],
        accessibility="direct",
        defense_level=1.0,
        repression_pressure=1.0,
    )
    blocked_activation = activation(
        trace_id="blocked",
        activation_rank=1,
        association_score=0.95,
    )
    blocked_decision = decision(
        trace_id="blocked",
        activation_rank=1,
        original_accessibility="direct",
        decided_accessibility="blocked_action_only",
        conscious_access="blocked_action_only",
        mechanism="blocked_action_only",
        emits_conscious_cue=False,
        defense_pressure=1.0,
    )

    result = MemoryDistortionEngine().build_distortion_result(
        activations=[blocked_activation],
        traces=[blocked_trace],
        decisions=[blocked_decision],
    )

    assert not any(cue.cue_type == "displaced_memory" for cue in result.distorted_cues)
    assert not any(item.mode == "displacement" for item in result.distortion_decisions)
    assert not any(record.mechanism == "displacement" for record in result.transformation_chain)
