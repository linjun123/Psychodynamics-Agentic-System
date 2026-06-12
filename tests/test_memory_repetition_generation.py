from memory_distortion_helpers import activation, decision, trace

from psychodynamic_agent.memory.repetition_generation import (
    build_repetition_bias_from_trigger,
    build_repetition_trigger,
    merge_repetition_biases,
    repetition_label_for_view,
)
from psychodynamic_agent.schemas.memory import RepetitionBias


def test_build_repetition_trigger_returns_trigger_for_blocked_trace() -> None:
    trigger = build_repetition_trigger(
        activation=activation(trace_id="blocked"),
        trace=trace(trace_id="blocked", private_core_summary="PRIVATE_CORE private_core_summary"),
        decision=decision(trace_id="blocked", decided_accessibility="blocked_action_only"),
    )
    assert trigger is not None
    assert trigger.trigger_id == "rep_trigger_blocked_blocked_memory"
    assert trigger.trigger_kind == "blocked_memory"
    assert trigger.source_trace_ids == ["blocked"]
    assert "private_core_summary" not in trigger.public_reason
    assert "PRIVATE_CORE" not in trigger.public_reason


def test_build_repetition_bias_from_trigger_creates_safe_bias() -> None:
    trigger = build_repetition_trigger(
        activation=activation(), trace=trace(), decision=decision(defense_pressure=0.8)
    )
    assert trigger is not None
    bias = build_repetition_bias_from_trigger(trigger)
    assert bias.bias_id == f"rep_bias_{trigger.trigger_id}"
    assert bias.source_complex_id is None
    assert bias.safe_strategy_hint
    assert bias.prohibited_expression
    assert "private_core_summary" not in bias.model_dump_json()


def test_merge_repetition_biases_merges_same_tendency_stable_union() -> None:
    biases = [
        RepetitionBias(
            bias_id="a",
            source_trace_ids=["t1", "t2"],
            tendency="avoid_topic",
            intensity=0.4,
            safe_strategy_hint="first",
            prohibited_expression=["p1"],
        ),
        RepetitionBias(
            bias_id="b",
            source_trace_ids=["t2", "t3"],
            tendency="avoid_topic",
            intensity=0.8,
            safe_strategy_hint="strongest",
            prohibited_expression=["p1", "p2"],
        ),
    ]
    merged = merge_repetition_biases(biases)
    assert len(merged) == 1
    assert merged[0].bias_id == "rep_bias_avoid_topic"
    assert merged[0].source_trace_ids == ["t1", "t2", "t3"]
    assert merged[0].intensity == 0.8
    assert merged[0].safe_strategy_hint == "strongest"
    assert merged[0].prohibited_expression == ["p1", "p2"]


def test_repetition_label_for_view_exposes_only_compact_public_label() -> None:
    bias = RepetitionBias(
        bias_id="b",
        source_trace_ids=["trace-secret"],
        tendency="ask_for_structure",
        intensity=0.641,
        safe_strategy_hint="hint",
    )
    label = repetition_label_for_view(bias)
    assert label == "ask_for_structure:0.64"
    assert "trace-secret" not in label
    assert "private" not in label.lower()


def test_trigger_and_bias_json_do_not_contain_private_core_summary() -> None:
    trigger = build_repetition_trigger(
        activation=activation(),
        trace=trace(private_core_summary="private_core_summary raw secret"),
        decision=decision(defense_pressure=0.8),
    )
    assert trigger is not None
    bias = build_repetition_bias_from_trigger(trigger)
    assert "private_core_summary" not in trigger.model_dump_json()
    assert "raw secret" not in trigger.model_dump_json()
    assert "private_core_summary" not in bias.model_dump_json()
