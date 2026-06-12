from psychodynamic_agent.memory.complex_clustering import create_complex_from_trace
from psychodynamic_agent.memory.complex_engine import MemoryComplexEngine
from psychodynamic_agent.schemas.memory import (
    AffectiveSignature,
    AssociationScoreBreakdown,
    DesireSignature,
    MemoryActivation,
    MemoryTrace,
    ThreatSignature,
)


def _trace(trace_id: str, turn: int = 1) -> MemoryTrace:
    return MemoryTrace(
        trace_id=trace_id,
        created_turn=turn,
        surface_event_summary="public",
        private_core_summary="private_core_summary secret",
        affective_signature=AffectiveSignature(
            valence=0.5,
            arousal=0.8,
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
        repression_pressure=0.2,
        accessibility="screened",
    )


def _activation(trace_id: str) -> MemoryActivation:
    return MemoryActivation(
        trace_id=trace_id,
        created_turn=1,
        activation_rank=1,
        association_score=0.9,
        components=AssociationScoreBreakdown(
            affect_similarity=0.9,
            desire_similarity=0.9,
            threat_similarity=0.9,
            object_overlap=0,
            salient_symbol_overlap=0,
            repetition_frequency=0,
            fact_similarity=0,
            defense_barrier=0,
            weighted_score_before_defense=0.9,
            final_score=0.9,
        ),
        accessibility="direct",
        public_reason="related",
    )


def test_update_with_trace_creates_and_updates_without_mutation() -> None:
    engine = MemoryComplexEngine()
    first = _trace("a")
    complexes, created, updated, next_index = engine.update_with_trace(
        trace=first, complexes=[], all_traces=[first], next_complex_index=1
    )
    assert created[0].complex_id == "cx_000001"
    assert updated == []
    second = _trace("b", 2)
    original_trace_ids = list(complexes[0].trace_ids)
    complexes2, created2, updated2, next_index2 = engine.update_with_trace(
        trace=second, complexes=complexes, all_traces=[first, second], next_complex_index=next_index
    )
    assert complexes[0].trace_ids == original_trace_ids
    assert created2 == []
    assert updated2[0].trace_ids == ["a", "b"]
    assert next_index2 == next_index
    assert complexes2[0].trace_ids == ["a", "b"]


def test_activate_returns_update_result_without_mutating_inputs() -> None:
    engine = MemoryComplexEngine()
    trace = _trace("a")
    complex_node = create_complex_from_trace(trace=trace, complex_id="cx_000001")
    original_turn = complex_node.last_activated_turn
    result = engine.activate(
        complexes=[complex_node], activations=[_activation("a")], traces=[trace], current_turn=5
    )
    assert result.activated_complexes
    assert result.activated_complexes[0].public_reason
    assert result.activated_complexes[0].public_label == "evaluation_sensitivity_cluster"
    assert result.complexes[0].last_activated_turn == 5
    assert complex_node.last_activated_turn == original_turn
