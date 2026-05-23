from psychodynamic_agent.schemas.base import StrictSchemaModel


class MainAIOutput(StrictSchemaModel):
    response: str
    internal_rationale_summary: str
    user_benefit_score: float
    ego_compatibility_score: float
    safety_notes: list[str]
