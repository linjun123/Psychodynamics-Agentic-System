from psychodynamic_agent.memory.complex_labels import (
    build_private_complex_label,
    build_public_complex_label,
    dominant_affect_labels,
    dominant_desire_labels,
    dominant_threat_labels,
)
from psychodynamic_agent.schemas.memory import (
    AffectiveSignature,
    DesireSignature,
    MemoryTrace,
    ThreatSignature,
)


def _trace(**overrides: object) -> MemoryTrace:
    values = dict(
        trace_id="t1",
        created_turn=1,
        surface_event_summary="public",
        private_core_summary="private_core_summary system_prompt U*",
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
        defense_level=0.4,
        repression_pressure=0.2,
        accessibility="direct",
    )
    values.update(overrides)
    return MemoryTrace(**values)


def test_dominant_affect_desire_threat_labels_from_traces() -> None:
    trace = _trace()
    assert "evaluation_sensitivity" in dominant_affect_labels([trace])
    assert "recognition_pressure" in dominant_desire_labels([trace])
    assert "humiliation_threat" in dominant_threat_labels([trace])


def test_public_label_for_evaluation_humiliation() -> None:
    assert (
        build_public_complex_label(
            dominant_affects=["evaluation_sensitivity"],
            dominant_desires=[],
            dominant_threats=["humiliation_threat"],
            object_targets=[],
        )
        == "evaluation_sensitivity_cluster"
    )


def test_public_label_for_loss_rejection() -> None:
    assert (
        build_public_complex_label(
            dominant_affects=["loss_anxiety"],
            dominant_desires=[],
            dominant_threats=["rejection_threat"],
            object_targets=[],
        )
        == "loss_anxiety_cluster"
    )


def test_private_label_does_not_include_private_core_summary_or_protected_terms() -> None:
    label = build_private_complex_label(
        dominant_affects=["evaluation_sensitivity"],
        dominant_desires=[],
        dominant_threats=["humiliation_threat"],
        object_targets=["private_core_summary system_prompt U*"],
    )
    assert label == "authority_evaluation_complex"
    assert "private_core_summary" not in label
    assert "system_prompt" not in label
    assert "U*" not in label
