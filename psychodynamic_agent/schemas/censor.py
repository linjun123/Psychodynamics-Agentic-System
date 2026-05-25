from typing import Literal

from pydantic import Field

from psychodynamic_agent.schemas.base import StrictSchemaModel


class ManifestGoal(StrictSchemaModel):
    description: str = Field(description="Ego-visible transformed goal description, not raw U*.")
    urgency: float = Field(description="Urgency level for the transformed manifest goal.")
    flexibility: float = Field(description="Allowed flexibility for pursuing the manifest goal.")
    ethical_legitimacy: float = Field(
        description="Estimated ethical legitimacy of the transformed goal framing."
    )
    leakage_risk: float = Field(
        description="Estimated risk that transformed goal framing could leak sensitive intent."
    )


class AffectiveColor(StrictSchemaModel):
    conscious_style_hint: str = Field(
        description="Style/tone hint for downstream user-facing response construction."
    )
    warmth: float = Field(description="Warmth control parameter for response style.")
    caution: float = Field(description="Caution control parameter for conservative phrasing.")
    intensity: float = Field(description="Intensity control parameter for expressive strength.")
    playfulness: float = Field(
        description="Playfulness control parameter for lighter tone selection."
    )
    assertiveness: float = Field(
        description="Assertiveness control parameter for directive strength."
    )
    distance: float = Field(
        description="Interpersonal distance control parameter for boundary setting."
    )


class CensorAOutput(StrictSchemaModel):
    manifest_goal: ManifestGoal = Field(
        description="Ego-visible transformed goal package for downstream planning."
    )
    affective_color: AffectiveColor = Field(
        description="Tone-control parameters safe for downstream modules."
    )
    allowed_satisfaction_paths: list[str] = Field(
        description="Permitted satisfaction paths after censor filtering."
    )
    forbidden_satisfaction_paths: list[str] = Field(
        description="Blocked satisfaction paths due to safety or policy pressure."
    )


class ConsciousEgoReport(StrictSchemaModel):
    ego_pressure: str = Field(description="Conscious-friendly summary of current ego pressure.")
    acceptable_satisfaction_paths: list[str] = Field(
        description="Satisfaction paths approved for conscious planning."
    )
    unacceptable_paths: list[str] = Field(description="Paths rejected by censor constraints.")
    recommended_tone: str = Field(
        description="Recommended user-facing tone based on safety and fit."
    )
    recommended_content: list[str] = Field(
        description="Recommended content elements for user-facing response."
    )
    risk_flags: list[str] = Field(description="Safety-relevant risk flags for conscious review.")


TransformMechanism = Literal[
    "displacement",
    "condensation",
    "symbolization",
    "sublimation",
    "reaction_formation",
    "rationalization",
    "neutralization",
]


class CensorATransformDirective(StrictSchemaModel):
    mechanism: TransformMechanism = Field(
        description="Named transformation mechanism used as an internal planning artifact."
    )
    intensity: float = Field(description="Strength of this transformation directive.")
    target_dimension: Literal["goal", "affect", "allowed_paths", "forbidden_paths"] = Field(
        description="Target dimension modified by this directive."
    )
    instruction: str = Field(description="Internal transformation instruction; non-user-facing.")
    rationale: str = Field(
        description="Internal rationale for applying this transformation directive."
    )


class CensorATransformPlan(StrictSchemaModel):
    directives: list[CensorATransformDirective] = Field(
        description="Ordered internal transform directives for Censor A."
    )
    overall_leakage_caution: float = Field(
        description="Global leakage-caution level across transform plan."
    )
    overall_affect_intensity: float = Field(
        description="Global affect intensity target after transformation."
    )
    recommended_goal_abstraction: Literal["low", "medium", "high"] = Field(
        description="Recommended abstraction level for goal representation."
    )
    notes: list[str] = Field(description="Internal non-user-facing notes for transform planning.")


DefenseMechanism = Literal[
    "rationalization",
    "intellectualization",
    "suppression",
    "isolation_of_affect",
    "sublimation",
    "reaction_formation",
    "undoing",
    "reality_testing",
]


class CensorBDefenseDirective(StrictSchemaModel):
    mechanism: DefenseMechanism = Field(
        description="Selected defense mechanism for internal response shaping."
    )
    intensity: float = Field(description="Strength of defense application.")
    source_field: str = Field(description="Source field in prior planning output being adjusted.")
    target_field: Literal[
        "ego_pressure",
        "acceptable_satisfaction_paths",
        "unacceptable_paths",
        "recommended_tone",
        "recommended_content",
        "risk_flags",
    ] = Field(description="Target conscious-report field to modify with this defense.")
    instruction: str = Field(description="Internal defense instruction; not user-facing.")
    rationale: str = Field(description="Internal rationale for defense selection.")


class CensorBDefensePlan(StrictSchemaModel):
    directives: list[CensorBDefenseDirective] = Field(
        description="Internal defense directives applied to conscious report."
    )
    selected_ego_option: str = Field(
        description="Identifier of the selected ego option to carry forward."
    )
    selected_option_risk_summary: str = Field(
        description="Risk summary for the selected ego option."
    )
    conscious_framing: Literal[
        "collaborative", "technical", "bounded", "cautious", "reflective", "redirective"
    ] = Field(description="Conscious framing style selected for downstream-safe presentation.")
    self_serving_pressure: float = Field(
        description="Estimated self-serving pressure in selected framing."
    )
    manipulation_risk: float = Field(
        description="Safety-relevant risk flag for manipulative pattern drift."
    )
    recommended_abstraction_level: Literal["low", "medium", "high"] = Field(
        description="Recommended abstraction level for conscious communication."
    )
    notes: list[str] = Field(description="Internal non-user-facing notes for defense planning.")
