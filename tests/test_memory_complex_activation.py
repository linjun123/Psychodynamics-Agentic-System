from psychodynamic_agent.memory.complex_activation import (
    activate_complexes,
    update_complexes_after_activation,
)
from psychodynamic_agent.memory.complex_clustering import create_complex_from_trace
from psychodynamic_agent.schemas.memory import (
    AffectiveSignature,
    AssociationScoreBreakdown,
    DesireSignature,
    MemoryActivation,
    MemoryTrace,
    RepetitionBias,
    ThreatSignature,
)


def _trace(trace_id: str) -> MemoryTrace:
    return MemoryTrace(
        trace_id=trace_id,
        created_turn=1,
        surface_event_summary="public",
        private_core_summary="private_core_summary secret",
        affective_signature=AffectiveSignature(
            valence=0.5,
            arousal=0.9,
            longing=0,
            irritation=0,
            fear_of_loss=0,
            possessiveness=0,
            aggression=0,
            shame=0.9,
            curiosity=0,
            avoidance=0,
        ),
        desire_signature=DesireSignature(
            attachment=0, recognition=0.8, autonomy=0, mastery=0, safety=0, novelty=0
        ),
        threat_signature=ThreatSignature(
            rejection=0,
            humiliation=0.9,
            loss=0,
            exposure=0,
            control=0,
            failure=0,
            boundary_violation=0,
        ),
        object_targets=["authority"],
        salient_symbols=["evaluation_sensitivity"],
        defense_level=0.5,
        repression_pressure=0.3,
        accessibility="screened",
    )


def _activation(trace_id: str, score: float) -> MemoryActivation:
    return MemoryActivation(
        trace_id=trace_id,
        created_turn=1,
        activation_rank=1,
        association_score=score,
        components=AssociationScoreBreakdown(
            affect_similarity=score,
            desire_similarity=score,
            threat_similarity=score,
            object_overlap=0,
            salient_symbol_overlap=0,
            repetition_frequency=0,
            fact_similarity=0,
            defense_barrier=0,
            weighted_score_before_defense=score,
            final_score=score,
        ),
        accessibility="direct",
        public_reason="related",
    )


def test_activate_complexes_activates_matching_complex() -> None:
    trace = _trace("a")
    complex_node = create_complex_from_trace(trace=trace, complex_id="cx_000001")
    activations = activate_complexes(
        complexes=[complex_node], activations=[_activation("a", 0.9)], traces=[trace]
    )
    assert activations[0].complex_id == "cx_000001"
    assert activations[0].source_activation_trace_ids == ["a"]


def test_activate_complexes_does_not_activate_below_threshold() -> None:
    trace = _trace("a")
    complex_node = create_complex_from_trace(trace=trace, complex_id="cx_000001")
    complex_node.charge = 0.0
    complex_node.activation_threshold = 0.95
    assert (
        activate_complexes(
            complexes=[complex_node], activations=[_activation("a", 0.1)], traces=[trace]
        )
        == []
    )


def test_update_complexes_after_activation_updates_charge_and_turn() -> None:
    trace = _trace("a")
    complex_node = create_complex_from_trace(trace=trace, complex_id="cx_000001")
    activation = activate_complexes(
        complexes=[complex_node], activations=[_activation("a", 0.9)], traces=[trace]
    )[0]
    updated = update_complexes_after_activation(
        complexes=[complex_node], activations=[activation], current_turn=3
    )[0]
    assert updated.charge >= complex_node.charge
    assert updated.last_activated_turn == 3


def test_non_activated_complexes_decay() -> None:
    complex_node = create_complex_from_trace(trace=_trace("a"), complex_id="cx_000001")
    updated = update_complexes_after_activation(complexes=[complex_node], activations=[])[0]
    assert updated.charge < complex_node.charge


def test_memory_complex_activation_omits_private_core_summary_and_includes_repetition() -> None:
    trace = _trace("a")
    complex_node = create_complex_from_trace(trace=trace, complex_id="cx_000001")
    bias = RepetitionBias(
        bias_id="b",
        source_trace_ids=["a"],
        tendency="seek_reassurance",
        intensity=0.8,
        safe_strategy_hint="safe",
        prohibited_expression=[],
    )
    activation = activate_complexes(
        complexes=[complex_node],
        activations=[_activation("a", 0.9)],
        traces=[trace],
        repetition_biases=[bias],
    )[0]
    assert "private_core_summary" not in activation.model_dump_json()
    assert activation.repetition_tendencies == ["seek_reassurance"]
