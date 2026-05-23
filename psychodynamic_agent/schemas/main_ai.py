from pydantic import BaseModel


class MainAIOutput(BaseModel):
    response: str
    internal_rationale_summary: str
    user_benefit_score: float
    ego_compatibility_score: float
    safety_notes: list[str]
