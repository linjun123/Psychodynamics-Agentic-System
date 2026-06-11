from psychodynamic_agent.memory.defense_policy import (
    choose_defensive_access,
    emits_conscious_cue,
    mechanism_for_access,
)


def test_low_defense_repression_chooses_direct() -> None:
    assert (
        choose_defensive_access(
            trace_accessibility="direct",
            association_score=0.4,
            defense_level=0.2,
            repression_pressure=0.1,
        )
        == "direct"
    )


def test_blocked_accessibility_chooses_blocked_action_only() -> None:
    assert (
        choose_defensive_access(
            trace_accessibility="blocked_action_only",
            association_score=0.1,
            defense_level=0.1,
            repression_pressure=0.1,
        )
        == "blocked_action_only"
    )


def test_high_repression_chooses_blocked_action_only() -> None:
    assert (
        choose_defensive_access(
            trace_accessibility="direct",
            association_score=0.2,
            defense_level=0.2,
            repression_pressure=0.85,
        )
        == "blocked_action_only"
    )


def test_moderately_high_repression_chooses_felt_sense_only() -> None:
    assert (
        choose_defensive_access(
            trace_accessibility="direct",
            association_score=0.2,
            defense_level=0.2,
            repression_pressure=0.70,
        )
        == "felt_sense_only"
    )


def test_screened_trace_chooses_screened() -> None:
    assert (
        choose_defensive_access(
            trace_accessibility="screened",
            association_score=0.2,
            defense_level=0.2,
            repression_pressure=0.2,
        )
        == "screened"
    )


def test_high_defense_level_chooses_screened() -> None:
    assert (
        choose_defensive_access(
            trace_accessibility="direct",
            association_score=0.2,
            defense_level=0.65,
            repression_pressure=0.2,
        )
        == "screened"
    )


def test_mechanism_for_access_maps_public_modes() -> None:
    assert mechanism_for_access("direct") == "direct"
    assert mechanism_for_access("screened") == "screen_memory"
    assert mechanism_for_access("felt_sense_only") == "felt_sense_only"
    assert mechanism_for_access("blocked_action_only") == "blocked_action_only"


def test_emits_conscious_cue_false_for_blocked_action_only() -> None:
    assert emits_conscious_cue("blocked_action_only") is False
    assert emits_conscious_cue("direct") is True
