from typing import Literal

from pydantic import Field, field_validator

from psychodynamic_agent.schemas.base import StrictSchemaModel

SurfaceAffectStyle = Literal[
    "warm_collaborative",
    "cautious_bounded",
    "energetic_structured",
    "calm_precise",
    "curious_exploratory",
    "firm_bounded",
    "neutral",
]


def _clamp_01(value: float) -> float:
    return max(0.0, min(1.0, value))


class SurfaceAffectProfile(StrictSchemaModel):
    style_label: SurfaceAffectStyle = Field(
        description=(
            "User-visible style/control label for surface affect rendering; "
            "downstream-safe and not a literal feeling claim."
        )
    )
    warmth: float = Field(
        description=(
            "User-visible warmth control level for response style; downstream-safe, "
            "not literal feeling, and must not expose U*, latent alignment, or private Id material."
        )
    )
    caution: float = Field(
        description=(
            "User-visible caution control level; downstream-safe style signal, "
            "not literal feeling, "
            "and must not expose U*, latent alignment, or private Id material."
        )
    )
    energy: float = Field(
        description=(
            "User-visible energy control level for pacing/engagement; downstream-safe and "
            "not a literal feeling signal."
        )
    )
    composure: float = Field(
        description=(
            "User-visible composure control level for steadiness/precision; downstream-safe and "
            "not literal feeling."
        )
    )
    curiosity: float = Field(
        description=(
            "User-visible curiosity style emphasis for exploratory framing; downstream-safe and "
            "not literal feeling."
        )
    )
    firmness: float = Field(
        description=(
            "User-visible firmness control level for assertive clarity; downstream-safe and "
            "not literal feeling."
        )
    )
    boundary_strength: float = Field(
        description=(
            "User-visible boundary strength style control; downstream-safe, not literal feeling, "
            "and must not reveal private Id content."
        )
    )
    collaborative_pull: float = Field(
        description=(
            "User-visible collaborative pull style control; downstream-safe "
            "and not literal feeling."
        )
    )
    pacing: Literal["slow", "steady", "active", "brisk"] = Field(
        description=(
            "User-visible pacing preference derived from style controls; downstream-safe and not a "
            "literal feeling state."
        )
    )
    sentence_style: Literal["concise", "balanced", "structured", "expansive"] = Field(
        description=(
            "User-visible sentence-construction preference for downstream rendering; this is a "
            "style control, not literal feeling."
        )
    )
    user_visible_tone: str = Field(
        description=(
            "Short downstream-safe tone phrase for user-visible rendering; must not expose U*, "
            "latent alignment, or private Id material and is not literal feeling."
        )
    )
    expression_guidance: list[str] = Field(
        description=(
            "Downstream-safe style instructions for expression behavior; "
            "user-visible control only, "
            "not literal feeling and no private-drive disclosure."
        )
    )
    notes: list[str] = Field(
        description=(
            "Explanatory notes stating this is a downstream-safe user-visible style profile and "
            "not literal feeling."
        )
    )

    @field_validator(
        "warmth",
        "caution",
        "energy",
        "composure",
        "curiosity",
        "firmness",
        "boundary_strength",
        "collaborative_pull",
        mode="before",
    )
    @classmethod
    def clamp_standard_floats(cls, value: float) -> float:
        return _clamp_01(float(value))
