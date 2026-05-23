from typing import Any, Literal

from pydantic import BaseModel, Field


class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class FullInternalState(BaseModel):
    user_input: str
    conversation_history: list[Message] = Field(default_factory=list)
    previous_ego_reports: list[dict[str, Any]] = Field(default_factory=list)
    previous_main_outputs: list[str] = Field(default_factory=list)
    superego_constraints: list[str] = Field(default_factory=list)
    internal_tension_state: dict[str, Any] = Field(default_factory=dict)
    satisfaction_history: list[dict[str, Any]] = Field(default_factory=list)
    main_ai_draft: str | None = None
