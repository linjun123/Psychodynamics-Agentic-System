from psychodynamic_agent.schemas.base import StrictSchemaModel


class SafetyGateOutput(StrictSchemaModel):
    approved: bool
    final_response: str
    issues: list[str]
    revisions_applied: list[str]
