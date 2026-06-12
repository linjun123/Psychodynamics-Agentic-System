from psychodynamic_agent.memory.complex_labels import (
    build_private_complex_label,
    build_public_complex_label,
    dominant_affect_labels,
    dominant_desire_labels,
    dominant_object_targets,
    dominant_threat_labels,
    refresh_complex_labels,
)
from psychodynamic_agent.memory.complex_policy import (
    initial_complex_charge,
    preferred_defenses_from_traces,
    should_join_complex,
    trace_complex_membership_score,
    update_complex_charge,
)
from psychodynamic_agent.memory.heuristics import unique_stable
from psychodynamic_agent.schemas.memory import ComplexNode, MemoryTrace


def create_complex_from_trace(*, trace: MemoryTrace, complex_id: str) -> ComplexNode:
    traces = [trace]
    dominant_affects = dominant_affect_labels(traces)
    dominant_desires = dominant_desire_labels(traces)
    dominant_threats = dominant_threat_labels(traces)
    object_targets = dominant_object_targets(traces)
    return ComplexNode(
        complex_id=complex_id,
        private_label=build_private_complex_label(
            dominant_affects=dominant_affects,
            dominant_desires=dominant_desires,
            dominant_threats=dominant_threats,
            object_targets=object_targets,
        ),
        public_label=build_public_complex_label(
            dominant_affects=dominant_affects,
            dominant_desires=dominant_desires,
            dominant_threats=dominant_threats,
            object_targets=object_targets,
        ),
        dominant_affects=dominant_affects,
        dominant_desires=dominant_desires,
        dominant_threats=dominant_threats,
        object_targets=object_targets,
        trace_ids=[trace.trace_id],
        charge=initial_complex_charge(trace),
        activation_threshold=0.5,
        preferred_defenses=preferred_defenses_from_traces(traces),
        repetition_tendencies=[],
    )


def add_trace_to_complex(
    *,
    complex_node: ComplexNode,
    trace: MemoryTrace,
    all_traces: list[MemoryTrace],
) -> ComplexNode:
    updated = complex_node.model_copy(deep=True)
    if trace.trace_id not in updated.trace_ids:
        updated.trace_ids = unique_stable(updated.trace_ids + [trace.trace_id])
    updated.charge = update_complex_charge(updated.charge, trace)
    traces_by_id = {item.trace_id: item for item in all_traces}
    member_traces = [
        traces_by_id[trace_id] for trace_id in updated.trace_ids if trace_id in traces_by_id
    ]
    if trace.trace_id not in {item.trace_id for item in member_traces}:
        member_traces.append(trace)
    updated = refresh_complex_labels(updated, member_traces)
    updated.preferred_defenses = preferred_defenses_from_traces(member_traces)
    return updated


def assign_trace_to_complexes(
    *,
    trace: MemoryTrace,
    complexes: list[ComplexNode],
    all_traces: list[MemoryTrace],
    next_complex_index: int,
) -> tuple[list[ComplexNode], list[ComplexNode], list[ComplexNode], int]:
    traces_by_id = {item.trace_id: item for item in all_traces}
    candidates = []
    for index, complex_node in enumerate(complexes):
        if trace.trace_id in complex_node.trace_ids:
            continue
        score = trace_complex_membership_score(trace, complex_node, traces_by_id)
        if should_join_complex(trace, complex_node, traces_by_id):
            candidates.append((score, index, complex_node))
    candidates.sort(key=lambda item: (-item[0], item[2].complex_id))
    join_indexes = {index for _, index, _ in candidates[:2]}

    updated_complexes: list[ComplexNode] = []
    changed_complexes: list[ComplexNode] = []
    created_complexes: list[ComplexNode] = []
    for index, complex_node in enumerate(complexes):
        if index in join_indexes:
            updated = add_trace_to_complex(
                complex_node=complex_node,
                trace=trace,
                all_traces=all_traces,
            )
            updated_complexes.append(updated)
            changed_complexes.append(updated.model_copy(deep=True))
        else:
            updated_complexes.append(complex_node.model_copy(deep=True))

    if not join_indexes:
        created = create_complex_from_trace(
            trace=trace,
            complex_id=f"cx_{next_complex_index:06d}",
        )
        updated_complexes.append(created)
        created_complexes.append(created.model_copy(deep=True))
        next_complex_index += 1

    return updated_complexes, created_complexes, changed_complexes, next_complex_index


def rebuild_complexes_from_traces(traces: list[MemoryTrace]) -> list[ComplexNode]:
    complexes: list[ComplexNode] = []
    next_complex_index = 1
    for trace in sorted(traces, key=lambda item: (item.created_turn, item.trace_id)):
        all_so_far = [
            item
            for item in traces
            if (item.created_turn, item.trace_id) <= (trace.created_turn, trace.trace_id)
        ]
        complexes, _, _, next_complex_index = assign_trace_to_complexes(
            trace=trace,
            complexes=complexes,
            all_traces=all_so_far,
            next_complex_index=next_complex_index,
        )
    return [complex_node.model_copy(deep=True) for complex_node in complexes]
