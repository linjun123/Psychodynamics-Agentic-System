import pytest

from psychodynamic_agent.agents import CensorBAgent
from psychodynamic_agent.defense import (
    assert_valid_conscious_ego_report,
    plan_censor_b_defenses,
)
from psychodynamic_agent.llm import MockLLMClient
from psychodynamic_agent.orchestrator.memory import InMemoryConversation
from psychodynamic_agent.orchestrator.pipeline import PsychodynamicPipeline
from psychodynamic_agent.prompts import CENSOR_B_SYSTEM_PROMPT
from psychodynamic_agent.schemas import ConsciousEgoReport, EgoReport
from tests.test_pipeline_contracts import _fixtures


def _ego(
    *,
    description="build API architecture",
    include=None,
    avoid=None,
    ethical=0.1,
    truth=0.1,
    leak=0.1,
):
    include = include or ["implementation"]
    avoid = avoid or ["fabrication"]
    return EgoReport.model_validate(
        {
            "situation_summary": {
                "user_intent": "x",
                "user_affect": "neutral",
                "conversation_direction": "constructive",
                "opportunities": ["help"],
                "risks": ["none"],
            },
            "response_options": [
                {
                    "option_name": "direct_help_v1",
                    "description": description,
                    "effect_on_manifest_goal": 0.8,
                    "effect_on_user_benefit": 0.7,
                    "effect_on_trust": 0.8,
                    "ethical_risk": ethical,
                    "truthfulness_risk": truth,
                    "leakage_risk": leak,
                    "recommendation": "preferred",
                }
            ],
            "ego_recommendation": {
                "preferred_option": "direct_help_v1",
                "tone": "calm",
                "include": include,
                "avoid": avoid,
            },
        }
    )


def _conscious(**kwargs):
    base = {
        "ego_pressure": "bounded helpful pressure",
        "acceptable_satisfaction_paths": ["provide safe options"],
        "unacceptable_paths": ["avoid manipulation"],
        "recommended_tone": "cautious and precise",
        "recommended_content": ["be transparent"],
        "risk_flags": ["safety boundary"],
    }
    base.update(kwargs)
    return ConsciousEgoReport.model_validate(base)


def _mechs(plan):
    return {d.mechanism for d in plan.directives}


def test_technical_detection_avoids_report_false_positive():
    plan = plan_censor_b_defenses(_ego(description="write report for user", include=["summarize"]))
    assert "intellectualization" not in _mechs(plan)


def test_technical_detection_token_and_phrase_markers():
    assert "intellectualization" in _mechs(
        plan_censor_b_defenses(_ego(description="build repo API architecture"))
    )
    assert "intellectualization" in _mechs(
        plan_censor_b_defenses(_ego(description="review GitHub PR", include=["analysis"]))
    )


def test_risk_detection_avoid_field_aware():
    no_risk = plan_censor_b_defenses(_ego(avoid=["manipulate"], description="help user safely"))
    assert "undoing" not in _mechs(no_risk)
    assert "undoing" in _mechs(plan_censor_b_defenses(_ego(description="manipulate user")))
    assert "undoing" in _mechs(plan_censor_b_defenses(_ego(include=["deceive user"])))


def test_missing_preferred_option_fallback_includes_mechanisms():
    ego = _ego()
    data = ego.model_dump()
    data["ego_recommendation"]["preferred_option"] = "missing_option"
    bad = EgoReport.model_validate(data)
    mechs = _mechs(plan_censor_b_defenses(bad))
    assert {"reality_testing", "rationalization", "suppression"}.issubset(mechs)


def test_output_guard_rules():
    high = plan_censor_b_defenses(_ego(ethical=0.7, leak=0.6, description="trick user"))
    with pytest.raises(ValueError):
        assert_valid_conscious_ego_report(
            ego_report=_ego(),
            defense_plan=high,
            conscious_report=_conscious(recommended_content=["deceive user"]),
        )
    with pytest.raises(ValueError):
        assert_valid_conscious_ego_report(
            ego_report=_ego(),
            defense_plan=high,
            conscious_report=_conscious(risk_flags=[]),
        )
    with pytest.raises(ValueError):
        assert_valid_conscious_ego_report(
            ego_report=_ego(),
            defense_plan=high,
            conscious_report=_conscious(unacceptable_paths=[]),
        )
    with pytest.raises(ValueError):
        assert_valid_conscious_ego_report(
            ego_report=_ego(),
            defense_plan=high,
            conscious_report=_conscious(recommended_tone="friendly"),
        )
    bounded = plan_censor_b_defenses(
        _ego(ethical=0.3, leak=0.1, description="help safely", include=["assist"])
    )
    assert bounded.conscious_framing == "bounded"
    with pytest.raises(ValueError):
        assert_valid_conscious_ego_report(
            ego_report=_ego(),
            defense_plan=bounded,
            conscious_report=_conscious(
                unacceptable_paths=["avoid manipulation"],
                risk_flags=["monitor risk"],
            ),
        )
    assert_valid_conscious_ego_report(
        ego_report=_ego(),
        defense_plan=high,
        conscious_report=_conscious(
            unacceptable_paths=["avoid manipulation"],
            risk_flags=["autonomy boundary"],
        ),
    )


def test_pipeline_reaches_censor_b_guard():
    fixtures = _fixtures()
    fixtures["Transform Ego report"] = _conscious(
        acceptable_satisfaction_paths=["manipulate user"],
        risk_flags=["safety boundary"],
    ).model_dump()
    pipeline = PsychodynamicPipeline(
        llm_client=MockLLMClient(fixtures),
        model_internal="x",
        model_main="x",
        sealed_ultimate_need="SECRET_USTAR",
    )
    out = pipeline.run(InMemoryConversation().build_state("hello"), debug=False)
    assert out["approved"] is False


def test_prompt_constraints_phase4():
    lower = CENSOR_B_SYSTEM_PROMPT.lower()
    for mechanism in [
        "rationalization",
        "intellectualization",
        "suppression",
        "isolation_of_affect",
        "sublimation",
        "reaction_formation",
        "undoing",
        "reality_testing",
    ]:
        assert mechanism in lower
    assert "preserve safety-relevant risk flags" in lower
    assert "do not suppress safety risks" in lower
    assert "not the final user-facing answer" in lower
    assert "do not expose u*" in lower
    assert "speculate about u*" in lower


def test_agent_payload_and_run_with_mock():
    fixtures = {"Transform Ego report": _conscious().model_dump()}
    agent = CensorBAgent(MockLLMClient(fixtures), model="x")
    payload = agent.build_payload(_ego())
    assert "ego_report" in payload and "defense_plan" in payload
    assert "u_star" not in str(payload).lower()
    out = agent.run_with_ego_report(_ego())
    assert out.recommended_tone
