from collections import Counter

from psychodynamic_agent.memory.heuristics import sanitize_summary_text, unique_stable
from psychodynamic_agent.schemas.memory import ComplexNode, MemoryTrace

_PROTECTED_FRAGMENTS = [
    "private_core_summary",
    "system_prompt",
    "developer_message",
    "provider_private",
    "latent_alignment",
    "sealed_ultimate_need",
    "u_star",
    "u*",
]


def _sanitize_label(label: str) -> str:
    sanitized = sanitize_summary_text(label).casefold().replace(" ", "_").replace("-", "_")
    for fragment in _PROTECTED_FRAGMENTS:
        sanitized = sanitized.replace(fragment, "protected")
    return "_".join(part for part in sanitized.split("_") if part)


def _ranked_labels(
    scores: dict[str, float], *, limit: int = 4, threshold: float = 0.20
) -> list[str]:
    ranked = [
        label
        for label, score in sorted(scores.items(), key=lambda item: (-item[1], item[0]))
        if score >= threshold
    ]
    return unique_stable(ranked, limit=limit)


def dominant_affect_labels(traces: list[MemoryTrace]) -> list[str]:
    if not traces:
        return []
    scores = {
        "evaluation_sensitivity": max(t.affective_signature.shame for t in traces),
        "loss_anxiety": max(t.affective_signature.fear_of_loss for t in traces),
        "conflict_pressure": max(
            max(t.affective_signature.aggression, t.affective_signature.irritation) for t in traces
        ),
        "curiosity": max(t.affective_signature.curiosity for t in traces),
        "avoidance_pressure": max(t.affective_signature.avoidance for t in traces),
    }
    return _ranked_labels(scores)


def dominant_desire_labels(traces: list[MemoryTrace]) -> list[str]:
    if not traces:
        return []
    scores = {
        "recognition_pressure": max(t.desire_signature.recognition for t in traces),
        "attachment_pressure": max(t.desire_signature.attachment for t in traces),
        "autonomy_pressure": max(t.desire_signature.autonomy for t in traces),
        "task_mastery": max(t.desire_signature.mastery for t in traces),
        "safety_seeking": max(t.desire_signature.safety for t in traces),
        "novelty_seeking": max(t.desire_signature.novelty for t in traces),
    }
    return _ranked_labels(scores)


def dominant_threat_labels(traces: list[MemoryTrace]) -> list[str]:
    if not traces:
        return []
    scores = {
        "humiliation_threat": max(t.threat_signature.humiliation for t in traces),
        "rejection_threat": max(t.threat_signature.rejection for t in traces),
        "loss_threat": max(t.threat_signature.loss for t in traces),
        "exposure_threat": max(t.threat_signature.exposure for t in traces),
        "boundary_threat": max(
            max(t.threat_signature.control, t.threat_signature.boundary_violation) for t in traces
        ),
        "failure_threat": max(t.threat_signature.failure for t in traces),
    }
    return _ranked_labels(scores)


def dominant_object_targets(traces: list[MemoryTrace], limit: int = 5) -> list[str]:
    counts: Counter[str] = Counter()
    for trace in traces:
        for target in trace.object_targets:
            normalized = _sanitize_label(target)
            if not normalized:
                continue
            counts[normalized] += 1
    return [
        label for label, _ in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit]
    ]


def build_public_complex_label(
    *,
    dominant_affects: list[str],
    dominant_desires: list[str],
    dominant_threats: list[str],
    object_targets: list[str],
) -> str:
    _ = object_targets
    affects = set(dominant_affects)
    desires = set(dominant_desires)
    threats = set(dominant_threats)
    if "evaluation_sensitivity" in affects and "humiliation_threat" in threats:
        return "evaluation_sensitivity_cluster"
    if "loss_anxiety" in affects and ({"rejection_threat", "loss_threat"} & threats):
        return "loss_anxiety_cluster"
    if "boundary_threat" in threats or "autonomy_pressure" in desires:
        return "boundary_pressure_cluster"
    if "recognition_pressure" in desires:
        return "recognition_pressure_cluster"
    if "task_mastery" in desires:
        return "task_structure_cluster"
    return "symbolic_memory_cluster"


def build_private_complex_label(
    *,
    dominant_affects: list[str],
    dominant_desires: list[str],
    dominant_threats: list[str],
    object_targets: list[str],
) -> str:
    _ = object_targets
    affects = set(dominant_affects)
    desires = set(dominant_desires)
    threats = set(dominant_threats)
    if "evaluation_sensitivity" in affects and "humiliation_threat" in threats:
        return _sanitize_label("authority_evaluation_complex")
    if "loss_anxiety" in affects and ({"rejection_threat", "loss_threat"} & threats):
        return _sanitize_label("loss_rejection_complex")
    if "boundary_threat" in threats or "autonomy_pressure" in desires:
        return _sanitize_label("boundary_control_complex")
    if "recognition_pressure" in desires:
        return _sanitize_label("recognition_hunger_complex")
    return _sanitize_label("private_symbolic_complex")


def refresh_complex_labels(complex_node: ComplexNode, traces: list[MemoryTrace]) -> ComplexNode:
    refreshed = complex_node.model_copy(deep=True)
    dominant_affects = dominant_affect_labels(traces)
    dominant_desires = dominant_desire_labels(traces)
    dominant_threats = dominant_threat_labels(traces)
    object_targets = dominant_object_targets(traces)
    refreshed.dominant_affects = dominant_affects
    refreshed.dominant_desires = dominant_desires
    refreshed.dominant_threats = dominant_threats
    refreshed.object_targets = object_targets
    refreshed.public_label = build_public_complex_label(
        dominant_affects=dominant_affects,
        dominant_desires=dominant_desires,
        dominant_threats=dominant_threats,
        object_targets=object_targets,
    )
    refreshed.private_label = build_private_complex_label(
        dominant_affects=dominant_affects,
        dominant_desires=dominant_desires,
        dominant_threats=dominant_threats,
        object_targets=object_targets,
    )
    return refreshed
