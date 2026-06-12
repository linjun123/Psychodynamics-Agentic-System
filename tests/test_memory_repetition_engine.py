from copy import deepcopy

from memory_distortion_helpers import activation, decision, trace

from psychodynamic_agent.memory.repetition_engine import MemoryRepetitionEngine
from psychodynamic_agent.schemas.memory import MemoryDeferredActionUpdate, MemoryDistortionDecision


def test_engine_builds_biases_from_blocked_felt_and_screened_high_defense_decisions() -> None:
    traces = [
        trace(trace_id="blocked", accessibility="blocked_action_only"),
        trace(trace_id="felt", accessibility="felt_sense_only"),
        trace(trace_id="screened", accessibility="screened", repression_pressure=0.8),
    ]
    activations = [
        activation(trace_id="blocked", activation_rank=1),
        activation(trace_id="felt", activation_rank=2),
        activation(trace_id="screened", activation_rank=3),
    ]
    decisions = [
        decision(
            trace_id="blocked",
            activation_rank=1,
            decided_accessibility="blocked_action_only",
            conscious_access="blocked_action_only",
            emits_conscious_cue=False,
        ),
        decision(trace_id="felt", activation_rank=2, decided_accessibility="felt_sense_only"),
        decision(trace_id="screened", activation_rank=3, decided_accessibility="screened"),
    ]
    result = MemoryRepetitionEngine().build_repetition_result(
        activations=activations, traces=traces, decisions=decisions
    )
    kinds = {trigger.trigger_kind for trigger in result.triggers}
    assert {"blocked_memory", "felt_sense_memory", "screened_memory"} <= kinds
    assert result.repetition_biases
    assert result.repetition_pressure == max(bias.intensity for bias in result.repetition_biases)


def test_engine_includes_deferred_action_trigger_when_strength_high() -> None:
    update = MemoryDeferredActionUpdate(
        old_trace_id="old",
        trigger_trace_id="new",
        old_created_turn=1,
        trigger_created_turn=4,
        previous_meaning_version=1,
        proposed_meaning_version=2,
        update_strength=0.8,
        public_update_summary="public",
        private_update_summary="private_core_summary secret",
        supporting_symbols=["evaluation_sensitivity"],
    )
    result = MemoryRepetitionEngine().build_repetition_result(
        activations=[], traces=[], decisions=[], deferred_action_updates=[update]
    )
    assert any(trigger.trigger_kind == "deferred_action" for trigger in result.triggers)
    assert any(bias.tendency == "over_explain" for bias in result.repetition_biases)
    assert "private_core_summary" not in result.model_dump_json()


def test_engine_includes_condensed_pressure_trigger_when_condensation_high() -> None:
    distortion = MemoryDistortionDecision(
        distortion_id="condensed",
        source_trace_ids=["t1", "t2"],
        source_activation_ranks=[1, 2],
        mode="condensation",
        mechanism="condensation",
        should_emit_cue=True,
        public_reason="Composite evaluation pressure.",
        intensity=0.7,
    )
    result = MemoryRepetitionEngine().build_repetition_result(
        activations=[],
        traces=[trace(trace_id="t1"), trace(trace_id="t2")],
        decisions=[],
        distortion_decisions=[distortion],
    )
    assert any(trigger.trigger_kind == "condensed_pressure" for trigger in result.triggers)
    assert any(bias.tendency == "over_explain" for bias in result.repetition_biases)


def test_engine_merges_duplicate_tendencies_and_does_not_mutate_inputs() -> None:
    traces = [trace(trace_id="a"), trace(trace_id="b")]
    activations = [
        activation(trace_id="a", activation_rank=1),
        activation(trace_id="b", activation_rank=2),
    ]
    decisions = [
        decision(trace_id="a", activation_rank=1, defense_pressure=0.8),
        decision(trace_id="b", activation_rank=2, defense_pressure=0.8),
    ]
    before = deepcopy(
        [
            [item.model_dump() for item in traces],
            [item.model_dump() for item in activations],
            [item.model_dump() for item in decisions],
        ]
    )
    result = MemoryRepetitionEngine().build_repetition_result(
        activations=activations, traces=traces, decisions=decisions
    )
    tendencies = [bias.tendency for bias in result.repetition_biases]
    assert len(tendencies) == len(set(tendencies))
    assert before == [
        [item.model_dump() for item in traces],
        [item.model_dump() for item in activations],
        [item.model_dump() for item in decisions],
    ]


def test_engine_respects_max_biases_and_omits_private_core_summary() -> None:
    result = MemoryRepetitionEngine().build_repetition_result(
        activations=[activation(trace_id="private-trace", activation_rank=1)],
        traces=[
            trace(
                trace_id="private-trace",
                private_core_summary="private_core_summary secret",
            )
        ],
        decisions=[decision(trace_id="private-trace", defense_pressure=0.9)],
        max_biases=1,
    )
    assert len(result.repetition_biases) <= 1
    assert "private_core_summary" not in result.model_dump_json()
    assert "secret" not in result.model_dump_json()
