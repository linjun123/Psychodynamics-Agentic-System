from psychodynamic_agent.affect import assert_affective_color_consistent
from psychodynamic_agent.agents import (
    CensorAAgent,
    CensorBAgent,
    EgoAgent,
    FinalSafetyGateAgent,
    IdAgent,
    MainAIAgent,
)
from psychodynamic_agent.censoring import assert_no_direct_latent_copy
from psychodynamic_agent.defense import assert_valid_conscious_ego_report
from psychodynamic_agent.ego import assert_valid_ego_report
from psychodynamic_agent.id_dynamics import (
    appraise_conversation_trajectory,
    initial_id_affect_state,
)
from psychodynamic_agent.orchestrator.logging import safe_serialize
from psychodynamic_agent.safety import assert_no_secret
from psychodynamic_agent.schemas import CensorBDefensePlan
from psychodynamic_agent.schemas.ego import EgoRealityPlan
from psychodynamic_agent.schemas.main_ai import MainAIResponsePlan
from psychodynamic_agent.superego.output_guard import assert_valid_main_ai_output


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
        self.id_affect_state = initial_id_affect_state()

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
            trajectory = appraise_conversation_trajectory(state)
            id_turn = self.id_agent.run_turn(state=state, previous_affect_state=self.id_affect_state, conversation_trajectory=trajectory)
            self.id_affect_state = id_turn.updated_affect_state
            id_output = id_turn.id_output
            self._assert_boundary(id_output.model_dump(), "id_output_before_censor_a")
            self._assert_boundary(id_turn.updated_affect_state.model_dump(), "id_affect_state")
            self._assert_boundary(id_turn.public_affect_dynamics.model_dump(), "id_public_affect_dynamics")
            self._assert_boundary(trajectory.model_dump(), "conversation_trajectory")

            censor_a_payload = self.censor_a.build_payload(id_output)
            self._assert_boundary(censor_a_payload, "censor_a_input")
            censor_a_output = self.censor_a.run_payload(censor_a_payload)
            try:
                assert_no_direct_latent_copy(id_output=id_output, censor_a_output=censor_a_output)
            except ValueError as exc:
                raise PipelineSafetyError(str(exc)) from exc

            from psychodynamic_agent.schemas import AffectPropagationTrace, EgoAffectSummary
            assert_affective_color_consistent(affect_trace=AffectPropagationTrace.model_validate(censor_a_payload["affect_trace"]), censor_a_output=censor_a_output)

            ego_payload = self.ego_agent.build_payload(
                censor_a_output=censor_a_output,
                state=state,
                ego_affect_summary=EgoAffectSummary.model_validate(censor_a_payload["ego_affect_summary"]),
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

            censor_b_payload = self.censor_b.build_payload(ego_report)
            self._assert_boundary(censor_b_payload, "censor_b_input")
            conscious_report = self.censor_b.run_payload(censor_b_payload)
            try:
                assert_valid_conscious_ego_report(
                    ego_report=ego_report,
                    defense_plan=CensorBDefensePlan.model_validate(censor_b_payload["defense_plan"]),
                    conscious_report=conscious_report,
                )
            except ValueError as exc:
                raise PipelineSafetyError(str(exc)) from exc

            main_ai_payload = self.main_ai.build_payload(
                conscious_report=conscious_report,
                state=state,
            )
            self._assert_boundary(main_ai_payload, "main_ai_input")
            main_output = self.main_ai.run_payload(main_ai_payload)
            try:
                assert_valid_main_ai_output(
                    main_output=main_output,
                    response_plan=MainAIResponsePlan.model_validate(main_ai_payload["main_ai_response_plan"]),
                    conscious_report=conscious_report,
                )
            except ValueError as exc:
                raise PipelineSafetyError(str(exc)) from exc

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
            "conversation_trajectory": trajectory.model_dump(),
            "public_affect_dynamics": id_turn.public_affect_dynamics.model_dump(),
            "updated_id_affect_state": id_turn.updated_affect_state.model_dump(),
            "affect_trace": censor_a_payload["affect_trace"],
            "ego_affect_summary": censor_a_payload["ego_affect_summary"],
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
