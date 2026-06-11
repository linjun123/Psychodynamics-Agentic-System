from psychodynamic_agent.memory.associator import MemoryAssociator
from psychodynamic_agent.schemas.memory import (
    AffectiveSignature,
    DesireSignature,
    MemoryRetrievalQuery,
    MemoryTrace,
    ThreatSignature,
)


def _affective(shame: float = 0.0) -> AffectiveSignature:
    return AffectiveSignature(
        valence=0.5,
        arousal=0.3,
        longing=0.0,
        irritation=0.0,
        fear_of_loss=0.0,
        possessiveness=0.0,
        aggression=0.0,
        shame=shame,
        curiosity=0.0,
        avoidance=0.0,
    )


def _desire(recognition: float = 0.0) -> DesireSignature:
    return DesireSignature(
        attachment=0.0,
        recognition=recognition,
        autonomy=0.0,
        mastery=0.0,
        safety=0.0,
        novelty=0.0,
    )


def _threat(humiliation: float = 0.0) -> ThreatSignature:
    return ThreatSignature(
        rejection=0.0,
        humiliation=humiliation,
        loss=0.0,
        exposure=0.0,
        control=0.0,
        failure=0.0,
        boundary_violation=0.0,
    )


def _query(
    *,
    shame: float = 0.8,
    recognition: float = 0.8,
    humiliation: float = 0.8,
    object_targets: list[str] | None = None,
    salient_symbols: list[str] | None = None,
    query_summary: str = "boss feedback",
) -> MemoryRetrievalQuery:
    return MemoryRetrievalQuery(
        affective_signature=_affective(shame),
        desire_signature=_desire(recognition),
        threat_signature=_threat(humiliation),
        object_targets=["boss"] if object_targets is None else object_targets,
        salient_symbols=(
            ["evaluation_sensitivity"] if salient_symbols is None else salient_symbols
        ),
        query_summary=query_summary,
    )


def _trace(
    trace_id: str,
    *,
    created_turn: int = 1,
    shame: float = 0.0,
    recognition: float = 0.0,
    humiliation: float = 0.0,
    defense_level: float = 0.2,
    repression_pressure: float = 0.1,
    accessibility: str = "direct",
    activation_count: int = 1,
    surface_event_summary: str = "boss feedback",
    object_targets: list[str] | None = None,
    salient_symbols: list[str] | None = None,
) -> MemoryTrace:
    return MemoryTrace(
        trace_id=trace_id,
        created_turn=created_turn,
        surface_event_summary=surface_event_summary,
        private_core_summary="private",
        affective_signature=_affective(shame),
        desire_signature=_desire(recognition),
        threat_signature=_threat(humiliation),
        object_targets=["boss"] if object_targets is None else object_targets,
        salient_symbols=(
            ["evaluation_sensitivity"] if salient_symbols is None else salient_symbols
        ),
        defense_level=defense_level,
        repression_pressure=repression_pressure,
        accessibility=accessibility,  # type: ignore[arg-type]
        activation_count=activation_count,
    )


def test_retrieve_returns_top_k_sorted_by_association_score() -> None:
    traces = [
        _trace("low", shame=0.1, recognition=0.1, humiliation=0.1),
        _trace("high", shame=0.8, recognition=0.8, humiliation=0.8),
    ]

    activations = MemoryAssociator().retrieve(query=_query(), traces=traces, top_k=1)

    assert [activation.trace_id for activation in activations] == ["high"]
    assert activations[0].activation_rank == 1


def test_include_blocked_false_excludes_blocked_action_only_traces() -> None:
    traces = [
        _trace(
            "blocked",
            shame=0.8,
            recognition=0.8,
            humiliation=0.8,
            accessibility="blocked_action_only",
        ),
        _trace("direct", shame=0.2, recognition=0.2, humiliation=0.2),
    ]

    activations = MemoryAssociator().retrieve(
        query=_query(),
        traces=traces,
        include_blocked=False,
    )

    assert [activation.trace_id for activation in activations] == ["direct"]


def test_min_score_filters_low_score_traces() -> None:
    activations = MemoryAssociator().retrieve(
        query=_query(),
        traces=[_trace("low", shame=0.0, recognition=0.0, humiliation=0.0)],
        min_score=0.95,
    )

    assert activations == []


def test_retrieval_does_not_mutate_activation_count() -> None:
    trace = _trace("same", shame=0.8, recognition=0.8, humiliation=0.8, activation_count=3)

    MemoryAssociator().retrieve(query=_query(), traces=[trace])

    assert trace.activation_count == 3


def test_tie_breaking_is_stable() -> None:
    older = _trace("b", created_turn=1, shame=0.8, recognition=0.8, humiliation=0.8)
    newer = _trace("a", created_turn=2, shame=0.8, recognition=0.8, humiliation=0.8)
    higher_defense = _trace(
        "c",
        created_turn=3,
        shame=0.8,
        recognition=0.8,
        humiliation=0.8,
        defense_level=0.4,
    )

    activations = MemoryAssociator().retrieve(
        query=_query(),
        traces=[older, newer, higher_defense],
    )

    assert [activation.trace_id for activation in activations] == ["a", "b", "c"]


def test_neutral_unrelated_traces_have_low_scores_and_can_be_filtered() -> None:
    query = _query(
        shame=0.0,
        recognition=0.0,
        humiliation=0.0,
        object_targets=[],
        salient_symbols=[],
        query_summary="ordinary message",
    )
    traces = [
        _trace(
            "neutral-a",
            surface_event_summary="unrelated ordinary text",
            object_targets=[],
            salient_symbols=[],
        ),
        _trace(
            "neutral-b",
            surface_event_summary="another low signal note",
            object_targets=[],
            salient_symbols=[],
        ),
    ]

    activations = MemoryAssociator().retrieve(query=query, traces=traces, min_score=0.0)
    filtered = MemoryAssociator().retrieve(query=query, traces=traces, min_score=0.1)

    assert activations
    assert all(activation.association_score <= 0.05 for activation in activations)
    assert filtered == []
