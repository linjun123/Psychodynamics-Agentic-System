from collections.abc import Mapping, Sequence

from psychodynamic_agent.memory.heuristics import (
    clamp_01,
    keyword_score,
    level_to_float,
    safe_get,
    truncate_summary,
    unique_stable,
)
from psychodynamic_agent.memory.signature_extraction import (
    AUTONOMY_KEYWORDS,
    MASTERY_KEYWORDS,
    RECOGNITION_KEYWORDS,
)
from psychodynamic_agent.schemas.memory import (
    AffectiveSignature,
    DesireSignature,
    MemoryAccessMode,
    ThreatSignature,
)

_OBJECT_KEYWORD_FAMILIES = [
    ("task_structure", MASTERY_KEYWORDS),
    ("recognition", RECOGNITION_KEYWORDS),
    ("authority", ["authority", "boss", "teacher", "manager", "权威", "领导", "老师"]),
    (
        "relationship",
        ["relationship", "friend", "partner", "family", "关系", "朋友", "伴侣", "家人"],
    ),
    ("safety", ["safe", "safety", "risk", "threat", "安全", "风险", "威胁"]),
    ("autonomy", AUTONOMY_KEYWORDS),
]


def _text_from_debug(value: object) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, Mapping):
        return " ".join(_text_from_debug(item) for item in value.values())
    if isinstance(value, Sequence) and not isinstance(value, bytes | bytearray):
        return " ".join(_text_from_debug(item) for item in value)
    return ""


def extract_object_targets(safe_debug_trace: dict | None, user_input: str) -> list[str]:
    cathexis = safe_get(safe_debug_trace, ("id_output", "object_cathexis"), None)
    if isinstance(cathexis, Sequence) and not isinstance(cathexis, bytes | bytearray | str):
        ranked: list[tuple[float, str]] = []
        for item in cathexis:
            if not isinstance(item, Mapping):
                continue
            target = item.get("target")
            if not isinstance(target, str) or len(target.strip()) > 80:
                continue
            ranked.append((clamp_01(item.get("intensity"), 0.0), target.strip()))
        if ranked:
            ranked.sort(key=lambda pair: (-pair[0], pair[1]))
            return unique_stable([target for _, target in ranked], limit=5)

    fallback = [
        label
        for label, keywords in _OBJECT_KEYWORD_FAMILIES
        if keyword_score(user_input, keywords) > 0.0
    ]
    return unique_stable(fallback, limit=5)


def build_salient_symbols(
    affective: AffectiveSignature,
    desire: DesireSignature,
    threat: ThreatSignature,
) -> list[str]:
    symbols: list[str] = []
    if max(affective.fear_of_loss, threat.loss) >= 0.5:
        symbols.append("loss_anxiety")
    if max(affective.shame, threat.humiliation) >= 0.25:
        symbols.append("evaluation_sensitivity")
    if max(threat.boundary_violation, threat.control) >= 0.5:
        symbols.append("boundary_pressure")
    if desire.recognition >= 0.25:
        symbols.append("recognition_pressure")
    if desire.mastery >= 0.25:
        symbols.append("task_mastery")
    if max(affective.curiosity, desire.novelty) >= 0.5:
        symbols.append("curiosity")
    return unique_stable(symbols)


def build_surface_event_summary(created_turn: int, user_input: str) -> str:
    snippet = truncate_summary(user_input, 120)
    if not snippet:
        return f"Turn {created_turn} user input recorded for psychoanalytic memory simulation."
    return (
        f"Turn {created_turn} user input recorded for psychoanalytic memory simulation: "
        f"{snippet}"
    )


def build_private_core_summary(
    affective: AffectiveSignature,
    desire: DesireSignature,
    threat: ThreatSignature,
    salient_symbols: list[str],
) -> str:
    del affective, desire, threat
    if salient_symbols:
        symbolic_text = ", ".join(salient_symbols[:4])
    else:
        symbolic_text = "neutral affective registration"
    return (
        "Simulation trace links this turn with "
        f"{symbolic_text}. This is a heuristic memory interpretation, not a clinical "
        "diagnosis or claim about historical truth."
    )


def compute_defense_level(
    safe_debug_trace: dict | None,
    affective: AffectiveSignature,
    threat: ThreatSignature,
) -> float:
    del affective
    return clamp_01(
        max(
            0.2,
            clamp_01(safe_get(safe_debug_trace, ("ego_affect_summary", "caution_need"), 0.0)),
            clamp_01(safe_get(safe_debug_trace, ("affect_trace", "boundary_need"), 0.0)),
            level_to_float(
                safe_get(safe_debug_trace, ("public_affect_dynamics", "caution_level"), None),
                0.0,
            ),
            threat.exposure,
            threat.boundary_violation,
        )
    )


def compute_repression_pressure(
    affective: AffectiveSignature,
    threat: ThreatSignature,
    defense_level: float,
) -> float:
    return clamp_01(
        (0.4 * affective.avoidance)
        + (0.3 * defense_level)
        + (0.2 * threat.humiliation)
        + (0.1 * threat.rejection)
    )


def choose_accessibility(
    defense_level: float,
    repression_pressure: float,
) -> MemoryAccessMode:
    if repression_pressure >= 0.80:
        return "blocked_action_only"
    if defense_level >= 0.65 or repression_pressure >= 0.60:
        return "screened"
    return "direct"
