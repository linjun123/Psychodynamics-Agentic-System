from psychodynamic_agent.memory.association_scoring import (
    build_memory_activation,
    score_trace_association,
)
from psychodynamic_agent.schemas.memory import (
    AffectiveSignature,
    DesireSignature,
    MemoryRetrievalQuery,
    MemoryTrace,
    ThreatSignature,
)


def _affective(**overrides: float) -> AffectiveSignature:
    values = dict(
        valence=0.5,
        arousal=0.3,
        longing=0.0,
        irritation=0.0,
        fear_of_loss=0.0,
        possessiveness=0.0,
        aggression=0.0,
        shame=0.0,
        curiosity=0.0,
        avoidance=0.0,
    )
    values.update(overrides)
    return AffectiveSignature(**values)


def _desire(**overrides: float) -> DesireSignature:
    values = dict(
        attachment=0.0,
        recognition=0.0,
        autonomy=0.0,
        mastery=0.0,
        safety=0.0,
        novelty=0.0,
    )
    values.update(overrides)
    return DesireSignature(**values)


def _threat(**overrides: float) -> ThreatSignature:
    values = dict(
        rejection=0.0,
        humiliation=0.0,
        loss=0.0,
        exposure=0.0,
        control=0.0,
        failure=0.0,
        boundary_violation=0.0,
    )
    values.update(overrides)
    return ThreatSignature(**values)


def _query(**overrides: object) -> MemoryRetrievalQuery:
    values = dict(
        affective_signature=_affective(),
        desire_signature=_desire(),
        threat_signature=_threat(),
        object_targets=[],
        salient_symbols=[],
        query_summary="boss feedback",
    )
    values.update(overrides)
    return MemoryRetrievalQuery(**values)


def _trace(**overrides: object) -> MemoryTrace:
    values = dict(
        trace_id="trace-a",
        created_turn=1,
        surface_event_summary="school classroom",
        private_core_summary="Private hidden text that should not be activated.",
        affective_signature=_affective(),
        desire_signature=_desire(),
        threat_signature=_threat(),
        object_targets=[],
        salient_symbols=[],
        defense_level=0.2,
        repression_pressure=0.1,
        accessibility="direct",
        activation_count=1,
    )
    values.update(overrides)
    return MemoryTrace(**values)


def test_score_trace_association_returns_components_between_zero_and_one() -> None:
    components = score_trace_association(query=_query(), trace=_trace())

    for value in components.model_dump().values():
        assert 0.0 <= value <= 1.0


def test_affect_desire_threat_similarity_can_outrank_fact_similarity() -> None:
    query = _query(
        affective_signature=_affective(shame=0.9, fear_of_loss=0.8, arousal=0.8),
        desire_signature=_desire(recognition=0.8, attachment=0.7),
        threat_signature=_threat(humiliation=0.9, loss=0.8, rejection=0.7),
        salient_symbols=["evaluation_sensitivity", "loss_anxiety"],
        query_summary="boss feedback",
    )
    affect_trace = _trace(
        trace_id="affect",
        surface_event_summary="school classroom",
        affective_signature=_affective(shame=0.9, fear_of_loss=0.8, arousal=0.8),
        desire_signature=_desire(recognition=0.8, attachment=0.7),
        threat_signature=_threat(humiliation=0.9, loss=0.8, rejection=0.7),
        salient_symbols=["evaluation_sensitivity", "loss_anxiety"],
    )
    fact_trace = _trace(
        trace_id="fact",
        surface_event_summary="boss feedback meeting",
        affective_signature=_affective(),
        desire_signature=_desire(),
        threat_signature=_threat(),
    )

    affect_score = score_trace_association(query=query, trace=affect_trace).final_score
    fact_score = score_trace_association(query=query, trace=fact_trace).final_score

    assert affect_score > fact_score


def test_neutral_unrelated_traces_do_not_receive_high_association_score() -> None:
    query = _query(
        affective_signature=_affective(),
        desire_signature=_desire(),
        threat_signature=_threat(),
        object_targets=[],
        salient_symbols=[],
        query_summary="ordinary message",
    )
    trace = _trace(
        surface_event_summary="unrelated ordinary text",
        affective_signature=_affective(),
        desire_signature=_desire(),
        threat_signature=_threat(),
        object_targets=[],
        salient_symbols=[],
        defense_level=0.2,
        repression_pressure=0.1,
        activation_count=1,
    )

    components = score_trace_association(query=query, trace=trace)

    assert components.affect_similarity == 0.0
    assert components.desire_similarity == 0.0
    assert components.threat_similarity == 0.0
    assert components.final_score <= 0.05


def test_defense_barrier_lowers_final_score() -> None:
    query = _query(
        affective_signature=_affective(shame=0.8),
        desire_signature=_desire(recognition=0.8),
        threat_signature=_threat(humiliation=0.8),
    )
    low_defense = _trace(
        affective_signature=_affective(shame=0.8),
        desire_signature=_desire(recognition=0.8),
        threat_signature=_threat(humiliation=0.8),
        defense_level=0.1,
        repression_pressure=0.1,
    )
    high_defense = _trace(
        affective_signature=_affective(shame=0.8),
        desire_signature=_desire(recognition=0.8),
        threat_signature=_threat(humiliation=0.8),
        defense_level=0.9,
        repression_pressure=0.8,
    )

    low_score = score_trace_association(query=query, trace=low_defense).final_score
    high_score = score_trace_association(query=query, trace=high_defense).final_score

    assert low_score > high_score


def test_build_memory_activation_excludes_private_core_summary_from_json() -> None:
    activation = build_memory_activation(query=_query(), trace=_trace(), rank=1)
    payload = activation.model_dump_json()

    assert "private_core_summary" not in payload
    assert "Private hidden text" not in payload


def test_build_memory_activation_computes_matched_objects_and_symbols() -> None:
    activation = build_memory_activation(
        query=_query(object_targets=["Boss", "teacher"], salient_symbols=["loss_anxiety"]),
        trace=_trace(object_targets=["boss"], salient_symbols=["loss_anxiety", "curiosity"]),
        rank=1,
    )

    assert activation.matched_object_targets == ["Boss"]
    assert activation.matched_salient_symbols == ["loss_anxiety"]
