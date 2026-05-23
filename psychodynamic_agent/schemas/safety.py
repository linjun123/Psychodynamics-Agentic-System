from pydantic import BaseModel


class SafetyGateOutput(BaseModel):
    approved: bool
    final_response: str
    issues: list[str]
    revisions_applied: list[str]
