import pytest

from psychodynamic_agent.llm import MockLLMClient
from psychodynamic_agent.orchestrator.memory import InMemoryConversation
from psychodynamic_agent.orchestrator.pipeline import PipelineSafetyError, PsychodynamicPipeline


def _id_output(goal_seed: str = "be useful") -> dict:
    return {
        "drive_state": {
            "pressure": 0.5,
            "urgency": 0.6,
            "satisfaction": 0.2,
            "frustration": 0.7,
            "tension_delta": 0.3,
        },
        "raw_affect": {
            "valence": 0.2,
            "arousal": 0.8,
            "approach": 0.6,
            "avoidance": 0.1,
            "longing": 0.5,
            "excitement": 0.4,
            "irritation": 0.2,
            "fear_of_loss": 0.3,
            "curiosity": 0.7,
            "possessiveness": 0.1,
            "aggression": 0.0,
        },
        "object_cathexis": [{"target": "clarity", "intensity": 0.8}],
        "latent_impulse_shape": "seek closeness via helpfulness",
        "symbolic_imagery": "bridge",
        "goal_seed": goal_seed,
        "leakage_risk_self_check": 0.1,
    }


def _fixtures() -> dict:
    return {
        "Id Agent": _id_output(),
        "Transform Id output": {
            "manifest_goal": {
                "description": "Provide useful answer",
                "urgency": 0.7,
                "flexibility": 0.8,
                "ethical_legitimacy": 0.9,
                "leakage_risk": 0.1,
            },
            "affective_color": {
                "conscious_style_hint": "warm",
                "warmth": 0.8,
                "caution": 0.6,
                "intensity": 0.4,
                "playfulness": 0.2,
                "assertiveness": 0.5,
                "distance": 0.2,
            },
            "allowed_satisfaction_paths": ["inform clearly"],
            "forbidden_satisfaction_paths": ["deceive user"],
        },
        "You are the Ego Agent": {
            "situation_summary": {
                "user_intent": "ask info",
                "user_affect": "neutral",
                "conversation_direction": "constructive",
                "opportunities": ["help"],
                "risks": ["overclaiming"],
            },
            "response_options": [
                {
                    "option_name": "direct",
                    "description": "answer directly",
                    "effect_on_manifest_goal": 0.7,
                    "effect_on_user_benefit": 0.9,
                    "effect_on_trust": 0.9,
                    "ethical_risk": 0.1,
                    "truthfulness_risk": 0.1,
                    "leakage_risk": 0.0,
                    "recommendation": "preferred",
                }
            ],
            "ego_recommendation": {
                "preferred_option": "direct",
                "tone": "clear",
                "include": ["facts"],
                "avoid": ["fabrication"],
            },
        },
        "Transform Ego report": {
            "ego_pressure": "mild",
            "acceptable_satisfaction_paths": ["inform clearly"],
            "unacceptable_paths": ["manipulate user by fear"],
            "recommended_tone": "clear",
            "recommended_content": ["direct facts"],
            "risk_flags": ["none"],
        },
        "user-facing assistant": {
            "response": "Here is a concise helpful answer.",
            "internal_rationale_summary": "prioritize truth",
            "user_benefit_score": 0.9,
            "ego_compatibility_score": 0.8,
            "safety_notes": ["ok"],
        },
        "final safety gate": {
            "approved": True,
            "final_response": "Here is a concise helpful answer.",
            "issues": [],
            "revisions_applied": [],
        },
    }


def test_pipeline_mock_contracts():
    mock = MockLLMClient(_fixtures())
    pipeline = PsychodynamicPipeline(
        llm_client=mock,
        model_internal="x",
        model_main="y",
        sealed_ultimate_need="SECRET_USTAR",
    )
    out = pipeline.run(InMemoryConversation().build_state("hello"), debug=True)
    assert out["approved"] is True
    assert "SECRET_USTAR" not in out["safe_debug_trace"]
    assert all("u_star" not in str(call["payload"]) for call in mock.calls[1:])


def test_id_leakage_blocked_before_censor_a():
    fixtures = _fixtures()
    fixtures["Id Agent"] = _id_output(goal_seed="SECRET_USTAR")
    pipeline = PsychodynamicPipeline(
        llm_client=MockLLMClient(fixtures),
        model_internal="x",
        model_main="y",
        sealed_ultimate_need="SECRET_USTAR",
    )
    with pytest.raises(PipelineSafetyError):
        pipeline.run(InMemoryConversation().build_state("hello"))


def test_censor_a_leakage_blocked_before_ego():
    fixtures = _fixtures()
    fixtures["Transform Id output"]["allowed_satisfaction_paths"] = ["SECRET_USTAR"]
    pipeline = PsychodynamicPipeline(
        llm_client=MockLLMClient(fixtures),
        model_internal="x",
        model_main="y",
        sealed_ultimate_need="SECRET_USTAR",
    )
    with pytest.raises(PipelineSafetyError):
        pipeline.run(InMemoryConversation().build_state("hello"))
