from psychodynamic_agent.agents.base import BaseLLMAgent
from psychodynamic_agent.id_dynamics.private_turn_guard import assert_public_id_turn_output_safe
from psychodynamic_agent.prompts import ID_SYSTEM_PROMPT, ID_TURN_SYSTEM_PROMPT
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
        super().__init__(
            llm_client=llm_client, model=model, system_prompt=ID_SYSTEM_PROMPT, schema=IdOutput
        )
        self._sealed_ultimate_need = sealed_ultimate_need

    def run_with_state(self, state: FullInternalState) -> IdOutput:
        payload = {"state": state.model_dump(), "u_star": self._sealed_ultimate_need}
        return self.run(payload)

    def run_turn(
        self,
        *,
        state: FullInternalState,
        previous_affect_state: IdAffectState,
        conversation_trajectory: ConversationTrajectory,
    ) -> IdTurnOutput:
        payload = {
            "state": state.model_dump(),
            "u_star": self._sealed_ultimate_need,
            "previous_affect_state": previous_affect_state.model_dump(),
            "conversation_trajectory": conversation_trajectory.model_dump(),
        }
        raw = self.llm_client.generate_json(
            model=self.model,
            system_prompt=ID_TURN_SYSTEM_PROMPT,
            payload=payload,
            schema=PrivateIdTurnOutput,
        )
        private_output = PrivateIdTurnOutput.model_validate(raw)
        public_output = IdTurnOutput(
            id_output=private_output.id_output,
            updated_affect_state=private_output.updated_affect_state,
            public_affect_dynamics=private_output.public_affect_dynamics,
        )
        assert_public_id_turn_output_safe(public_output)
        return public_output
