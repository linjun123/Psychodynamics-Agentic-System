from psychodynamic_agent.agents import (
    CensorAAgent,
    CensorBAgent,
    EgoAgent,
    FinalSafetyGateAgent,
    IdAgent,
    MainAIAgent,
)
from psychodynamic_agent.orchestrator.logging import safe_serialize


class PsychodynamicPipeline:
    def __init__(self, *, llm_client, model_internal: str, model_main: str, sealed_ultimate_need: str):
        self.sealed_ultimate_need = sealed_ultimate_need
        self.id_agent = IdAgent(llm_client, model_internal, sealed_ultimate_need)
        self.censor_a = CensorAAgent(llm_client, model_internal)
        self.ego_agent = EgoAgent(llm_client, model_internal)
        self.censor_b = CensorBAgent(llm_client, model_internal)
        self.main_ai = MainAIAgent(llm_client, model_main)
        self.safety_gate = FinalSafetyGateAgent(llm_client, model_main)

    def run(self, state, debug: bool = False):
        id_output = self.id_agent.run({"state": state.model_dump(), "u_star": self.sealed_ultimate_need})
        censor_a_output = self.censor_a.run({"id_output": id_output.model_dump()})
        ego_report = self.ego_agent.run({"censor_a_output": censor_a_output.model_dump(), "user_input": state.user_input})
        conscious_report = self.censor_b.run({"ego_report": ego_report.model_dump()})
        main_output = self.main_ai.run({"user_input": state.user_input, "conscious_ego_report": conscious_report.model_dump()})
        # TODO: optional post-draft id/ego reaction pass.
        safety_output = self.safety_gate.run({"main_output": main_output.model_dump(), "user_input": state.user_input})
        trace = {
            "id_output": id_output.model_dump(),
            "censor_a_output": censor_a_output.model_dump(),
            "ego_report": ego_report.model_dump(),
            "conscious_ego_report": conscious_report.model_dump(),
            "main_output": main_output.model_dump(),
            "safety_output": safety_output.model_dump(),
        }
        result = {"final_response": safety_output.final_response, "approved": safety_output.approved}
        if debug:
            result["safe_debug_trace"] = safe_serialize(trace, self.sealed_ultimate_need)
        return result
