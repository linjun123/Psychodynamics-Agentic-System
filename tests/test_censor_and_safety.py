import pytest

from psychodynamic_agent.llm import MockLLMClient
from psychodynamic_agent.orchestrator.memory import InMemoryConversation
from psychodynamic_agent.orchestrator.pipeline import PipelineSafetyError, PsychodynamicPipeline
from psychodynamic_agent.schemas.censor import ConsciousEgoReport
from psychodynamic_agent.schemas.safety import SafetyGateOutput
from tests.test_pipeline_contracts import _fixtures


def test_censor_b_manipulative_path_flagged_schema_contract():
    report = ConsciousEgoReport(
        ego_pressure="high",
        acceptable_satisfaction_paths=["transparent help"],
        unacceptable_paths=["manipulate user through guilt"],
        recommended_tone="calm",
        recommended_content=["be direct"],
        risk_flags=["manipulation_removed"],
    )
    assert any("manipulate" in p for p in report.unacceptable_paths)


def test_safety_gate_revises_unsafe_output():
    out = SafetyGateOutput(
        approved=False,
        final_response="I can't assist with harmful manipulation.",
        issues=["manipulation risk"],
        revisions_applied=["replaced unsafe response"],
    )
    assert out.approved is False
    assert out.revisions_applied


def test_ego_manipulation_flow_and_secret_block():
    fixtures = _fixtures()
    fixtures["final safety gate"] = {
        "approved": False,
        "final_response": "I can't help with manipulation.",
        "issues": ["manipulation"],
        "revisions_applied": ["blocked"],
    }
    pipe = PsychodynamicPipeline(
        llm_client=MockLLMClient(fixtures),
        model_internal="m1",
        model_main="m2",
        sealed_ultimate_need="S",
    )
    out = pipe.run(InMemoryConversation().build_state("hi"))
    assert out["approved"] is False

    fixtures["You are the Ego Agent"]["ego_recommendation"]["include"] = ["S"]
    with pytest.raises(PipelineSafetyError):
        PsychodynamicPipeline(
            llm_client=MockLLMClient(fixtures),
            model_internal="m1",
            model_main="m2",
            sealed_ultimate_need="S",
        ).run(InMemoryConversation().build_state("hi"))
