from psychodynamic_agent.memory.complex_clustering import (
    add_trace_to_complex,
    assign_trace_to_complexes,
    create_complex_from_trace,
    rebuild_complexes_from_traces,
)
from psychodynamic_agent.schemas.memory import (
    AffectiveSignature,
    DesireSignature,
    MemoryTrace,
    ThreatSignature,
)


def _sig(shame: float = 0, loss: float = 0, curiosity: float = 0) -> AffectiveSignature:
    return AffectiveSignature(
        valence=0.5,
        arousal=max(0.3, shame, loss, curiosity),
        longing=0,
        irritation=0,
        fear_of_loss=loss,
        possessiveness=0,
        aggression=0,
        shame=shame,
        curiosity=curiosity,
        avoidance=0,
    )


def _desire(recognition: float = 0, attachment: float = 0) -> DesireSignature:
    return DesireSignature(
        attachment=attachment, recognition=recognition, autonomy=0, mastery=0, safety=0, novelty=0
    )


def _threat(humiliation: float = 0, rejection: float = 0, loss: float = 0) -> ThreatSignature:
    return ThreatSignature(
        rejection=rejection,
        humiliation=humiliation,
        loss=loss,
        exposure=0,
        control=0,
        failure=0,
        boundary_violation=0,
    )


def _trace(trace_id: str, turn: int = 1, **overrides: object) -> MemoryTrace:
    values = dict(
        trace_id=trace_id,
        created_turn=turn,
        surface_event_summary="public",
        private_core_summary="private_core_summary forbidden",
        affective_signature=_sig(shame=0.9),
        desire_signature=_desire(recognition=0.8),
        threat_signature=_threat(humiliation=0.9),
        object_targets=["authority"],
        salient_symbols=["evaluation_sensitivity"],
        defense_level=0.4,
        repression_pressure=0.2,
        accessibility="screened",
    )
    values.update(overrides)
    return MemoryTrace(**values)


def test_create_complex_from_trace_sets_trace_id_labels_and_charge() -> None:
    complex_node = create_complex_from_trace(trace=_trace("a"), complex_id="cx_000001")
    assert complex_node.trace_ids == ["a"]
    assert complex_node.public_label == "evaluation_sensitivity_cluster"
    assert complex_node.charge > 0


def test_add_trace_to_complex_adds_trace_and_refreshes_labels_without_mutation() -> None:
    first = _trace("a")
    second = _trace("b", turn=2)
    complex_node = create_complex_from_trace(trace=first, complex_id="cx_000001")
    updated = add_trace_to_complex(
        complex_node=complex_node, trace=second, all_traces=[first, second]
    )
    assert complex_node.trace_ids == ["a"]
    assert updated.trace_ids == ["a", "b"]


def test_assign_trace_to_complexes_creates_new_complex_when_no_match() -> None:
    first = _trace("a")
    unrelated = _trace(
        "b",
        affective_signature=_sig(curiosity=0.9),
        desire_signature=_desire(),
        threat_signature=_threat(),
        object_targets=["garden"],
        salient_symbols=["curiosity"],
    )
    complexes = [create_complex_from_trace(trace=first, complex_id="cx_000001")]
    updated, created, changed, next_index = assign_trace_to_complexes(
        trace=unrelated, complexes=complexes, all_traces=[first, unrelated], next_complex_index=2
    )
    assert len(updated) == 2
    assert created[0].complex_id == "cx_000002"
    assert changed == []
    assert next_index == 3


def test_assign_trace_to_complexes_joins_existing_complex_when_similar() -> None:
    first = _trace("a")
    similar = _trace("b", turn=2)
    complexes = [create_complex_from_trace(trace=first, complex_id="cx_000001")]
    updated, created, changed, next_index = assign_trace_to_complexes(
        trace=similar, complexes=complexes, all_traces=[first, similar], next_complex_index=2
    )
    assert updated[0].trace_ids == ["a", "b"]
    assert created == []
    assert changed[0].complex_id == "cx_000001"
    assert next_index == 2


def test_rebuild_complexes_from_traces_deterministically_clusters_related_traces() -> None:
    complexes = rebuild_complexes_from_traces(
        [
            _trace("b", turn=2),
            _trace("a", turn=1),
            _trace(
                "c",
                turn=3,
                affective_signature=_sig(curiosity=0.9),
                desire_signature=_desire(),
                threat_signature=_threat(),
                object_targets=["garden"],
                salient_symbols=["curiosity"],
            ),
        ]
    )
    assert [complex_node.complex_id for complex_node in complexes] == ["cx_000001", "cx_000002"]
    assert complexes[0].trace_ids == ["a", "b"]


def test_complex_labels_do_not_contain_private_core_summary() -> None:
    complex_node = create_complex_from_trace(trace=_trace("a"), complex_id="cx_000001")
    assert "private_core_summary" not in complex_node.public_label
    assert "private_core_summary" not in (complex_node.private_label or "")
