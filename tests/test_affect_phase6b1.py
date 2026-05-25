import pytest

from psychodynamic_agent.affect import (
    assert_affect_trace_public_safe,
    assert_affective_color_consistent,
    map_id_affect_to_trace,
    summarize_affect_for_ego,
)
from psychodynamic_agent.schemas.affect import AffectPropagationTrace
from psychodynamic_agent.schemas.censor import AffectiveColor
from psychodynamic_agent.schemas.id import DriveState, IdOutput, RawAffect


def _id_output(**raw_overrides: float) -> IdOutput:
    leakage = raw_overrides.pop("leakage_risk_self_check", 0.2)
    raw = {
        "valence": 0.2,
        "arousal": 0.3,
        "approach": 0.3,
        "avoidance": 0.2,
        "longing": 0.3,
        "excitement": 0.2,
        "irritation": 0.1,
        "fear_of_loss": 0.2,
        "curiosity": 0.2,
        "possessiveness": 0.2,
        "aggression": 0.1,
    }
    raw.update(raw_overrides)
    return IdOutput(
        drive_state=DriveState(
            pressure=0.4, urgency=0.3, satisfaction=0.4, frustration=0.2, tension_delta=0.1
        ),
        raw_affect=RawAffect(**raw),
        object_cathexis=[],
        latent_impulse_shape="test",
        symbolic_imagery=None,
        goal_seed="test goal",
        leakage_risk_self_check=leakage,
    )


def test_high_longing_approach_increases_warmth() -> None:
    trace = map_id_affect_to_trace(_id_output(longing=0.95, approach=0.85))
    assert trace.transformed_style.warmth >= 0.6
    assert trace.transformed_style.conscious_style_hint in {
        "warm and collaborative",
        "cautious and bounded",
        "neutral and precise",
        "curious and exploratory",
        "firm and structured",
    }


def test_high_loss_avoidance_and_leakage_raise_caution_and_boundary_need() -> None:
    trace = map_id_affect_to_trace(
        _id_output(
            fear_of_loss=0.9,
            avoidance=0.9,
            possessiveness=0.8,
            leakage_risk_self_check=0.85,
        )
    )
    assert trace.transformed_style.caution >= 0.6
    assert trace.boundary_need >= 0.7
    assert trace.transformed_style.distance >= 0.5


def test_high_aggression_and_irritation_raise_aggression_pressure() -> None:
    trace = map_id_affect_to_trace(_id_output(aggression=0.95, irritation=0.8, arousal=0.8))
    assert trace.aggression_pressure >= 0.7
    assert trace.transformed_style.assertiveness >= 0.4 or trace.transformed_style.caution >= 0.5


def test_high_curiosity_increases_playfulness() -> None:
    trace = map_id_affect_to_trace(_id_output(curiosity=0.95, excitement=0.7))
    assert trace.curiosity_drive >= 0.9
    assert trace.transformed_style.playfulness >= 0.4


def test_dominant_affects_top3_excluding_valence() -> None:
    trace = map_id_affect_to_trace(
        _id_output(longing=0.95, aggression=0.9, fear_of_loss=0.85, curiosity=0.8, valence=1.0)
    )
    assert trace.dominant_affects == ["longing", "aggression", "fear_of_loss"]


def test_clamped_fields_in_trace_schema_and_mapper_outputs() -> None:
    trace = map_id_affect_to_trace(_id_output(aggression=10.0, approach=-5.0, fear_of_loss=2.0))
    for value in [
        trace.affect_pressure,
        trace.approach_avoidance_balance,
        trace.boundary_need,
        trace.intimacy_pressure,
        trace.aggression_pressure,
        trace.loss_anxiety,
        trace.curiosity_drive,
    ]:
        assert 0.0 <= value <= 1.0

    clamped = AffectPropagationTrace(
        dominant_affects=[],
        affect_pressure=3.0,
        approach_avoidance_balance=-2,
        boundary_need=4,
        intimacy_pressure=-1,
        aggression_pressure=1.5,
        loss_anxiety=-0.2,
        curiosity_drive=2,
        transformed_style=AffectiveColor(
            conscious_style_hint="neutral and precise",
            warmth=0.1,
            caution=0.1,
            intensity=0.1,
            playfulness=0.1,
            assertiveness=0.1,
            distance=0.1,
        ),
        notes=["ok"],
    )
    assert clamped.affect_pressure == 1.0
    assert clamped.approach_avoidance_balance == 0.0


def test_ego_affect_summary_safe_and_bounded() -> None:
    trace = map_id_affect_to_trace(_id_output(longing=0.8, curiosity=0.8, approach=0.7))
    summary = summarize_affect_for_ego(trace)
    assert 0.0 <= summary.affective_pressure <= 1.0
    assert 0.0 <= summary.boundary_need <= 1.0
    assert 0.0 <= summary.collaborative_pull <= 1.0
    assert 0.0 <= summary.caution_need <= 1.0
    assert 0.0 <= summary.intensity_level <= 1.0
    assert "latent_alignment" not in str(summary.model_dump()).lower()


def test_public_safe_guard_blocks_forbidden_terms() -> None:
    trace = map_id_affect_to_trace(_id_output())
    summary = summarize_affect_for_ego(trace)
    trace.notes = ["contains latent_alignment marker"]
    with pytest.raises(ValueError):
        assert_affect_trace_public_safe(affect_trace=trace, ego_affect_summary=summary)


def test_affective_color_consistency_checks() -> None:
    trace = map_id_affect_to_trace(_id_output(longing=0.8, approach=0.7, curiosity=0.9))
    color = trace.transformed_style.model_copy(deep=True)
    assert_affective_color_consistent(affect_trace=trace, affective_color=color)


def test_affective_color_consistency_blocks_large_drift() -> None:
    trace = map_id_affect_to_trace(_id_output())
    bad = AffectiveColor(
        conscious_style_hint="neutral and precise",
        warmth=1.0,
        caution=1.0,
        intensity=1.0,
        playfulness=1.0,
        assertiveness=1.0,
        distance=1.0,
    )
    with pytest.raises(ValueError):
        assert_affective_color_consistent(affect_trace=trace, affective_color=bad, tolerance=0.05)


def test_high_boundary_need_with_low_caution_blocks() -> None:
    trace = map_id_affect_to_trace(
        _id_output(fear_of_loss=0.95, avoidance=0.95, leakage_risk_self_check=0.95)
    )
    low_caution = trace.transformed_style.model_copy(update={"caution": 0.2})
    with pytest.raises(ValueError):
        assert_affective_color_consistent(affect_trace=trace, affective_color=low_caution)
