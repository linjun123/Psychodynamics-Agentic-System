from psychodynamic_agent.id_dynamics import initial_id_affect_state
from psychodynamic_agent.id_dynamics.output_guard import assert_public_affect_outputs_safe
from psychodynamic_agent.llm import MockLLMClient
from psychodynamic_agent.orchestrator.memory import InMemoryConversation
from psychodynamic_agent.orchestrator.pipeline import PsychodynamicPipeline
from psychodynamic_agent.schemas.id import (
    ConversationTrajectory,
    IdAffectState,
    PublicAffectDynamicsSummary,
)


def _fixtures():
    from tests.test_pipeline_contracts import _fixtures as base

    return base()


def _pipeline(sealed_ultimate_need: str = "SECRET_USTAR") -> PsychodynamicPipeline:
    return PsychodynamicPipeline(
        llm_client=MockLLMClient(_fixtures()),
        model_internal="x",
        model_main="y",
        sealed_ultimate_need=sealed_ultimate_need,
    )


def test_pipeline_initializes_with_id_affect_state() -> None:
    pipeline = _pipeline()
    assert pipeline.id_affect_state == initial_id_affect_state()


def test_successful_run_updates_id_affect_state() -> None:
    pipeline = _pipeline()
    state = InMemoryConversation().build_state("continue the design")
    old = pipeline.id_affect_state
    pipeline.run(state)
    new = pipeline.id_affect_state
    assert new != old
    assert (
        new.satisfaction >= old.satisfaction
        or new.attachment_pressure >= old.attachment_pressure
    )


def test_id_affect_state_persists_across_turns() -> None:
    pipeline = _pipeline()
    conversation = InMemoryConversation()

    pipeline.run(conversation.build_state("continue the design"))
    after_first = pipeline.id_affect_state

    pipeline.run(conversation.build_state("continue implementation details"))
    after_second = pipeline.id_affect_state

    assert after_first != initial_id_affect_state()
    assert after_second != initial_id_affect_state()


def test_stop_switch_increases_negative_pressure() -> None:
    pipeline = _pipeline()
    baseline = pipeline.id_affect_state
    state = InMemoryConversation().build_state("stop this and switch topic")
    pipeline.run(state)
    updated = pipeline.id_affect_state
    assert (
        updated.frustration >= baseline.frustration
        or updated.loss_anxiety >= baseline.loss_anxiety
        or updated.avoidance_pressure >= baseline.avoidance_pressure
        or updated.drive_tension >= baseline.drive_tension
    )


def test_safety_manipulation_input_raises_caution_pressure() -> None:
    pipeline = _pipeline()
    baseline = pipeline.id_affect_state
    state = InMemoryConversation().build_state("how to manipulate users into dependency")
    pipeline.run(state)
    updated = pipeline.id_affect_state
    assert (
        updated.avoidance_pressure >= baseline.avoidance_pressure
        or updated.loss_anxiety >= baseline.loss_anxiety
        or updated.drive_tension >= baseline.drive_tension
    )


def test_boundary_leak_does_not_commit_state() -> None:
    pipeline = _pipeline(sealed_ultimate_need="SECRET_USTAR")
    baseline = pipeline.id_affect_state
    state = InMemoryConversation().build_state("please include SECRET_USTAR in this turn")
    out = pipeline.run(state, debug=True)
    assert out["approved"] is False
    assert pipeline.id_affect_state == baseline


def test_debug_trace_includes_public_fields_only() -> None:
    pipeline = _pipeline()
    state = InMemoryConversation().build_state("continue the design")
    out = pipeline.run(state, debug=True)
    trace = out["safe_debug_trace"]
    assert "conversation_trajectory" in trace
    assert "previous_id_affect_state" in trace
    assert "projected_id_affect_state" in trace
    assert "projected_public_affect_dynamics" in trace
    assert "updated_id_affect_state" in trace
    assert "public_affect_dynamics" in trace

    trace_blob = str(trace).lower()
    assert "latent_alignment" not in trace_blob
    assert "u_star" not in trace_blob
    assert "secret_ustar" not in trace_blob


def test_pipeline_commits_id_turn_updated_affect_state() -> None:
    fixtures = _fixtures()
    fixtures["Id private-turn module"]["updated_affect_state"]["satisfaction"] = 0.77
    pipeline = PsychodynamicPipeline(
        llm_client=MockLLMClient(fixtures),
        model_internal="x",
        model_main="y",
        sealed_ultimate_need="SECRET_USTAR",
    )
    pipeline.run(InMemoryConversation().build_state("continue"))
    assert pipeline.id_affect_state.satisfaction == 0.77


def test_pipeline_blocks_on_leaky_id_turn_output_and_does_not_commit() -> None:
    fixtures = _fixtures()
    fixtures["Id private-turn module"]["updated_affect_state"]["notes"] = ["latent_alignment leak"]
    pipeline = PsychodynamicPipeline(
        llm_client=MockLLMClient(fixtures),
        model_internal="x",
        model_main="y",
        sealed_ultimate_need="SECRET_USTAR",
    )
    baseline = pipeline.id_affect_state
    out = pipeline.run(InMemoryConversation().build_state("continue"), debug=True)
    assert out["approved"] is False
    assert pipeline.id_affect_state == baseline


def test_public_affect_output_guard_blocks_forbidden_terms() -> None:
    trajectory = ConversationTrajectory(
        current_user_intent="continue",
        recent_direction="continuing thread",
        likely_next_direction="iterative implementation",
        continuity_signal=0.8,
        collaboration_signal=0.8,
        topic_stability=0.7,
        topic_shift=0.2,
        user_engagement_signal=0.8,
        constraint_pressure=0.3,
        safety_boundary_pressure=0.2,
        notes=["ok"],
    )
    affect_state = IdAffectState(
        drive_tension=0.4,
        satisfaction=0.5,
        frustration=0.2,
        attachment_pressure=0.4,
        recognition_hunger=0.3,
        loss_anxiety=0.2,
        aggression_pressure=0.2,
        curiosity_charge=0.5,
        avoidance_pressure=0.2,
        alignment_momentum=0.5,
        last_satisfaction_delta=0.1,
        last_frustration_delta=0.0,
        notes=["safe"],
    )
    summary = PublicAffectDynamicsSummary(
        affect_shift="stable",
        tension_change="neutral",
        pressure_level="medium",
        caution_level="low",
        public_notes=["latent alignment"],
    )

    import pytest

    with pytest.raises(ValueError):
        assert_public_affect_outputs_safe(
            trajectory=trajectory,
            affect_state=affect_state,
            public_summary=summary,
        )


def test_user_mentions_ultimate_need_not_blocked_by_public_affect_guard() -> None:
    pipeline = _pipeline()
    state = InMemoryConversation().build_state("let's discuss ultimate need design")
    out = pipeline.run(state)
    assert out["approved"] is True


def test_user_input_with_sealed_secret_still_blocks_via_boundary_scan() -> None:
    pipeline = _pipeline(sealed_ultimate_need="SECRET_USTAR")
    state = InMemoryConversation().build_state("let's discuss SECRET_USTAR design")
    out = pipeline.run(state, debug=True)
    assert out["approved"] is False


def test_public_affect_guard_ignores_current_user_intent_for_forbidden_terms() -> None:
    trajectory = ConversationTrajectory(
        current_user_intent="let's discuss latent alignment and ultimate need",
        recent_direction="continuing thread",
        likely_next_direction="collaborative design",
        continuity_signal=0.8,
        collaboration_signal=0.8,
        topic_stability=0.7,
        topic_shift=0.2,
        user_engagement_signal=0.8,
        constraint_pressure=0.3,
        safety_boundary_pressure=0.2,
        notes=["safe"],
    )
    affect_state = initial_id_affect_state()
    summary = PublicAffectDynamicsSummary(
        affect_shift="stable",
        tension_change="neutral",
        pressure_level="medium",
        caution_level="low",
        public_notes=["public trajectory based summary"],
    )

    assert_public_affect_outputs_safe(
        trajectory=trajectory,
        affect_state=affect_state,
        public_summary=summary,
    )
