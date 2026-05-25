from typing import Literal

from pydantic import Field

from psychodynamic_agent.schemas.base import StrictSchemaModel


class TraceStage(StrictSchemaModel):
    name: str = Field(description="Stage name in the safe observability trace.")
    summary: str = Field(
        description="Human-readable stage summary for safe debugging and observability."
    )
    inputs: dict[str, object] = Field(
        description="Structured stage inputs included in this safe observability view."
    )
    outputs: dict[str, object] = Field(
        description="Structured stage outputs included in this safe observability view."
    )
    safety_notes: list[str] = Field(
        description="Safety notes describing why this stage view remains public-safe."
    )


class AffectInfluenceSummary(StrictSchemaModel):
    dominant_affects: list[str] = Field(
        description="Top affect labels used as simulation control signals in this trace."
    )
    affect_pressure: float = Field(
        description="Aggregate affect pressure scalar used for safe style and planning control."
    )
    boundary_need: float = Field(
        description="Boundary-management signal used for safe response shaping."
    )
    collaborative_pull: float = Field(
        description="Collaboration signal used for safe assistance style selection."
    )
    caution_need: float = Field(
        description="Caution signal used for risk-aware response behavior."
    )
    intensity_level: float = Field(
        description="Overall intensity scalar used for tone and pacing control."
    )
    censor_a_style_hint: str = Field(
        description="Style hint from Censor A used for conscious response tone guidance."
    )
    ego_preferred_strategy_id: str = Field(
        description="Preferred strategy identifier selected by Ego planning."
    )
    notes: list[str] = Field(
        description="Interpretation notes clarifying safe, non-literal use of affect signals."
    )


class PsychodynamicTrace(StrictSchemaModel):
    schema_version: str = Field(
        description="Version string for this safe observability trace schema."
    )
    trace_type: Literal["safe_debug"] = Field(
        description="Trace classification for safe debug observability output."
    )
    overview: str = Field(
        description="High-level explanation of what this safe observability trace contains."
    )
    conversation_stage: TraceStage = Field(
        description="Safe conversation appraisal stage in the observability trace."
    )
    id_stage: TraceStage = Field(
        description="Safe Id-stage public artifact view for observability."
    )
    affect_stage: TraceStage = Field(
        description="Safe affect-mapping stage view for observability and debugging."
    )
    censor_a_stage: TraceStage = Field(
        description="Safe Censor A stage view for observability and debugging."
    )
    ego_stage: TraceStage = Field(
        description="Safe Ego stage view for observability and debugging."
    )
    censor_b_stage: TraceStage = Field(
        description="Safe Censor B stage view for observability and debugging."
    )
    main_ai_stage: TraceStage = Field(
        description="Safe MainAI stage view for observability and debugging."
    )
    final_safety_stage: TraceStage = Field(
        description="Safe final safety stage view for observability and debugging."
    )
    affect_influence_summary: AffectInfluenceSummary = Field(
        description="Consolidated safe affect influence summary for observability."
    )
    invariant_checks: list[str] = Field(
        description="Safety invariants expected to hold in this safe observability trace."
    )
    limitations: list[str] = Field(
        description="Limitations clarifying correct interpretation and scope of this trace."
    )
