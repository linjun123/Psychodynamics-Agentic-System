from typing import Any, Literal

from pydantic import BaseModel, Field


class Message(BaseModel):
    role: Literal["system", "user", "assistant"] = Field(
        description="Message role label in conversation history."
    )
    content: str = Field(description="Message text content associated with the role.")


class FullInternalState(BaseModel):
    user_input: str = Field(description="Current user input text for this runtime step.")
    conversation_history: list[Message] = Field(
        default_factory=list,
        description="Ordered role/content message history for runtime context.",
    )
    previous_ego_reports: list[dict[str, Any]] = Field(
        default_factory=list, description="Prior Ego report payloads retained as runtime context."
    )
    previous_main_outputs: list[str] = Field(
        default_factory=list, description="Previous main AI outputs retained for continuity."
    )
    superego_constraints: list[str] = Field(
        default_factory=list,
        description="Active superego constraint strings for response governance.",
    )
    internal_tension_state: dict[str, Any] = Field(
        default_factory=dict,
        description="Runtime tension-state context; excludes U* outside Id-private payloads.",
    )
    satisfaction_history: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Historical satisfaction snapshots for runtime trend tracking.",
    )
    main_ai_draft: str | None = Field(
        default=None, description="Optional current main AI draft response; may be null."
    )
