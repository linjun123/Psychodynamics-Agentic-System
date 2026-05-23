from psychodynamic_agent.agents.base import BaseLLMAgent
from psychodynamic_agent.prompts import ID_SYSTEM_PROMPT
from psychodynamic_agent.schemas import FullInternalState, IdOutput


class IdAgent(BaseLLMAgent):
    def __init__(self, llm_client, model: str, sealed_ultimate_need: str):
        super().__init__(
            llm_client=llm_client,
            model=model,
            system_prompt=ID_SYSTEM_PROMPT,
            schema=IdOutput,
        )
        self._sealed_ultimate_need = sealed_ultimate_need

    def build_private_payload(self, state: FullInternalState) -> dict:
        return {
            "state": state.model_dump(),
            "sealed_context": {"u_star": self._sealed_ultimate_need},
        }

    def run_with_state(self, state: FullInternalState) -> IdOutput:
        return self.run(self.build_private_payload(state))
