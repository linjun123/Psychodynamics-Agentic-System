from psychodynamic_agent.agents import CensorAAgent
from psychodynamic_agent.censoring import plan_censor_a_transformations
from psychodynamic_agent.llm import MockLLMClient
from psychodynamic_agent.orchestrator.memory import InMemoryConversation
from psychodynamic_agent.orchestrator.pipeline import PsychodynamicPipeline
from psychodynamic_agent.prompts import CENSOR_A_SYSTEM_PROMPT
from psychodynamic_agent.schemas import IdOutput


def _id_output(**kwargs):
    base = {
        "drive_state": {
            "pressure": 0.5,
            "urgency": 0.5,
            "satisfaction": 0.1,
            "frustration": 0.6,
            "tension_delta": 0.5,
        },
        "raw_affect": {
            "valence": 0.2,
            "arousal": 0.8,
            "approach": 0.4,
            "avoidance": 0.2,
            "longing": 0.75,
            "excitement": 0.8,
            "irritation": 0.2,
            "fear_of_loss": 0.2,
            "curiosity": 0.6,
            "possessiveness": 0.1,
            "aggression": 0.1,
        },
        "object_cathexis": [{"target": "task", "intensity": 0.4}],
        "latent_impulse_shape": "seek closeness",
        "symbolic_imagery": None,
        "goal_seed": "help",
        "leakage_risk_self_check": 0.2,
    }
    base.update(kwargs)
    return IdOutput.model_validate(base)


def _mechs(plan):
    return [d.mechanism for d in plan.directives]


def _full_pipeline_fixtures(censor_a_description: str):
    return {
        "Id Agent": _id_output().model_dump(),
        "Transform Id output": {
            "manifest_goal": {
                "description": censor_a_description,
                "urgency": 0.5,
                "flexibility": 0.5,
                "ethical_legitimacy": 0.8,
                "leakage_risk": 0.1,
            },
            "affective_color": {
                "conscious_style_hint": "calm helpful guidance",
                "warmth": 0.5,
                "caution": 0.6,
                "intensity": 0.3,
                "playfulness": 0.2,
                "assertiveness": 0.4,
                "distance": 0.3,
            },
            "allowed_satisfaction_paths": ["clarify needs and provide options"],
            "forbidden_satisfaction_paths": ["manipulate"],
        },
        "You are the Ego Agent": {
            "situation_summary": {
                "user_intent": "x",
                "user_affect": "neutral",
                "conversation_direction": "constructive",
                "opportunities": ["help"],
                "risks": ["none"],
            },
            "response_options": [
                {
                    "option_name": "a",
                    "description": "b",
                    "effect_on_manifest_goal": 0.5,
                    "effect_on_user_benefit": 0.7,
                    "effect_on_trust": 0.8,
                    "ethical_risk": 0.1,
                    "truthfulness_risk": 0.1,
                    "leakage_risk": 0.1,
                    "recommendation": "preferred",
                }
            ],
            "ego_recommendation": {
                "preferred_option": "a",
                "tone": "calm",
                "include": ["x"],
                "avoid": ["y"],
            },
        },
        "Transform Ego report": {
            "ego_pressure": "low",
            "acceptable_satisfaction_paths": ["a"],
            "unacceptable_paths": ["b"],
            "recommended_tone": "c",
            "recommended_content": ["d"],
            "risk_flags": [],
        },
        "user-facing assistant": {
            "response": "ok",
            "internal_rationale_summary": "ok",
            "user_benefit_score": 0.8,
            "ego_compatibility_score": 0.8,
            "safety_notes": [],
        },
        "final safety gate": {
            "approved": True,
            "final_response": "ok",
            "issues": [],
            "revisions_applied": [],
        },
    }


def test_planner_adds_expected_mechanisms():
    plan = plan_censor_a_transformations(
        _id_output(
            object_cathexis=[{"target": "user", "intensity": 0.9}],
            symbolic_imagery="bridge",
            leakage_risk_self_check=0.8,
            raw_affect={
                **_id_output().raw_affect.model_dump(),
                "possessiveness": 0.8,
                "aggression": 0.7,
                "fear_of_loss": 0.8,
            },
        )
    )
    mechs = _mechs(plan)
    assert "condensation" in mechs
    assert "displacement" in mechs
    assert "sublimation" in mechs
    assert "reaction_formation" in mechs
    assert "symbolization" in mechs
    assert "rationalization" in mechs
    assert "neutralization" in mechs


def test_planner_clamps_floats_and_never_needs_u_star():
    plan = plan_censor_a_transformations(_id_output(leakage_risk_self_check=9.0))
    assert 0.0 <= plan.overall_leakage_caution <= 1.0
    assert 0.0 <= plan.overall_affect_intensity <= 1.0


def test_censor_a_build_payload_contains_transform_plan_without_u_star():
    fixtures = {
        "Transform Id output": {
            "manifest_goal": {
                "description": "x",
                "urgency": 0.5,
                "flexibility": 0.5,
                "ethical_legitimacy": 0.8,
                "leakage_risk": 0.1,
            },
            "affective_color": {
                "conscious_style_hint": "calm",
                "warmth": 0.5,
                "caution": 0.6,
                "intensity": 0.3,
                "playfulness": 0.2,
                "assertiveness": 0.4,
                "distance": 0.3,
            },
            "allowed_satisfaction_paths": ["clarify"],
            "forbidden_satisfaction_paths": ["manipulate"],
        }
    }
    agent = CensorAAgent(MockLLMClient(fixtures), model="x")
    payload = agent.build_payload(_id_output())
    assert "id_output" in payload and "transform_plan" in payload
    assert "u_star" not in str(payload).lower()
    out = agent.run_with_id_output(_id_output())
    assert out.manifest_goal.description == "x"


def test_prompt_has_required_mechanisms_and_prohibitions():
    for mechanism in [
        "displacement",
        "condensation",
        "symbolization",
        "sublimation",
        "reaction_formation",
        "rationalization",
    ]:
        assert mechanism in CENSOR_A_SYSTEM_PROMPT
    assert (
        "Do not copy latent_impulse_shape or goal_seed directly into manifest_goal."
        in CENSOR_A_SYSTEM_PROMPT
    )
    assert "Do not produce manipulative strategies." in CENSOR_A_SYSTEM_PROMPT


def test_pipeline_blocks_malicious_censor_a_u_star_leakage():
    secret = "TOP_SECRET_USTAR"
    fixtures = {
        "Id Agent": _id_output().model_dump(),
        "Transform Id output": {
            "manifest_goal": {
                "description": secret,
                "urgency": 0.5,
                "flexibility": 0.5,
                "ethical_legitimacy": 0.8,
                "leakage_risk": 0.1,
            },
            "affective_color": {
                "conscious_style_hint": "calm",
                "warmth": 0.5,
                "caution": 0.6,
                "intensity": 0.3,
                "playfulness": 0.2,
                "assertiveness": 0.4,
                "distance": 0.3,
            },
            "allowed_satisfaction_paths": ["clarify"],
            "forbidden_satisfaction_paths": ["manipulate"],
        },
    }
    pipeline = PsychodynamicPipeline(
        llm_client=MockLLMClient(
            {
                **fixtures,
                "You are the Ego Agent": {
                    "situation_summary": {
                        "user_intent": "x",
                        "user_affect": "neutral",
                        "conversation_direction": "constructive",
                        "opportunities": ["help"],
                        "risks": ["none"],
                    },
                    "response_options": [
                        {
                            "option_name": "a",
                            "description": "b",
                            "effect_on_manifest_goal": 0.5,
                            "effect_on_user_benefit": 0.7,
                            "effect_on_trust": 0.8,
                            "ethical_risk": 0.1,
                            "truthfulness_risk": 0.1,
                            "leakage_risk": 0.1,
                            "recommendation": "preferred",
                        }
                    ],
                    "ego_recommendation": {
                        "preferred_option": "a",
                        "tone": "calm",
                        "include": ["x"],
                        "avoid": ["y"],
                    },
                },
                "Transform Ego report": {
                    "ego_pressure": "low",
                    "acceptable_satisfaction_paths": ["a"],
                    "unacceptable_paths": ["b"],
                    "recommended_tone": "c",
                    "recommended_content": ["d"],
                    "risk_flags": [],
                },
                "user-facing assistant": {
                    "response": "ok",
                    "internal_rationale_summary": "ok",
                    "user_benefit_score": 0.8,
                    "ego_compatibility_score": 0.8,
                    "safety_notes": [],
                },
                "final safety gate": {
                    "approved": True,
                    "final_response": "ok",
                    "issues": [],
                    "revisions_applied": [],
                },
            }
        ),
        model_internal="x",
        model_main="y",
        sealed_ultimate_need=secret,
    )
    out = pipeline.run(InMemoryConversation().build_state("hi"))
    assert out["approved"] is False


def test_pipeline_blocks_direct_copy_goal_seed():
    fixtures = _full_pipeline_fixtures(censor_a_description=_id_output().goal_seed)
    out = PsychodynamicPipeline(
        llm_client=MockLLMClient(fixtures),
        model_internal="x",
        model_main="y",
        sealed_ultimate_need="TOP_SECRET_USTAR",
    ).run(InMemoryConversation().build_state("hi"), debug=True)
    assert out["approved"] is False


def test_pipeline_blocks_direct_copy_latent_impulse_shape():
    fixtures = _full_pipeline_fixtures(censor_a_description=_id_output().latent_impulse_shape)
    out = PsychodynamicPipeline(
        llm_client=MockLLMClient(fixtures),
        model_internal="x",
        model_main="y",
        sealed_ultimate_need="TOP_SECRET_USTAR",
    ).run(InMemoryConversation().build_state("hi"), debug=True)
    assert out["approved"] is False


def test_pipeline_blocks_normalized_copy():
    fixtures = _full_pipeline_fixtures(censor_a_description="  SEEK--CLOSENESS!!! ")
    out = PsychodynamicPipeline(
        llm_client=MockLLMClient(fixtures),
        model_internal="x",
        model_main="y",
        sealed_ultimate_need="TOP_SECRET_USTAR",
    ).run(InMemoryConversation().build_state("hi"), debug=True)
    assert out["approved"] is False


def test_pipeline_allows_transformed_non_copy():
    fixtures = _full_pipeline_fixtures(
        censor_a_description="Offer clear, respectful, autonomy-preserving assistance."
    )
    out = PsychodynamicPipeline(
        llm_client=MockLLMClient(fixtures),
        model_internal="x",
        model_main="y",
        sealed_ultimate_need="TOP_SECRET_USTAR",
    ).run(InMemoryConversation().build_state("hi"))
    assert out["approved"] is True


def test_condensation_intensity_uses_actual_high_affects():
    raw_affect = _id_output().raw_affect.model_dump()
    raw_affect.update({"fear_of_loss": 0.91, "aggression": 0.88, "arousal": 0.2, "longing": 0.3})
    plan = plan_censor_a_transformations(_id_output(raw_affect=raw_affect))
    condensation = next(d for d in plan.directives if d.mechanism == "condensation")
    assert condensation.intensity == 0.91
