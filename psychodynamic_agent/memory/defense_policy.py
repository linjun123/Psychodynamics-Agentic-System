from psychodynamic_agent.memory.heuristics import clamp_01
from psychodynamic_agent.schemas.memory import MemoryAccessMode, MemoryMechanism


def defense_pressure_score(
    *,
    association_score: float,
    defense_level: float,
    repression_pressure: float,
) -> float:
    return clamp_01(
        (0.45 * repression_pressure) + (0.35 * defense_level) + (0.20 * association_score)
    )


def choose_defensive_access(
    *,
    trace_accessibility: MemoryAccessMode,
    association_score: float,
    defense_level: float,
    repression_pressure: float,
) -> MemoryAccessMode:
    if trace_accessibility == "blocked_action_only":
        return "blocked_action_only"
    if repression_pressure >= 0.85:
        return "blocked_action_only"
    if repression_pressure >= 0.70:
        return "felt_sense_only"
    if trace_accessibility in {"condensed", "displaced"}:
        return trace_accessibility
    if trace_accessibility == "screened":
        return "screened"
    if defense_level >= 0.65:
        return "screened"
    if (
        defense_pressure_score(
            association_score=association_score,
            defense_level=defense_level,
            repression_pressure=repression_pressure,
        )
        >= 0.70
    ):
        return "screened"
    return "direct"


def mechanism_for_access(access: MemoryAccessMode) -> MemoryMechanism:
    if access == "screened":
        return "screen_memory"
    if access == "condensed":
        return "condensation"
    if access == "displaced":
        return "displacement"
    if access == "felt_sense_only":
        return "felt_sense_only"
    if access == "blocked_action_only":
        return "blocked_action_only"
    return "direct"


def emits_conscious_cue(access: MemoryAccessMode) -> bool:
    return access in {"direct", "screened", "felt_sense_only"}


def public_defense_reason(access: MemoryAccessMode) -> str:
    if access == "condensed":
        return "Trace is available only through a condensed transformation record."
    if access == "displaced":
        return "Trace is available only through a displaced transformation record."
    if access == "screened":
        return "Trace is available only through a screened conscious cue."
    if access == "felt_sense_only":
        return "Trace is available only as a diffuse affective cue."
    if access == "blocked_action_only":
        return "Trace is blocked from conscious view by defensive pressure."
    return "Trace is available as a direct conscious memory cue."
