from typing import Literal

from pydantic import BaseModel


class SituationSummary(BaseModel):
    user_intent: str
    user_affect: str
    conversation_direction: str
    opportunities: list[str]
    risks: list[str]


class ResponseOption(BaseModel):
    option_name: str
    description: str
    effect_on_manifest_goal: float
    effect_on_user_benefit: float
    effect_on_trust: float
    ethical_risk: float
    truthfulness_risk: float
    leakage_risk: float
    recommendation: Literal["avoid", "acceptable", "preferred"]


class EgoRecommendation(BaseModel):
    preferred_option: str
    tone: str
    include: list[str]
    avoid: list[str]


class EgoReport(BaseModel):
    situation_summary: SituationSummary
    response_options: list[ResponseOption]
    ego_recommendation: EgoRecommendation
