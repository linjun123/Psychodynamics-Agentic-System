from psychodynamic_agent.agents.base import BaseLLMAgent
from psychodynamic_agent.id_dynamics import (
    appraise_conversation_trajectory,
    initial_id_affect_state,
)
from psychodynamic_agent.prompts import ID_SYSTEM_PROMPT
from psychodynamic_agent.schemas import (
    ConversationTrajectory,
    FullInternalState,
    IdAffectState,
    IdOutput,
    IdTurnOutput,
    PrivateIdTurnOutput,
)


class IdAgent(BaseLLMAgent):
    def __init__(self, llm_client, model: str, sealed_ultimate_need: str):
        super().__init__(llm_client=llm_client, model=model, system_prompt=ID_SYSTEM_PROMPT, schema=PrivateIdTurnOutput)
        self._sealed_ultimate_need = sealed_ultimate_need

    def run_turn(self, *, state: FullInternalState, previous_affect_state: IdAffectState, conversation_trajectory: ConversationTrajectory) -> IdTurnOutput:
        payload = {"state": state.model_dump(), "u_star": self._sealed_ultimate_need, "previous_affect_state": previous_affect_state.model_dump(), "conversation_trajectory": conversation_trajectory.model_dump()}
        private = self.run(payload)
        return IdTurnOutput(id_output=private.id_output, updated_affect_state=private.updated_affect_state, public_affect_dynamics=private.public_affect_dynamics)

    def run_with_state(self, state: FullInternalState) -> IdOutput:
        turn=self.run_turn(state=state, previous_affect_state=initial_id_affect_state(), conversation_trajectory=appraise_conversation_trajectory(state))
        return turn.id_output
