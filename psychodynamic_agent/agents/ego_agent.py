from psychodynamic_agent.agents.base import BaseLLMAgent
from psychodynamic_agent.ego import plan_ego_reality
from psychodynamic_agent.prompts import EGO_SYSTEM_PROMPT
from psychodynamic_agent.schemas import CensorAOutput, EgoReport, FullInternalState


class EgoAgent(BaseLLMAgent):
    def __init__(self, llm_client, model: str):
        super().__init__(
            llm_client=llm_client, model=model, system_prompt=EGO_SYSTEM_PROMPT, schema=EgoReport
        )

    def build_payload(self, censor_a_output: CensorAOutput, state: FullInternalState) -> dict:
        plan = plan_ego_reality(censor_a_output=censor_a_output, state=state)
        return {
            "censor_a_output": censor_a_output.model_dump(),
            "state_context": {
                "user_input": state.user_input,
                "conversation_history": [m.model_dump() for m in state.conversation_history],
                "previous_ego_reports": state.previous_ego_reports,
                "previous_main_outputs": state.previous_main_outputs,
                "superego_constraints": state.superego_constraints,
                "internal_tension_state": state.internal_tension_state,
                "satisfaction_history": state.satisfaction_history,
            },
            "ego_reality_plan": plan.model_dump(),
        }

    def run_payload(self, payload: dict) -> EgoReport:
        return self.run(payload)

    def run_with_censor_a_output(
        self,
        censor_a_output: CensorAOutput,
        state: FullInternalState,
    ) -> EgoReport:
        return self.run_payload(self.build_payload(censor_a_output, state))
