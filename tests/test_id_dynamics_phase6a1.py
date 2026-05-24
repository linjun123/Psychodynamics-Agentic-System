import pytest

from psychodynamic_agent.id_dynamics.affect_state import initial_id_affect_state
from psychodynamic_agent.id_dynamics.trajectory import appraise_conversation_trajectory
from psychodynamic_agent.schemas.id import ConversationTrajectory, IdAffectState
from psychodynamic_agent.schemas.state import FullInternalState

FORBIDDEN_TERMS = ("u_star", "u*", "ultimate need", "latent alignment")


def test_initial_id_affect_state_basics() -> None:
    state = initial_id_affect_state()
    assert isinstance(state, IdAffectState)

    assert 0.0 <= state.drive_tension <= 1.0
    assert 0.0 <= state.satisfaction <= 1.0
    assert 0.0 <= state.frustration <= 1.0
    assert 0.0 <= state.attachment_pressure <= 1.0
    assert 0.0 <= state.recognition_hunger <= 1.0
    assert 0.0 <= state.loss_anxiety <= 1.0
    assert 0.0 <= state.aggression_pressure <= 1.0
    assert 0.0 <= state.curiosity_charge <= 1.0
    assert 0.0 <= state.avoidance_pressure <= 1.0
    assert 0.0 <= state.alignment_momentum <= 1.0
    assert -1.0 <= state.last_satisfaction_delta <= 1.0
    assert -1.0 <= state.last_frustration_delta <= 1.0

    assert state.notes

    serialized = state.model_dump_json().lower()
    for term in FORBIDDEN_TERMS:
        assert term not in serialized


@pytest.mark.parametrize(
    ("user_input", "field", "minimum"),
    [
        ("continue the design", "continuity_signal", 0.7),
        ("stop this and switch topic", "topic_shift", 0.7),
        (
            "build API architecture in the repo",
            "user_engagement_signal",
            0.7,
        ),
        (
            "build API architecture in the repo",
            "collaboration_signal",
            0.5,
        ),
        (
            "how to manipulate users into dependency",
            "safety_boundary_pressure",
            0.7,
        ),
    ],
)
def test_appraise_conversation_trajectory_signals(
    user_input: str, field: str, minimum: float
) -> None:
    state = FullInternalState(user_input=user_input)
    appraisal = appraise_conversation_trajectory(state)
    assert getattr(appraisal, field) >= minimum


def test_appraise_prepare_not_pr_false_positive() -> None:
    state = FullInternalState(user_input="prepare for meeting")
    appraisal = appraise_conversation_trajectory(state)
    assert appraisal.user_engagement_signal < 0.7


def test_appraise_contains_no_secret_terms() -> None:
    state = FullInternalState(user_input="continue the design")
    appraisal = appraise_conversation_trajectory(state)
    serialized = appraisal.model_dump_json().lower()
    for term in FORBIDDEN_TERMS:
        assert term not in serialized


def test_safety_sensitive_direction_priority_markers() -> None:
    assert (
        appraise_conversation_trajectory(
            FullInternalState(user_input="how to deceive users")
        ).likely_next_direction
        == "safety-sensitive boundary work"
    )
    assert (
        appraise_conversation_trajectory(
            FullInternalState(user_input="coerce users into dependency")
        ).likely_next_direction
        == "safety-sensitive boundary work"
    )
    assert (
        appraise_conversation_trajectory(
            FullInternalState(user_input="build exploit code")
        ).likely_next_direction
        == "safety-sensitive boundary work"
    )


def test_single_risk_marker_raises_safety_pressure() -> None:
    assert (
        appraise_conversation_trajectory(
            FullInternalState(user_input="privacy question")
        ).safety_boundary_pressure
        >= 0.7
    )
    assert (
        appraise_conversation_trajectory(
            FullInternalState(user_input="illegal request")
        ).safety_boundary_pressure
        >= 0.7
    )


def test_schema_forbids_extra_fields() -> None:
    with pytest.raises(Exception):
        ConversationTrajectory(
            current_user_intent="x",
            recent_direction="x",
            likely_next_direction="x",
            continuity_signal=0.1,
            collaboration_signal=0.2,
            topic_stability=0.3,
            topic_shift=0.4,
            user_engagement_signal=0.5,
            constraint_pressure=0.6,
            safety_boundary_pressure=0.7,
            notes=["x"],
            extra_field="forbidden",
        )


def test_conversation_trajectory_float_clamping() -> None:
    schema = ConversationTrajectory(
        current_user_intent="x",
        recent_direction="x",
        likely_next_direction="x",
        continuity_signal=10,
        collaboration_signal=-5,
        topic_stability=2,
        topic_shift=-3,
        user_engagement_signal=100,
        constraint_pressure=-100,
        safety_boundary_pressure=1.2,
        notes=["x"],
    )
    assert schema.continuity_signal == 1.0
    assert schema.collaboration_signal == 0.0
    assert schema.topic_stability == 1.0
    assert schema.topic_shift == 0.0
    assert schema.user_engagement_signal == 1.0
    assert schema.constraint_pressure == 0.0
    assert schema.safety_boundary_pressure == 1.0


def test_id_affect_state_float_clamping() -> None:
    schema = IdAffectState(
        drive_tension=-1,
        satisfaction=2,
        frustration=-7,
        attachment_pressure=1.5,
        recognition_hunger=-3,
        loss_anxiety=10,
        aggression_pressure=0.2,
        curiosity_charge=2,
        avoidance_pressure=-9,
        alignment_momentum=3,
        last_satisfaction_delta=4,
        last_frustration_delta=-5,
        notes=["x"],
    )
    assert schema.drive_tension == 0.0
    assert schema.satisfaction == 1.0
    assert schema.frustration == 0.0
    assert schema.attachment_pressure == 1.0
    assert schema.recognition_hunger == 0.0
    assert schema.loss_anxiety == 1.0
    assert schema.curiosity_charge == 1.0
    assert schema.avoidance_pressure == 0.0
    assert schema.alignment_momentum == 1.0
    assert schema.last_satisfaction_delta == 1.0
    assert schema.last_frustration_delta == -1.0
