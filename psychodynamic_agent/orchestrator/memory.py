from psychodynamic_agent.schemas import FullInternalState, Message


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
