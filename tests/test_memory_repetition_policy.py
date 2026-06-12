from memory_distortion_helpers import activation, decision, trace

from psychodynamic_agent.memory.repetition_policy import (
    prohibited_expressions_for_tendency,
    repetition_pressure_score,
    safe_strategy_hint_for_tendency,
    should_generate_repetition_bias,
    tendency_from_trace,
)


def test_blocked_action_only_decision_generates_repetition_bias() -> None:
    assert should_generate_repetition_bias(
        activation=activation(),
        trace=trace(accessibility="direct"),
        decision=decision(decided_accessibility="blocked_action_only"),
    )


def test_felt_sense_only_decision_generates_repetition_bias() -> None:
    assert should_generate_repetition_bias(
        activation=activation(),
        trace=trace(accessibility="direct"),
        decision=decision(decided_accessibility="felt_sense_only"),
    )


def test_direct_low_defense_trace_does_not_generate_repetition_bias() -> None:
    assert not should_generate_repetition_bias(
        activation=activation(association_score=0.2),
        trace=trace(accessibility="direct", defense_level=0.1, repression_pressure=0.1),
        decision=decision(
            decided_accessibility="direct",
            defense_pressure=0.1,
            defense_level=0.1,
            repression_pressure=0.1,
        ),
    )


def test_high_defense_activation_generates_repetition_bias() -> None:
    assert should_generate_repetition_bias(
        activation=activation(association_score=0.5),
        trace=trace(accessibility="direct"),
        decision=decision(decided_accessibility="direct", defense_pressure=0.8),
    )


def test_repetition_pressure_score_uses_weighted_public_artifacts() -> None:
    score = repetition_pressure_score(
        activation=activation(association_score=1.0),
        trace=trace(defense_level=1.0, repression_pressure=1.0, activation_count=5),
        decision=decision(defense_pressure=1.0),
    )
    assert score == 1.0


def test_tendency_mapping_prefers_specific_threats_and_affects() -> None:
    assert tendency_from_trace(
        trace=trace(
            threat_signature=trace().threat_signature.model_copy(
                update={"rejection": 0.9}
            )
        ),
        activation=activation(),
        decision=decision(),
    ) == "preempt_rejection"
    assert tendency_from_trace(
        trace=trace(threat_signature=trace().threat_signature.model_copy(update={"loss": 0.9})),
        activation=activation(),
        decision=decision(),
    ) == "seek_reassurance"
    assert tendency_from_trace(
        trace=trace(
            threat_signature=trace().threat_signature.model_copy(
                update={"humiliation": 0.9}
            )
        ),
        activation=activation(),
        decision=decision(),
    ) == "over_explain"
    assert tendency_from_trace(
        trace=trace(
            threat_signature=trace().threat_signature.model_copy(
                update={"boundary_violation": 0.9}
            )
        ),
        activation=activation(),
        decision=decision(),
    ) == "test_boundary"
    assert tendency_from_trace(
        trace=trace(threat_signature=trace().threat_signature.model_copy(update={"control": 0.9})),
        activation=activation(),
        decision=decision(),
    ) == "control_uncertainty"
    assert tendency_from_trace(
        trace=trace(desire_signature=trace().desire_signature.model_copy(update={"mastery": 0.9})),
        activation=activation(),
        decision=decision(),
    ) == "ask_for_structure"
    assert tendency_from_trace(
        trace=trace(
            salient_symbols=[],
            affective_signature=trace().affective_signature.model_copy(update={"avoidance": 0.9}),
        ),
        activation=activation(matched_salient_symbols=[]),
        decision=decision(),
    ) == "avoid_topic"


def test_safe_strategy_and_prohibited_expression_are_available() -> None:
    for tendency in [
        "seek_reassurance",
        "avoid_topic",
        "over_explain",
        "test_boundary",
        "intellectualize",
        "ask_for_structure",
        "preempt_rejection",
        "control_uncertainty",
    ]:
        assert safe_strategy_hint_for_tendency(tendency)
        assert prohibited_expressions_for_tendency(tendency)
