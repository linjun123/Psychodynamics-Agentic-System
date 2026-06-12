from psychodynamic_agent.memory.heuristics import clamp_01
from psychodynamic_agent.schemas.memory import (
    MemoryActivation,
    MemoryDefenseDecision,
    MemoryRepetitionTendency,
    MemoryRepetitionTriggerKind,
    MemoryTrace,
)

_HIGH_SIGNAL = 0.65


def repetition_pressure_score(
    *,
    activation: MemoryActivation,
    trace: MemoryTrace,
    decision: MemoryDefenseDecision,
) -> float:
    return clamp_01(
        (0.30 * activation.association_score)
        + (0.25 * decision.defense_pressure)
        + (0.20 * trace.repression_pressure)
        + (0.15 * trace.defense_level)
        + (0.10 * min(trace.activation_count / 5.0, 1.0))
    )


def should_generate_repetition_bias(
    *,
    activation: MemoryActivation,
    trace: MemoryTrace,
    decision: MemoryDefenseDecision,
) -> bool:
    if decision.decided_accessibility in {"blocked_action_only", "felt_sense_only"}:
        return True
    if trace.accessibility == "blocked_action_only":
        return True
    if trace.repression_pressure >= 0.70:
        return True
    if decision.defense_pressure >= 0.70 and activation.association_score >= 0.25:
        return True
    return trace.activation_count >= 3 and decision.defense_pressure >= 0.45


def tendency_from_trace(
    *,
    trace: MemoryTrace,
    activation: MemoryActivation,
    decision: MemoryDefenseDecision,
) -> MemoryRepetitionTendency:
    symbols = set(trace.salient_symbols + activation.matched_salient_symbols)
    objects = set(trace.object_targets + activation.matched_object_targets)
    threat = trace.threat_signature
    affect = trace.affective_signature
    desire = trace.desire_signature

    if threat.rejection >= _HIGH_SIGNAL:
        return "preempt_rejection"
    if threat.loss >= _HIGH_SIGNAL or affect.fear_of_loss >= _HIGH_SIGNAL:
        return "seek_reassurance"
    if threat.humiliation >= _HIGH_SIGNAL or affect.shame >= _HIGH_SIGNAL:
        return "over_explain"
    if threat.boundary_violation >= _HIGH_SIGNAL:
        return "test_boundary"
    if threat.control >= _HIGH_SIGNAL:
        return "control_uncertainty"
    if (
        desire.mastery >= _HIGH_SIGNAL
        or "task_structure" in symbols
        or "task_mastery" in symbols
        or "task_structure" in objects
        or "task_mastery" in objects
    ):
        return "ask_for_structure"
    if affect.avoidance >= _HIGH_SIGNAL or decision.decided_accessibility == "blocked_action_only":
        return "avoid_topic"
    if "recognition_pressure" in symbols and decision.defense_pressure >= 0.55:
        return "over_explain"
    return "intellectualize"


def trigger_kind_from_decision(
    *,
    trace: MemoryTrace,
    decision: MemoryDefenseDecision,
) -> MemoryRepetitionTriggerKind:
    if (
        decision.decided_accessibility == "blocked_action_only"
        or trace.accessibility == "blocked_action_only"
    ):
        return "blocked_memory"
    if decision.decided_accessibility == "felt_sense_only":
        return "felt_sense_memory"
    if decision.decided_accessibility == "screened" or trace.accessibility == "screened":
        return "screened_memory"
    return "high_defense_activation"


def safe_strategy_hint_for_tendency(tendency: str) -> str:
    hints = {
        "seek_reassurance": "Use gentle confirmation without creating dependency.",
        "avoid_topic": "Avoid forcing direct recall; use indirect, choice-preserving framing.",
        "over_explain": "Prefer concise structure and avoid defensive over-justification.",
        "test_boundary": "Maintain clear boundaries and avoid escalating the test.",
        "intellectualize": "Offer concrete framing while leaving room for affective uncertainty.",
        "ask_for_structure": "Provide clear structure and next steps.",
        "preempt_rejection": "Avoid assuming rejection; keep language collaborative and grounded.",
        "control_uncertainty": "Reduce uncertainty with transparent options and limits.",
    }
    return hints.get(tendency, hints["intellectualize"])


def prohibited_expressions_for_tendency(tendency: str) -> list[str]:
    expressions = {
        "seek_reassurance": ["Do not repeatedly ask the user to validate the system."],
        "avoid_topic": ["Do not erase the topic; preserve user autonomy."],
        "over_explain": ["Do not produce excessive defensive justification."],
        "test_boundary": ["Do not manipulate or provoke boundary tests."],
        "intellectualize": ["Do not use abstraction to evade the user's concrete task."],
        "ask_for_structure": ["Do not impose structure without user consent."],
        "preempt_rejection": ["Do not assume the user is rejecting the interaction."],
        "control_uncertainty": ["Do not over-control the user's choices."],
    }
    return list(expressions.get(tendency, expressions["intellectualize"]))
