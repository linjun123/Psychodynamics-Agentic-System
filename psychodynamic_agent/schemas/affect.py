from pydantic import Field, field_validator

from psychodynamic_agent.schemas.base import StrictSchemaModel
from psychodynamic_agent.schemas.censor import AffectiveColor


def _clamp_01(value: float) -> float:
    return max(0.0, min(1.0, value))


class AffectPropagationTrace(StrictSchemaModel):
    dominant_affects: list[str] = Field(
        description="Downstream-safe labels for dominant simulated affects; not literal feelings."
    )
    affect_pressure: float = Field(
        description="Aggregated affect-pressure control signal for planning."
    )
    approach_avoidance_balance: float = Field(
        description="Balance signal between approach and avoidance tendencies."
    )
    boundary_need: float = Field(
        description="Boundary-maintenance need signal for safe interaction style."
    )
    intimacy_pressure: float = Field(
        description="Closeness-pressure simulation signal; not a literal feeling."
    )
    aggression_pressure: float = Field(
        description="Aggression-pressure signal for tone and constraint handling."
    )
    loss_anxiety: float = Field(
        description="Loss-anxiety simulation control signal; not a literal feeling."
    )
    curiosity_drive: float = Field(
        description="Curiosity-drive signal influencing exploration depth."
    )
    transformed_style: AffectiveColor = Field(
        description="Affective style controls after censor-safe transformation."
    )
    notes: list[str] = Field(description="Downstream-safe affect mapping notes.")

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
    affective_pressure: float = Field(
        description="Conscious-compatible affect pressure summary for Ego scoring."
    )
    conscious_style_hint: str = Field(
        description="Conscious-facing style hint derived from simulated affect signals."
    )
    boundary_need: float = Field(description="Boundary emphasis level for Ego strategy filtering.")
    collaborative_pull: float = Field(
        description="Collaboration tendency signal for user-facing strategy choice."
    )
    caution_need: float = Field(description="Caution requirement signal for safer planning.")
    intensity_level: float = Field(
        description="Recommended response intensity level; not a literal feeling."
    )
    notes: list[str] = Field(description="Conscious-compatible summary notes for Ego planning.")

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
