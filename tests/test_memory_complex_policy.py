from psychodynamic_agent.memory.complex_clustering import create_complex_from_trace
from psychodynamic_agent.memory.complex_policy import (
    complex_activation_score,
    decay_complex_charge,
    initial_complex_charge,
    preferred_defenses_from_traces,
    should_join_complex,
    trace_complex_similarity,
)
from psychodynamic_agent.schemas.memory import (
    AffectiveSignature,
    AssociationScoreBreakdown,
    DesireSignature,
    MemoryActivation,
    MemoryTrace,
    ThreatSignature,
)


def _affective(**overrides: float) -> AffectiveSignature:
    values = dict(
        valence=0.5,
        arousal=0.3,
        longing=0,
        irritation=0,
        fear_of_loss=0,
        possessiveness=0,
        aggression=0,
        shame=0,
        curiosity=0,
        avoidance=0,
    )
    values.update(overrides)
    return AffectiveSignature(**values)


def _desire(**overrides: float) -> DesireSignature:
    values = dict(attachment=0, recognition=0, autonomy=0, mastery=0, safety=0, novelty=0)
    values.update(overrides)
    return DesireSignature(**values)


def _threat(**overrides: float) -> ThreatSignature:
    values = dict(
        rejection=0, humiliation=0, loss=0, exposure=0, control=0, failure=0, boundary_violation=0
    )
    values.update(overrides)
    return ThreatSignature(**values)


def _trace(trace_id: str, **overrides: object) -> MemoryTrace:
    values = dict(
        trace_id=trace_id,
        created_turn=1,
        surface_event_summary="public",
        private_core_summary="private_core_summary secret",
        affective_signature=_affective(),
        desire_signature=_desire(),
        threat_signature=_threat(),
        object_targets=[],
        salient_symbols=[],
        defense_level=0.1,
        repression_pressure=0.1,
        accessibility="direct",
        activation_count=0,
    )
    values.update(overrides)
    return MemoryTrace(**values)


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


def test_trace_complex_similarity_high_for_similar_affect_threat_symbol_traces() -> None:
    left = _trace(
        "a",
        affective_signature=_affective(shame=0.9, arousal=0.8),
        desire_signature=_desire(recognition=0.8),
        threat_signature=_threat(humiliation=0.9),
        salient_symbols=["evaluation_sensitivity"],
    )
    right = _trace(
        "b",
        affective_signature=_affective(shame=0.85, arousal=0.75),
        desire_signature=_desire(recognition=0.75),
        threat_signature=_threat(humiliation=0.85),
        salient_symbols=["evaluation_sensitivity"],
    )
    assert trace_complex_similarity(left, right) > 0.75


def test_trace_complex_similarity_low_for_unrelated_neutral_traces() -> None:
    left = _trace("a", salient_symbols=["evaluation_sensitivity"])
    right = _trace("b", salient_symbols=["curiosity"], object_targets=["garden"])
    assert trace_complex_similarity(left, right) < 0.2


def test_should_join_complex_true_for_similar_trace_and_false_for_unrelated() -> None:
    base = _trace(
        "a",
        affective_signature=_affective(shame=0.9),
        threat_signature=_threat(humiliation=0.9),
        salient_symbols=["evaluation_sensitivity"],
    )
    similar = _trace(
        "b",
        affective_signature=_affective(shame=0.85),
        threat_signature=_threat(humiliation=0.85),
        salient_symbols=["evaluation_sensitivity"],
    )
    unrelated = _trace(
        "c",
        affective_signature=_affective(curiosity=0.9),
        threat_signature=_threat(),
        salient_symbols=["curiosity"],
    )
    complex_node = create_complex_from_trace(trace=base, complex_id="cx_000001")
    assert should_join_complex(similar, complex_node, {"a": base})
    assert not should_join_complex(unrelated, complex_node, {"a": base})


def test_initial_complex_charge_bounds_and_rises_with_pressure() -> None:
    low = initial_complex_charge(_trace("low"))
    high = initial_complex_charge(
        _trace(
            "high",
            affective_signature=_affective(arousal=1),
            threat_signature=_threat(humiliation=1),
            defense_level=1,
            repression_pressure=1,
            activation_count=5,
        )
    )
    assert 0 <= low <= 1
    assert 0 <= high <= 1
    assert high > low


def test_decay_complex_charge_lowers_and_clamps() -> None:
    assert decay_complex_charge(0.5) < 0.5
    assert decay_complex_charge(0.01) == 0.0


def test_complex_activation_score_increases_with_matched_activations() -> None:
    trace = _trace("a")
    complex_node = create_complex_from_trace(trace=trace, complex_id="cx_000001")
    unmatched = complex_activation_score(
        complex_node=complex_node, activations=[_activation("x", 0.9)]
    )
    matched = complex_activation_score(
        complex_node=complex_node, activations=[_activation("a", 0.9)]
    )
    assert matched > unmatched


def test_preferred_defenses_from_traces_maps_access_modes() -> None:
    defenses = preferred_defenses_from_traces(
        [
            _trace("screen", accessibility="screened"),
            _trace("block", accessibility="blocked_action_only"),
            _trace("cond", accessibility="condensed"),
            _trace("disp", accessibility="displaced"),
        ]
    )
    assert defenses == ["screening", "blocking", "condensation", "displacement"]
