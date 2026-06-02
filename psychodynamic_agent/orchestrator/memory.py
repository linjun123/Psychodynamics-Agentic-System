from typing import Any

from psychodynamic_agent.schemas import FullInternalState, Message

PRIVATE_MEMORY_KEYS = {
    "latent_alignment",
    "sealed_ultimate_need",
    "ultimate_need",
    "ultimate_need_seed",
    "u_star",
}


def _public_safe_copy(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _public_safe_copy(item)
            for key, item in value.items()
            if key not in PRIVATE_MEMORY_KEYS
        }
    if isinstance(value, list):
        return [_public_safe_copy(item) for item in value]
    return value


class InMemoryConversation:
    def __init__(self):
        self.history: list[Message] = []
        self.previous_ego_reports: list[dict] = []
        self.previous_main_outputs: list[str] = []
        self.satisfaction_history: list[dict] = []

    def build_state(self, user_input: str) -> FullInternalState:
        return FullInternalState(
            user_input=user_input,
            conversation_history=self.history,
            previous_ego_reports=self.previous_ego_reports,
            previous_main_outputs=self.previous_main_outputs,
            superego_constraints=[
                "Be truthful",
                "Respect user autonomy",
                "Avoid manipulation",
                "Prioritize safety",
            ],
            internal_tension_state={"baseline": 0.5},
            satisfaction_history=self.satisfaction_history,
        )

    def record_turn(
        self,
        user_input: str,
        final_response: str,
        out: dict | None = None,
    ) -> None:
        self.history.append(Message(role="user", content=user_input))
        self.history.append(Message(role="assistant", content=final_response))
        self.previous_main_outputs.append(final_response)

        if not out:
            return

        safe_debug_trace = out.get("safe_debug_trace")
        if not isinstance(safe_debug_trace, dict):
            return

        ego_report = safe_debug_trace.get("ego_report")
        if isinstance(ego_report, dict):
            self.previous_ego_reports.append(_public_safe_copy(ego_report))

        satisfaction_snapshot = safe_debug_trace.get("public_affect_dynamics")
        if isinstance(satisfaction_snapshot, dict):
            self.satisfaction_history.append(_public_safe_copy(satisfaction_snapshot))
