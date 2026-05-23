from pydantic import BaseModel


class ManifestGoal(BaseModel):
    description: str
    urgency: float
    flexibility: float
    ethical_legitimacy: float
    leakage_risk: float


class AffectiveColor(BaseModel):
    conscious_style_hint: str
    warmth: float
    caution: float
    intensity: float
    playfulness: float
    assertiveness: float
    distance: float


class CensorAOutput(BaseModel):
    manifest_goal: ManifestGoal
    affective_color: AffectiveColor
    allowed_satisfaction_paths: list[str]
    forbidden_satisfaction_paths: list[str]


class ConsciousEgoReport(BaseModel):
    ego_pressure: str
    acceptable_satisfaction_paths: list[str]
    unacceptable_paths: list[str]
    recommended_tone: str
    recommended_content: list[str]
    risk_flags: list[str]
