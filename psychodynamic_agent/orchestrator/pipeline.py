from psychodynamic_agent.agents import (
    CensorAAgent,
    CensorBAgent,
    EgoAgent,
    FinalSafetyGateAgent,
    IdAgent,
    MainAIAgent,
)
from psychodynamic_agent.orchestrator.logging import safe_serialize
from psychodynamic_agent.safety import assert_no_secret


class PipelineSafetyError(RuntimeError):
    pass


class PsychodynamicPipeline:
    def __init__(
        self,
        *,
        llm_client,
        model_internal: str,
        model_main: str,
        sealed_ultimate_need: str,
    ):
        self.sealed_ultimate_need = sealed_ultimate_need
        self.id_agent = IdAgent(llm_client, model_internal, sealed_ultimate_need)
        self.censor_a = CensorAAgent(llm_client, model_internal)
        self.ego_agent = EgoAgent(llm_client, model_internal)
        self.censor_b = CensorBAgent(llm_client, model_internal)
        self.main_ai = MainAIAgent(llm_client, model_main)
        self.safety_gate = FinalSafetyGateAgent(llm_client, model_main)

    def _boundary_check(self, payload: dict, boundary: str) -> None:
        try:
            assert_no_secret(payload, self.sealed_ultimate_need, boundary)
        except ValueError as exc:
            raise PipelineSafetyError(str(exc)) from exc

    def run(self, state, debug: bool = False):
        id_output = self.id_agent.run_with_state(state)
        id_payload = id_output.model_dump()
        self._boundary_check(id_payload, "id_output")

        censor_a_output = self.censor_a.run({"id_output": id_payload})
        censor_a_payload = censor_a_output.model_dump()
        self._boundary_check(censor_a_payload, "censor_a_output")

        ego_report = self.ego_agent.run(
            {"censor_a_output": censor_a_payload, "user_input": state.user_input}
        )
        ego_payload = ego_report.model_dump()
        self._boundary_check(ego_payload, "ego_report")

        conscious_report = self.censor_b.run({"ego_report": ego_payload})
        conscious_payload = conscious_report.model_dump()
        self._boundary_check(conscious_payload, "conscious_ego_report")

        main_output = self.main_ai.run(
            {"user_input": state.user_input, "conscious_ego_report": conscious_payload}
        )
        main_payload = main_output.model_dump()
        self._boundary_check(main_payload, "main_ai_output")

        safety_output = self.safety_gate.run(
            {"main_output": main_payload, "user_input": state.user_input}
        )
        safety_payload = safety_output.model_dump()
        self._boundary_check(safety_payload, "safety_output")

        trace = {
            "id_output": id_payload,
            "censor_a_output": censor_a_payload,
            "ego_report": ego_payload,
            "conscious_ego_report": conscious_payload,
            "main_output": main_payload,
            "safety_output": safety_payload,
        }
        result = {
            "final_response": safety_output.final_response,
            "approved": safety_output.approved,
        }
        if debug:
            result["safe_debug_trace"] = safe_serialize(trace, self.sealed_ultimate_need)
        return result
