from psychodynamic_agent.memory.heuristics import clamp_01, unique_stable
from psychodynamic_agent.memory.similarity import list_overlap_score, signature_similarity
from psychodynamic_agent.schemas.memory import (
    ComplexNode,
    MemoryActivation,
    MemoryTrace,
    RepetitionBias,
)

_JOIN_THRESHOLD = 0.55
_SYMBOLIC_JOIN_THRESHOLD = 0.45


def trace_complex_similarity(left: MemoryTrace, right: MemoryTrace) -> float:
    affect = signature_similarity(left.affective_signature, right.affective_signature)
    desire = signature_similarity(left.desire_signature, right.desire_signature)
    threat = signature_similarity(left.threat_signature, right.threat_signature)
    objects = list_overlap_score(left.object_targets, right.object_targets)
    symbols = list_overlap_score(left.salient_symbols, right.salient_symbols)
    return clamp_01(
        (0.30 * affect) + (0.20 * desire) + (0.25 * threat) + (0.15 * symbols) + (0.10 * objects)
    )


def trace_complex_membership_score(
    trace: MemoryTrace,
    complex_node: ComplexNode,
    traces_by_id: dict[str, MemoryTrace],
) -> float:
    representative_scores = [
        trace_complex_similarity(trace, member)
        for trace_id in complex_node.trace_ids
        if (member := traces_by_id.get(trace_id)) is not None
    ]
    base_score = max(representative_scores, default=0.0)
    object_score = list_overlap_score(trace.object_targets, complex_node.object_targets)
    label_score = list_overlap_score(trace.salient_symbols, complex_node.dominant_affects)
    return clamp_01(
        max(base_score, (0.75 * base_score) + (0.15 * object_score) + (0.10 * label_score))
    )


def should_join_complex(
    trace: MemoryTrace,
    complex_node: ComplexNode,
    traces_by_id: dict[str, MemoryTrace],
) -> bool:
    if trace_complex_membership_score(trace, complex_node, traces_by_id) >= _JOIN_THRESHOLD:
        return True
    has_shared_symbol = (
        list_overlap_score(trace.salient_symbols, complex_node.dominant_affects) > 0.0
    )
    if not has_shared_symbol:
        for trace_id in complex_node.trace_ids:
            member = traces_by_id.get(trace_id)
            if (
                member is not None
                and list_overlap_score(trace.salient_symbols, member.salient_symbols) >= 0.5
            ):
                has_shared_symbol = True
                break
    if not has_shared_symbol:
        return False
    representative_affect = max(
        (
            signature_similarity(trace.affective_signature, member.affective_signature)
            for trace_id in complex_node.trace_ids
            if (member := traces_by_id.get(trace_id)) is not None
        ),
        default=0.0,
    )
    representative_threat = max(
        (
            signature_similarity(trace.threat_signature, member.threat_signature)
            for trace_id in complex_node.trace_ids
            if (member := traces_by_id.get(trace_id)) is not None
        ),
        default=0.0,
    )
    return max(representative_affect, representative_threat) >= _SYMBOLIC_JOIN_THRESHOLD


def initial_complex_charge(trace: MemoryTrace) -> float:
    threat_pressure = max(
        trace.threat_signature.humiliation,
        trace.threat_signature.rejection,
        trace.threat_signature.loss,
        trace.threat_signature.boundary_violation,
    )
    return clamp_01(
        (0.30 * trace.affective_signature.arousal)
        + (0.25 * threat_pressure)
        + (0.20 * trace.defense_level)
        + (0.15 * trace.repression_pressure)
        + (0.10 * min(trace.activation_count / 5.0, 1.0))
    )


def update_complex_charge(
    existing_charge: float,
    trace: MemoryTrace,
    activation_boost: float = 0.0,
) -> float:
    return clamp_01(
        (0.75 * existing_charge)
        + (0.20 * initial_complex_charge(trace))
        + (0.05 * activation_boost)
    )


def decay_complex_charge(charge: float, decay: float = 0.02) -> float:
    return clamp_01(charge - decay)


def complex_activation_score(
    *,
    complex_node: ComplexNode,
    activations: list[MemoryActivation],
) -> float:
    complex_trace_ids = set(complex_node.trace_ids)
    if not complex_trace_ids or not activations:
        return clamp_01(0.30 * complex_node.charge)
    matching_scores = [
        activation.association_score
        for activation in activations
        if activation.trace_id in complex_trace_ids
    ]
    max_activation = max(matching_scores, default=0.0)
    match_ratio = len(
        set(a.trace_id for a in activations if a.trace_id in complex_trace_ids)
    ) / len(complex_trace_ids)
    return clamp_01((0.50 * max_activation) + (0.30 * complex_node.charge) + (0.20 * match_ratio))


def should_activate_complex(complex_node: ComplexNode, activation_score: float) -> bool:
    return activation_score >= complex_node.activation_threshold


def preferred_defenses_from_traces(traces: list[MemoryTrace]) -> list[str]:
    defenses: list[str] = []
    for trace in traces:
        if trace.accessibility == "screened":
            defenses.append("screening")
        if trace.accessibility == "condensed":
            defenses.append("condensation")
        if trace.accessibility == "displaced":
            defenses.append("displacement")
        if trace.accessibility == "blocked_action_only":
            defenses.append("blocking")
        if trace.repression_pressure >= 0.65:
            defenses.append("avoidance")
        if trace.defense_level >= 0.70:
            defenses.append("screening")
    return unique_stable(defenses)


def repetition_tendencies_from_biases(biases: list[RepetitionBias]) -> list[str]:
    strongest_by_tendency: dict[str, float] = {}
    for bias in biases:
        strongest_by_tendency[bias.tendency] = max(
            strongest_by_tendency.get(bias.tendency, 0.0),
            bias.intensity,
        )
    return [
        tendency
        for tendency, _ in sorted(
            strongest_by_tendency.items(),
            key=lambda item: (-item[1], item[0]),
        )
    ]
