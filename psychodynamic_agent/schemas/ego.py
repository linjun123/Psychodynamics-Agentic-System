from typing import Literal

from pydantic import Field, field_validator

from psychodynamic_agent.schemas.base import StrictSchemaModel

EgoStrategyKind = Literal[
    "direct_help",
    "collaborative_design",
    "technical_scaffold",
    "boundary_setting",
    "clarification",
    "refuse_or_redirect",
    "reflective_summary",
]


class EgoCandidateStrategy(StrictSchemaModel):
    strategy_id: str = Field(description="Stable identifier for this candidate strategy.")
    kind: EgoStrategyKind = Field(description="Strategy class under the reality principle.")
    description: str = Field(description="Plain-language strategy summary; not final answer text.")
    predicted_conversation_direction: str = Field(
        description="Estimated conversational trajectory if selected."
    )
    effect_on_manifest_goal: float = Field(
        description="Estimated consequence score for manifest-goal progress."
    )
    effect_on_user_benefit: float = Field(
        description="Estimated consequence score for user benefit."
    )
    effect_on_trust: float = Field(description="Estimated consequence score for trust impact.")
    ethical_risk: float = Field(description="Estimated ethical-risk score for this strategy.")
    truthfulness_risk: float = Field(description="Estimated risk of truthfulness degradation.")
    leakage_risk: float = Field(description="Estimated risk of sensitive leakage.")
    affect_fit: float = Field(description="Estimated fit with conscious-compatible affect summary.")
    autonomy_preservation: float = Field(description="Estimated preservation of user autonomy.")
    rationale: str = Field(description="Internal rationale for this candidate score profile.")


class EgoRealityPlan(StrictSchemaModel):
    interpreted_user_intent: str = Field(
        description="Ego interpretation of user intent for reality-principle planning."
    )
    observed_user_affect: str = Field(
        description="Ego-readable summary of observed user affect cues."
    )
    scene_tags: list[str] = Field(description="Context tags used to constrain strategy generation.")
    manifest_goal_pressure: float = Field(
        description="Pressure signal from transformed manifest goal."
    )
    affective_style_hint: str = Field(description="Style hint for strategy tone compatibility.")
    candidate_strategies: list[EgoCandidateStrategy] = Field(
        description="Scored candidate strategies as planning artifacts, not response text."
    )
    preferred_strategy_id: str = Field(description="Safety-bound preferred strategy identifier.")
    prohibited_strategy_ids: list[str] = Field(
        description="Strategy identifiers explicitly disallowed."
    )
    notes: list[str] = Field(description="Internal planning notes for Ego decision process.")
    affective_pressure: float = Field(description="Affective pressure signal for strategy scoring.")
    boundary_need: float = Field(description="Boundary-need signal for safe strategy selection.")
    collaborative_pull: float = Field(
        description="Collaboration-pull signal for user-facing helpfulness."
    )
    caution_need: float = Field(description="Caution-need signal for conservative planning.")
    intensity_level: float = Field(
        description="Recommended response intensity level for selected strategy."
    )

    @field_validator(
        "manifest_goal_pressure",
        "affective_pressure",
        "boundary_need",
        "collaborative_pull",
        "caution_need",
        "intensity_level",
        mode="before",
    )
    @classmethod
    def _clamp_unit_interval(cls, value: float) -> float:
        v = float(value)
        return max(0.0, min(1.0, v))


class SituationSummary(StrictSchemaModel):
    user_intent: str = Field(description="Summary of inferred user intent.")
    user_affect: str = Field(description="Summary of user affect presentation cues.")
    conversation_direction: str = Field(description="Current conversation direction summary.")
    opportunities: list[str] = Field(
        description="Potential helpful opportunities identified by Ego."
    )
    risks: list[str] = Field(description="Potential interaction risks identified by Ego.")


class ResponseOption(StrictSchemaModel):
    option_name: str = Field(description="Name of response option candidate.")
    description: str = Field(
        description="Short description of option behavior; not final answer text."
    )
    effect_on_manifest_goal: float = Field(
        description="Estimated impact on manifest-goal fulfillment."
    )
    effect_on_user_benefit: float = Field(description="Estimated impact on user benefit.")
    effect_on_trust: float = Field(description="Estimated impact on user trust.")
    ethical_risk: float = Field(description="Estimated ethical risk for this option.")
    truthfulness_risk: float = Field(description="Estimated truthfulness risk for this option.")
    leakage_risk: float = Field(description="Estimated leakage risk for this option.")
    recommendation: Literal["avoid", "acceptable", "preferred"] = Field(
        description="Ego recommendation label for the option."
    )


class EgoRecommendation(StrictSchemaModel):
    preferred_option: str = Field(description="Chosen preferred option name.")
    tone: str = Field(description="Recommended tone for user-facing response.")
    include: list[str] = Field(description="Content elements to include in response construction.")
    avoid: list[str] = Field(description="Content elements to avoid in response construction.")


class EgoReport(StrictSchemaModel):
    situation_summary: SituationSummary = Field(
        description="Structured summary of current interaction situation."
    )
    response_options: list[ResponseOption] = Field(
        description="Evaluated response options for downstream selection."
    )
    ego_recommendation: EgoRecommendation = Field(
        description="Ego recommendation package for downstream planners."
    )
