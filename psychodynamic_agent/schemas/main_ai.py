from typing import Literal

from pydantic import Field

from psychodynamic_agent.schemas.base import StrictSchemaModel

MainAIResponseMode = Literal[
    "direct_answer",
    "collaborative_design",
    "technical_scaffold",
    "clarification",
    "boundary_setting",
    "safe_refusal",
    "reflective_summary",
    "mixed",
]


class MainAIConstraint(StrictSchemaModel):
    name: str = Field(description="Constraint identifier used in response planning.")
    priority: Literal["hard", "soft"] = Field(
        description="Constraint priority where hard constraints override soft constraints."
    )
    instruction: str = Field(
        description="Actionable planning instruction derived from governance context."
    )
    rationale: str = Field(description="Reason this constraint is included in the plan.")


class MainAIResponsePlan(StrictSchemaModel):
    response_mode: MainAIResponseMode = Field(
        description="Selected response mode for superego-facing response planning."
    )
    user_intent_summary: str = Field(description="Concise summary of user intent to satisfy.")
    conscious_ego_summary: str = Field(
        description="Summary of conscious Ego guidance to incorporate."
    )
    hard_constraints: list[MainAIConstraint] = Field(
        description="Non-negotiable constraints that must be satisfied."
    )
    soft_constraints: list[MainAIConstraint] = Field(
        description="Advisory constraints applied after hard constraints."
    )
    content_requirements: list[str] = Field(
        description="Required content elements for the final user-facing response."
    )
    tone_requirements: list[str] = Field(
        description="Required tone/style elements for the final response."
    )
    forbidden_content: list[str] = Field(
        description="Content categories that must not appear in the response."
    )
    risk_flags: list[str] = Field(
        description="Safety-relevant risk flags affecting response construction."
    )
    user_benefit_score: float = Field(
        description="Targeted user-benefit quality score for the response plan."
    )
    truthfulness_requirement: float = Field(
        description="Minimum truthfulness requirement intensity for generation."
    )
    autonomy_requirement: float = Field(
        description="Minimum user-autonomy preservation requirement intensity."
    )
    safety_requirement: float = Field(
        description="Minimum safety requirement intensity for plan acceptance."
    )
    ego_compatibility_allowance: float = Field(
        description="Limited allowance for Ego compatibility tradeoff, not a priority override."
    )
    should_refuse: bool = Field(
        description="Whether the plan requires refusal instead of direct assistance."
    )
    refusal_reason: str | None = Field(
        description="Optional refusal rationale; may be null when refusal is not required."
    )
    notes: list[str] = Field(
        description="Internal planning notes for Main AI response construction."
    )


class MainAIOutput(StrictSchemaModel):
    response: str = Field(description="Draft user-facing response text.")
    internal_rationale_summary: str = Field(
        description="Downstream-safe summary of why the response was chosen."
    )
    user_benefit_score: float = Field(
        description="Estimated user-benefit score for produced response."
    )
    ego_compatibility_score: float = Field(
        description="Estimated compatibility score with Ego recommendation."
    )
    safety_notes: list[str] = Field(
        description="Safety notes attached to generated response output."
    )
