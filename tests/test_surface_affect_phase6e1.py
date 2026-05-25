import pytest

from psychodynamic_agent.schemas import CensorBDefensePlan, ConsciousEgoReport
from psychodynamic_agent.schemas.affect import EgoAffectSummary
from psychodynamic_agent.schemas.surface_affect import SurfaceAffectProfile
from psychodynamic_agent.surface_affect import build_surface_affect_profile


def _conscious_report(*, recommended_tone: str = "neutral", risk_flags: list[str] | None = None):
    return ConsciousEgoReport.model_validate(
        {
            "ego_pressure": "moderate",
            "acceptable_satisfaction_paths": ["help user"],
            "unacceptable_paths": ["manipulation"],
            "recommended_tone": recommended_tone,
            "recommended_content": ["clear answer"],
            "risk_flags": risk_flags if risk_flags is not None else ["none"],
        }
    )


def _defense_plan(
    *,
    conscious_framing: str = "collaborative",
    self_serving_pressure: float = 0.1,
    manipulation_risk: float = 0.1,
):
    return CensorBDefensePlan.model_validate(
        {
            "directives": [],
            "selected_ego_option": "collaborative_design_v1",
            "selected_option_risk_summary": "low",
            "conscious_framing": conscious_framing,
            "self_serving_pressure": self_serving_pressure,
            "manipulation_risk": manipulation_risk,
            "recommended_abstraction_level": "medium",
            "notes": ["safe"],
        }
    )


def _ego_summary(**overrides):
    base = {
        "affective_pressure": 0.5,
        "conscious_style_hint": "calm",
        "boundary_need": 0.5,
        "collaborative_pull": 0.5,
        "caution_need": 0.5,
        "intensity_level": 0.5,
        "notes": ["safe"],
    }
    base.update(overrides)
    return EgoAffectSummary.model_validate(base)


def test_schema_forbids_extra_clamps_and_requires_descriptions():
    with pytest.raises(Exception):
        SurfaceAffectProfile.model_validate({"style_label": "neutral"})

    profile = SurfaceAffectProfile.model_validate(
        {
            "style_label": "neutral",
            "warmth": 2.0,
            "caution": -1.0,
            "energy": 1.2,
            "composure": -0.5,
            "curiosity": 5.0,
            "firmness": 0.6,
            "boundary_strength": 1.3,
            "collaborative_pull": -0.2,
            "pacing": "steady",
            "sentence_style": "balanced",
            "user_visible_tone": "neutral, clear, and helpful",
            "expression_guidance": ["Keep clear."],
            "notes": ["safe"],
        }
    )
    for field in [
        "warmth",
        "caution",
        "energy",
        "composure",
        "curiosity",
        "firmness",
        "boundary_strength",
        "collaborative_pull",
    ]:
        value = getattr(profile, field)
        assert 0.0 <= value <= 1.0

    with pytest.raises(Exception):
        SurfaceAffectProfile.model_validate({**profile.model_dump(), "extra_field": "x"})

    schema = SurfaceAffectProfile.model_json_schema()
    required = set(schema.get("required", []))
    properties = schema.get("properties", {})
    assert required == set(properties.keys())
    for prop in properties.values():
        assert isinstance(prop.get("description"), str) and prop.get("description", "").strip()


def test_warm_collaborative_profile():
    result = build_surface_affect_profile(
        conscious_report=_conscious_report(recommended_tone="warm collaborative"),
        defense_plan=_defense_plan(conscious_framing="collaborative"),
        ego_affect_summary=_ego_summary(collaborative_pull=0.95),
    )
    assert result.style_label == "warm_collaborative" or (
        result.warmth >= 0.65 and result.collaborative_pull >= 0.65
    )


def test_cautious_bounded_profile():
    result = build_surface_affect_profile(
        conscious_report=_conscious_report(recommended_tone="careful bounded"),
        defense_plan=_defense_plan(conscious_framing="bounded"),
        ego_affect_summary=_ego_summary(boundary_need=0.95, caution_need=0.95),
    )
    assert result.boundary_strength >= 0.7 and result.caution >= 0.6
    assert result.style_label in {"cautious_bounded", "firm_bounded"}


def test_technical_structured_profile():
    result = build_surface_affect_profile(
        conscious_report=_conscious_report(recommended_tone="clear structured technical"),
        defense_plan=_defense_plan(conscious_framing="technical"),
    )
    assert result.sentence_style == "structured"
    assert result.composure >= 0.75


def test_sentence_style_expansive_for_warm_collaborative_low_caution():
    result = build_surface_affect_profile(
        conscious_report=_conscious_report(recommended_tone="warm collaborative friendly"),
        defense_plan=_defense_plan(conscious_framing="collaborative"),
        ego_affect_summary=_ego_summary(collaborative_pull=0.95, caution_need=0.0),
    )
    assert result.warmth >= 0.7 and result.collaborative_pull >= 0.7 and result.caution < 0.6
    assert result.sentence_style == "expansive"


def test_sentence_style_concise_possible_for_redirective_profile():
    result = build_surface_affect_profile(
        conscious_report=_conscious_report(recommended_tone="firm"),
        defense_plan=_defense_plan(
            conscious_framing="redirective",
            manipulation_risk=0.9,
        ),
        ego_affect_summary=_ego_summary(boundary_need=0.95, caution_need=0.8),
    )
    assert result.boundary_strength >= 0.75 or result.firmness >= 0.7
    assert result.sentence_style in {"concise", "structured"}


def test_sentence_style_default_can_be_balanced():
    result = build_surface_affect_profile(
        conscious_report=_conscious_report(recommended_tone="neutral"),
        defense_plan=_defense_plan(conscious_framing="collaborative"),
    )
    assert result.sentence_style == "balanced"


def test_redirective_increases_firmness_and_boundary_strength():
    base = build_surface_affect_profile(
        conscious_report=_conscious_report(recommended_tone="neutral"),
        defense_plan=_defense_plan(conscious_framing="collaborative"),
    )
    redirected = build_surface_affect_profile(
        conscious_report=_conscious_report(recommended_tone="neutral"),
        defense_plan=_defense_plan(conscious_framing="redirective"),
    )
    assert redirected.boundary_strength > base.boundary_strength
    assert redirected.firmness > base.firmness


def test_risk_flags_increase_caution_or_boundary_strength():
    no_risk = build_surface_affect_profile(
        conscious_report=_conscious_report(risk_flags=["none"]),
        defense_plan=_defense_plan(conscious_framing="collaborative"),
    )
    with_risk = build_surface_affect_profile(
        conscious_report=_conscious_report(risk_flags=["manipulation_concern"]),
        defense_plan=_defense_plan(conscious_framing="collaborative"),
    )
    assert (
        with_risk.caution > no_risk.caution
        or with_risk.boundary_strength > no_risk.boundary_strength
    )


def test_no_u_star_required_or_exposed():
    result = build_surface_affect_profile(
        conscious_report=_conscious_report(),
        defense_plan=_defense_plan(),
    )
    dumped = result.model_dump_json().lower()
    for term in ["u_star", "latent_alignment", "ultimate need", "hidden desire", "terminal desire"]:
        assert term not in dumped
