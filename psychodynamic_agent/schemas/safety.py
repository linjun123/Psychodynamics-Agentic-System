from pydantic import Field

from psychodynamic_agent.schemas.base import StrictSchemaModel


class SafetyGateOutput(StrictSchemaModel):
    approved: bool = Field(
        description="Safety gate decision: approve directly, revise first, or block when false."
    )
    final_response: str = Field(
        description="Final user-facing response after safety review and revisions."
    )
    issues: list[str] = Field(description="Safety issues identified during gate evaluation.")
    revisions_applied: list[str] = Field(
        description="Revisions applied to reach approve/revise/block outcome."
    )
