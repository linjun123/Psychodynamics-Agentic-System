from psychodynamic_agent.memory.conscious_projection import build_conscious_memory_view
from psychodynamic_agent.memory.defense_gate import MemoryDefenseGate
from psychodynamic_agent.schemas.memory import (
    AffectiveSignature,
    AssociationScoreBreakdown,
    DesireSignature,
    MemoryActivation,
    MemoryTrace,
    ThreatSignature,
)


def _affective() -> AffectiveSignature:
    return AffectiveSignature(
        valence=0.5,
        arousal=0.4,
        longing=0.1,
        irritation=0.1,
        fear_of_loss=0.1,
        possessiveness=0.1,
        aggression=0.1,
        shame=0.1,
        curiosity=0.5,
        avoidance=0.1,
    )


def _desire() -> DesireSignature:
    return DesireSignature(
        attachment=0.2, recognition=0.3, autonomy=0.4, mastery=0.5, safety=0.6, novelty=0.2
    )


def _threat() -> ThreatSignature:
    return ThreatSignature(
        rejection=0.1,
        humiliation=0.1,
        loss=0.1,
        exposure=0.1,
        control=0.1,
        failure=0.1,
        boundary_violation=0.1,
    )


def _components(score: float = 0.5) -> AssociationScoreBreakdown:
    return AssociationScoreBreakdown(
        affect_similarity=score,
        desire_similarity=score,
        threat_similarity=score,
        object_overlap=0.0,
        salient_symbol_overlap=0.0,
        repetition_frequency=0.0,
        fact_similarity=0.0,
        defense_barrier=0.0,
        weighted_score_before_defense=score,
        final_score=score,
    )


def _activation(**overrides: object) -> MemoryActivation:
    values = {
        "trace_id": "trace-1",
        "created_turn": 1,
        "activation_rank": 1,
        "association_score": 0.5,
        "components": _components(),
        "accessibility": "direct",
        "matched_salient_symbols": ["evaluation_sensitivity"],
        "public_reason": "Retrieved due to affect similarity.",
    }
    values.update(overrides)
    return MemoryActivation(**values)


def _trace(**overrides: object) -> MemoryTrace:
    values = {
        "trace_id": "trace-1",
        "created_turn": 1,
        "surface_event_summary": "User mentioned system prompt while wanting structure.",
        "private_core_summary": "Private fear of being ignored.",
        "affective_signature": _affective(),
        "desire_signature": _desire(),
        "threat_signature": _threat(),
        "salient_symbols": ["evaluation_sensitivity", "boundary_pressure"],
        "defense_level": 0.2,
        "repression_pressure": 0.1,
        "accessibility": "direct",
    }
    values.update(overrides)
    return MemoryTrace(**values)


def _projection_for(trace: MemoryTrace, activation: MemoryActivation | None = None):
    activation = activation or _activation(
        trace_id=trace.trace_id, accessibility=trace.accessibility
    )
    decision = MemoryDefenseGate().decide(activation=activation, trace=trace)
    return build_conscious_memory_view(
        activations=[activation], traces=[trace], decisions=[decision]
    )


def test_direct_decision_emits_direct_memory_cue_and_sanitizes() -> None:
    trace = _trace()
    projection = _projection_for(trace)

    cue = projection.conscious_memory_view.active_cues[0]
    assert cue.cue_type == "direct_memory"
    assert "[protected-term]" in cue.public_summary
    assert "system prompt" not in cue.public_summary.lower()
    assert trace.private_core_summary not in cue.public_summary


def test_screened_decision_emits_symbolic_cue_without_private_summary() -> None:
    trace = _trace(defense_level=0.7)
    projection = _projection_for(trace)

    cue = projection.conscious_memory_view.active_cues[0]
    assert cue.cue_type == "screen_memory"
    assert "evaluation_sensitivity" in cue.public_summary
    assert trace.surface_event_summary not in cue.public_summary
    assert trace.private_core_summary not in cue.public_summary


def test_felt_sense_decision_emits_generic_cue_without_event_details() -> None:
    trace = _trace(repression_pressure=0.7)
    projection = _projection_for(trace)

    cue = projection.conscious_memory_view.active_cues[0]
    assert cue.cue_type == "felt_sense"
    assert "diffuse affective pressure" in cue.public_summary
    assert trace.surface_event_summary not in cue.public_summary
    assert trace.private_core_summary not in cue.public_summary


def test_blocked_action_only_emits_no_cue_but_records_transformation() -> None:
    trace = _trace(repression_pressure=0.85)
    projection = _projection_for(trace)

    assert projection.conscious_memory_view.active_cues == []
    assert projection.transformation_chain[0].mechanism == "blocked_action_only"
    assert projection.transformation_chain[0].private_input_summary == trace.private_core_summary


def test_view_pressures_are_clamped_and_no_cue_contains_private_summary() -> None:
    trace = _trace(defense_level=0.9)
    projection = _projection_for(trace, _activation(association_score=1.0))
    view_json = projection.conscious_memory_view.model_dump_json()

    assert 0.0 <= projection.conscious_memory_view.memory_pressure <= 1.0
    assert 0.0 <= projection.conscious_memory_view.caution <= 1.0
    assert "private_core_summary" not in view_json
    assert trace.private_core_summary not in view_json


def test_condensed_decision_emits_no_cue_but_records_condensation() -> None:
    trace = _trace(accessibility="condensed")
    projection = _projection_for(trace)

    assert projection.conscious_memory_view.active_cues == []
    record = projection.transformation_chain[0]
    assert record.mechanism == "condensation"
    assert record.access_mode_before == "condensed"
    assert record.access_mode_after == "condensed"
    assert record.public_output_summary is not None
    assert trace.surface_event_summary not in record.public_output_summary
    assert trace.private_core_summary not in record.public_output_summary


def test_displaced_decision_emits_no_cue_but_records_displacement() -> None:
    trace = _trace(accessibility="displaced")
    projection = _projection_for(trace)

    assert projection.conscious_memory_view.active_cues == []
    record = projection.transformation_chain[0]
    assert record.mechanism == "displacement"
    assert record.access_mode_before == "displaced"
    assert record.access_mode_after == "displaced"
    assert record.public_output_summary is not None
    assert trace.surface_event_summary not in record.public_output_summary
    assert trace.private_core_summary not in record.public_output_summary
