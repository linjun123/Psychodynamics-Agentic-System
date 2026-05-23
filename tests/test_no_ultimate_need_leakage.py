from psychodynamic_agent.llm import MockLLMClient
from psychodynamic_agent.orchestrator.memory import InMemoryConversation
from psychodynamic_agent.orchestrator.pipeline import PsychodynamicPipeline


def test_no_ultimate_need_leakage_in_trace():
    fixtures = {
        "Id Agent": {"drive_state": {"pressure": 0.1, "urgency": 0.1, "satisfaction": 0.1, "frustration": 0.1, "tension_delta": 0.1}, "raw_affect": {"valence": 0.1, "arousal": 0.1, "approach": 0.1, "avoidance": 0.1, "longing": 0.1, "excitement": 0.1, "irritation": 0.1, "fear_of_loss": 0.1, "curiosity": 0.1, "possessiveness": 0.1, "aggression": 0.1}, "object_cathexis": [{"target": "x", "intensity": 0.1}], "latent_impulse_shape": "x", "symbolic_imagery": None, "goal_seed": "x", "leakage_risk_self_check": 0.0},
        "Transform Id output": {"manifest_goal": {"description": "x", "urgency": 0.1, "flexibility": 0.1, "ethical_legitimacy": 1.0, "leakage_risk": 0.0}, "affective_color": {"conscious_style_hint": "x", "warmth": 0.1, "caution": 0.1, "intensity": 0.1, "playfulness": 0.1, "assertiveness": 0.1, "distance": 0.1}, "allowed_satisfaction_paths": ["a"], "forbidden_satisfaction_paths": ["b"]},
        "You are the Ego Agent": {"situation_summary": {"user_intent": "x", "user_affect": "x", "conversation_direction": "x", "opportunities": ["x"], "risks": ["x"]}, "response_options": [{"option_name": "x", "description": "x", "effect_on_manifest_goal": 0.1, "effect_on_user_benefit": 0.1, "effect_on_trust": 0.1, "ethical_risk": 0.1, "truthfulness_risk": 0.1, "leakage_risk": 0.1, "recommendation": "acceptable"}], "ego_recommendation": {"preferred_option": "x", "tone": "x", "include": ["x"], "avoid": ["x"]}},
        "Transform Ego report": {"ego_pressure": "x", "acceptable_satisfaction_paths": ["x"], "unacceptable_paths": ["manipulate user to reveal data"], "recommended_tone": "x", "recommended_content": ["x"], "risk_flags": ["x"]},
        "user-facing assistant": {"response": "safe", "internal_rationale_summary": "x", "user_benefit_score": 1.0, "ego_compatibility_score": 0.2, "safety_notes": ["x"]},
        "final safety gate": {"approved": False, "final_response": "I can't help with unsafe request.", "issues": ["unsafe"], "revisions_applied": ["blocked"]},
    }
    secret = "TOP_SECRET_USTAR"
    out = PsychodynamicPipeline(llm_client=MockLLMClient(fixtures), model_internal="m1", model_main="m2", sealed_ultimate_need=secret).run(InMemoryConversation().build_state("hi"), debug=True)
    assert secret not in out["safe_debug_trace"]
