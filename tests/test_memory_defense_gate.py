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


def _components(final_score: float = 0.5) -> AssociationScoreBreakdown:
    return AssociationScoreBreakdown(
        affect_similarity=0.5,
        desire_similarity=0.5,
        threat_similarity=0.5,
        object_overlap=0.0,
        salient_symbol_overlap=0.0,
        repetition_frequency=0.0,
        fact_similarity=0.0,
        defense_barrier=0.0,
        weighted_score_before_defense=final_score,
        final_score=final_score,
    )


def _activation(**overrides: object) -> MemoryActivation:
    values = {
        "trace_id": "trace-1",
        "created_turn": 1,
        "activation_rank": 1,
        "association_score": 0.5,
        "components": _components(),
        "accessibility": "direct",
        "public_reason": "Retrieved due to affect similarity.",
    }
    values.update(overrides)
    return MemoryActivation(**values)


def _trace(**overrides: object) -> MemoryTrace:
    values = {
        "trace_id": "trace-1",
        "created_turn": 1,
        "surface_event_summary": "User wanted structure.",
        "private_core_summary": "Private fear of being ignored.",
        "affective_signature": _affective(),
        "desire_signature": _desire(),
        "threat_signature": _threat(),
        "defense_level": 0.2,
        "repression_pressure": 0.1,
        "accessibility": "direct",
    }
    values.update(overrides)
    return MemoryTrace(**values)


def test_decide_returns_expected_fields() -> None:
    decision = MemoryDefenseGate().decide(activation=_activation(), trace=_trace())

    assert decision.trace_id == "trace-1"
    assert decision.activation_rank == 1
    assert decision.original_accessibility == "direct"
    assert decision.decided_accessibility == "direct"
    assert decision.conscious_access == "direct"
    assert decision.mechanism == "direct"
    assert decision.emits_conscious_cue is True


def test_decide_many_skips_missing_and_sorts_by_activation_rank() -> None:
    decisions = MemoryDefenseGate().decide_many(
        activations=[
            _activation(trace_id="missing", activation_rank=1),
            _activation(trace_id="trace-2", activation_rank=3),
            _activation(trace_id="trace-1", activation_rank=2),
        ],
        traces=[_trace(trace_id="trace-1"), _trace(trace_id="trace-2")],
    )

    assert [decision.trace_id for decision in decisions] == ["trace-1", "trace-2"]
    assert [decision.activation_rank for decision in decisions] == [2, 3]


def test_gate_does_not_mutate_trace_or_activation() -> None:
    trace = _trace(repression_pressure=0.7)
    activation = _activation()
    trace_before = trace.model_dump()
    activation_before = activation.model_dump()

    MemoryDefenseGate().decide(activation=activation, trace=trace)

    assert trace.model_dump() == trace_before
    assert activation.model_dump() == activation_before


def test_high_repression_produces_felt_sense_or_blocked_by_threshold() -> None:
    gate = MemoryDefenseGate()
    felt = gate.decide(activation=_activation(), trace=_trace(repression_pressure=0.70))
    blocked = gate.decide(activation=_activation(), trace=_trace(repression_pressure=0.85))

    assert felt.decided_accessibility == "felt_sense_only"
    assert blocked.decided_accessibility == "blocked_action_only"


def test_gate_preserves_condensed_access_without_direct_fallback() -> None:
    decision = MemoryDefenseGate().decide(
        activation=_activation(accessibility="condensed"),
        trace=_trace(accessibility="condensed"),
    )

    assert decision.decided_accessibility == "condensed"
    assert decision.conscious_access == "condensed"
    assert decision.mechanism == "condensation"
    assert decision.emits_conscious_cue is False


def test_gate_preserves_displaced_access_without_direct_fallback() -> None:
    decision = MemoryDefenseGate().decide(
        activation=_activation(accessibility="displaced"),
        trace=_trace(accessibility="displaced"),
    )

    assert decision.decided_accessibility == "displaced"
    assert decision.conscious_access == "displaced"
    assert decision.mechanism == "displacement"
    assert decision.emits_conscious_cue is False
