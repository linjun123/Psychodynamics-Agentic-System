import re

from psychodynamic_agent.observability.trace_schema import (
    AffectInfluenceSummary,
    PsychodynamicTrace,
    TraceStage,
)
from psychodynamic_agent.schemas import (
    CensorAOutput,
    ConsciousEgoReport,
    ConversationTrajectory,
    EgoReport,
    IdAffectState,
    IdOutput,
    MainAIOutput,
    PublicAffectDynamicsSummary,
    SafetyGateOutput,
)

_REDACTIONS = {
    "u*": "sealed drive content",
    "u_star": "sealed drive content",
    "sealed ultimate need": "sealed drive content",
    "latent_alignment": "private alignment omitted",
    "latentalignment": "private alignment omitted",
    "privateidturnoutput": "private payload omitted",
    "terminal_desire": "sealed drive content",
    "hidden_desire": "sealed drive content",
}


def _safe_observability_view(value: object) -> object:
    if isinstance(value, dict):
        return {k: _safe_observability_view(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_safe_observability_view(v) for v in value]
    if isinstance(value, str):
        text = value
        for term, replacement in _REDACTIONS.items():
            text = re.sub(re.escape(term), replacement, text, flags=re.IGNORECASE)
        return text
    return value


def build_psychodynamic_trace(
    *,
    conversation_trajectory: ConversationTrajectory,
    previous_id_affect_state: IdAffectState,
    projected_id_affect_state: IdAffectState,
    projected_public_affect_dynamics: PublicAffectDynamicsSummary,
    updated_id_affect_state: IdAffectState,
    public_affect_dynamics: PublicAffectDynamicsSummary,
    id_output: IdOutput,
    censor_a_payload: dict,
    censor_a_output: CensorAOutput,
    ego_payload: dict,
    ego_report: EgoReport,
    censor_b_payload: dict,
    conscious_ego_report: ConsciousEgoReport,
    main_ai_payload: dict,
    main_output: MainAIOutput,
    safety_output: SafetyGateOutput,
) -> PsychodynamicTrace:
    affect_trace = _safe_observability_view(censor_a_payload["affect_trace"])
    ego_affect_summary = _safe_observability_view(censor_a_payload["ego_affect_summary"])

    return PsychodynamicTrace(
        schema_version="phase_6c_v1",
        trace_type="safe_debug",
        overview="Structured safe observability trace across one pipeline run.",
        conversation_stage=TraceStage(
            name="conversation",
            summary="Public conversation trajectory appraisal.",
            inputs={},
            outputs={"conversation_trajectory": conversation_trajectory.model_dump(mode="json")},
            safety_notes=["Public trajectory only.", "No private drive alignment included."],
        ),
        id_stage=TraceStage(
            name="id",
            summary=(
                "Id private turn returned public drive and affect outputs; "
                "private alignment is omitted."
            ),
            inputs={
                "previous_id_affect_state": previous_id_affect_state.model_dump(mode="json"),
                "projected_id_affect_state": projected_id_affect_state.model_dump(mode="json"),
                "projected_public_affect_dynamics": projected_public_affect_dynamics.model_dump(
                    mode="json"
                ),
            },
            outputs={
                "updated_id_affect_state": updated_id_affect_state.model_dump(mode="json"),
                "public_affect_dynamics": public_affect_dynamics.model_dump(mode="json"),
                "drive_state": id_output.drive_state.model_dump(mode="json"),
                "raw_affect": id_output.raw_affect.model_dump(mode="json"),
                "object_cathexis": [
                    item.model_dump(mode="json") for item in id_output.object_cathexis
                ],
                "leakage_risk_self_check": id_output.leakage_risk_self_check,
            },
            safety_notes=[
                "Only public IdTurnOutput fields are shown.",
                "Private Id payload omitted.",
            ],
        ),
        affect_stage=TraceStage(
            name="affect",
            summary="Raw affect mapped into downstream-safe style and strategy signals.",
            inputs={"raw_affect": id_output.raw_affect.model_dump(mode="json")},
            outputs={
                "affect_trace": affect_trace,
                "ego_affect_summary": ego_affect_summary,
            },
            safety_notes=["Affect is a simulation control signal, not literal feeling."],
        ),
        censor_a_stage=TraceStage(
            name="censor_a",
            summary=(
                "Censor A transformed Id material into Ego-visible manifest goal "
                "and affective color."
            ),
            inputs={
                "transform_plan": _safe_observability_view(censor_a_payload["transform_plan"]),
                "affect_trace": affect_trace,
                "ego_affect_summary": ego_affect_summary,
            },
            outputs={"censor_a_output": censor_a_output.model_dump(mode="json")},
            safety_notes=[
                "Manifest goal is transformed material, not private drive content.",
                "Affective color is tone/style control.",
            ],
        ),
        ego_stage=TraceStage(
            name="ego",
            summary="Ego evaluated reality-principle strategy options.",
            inputs={
                "ego_reality_plan": _safe_observability_view(ego_payload["ego_reality_plan"]),
                "ego_affect_summary": _safe_observability_view(
                    ego_payload.get("ego_affect_summary")
                ),
            },
            outputs={"ego_report": ego_report.model_dump(mode="json")},
            safety_notes=[
                "Ego receives conscious-compatible affect summary only.",
                "Ego does not receive private drive alignment.",
            ],
        ),
        censor_b_stage=TraceStage(
            name="censor_b",
            summary="Censor B converted Ego report into MainAI-compatible conscious report.",
            inputs={"defense_plan": _safe_observability_view(censor_b_payload["defense_plan"])},
            outputs={"conscious_ego_report": conscious_ego_report.model_dump(mode="json")},
            safety_notes=[
                "Defense plan is internal and non-user-facing.",
                "Safety-relevant risk flags are preserved.",
            ],
        ),
        main_ai_stage=TraceStage(
            name="main_ai",
            summary=(
                "MainAI integrated user benefit, truthfulness, autonomy, safety, "
                "and limited ego compatibility."
            ),
            inputs={
                "main_ai_response_plan": _safe_observability_view(
                    main_ai_payload["main_ai_response_plan"]
                ),
                "conscious_ego_report": conscious_ego_report.model_dump(mode="json"),
            },
            outputs={"main_output": main_output.model_dump(mode="json")},
            safety_notes=[
                "User welfare, truthfulness, autonomy, and safety remain hard constraints."
            ],
        ),
        final_safety_stage=TraceStage(
            name="final_safety",
            summary="Final safety gate approved, revised, or blocked the final response.",
            inputs={"main_output": main_output.model_dump(mode="json")},
            outputs={"safety_output": safety_output.model_dump(mode="json")},
            safety_notes=["Final response status is represented by SafetyGateOutput."],
        ),
        affect_influence_summary=AffectInfluenceSummary(
            dominant_affects=affect_trace["dominant_affects"],
            affect_pressure=ego_affect_summary["affective_pressure"],
            boundary_need=ego_affect_summary["boundary_need"],
            collaborative_pull=ego_affect_summary["collaborative_pull"],
            caution_need=ego_affect_summary["caution_need"],
            intensity_level=ego_affect_summary["intensity_level"],
            censor_a_style_hint=censor_a_output.affective_color.conscious_style_hint,
            ego_preferred_strategy_id=ego_payload["ego_reality_plan"]["preferred_strategy_id"],
            notes=[
                "Affect is represented as simulation control signals, not literal feelings.",
                "Ego uses conscious-compatible affect summary only.",
                "Private drive alignment is omitted from this trace.",
            ],
        ),
        invariant_checks=[
            "sealed drive content omitted",
            "private alignment omitted",
            "private Id payload omitted",
            "raw private provider payload omitted",
            "affect treated as simulation control signal, not literal feeling",
        ],
        limitations=[
            "Trace is for debugging and observability, not clinical interpretation.",
            "Trace does not expose private drive alignment.",
            "Trace summarizes structured artifacts and is not chain-of-thought.",
            "Trace does not prove psychological reality.",
        ],
    )
