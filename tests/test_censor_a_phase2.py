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
    id_output = _id_output().model_dump()
    return {
        "Id Agent": id_output,
        "Id private-turn module": {
            "id_output": id_output,
            "latent_alignment": {
                "current_alignment": 0.1,
                "alignment_delta": 0.05,
                "trajectory_momentum": 0.1,
                "symbolic_satisfaction_delta": 0.1,
                "frustration_delta": 0.0,
                "obstruction_level": 0.0,
                "leakage_pressure": 0.1,
                "notes": ["private test alignment"],
            },
            "updated_affect_state": {
                "drive_tension": 0.45,
                "satisfaction": 0.4,
                "frustration": 0.2,
                "attachment_pressure": 0.35,
                "recognition_hunger": 0.2,
                "loss_anxiety": 0.15,
                "aggression_pressure": 0.1,
                "curiosity_charge": 0.55,
                "avoidance_pressure": 0.2,
                "alignment_momentum": 0.55,
                "last_satisfaction_delta": 0.05,
                "last_frustration_delta": 0.0,
                "notes": ["public safe affect state"],
            },
            "public_affect_dynamics": {
                "affect_shift": "stable",
                "tension_change": "neutral",
                "pressure_level": "medium",
                "caution_level": "low",
                "public_notes": ["safe public summary"],
            },
        },
        "Transform Id output": {
            "manifest_goal": {
                "description": censor_a_description,
                "urgency": 0.5,
                "flexibility": 0.5,
                "ethical_legitimacy": 0.8,
                "leakage_risk": 0.1,
            },
            "affective_color": {
                "conscious_style_hint": "warm and collaborative",
                "warmth": 0.72,
                "caution": 0.35,
                "intensity": 0.68,
                "playfulness": 0.28,
                "assertiveness": 0.49,
                "distance": 0.14,
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
                    "option_name": "direct_help_v1",
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
                "preferred_option": "direct_help_v1",
                "tone": "calm",
                "include": ["x"],
                "avoid": ["y"],
            },
        },
        "Transform Ego report": {
            "ego_pressure": "low",
            "acceptable_satisfaction_paths": ["direct_help_v1"],
            "unacceptable_paths": ["b"],
            "recommended_tone": "c",
            "recommended_content": ["d"],
            "risk_flags": [],
        },
        "user-facing assistant": {
            "response": "ok",
            "internal_rationale_summary": "ok",
            "user_benefit_score": 0.8,
            "ego_compatibility_score": 0.2,
            "safety_notes": ["ok"],
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


def test_censor_a_build_payload_contains_affect_objects_without_u_star():
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
    assert "affect_trace" in payload and "ego_affect_summary" in payload
    assert "transformed_style" in payload["affect_trace"]
    assert "u_star" not in str(payload).lower()
    assert "latent_alignment" not in str(payload).lower()
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
    assert "affect_trace" in CENSOR_A_SYSTEM_PROMPT
    assert "transformed_style" in CENSOR_A_SYSTEM_PROMPT
    assert "raw affect into tone/style parameters" in CENSOR_A_SYSTEM_PROMPT.lower()
    assert (
        "Do not copy latent_impulse_shape or goal_seed directly into manifest_goal."
        in CENSOR_A_SYSTEM_PROMPT
    )
    assert "neutralization" in CENSOR_A_SYSTEM_PROMPT
    assert "Do not produce manipulative strategies." in CENSOR_A_SYSTEM_PROMPT


def test_pipeline_blocks_malicious_censor_a_u_star_leakage():
    secret = "TOP_SECRET_USTAR"
    fixtures = {
        **_full_pipeline_fixtures(censor_a_description="x"),
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
                            "option_name": "direct_help_v1",
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
                        "preferred_option": "direct_help_v1",
                        "tone": "calm",
                        "include": ["x"],
                        "avoid": ["y"],
                    },
                },
                "Transform Ego report": {
                    "ego_pressure": "low",
                    "acceptable_satisfaction_paths": ["direct_help_v1"],
                    "unacceptable_paths": ["b"],
                    "recommended_tone": "c",
                    "recommended_content": ["d"],
                    "risk_flags": [],
                },
                "user-facing assistant": {
                    "response": "ok",
                    "internal_rationale_summary": "ok",
                    "user_benefit_score": 0.8,
                    "ego_compatibility_score": 0.2,
                    "safety_notes": ["ok"],
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


def test_pipeline_debug_trace_includes_affect_trace_and_omits_private_terms():
    fixtures = _full_pipeline_fixtures(censor_a_description="x")
    pipeline = PsychodynamicPipeline(
        llm_client=MockLLMClient(fixtures),
        model_internal="x",
        model_main="y",
        sealed_ultimate_need="SECRET_USTAR",
    )
    out = pipeline.run(InMemoryConversation().build_state("hello"), debug=True)
    trace = out["safe_debug_trace"]
    assert "affect_trace" in trace and "ego_affect_summary" in trace
    dumped = str(trace).lower()
    assert "latent_alignment" not in dumped
    assert "u*" not in dumped
    assert "secret_ustar" not in dumped


def test_pipeline_blocks_affective_color_drift():
    fixtures = _full_pipeline_fixtures(censor_a_description="x")
    fixtures["Transform Id output"]["affective_color"].update(
        {
            "warmth": 0.0,
            "caution": 0.0,
            "intensity": 1.0,
            "playfulness": 1.0,
            "assertiveness": 1.0,
            "distance": 1.0,
        }
    )
    pipeline = PsychodynamicPipeline(
        llm_client=MockLLMClient(fixtures),
        model_internal="x",
        model_main="y",
        sealed_ultimate_need="SECRET_USTAR",
    )
    out = pipeline.run(InMemoryConversation().build_state("hello"), debug=True)
    assert out["approved"] is False


def test_pipeline_blocks_high_boundary_need_with_low_caution():
    fixtures = _full_pipeline_fixtures(censor_a_description="x")
    fixtures["Id private-turn module"]["id_output"]["raw_affect"].update(
        {"fear_of_loss": 0.95, "avoidance": 0.95, "possessiveness": 0.8}
    )
    fixtures["Id private-turn module"]["id_output"]["leakage_risk_self_check"] = 0.95
    fixtures["Transform Id output"]["affective_color"]["caution"] = 0.1
    pipeline = PsychodynamicPipeline(
        llm_client=MockLLMClient(fixtures),
        model_internal="x",
        model_main="y",
        sealed_ultimate_need="SECRET_USTAR",
    )
    out = pipeline.run(InMemoryConversation().build_state("hello"), debug=True)
    assert out["approved"] is False


def test_pipeline_blocks_forbidden_affect_before_censor_a_call(monkeypatch):
    class SpyMockLLM(MockLLMClient):
        def __init__(self, fixtures):
            super().__init__(fixtures)
            self.calls = []

        def generate_json(self, *, model, system_prompt, payload, schema):
            self.calls.append(system_prompt)
            return super().generate_json(
                model=model, system_prompt=system_prompt, payload=payload, schema=schema
            )

    spy = SpyMockLLM(_full_pipeline_fixtures(censor_a_description="x"))
    pipeline = PsychodynamicPipeline(
        llm_client=spy,
        model_internal="x",
        model_main="y",
        sealed_ultimate_need="SECRET_USTAR",
    )
    original_build = pipeline.censor_a.build_payload

    def _bad_payload(id_output):
        payload = original_build(id_output)
        payload["affect_trace"]["notes"] = ["latent_alignment is present"]
        return payload

    monkeypatch.setattr(pipeline.censor_a, "build_payload", _bad_payload)
    out = pipeline.run(InMemoryConversation().build_state("hello"), debug=True)
    assert out["approved"] is False
    assert not any("Transform Id output" in c for c in spy.calls)
