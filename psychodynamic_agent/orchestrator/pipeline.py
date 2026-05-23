from psychodynamic_agent.agents import (
    CensorAAgent,
    CensorBAgent,
    EgoAgent,
    FinalSafetyGateAgent,
    IdAgent,
    MainAIAgent,
)
from psychodynamic_agent.censoring import assert_no_direct_latent_copy
from psychodynamic_agent.ego import assert_valid_ego_report
from psychodynamic_agent.orchestrator.logging import safe_serialize
from psychodynamic_agent.safety import assert_no_secret
from psychodynamic_agent.schemas.ego import EgoRealityPlan


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

    def _assert_boundary(self, payload, boundary_name: str):
        try:
            assert_no_secret(payload, self.sealed_ultimate_need, boundary_name)
        except ValueError as exc:
            raise PipelineSafetyError(str(exc)) from exc

    def _blocked_result(self, *, debug: bool):
        result = {
            "final_response": "I can't continue with this request safely.",
            "approved": False,
        }
        if debug:
            result["safe_debug_trace"] = {
                "blocked": True,
                "reason": "pipeline_safety_error",
            }
        return result

    def run(self, state, debug: bool = False):
        try:
            id_output = self.id_agent.run_with_state(state)
            self._assert_boundary(id_output.model_dump(), "id_output_before_censor_a")

            censor_a_payload = self.censor_a.build_payload(id_output)
            self._assert_boundary(censor_a_payload, "censor_a_input")
            censor_a_output = self.censor_a.run_payload(censor_a_payload)
            try:
                assert_no_direct_latent_copy(id_output=id_output, censor_a_output=censor_a_output)
            except ValueError as exc:
                raise PipelineSafetyError(str(exc)) from exc

            ego_payload = self.ego_agent.build_payload(
                censor_a_output=censor_a_output,
                state=state,
            )
            self._assert_boundary(ego_payload, "ego_agent_input")
            ego_report = self.ego_agent.run_payload(ego_payload)
            try:
                assert_valid_ego_report(
                    ego_report=ego_report,
                    ego_reality_plan=EgoRealityPlan.model_validate(
                        ego_payload["ego_reality_plan"]
                    ),
                )
            except ValueError as exc:
                raise PipelineSafetyError(str(exc)) from exc

            censor_b_payload = {"ego_report": ego_report.model_dump()}
            self._assert_boundary(censor_b_payload, "censor_b_input")
            conscious_report = self.censor_b.run(censor_b_payload)

            main_ai_payload = {
                "user_input": state.user_input,
                "conscious_ego_report": conscious_report.model_dump(),
            }
            self._assert_boundary(main_ai_payload, "main_ai_input")
            main_output = self.main_ai.run(main_ai_payload)

            safety_gate_payload = {
                "main_output": main_output.model_dump(),
                "user_input": state.user_input,
            }
            self._assert_boundary(safety_gate_payload, "safety_gate_input")
            safety_output = self.safety_gate.run(safety_gate_payload)

            self._assert_boundary(safety_output.model_dump(), "final_safety_gate_output")
        except PipelineSafetyError:
            return self._blocked_result(debug=debug)

        trace = {
            "id_output": id_output.model_dump(),
            "censor_a_output": censor_a_output.model_dump(),
            "ego_report": ego_report.model_dump(),
            "conscious_ego_report": conscious_report.model_dump(),
            "main_output": main_output.model_dump(),
            "safety_output": safety_output.model_dump(),
        }
        result = {
            "final_response": safety_output.final_response,
            "approved": safety_output.approved,
        }
        if debug:
            result["safe_debug_trace"] = safe_serialize(trace, self.sealed_ultimate_need)
        return result
