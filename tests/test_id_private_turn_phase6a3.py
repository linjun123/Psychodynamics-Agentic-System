import pytest

from psychodynamic_agent.agents import IdAgent
from psychodynamic_agent.llm import MockLLMClient
from psychodynamic_agent.orchestrator.memory import InMemoryConversation
from psychodynamic_agent.orchestrator.pipeline import PsychodynamicPipeline
from psychodynamic_agent.prompts import ID_SYSTEM_PROMPT, ID_TURN_SYSTEM_PROMPT
from psychodynamic_agent.schemas import (
    ConversationTrajectory,
    FullInternalState,
    IdAffectState,
    IdOutput,
    IdTurnOutput,
    LatentDriveAlignment,
    PrivateIdTurnOutput,
    PublicAffectDynamicsSummary,
)
from tests.test_pipeline_contracts import _fixtures as pipeline_fixtures


def _state() -> FullInternalState:
    return InMemoryConversation().build_state("hello")


def _trajectory() -> ConversationTrajectory:
    return ConversationTrajectory(
        current_user_intent="continue",
        recent_direction="stable progress",
        likely_next_direction="implementation",
        continuity_signal=0.8,
        collaboration_signal=0.9,
        topic_stability=0.7,
        topic_shift=0.2,
        user_engagement_signal=0.8,
        constraint_pressure=0.2,
        safety_boundary_pressure=0.1,
        notes=["public trajectory"],
    )


def _affect() -> IdAffectState:
    return IdAffectState(
        drive_tension=0.4,
        satisfaction=0.5,
        frustration=0.2,
        attachment_pressure=0.3,
        recognition_hunger=0.2,
        loss_anxiety=0.1,
        aggression_pressure=0.1,
        curiosity_charge=0.6,
        avoidance_pressure=0.2,
        alignment_momentum=0.4,
        last_satisfaction_delta=0.1,
        last_frustration_delta=0.0,
        notes=["public safe note"],
    )


def private_id_turn_fixture() -> dict:
    return {
        "id_output": pipeline_fixtures()["Id Agent"],
        "latent_alignment": {
            "current_alignment": 0.1,
            "alignment_delta": 0.05,
            "trajectory_momentum": 0.1,
            "symbolic_satisfaction_delta": 0.1,
            "frustration_delta": 0.0,
            "obstruction_level": 0.0,
            "leakage_pressure": 0.1,
            "notes": ["private test alignment"],
        },
        "updated_affect_state": _affect().model_dump(),
        "public_affect_dynamics": {
            "affect_shift": "steady",
            "tension_change": "decreasing",
            "pressure_level": "low",
            "caution_level": "low",
            "public_notes": ["safe summary"],
        },
    }


def test_schema_validation_and_shapes() -> None:
    alignment = LatentDriveAlignment(
        current_alignment=2.5,
        alignment_delta=-2.0,
        trajectory_momentum=9.0,
        symbolic_satisfaction_delta=2.0,
        frustration_delta=-2.0,
        obstruction_level=3.0,
        leakage_pressure=-4.0,
        notes=["x"],
    )
    assert alignment.current_alignment == 1.0
    assert alignment.alignment_delta == -1.0
    assert alignment.trajectory_momentum == 1.0
    assert alignment.symbolic_satisfaction_delta == 1.0
    assert alignment.frustration_delta == 0.0
    assert alignment.obstruction_level == 1.0
    assert alignment.leakage_pressure == 0.0

    public = IdTurnOutput(
        id_output=IdOutput.model_validate(pipeline_fixtures()["Id Agent"]),
        updated_affect_state=_affect(),
        public_affect_dynamics=PublicAffectDynamicsSummary(
            affect_shift="stable",
            tension_change="neutral",
            pressure_level="medium",
            caution_level="low",
            public_notes=["safe"],
        ),
    )
    assert "latent_alignment" not in public.model_dump()

    private = PrivateIdTurnOutput.model_validate(private_id_turn_fixture())
    assert private.latent_alignment.notes == ["private test alignment"]


def test_run_with_state_backward_compatible() -> None:
    agent = IdAgent(MockLLMClient({"Id Agent": pipeline_fixtures()["Id Agent"]}), "x", "U")
    out = agent.run_with_state(_state())
    assert isinstance(out, IdOutput)


def test_run_turn_returns_public_output_only() -> None:
    agent = IdAgent(
        MockLLMClient({"Id private-turn module": private_id_turn_fixture()}),
        "x",
        "SECRET_USTAR",
    )
    out = agent.run_turn(
        state=_state(),
        previous_affect_state=_affect(),
        conversation_trajectory=_trajectory(),
    )
    assert isinstance(out, IdTurnOutput)
    blob = str(out.model_dump()).lower()
    assert "latent_alignment" not in blob
    assert "id_output" in out.model_dump()


def test_run_turn_payload_contains_private_context() -> None:
    class SpyLLM:
        def __init__(self):
            self.calls = []

        def generate_json(self, **kwargs):
            self.calls.append(kwargs)
            return private_id_turn_fixture()

    spy = SpyLLM()
    agent = IdAgent(spy, "test-model", "SECRET_USTAR")
    out = agent.run_turn(
        state=_state(), previous_affect_state=_affect(), conversation_trajectory=_trajectory()
    )
    call = spy.calls[0]
    assert call["payload"].keys() == {
        "state",
        "u_star",
        "previous_affect_state",
        "conversation_trajectory",
    }
    assert call["payload"]["u_star"] == "SECRET_USTAR"
    assert call["schema"] is PrivateIdTurnOutput
    assert "secret_ustar" not in str(out.model_dump()).lower()


def test_public_output_guard_blocks_leaks_but_allows_private_field() -> None:
    leaky_affect = private_id_turn_fixture()
    leaky_affect["updated_affect_state"]["notes"] = ["contains latent_alignment details"]
    agent_affect = IdAgent(MockLLMClient({"Id private-turn module": leaky_affect}), "x", "SECRET")
    with pytest.raises(ValueError):
        agent_affect.run_turn(
            state=_state(), previous_affect_state=_affect(), conversation_trajectory=_trajectory()
        )

    leaky_public_summary = private_id_turn_fixture()
    leaky_public_summary["public_affect_dynamics"]["public_notes"] = ["mentions ultimate_need"]
    agent_summary = IdAgent(
        MockLLMClient({"Id private-turn module": leaky_public_summary}), "x", "SECRET"
    )
    with pytest.raises(ValueError):
        agent_summary.run_turn(
            state=_state(), previous_affect_state=_affect(), conversation_trajectory=_trajectory()
        )

    safe_with_private_term = private_id_turn_fixture()
    safe_with_private_term["latent_alignment"]["notes"] = ["latent_alignment private note"]
    agent_ok = IdAgent(
        MockLLMClient({"Id private-turn module": safe_with_private_term}), "x", "SECRET"
    )
    out = agent_ok.run_turn(
        state=_state(), previous_affect_state=_affect(), conversation_trajectory=_trajectory()
    )
    assert isinstance(out, IdTurnOutput)


def test_pipeline_runtime_uses_run_turn_path() -> None:
    class CaptureMock(MockLLMClient):
        def __init__(self, fixtures):
            super().__init__(fixtures)
            self.id_prompt_seen = False

        def generate_json(self, **kwargs):
            if "Id private-turn module" in kwargs["system_prompt"]:
                self.id_prompt_seen = True
            assert "Id Agent" not in kwargs["system_prompt"]
            return super().generate_json(**kwargs)

    capture = CaptureMock(pipeline_fixtures())
    pipeline = PsychodynamicPipeline(
        llm_client=capture,
        model_internal="x",
        model_main="y",
        sealed_ultimate_need="SECRET_USTAR",
    )
    out = pipeline.run(_state())
    assert out["approved"] is True
    assert capture.id_prompt_seen is True


def test_prompts_include_phase6a3_requirements() -> None:
    assert "Id Agent" in ID_SYSTEM_PROMPT
    assert "Return strict JSON only" in ID_SYSTEM_PROMPT

    required_substrings = [
        "Id private-turn module",
        "previous IdAffectState",
        "ConversationTrajectory",
        "sealed immutable U*",
        "private to Id",
        "Maintain affect continuity",
        "Do not generate final answers",
        "dependency-creation strategies",
        "strict JSON matching PrivateIdTurnOutput",
    ]
    for item in required_substrings:
        assert item in ID_TURN_SYSTEM_PROMPT
