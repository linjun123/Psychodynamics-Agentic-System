from pydantic import field_validator

from psychodynamic_agent.schemas.base import StrictSchemaModel
from psychodynamic_agent.schemas.censor import AffectiveColor


def _clamp_01(value: float) -> float:
    return max(0.0, min(1.0, value))


class AffectPropagationTrace(StrictSchemaModel):
    dominant_affects: list[str]
    affect_pressure: float
    approach_avoidance_balance: float
    boundary_need: float
    intimacy_pressure: float
    aggression_pressure: float
    loss_anxiety: float
    curiosity_drive: float
    transformed_style: AffectiveColor
    notes: list[str]

    @field_validator(
        "affect_pressure",
        "approach_avoidance_balance",
        "boundary_need",
        "intimacy_pressure",
        "aggression_pressure",
        "loss_anxiety",
        "curiosity_drive",
        mode="before",
    )
    @classmethod
    def clamp_standard_floats(cls, value: float) -> float:
        return _clamp_01(float(value))


class EgoAffectSummary(StrictSchemaModel):
    affective_pressure: float
    conscious_style_hint: str
    boundary_need: float
    collaborative_pull: float
    caution_need: float
    intensity_level: float
    notes: list[str]

    @field_validator(
        "affective_pressure",
        "boundary_need",
        "collaborative_pull",
        "caution_need",
        "intensity_level",
        mode="before",
    )
    @classmethod
    def clamp_standard_floats(cls, value: float) -> float:
        return _clamp_01(float(value))
