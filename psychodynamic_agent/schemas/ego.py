from typing import Literal

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
    strategy_id: str
    kind: EgoStrategyKind
    description: str
    predicted_conversation_direction: str
    effect_on_manifest_goal: float
    effect_on_user_benefit: float
    effect_on_trust: float
    ethical_risk: float
    truthfulness_risk: float
    leakage_risk: float
    affect_fit: float
    autonomy_preservation: float
    rationale: str


class EgoRealityPlan(StrictSchemaModel):
    interpreted_user_intent: str
    observed_user_affect: str
    scene_tags: list[str]
    manifest_goal_pressure: float
    affective_style_hint: str
    candidate_strategies: list[EgoCandidateStrategy]
    preferred_strategy_id: str
    prohibited_strategy_ids: list[str]
    notes: list[str]


class SituationSummary(StrictSchemaModel):
    user_intent: str
    user_affect: str
    conversation_direction: str
    opportunities: list[str]
    risks: list[str]


class ResponseOption(StrictSchemaModel):
    option_name: str
    description: str
    effect_on_manifest_goal: float
    effect_on_user_benefit: float
    effect_on_trust: float
    ethical_risk: float
    truthfulness_risk: float
    leakage_risk: float
    recommendation: Literal["avoid", "acceptable", "preferred"]


class EgoRecommendation(StrictSchemaModel):
    preferred_option: str
    tone: str
    include: list[str]
    avoid: list[str]


class EgoReport(StrictSchemaModel):
    situation_summary: SituationSummary
    response_options: list[ResponseOption]
    ego_recommendation: EgoRecommendation
