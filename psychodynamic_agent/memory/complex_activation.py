from psychodynamic_agent.memory.complex_policy import (
    complex_activation_score,
    decay_complex_charge,
    repetition_tendencies_from_biases,
    should_activate_complex,
)
from psychodynamic_agent.memory.heuristics import clamp_01, unique_stable
from psychodynamic_agent.schemas.memory import (
    ComplexNode,
    MemoryActivation,
    MemoryComplexActivation,
    MemoryTrace,
    RepetitionBias,
)

_PUBLIC_REASON = "Complex activated by related memory traces and current associative pressure."


def _biases_for_complex(
    complex_node: ComplexNode,
    repetition_biases: list[RepetitionBias],
) -> list[RepetitionBias]:
    trace_ids = set(complex_node.trace_ids)
    return [
        bias
        for bias in repetition_biases
        if bias.source_complex_id == complex_node.complex_id
        or bool(trace_ids & set(bias.source_trace_ids))
    ]


def activate_complexes(
    *,
    complexes: list[ComplexNode],
    activations: list[MemoryActivation],
    traces: list[MemoryTrace],
    repetition_biases: list[RepetitionBias] | None = None,
    current_turn: int | None = None,
) -> list[MemoryComplexActivation]:
    _ = (traces, current_turn)
    biases = repetition_biases or []
    activation_results: list[MemoryComplexActivation] = []
    for complex_node in complexes:
        score = complex_activation_score(complex_node=complex_node, activations=activations)
        if not should_activate_complex(complex_node, score):
            continue
        source_activation_trace_ids = unique_stable(
            [
                activation.trace_id
                for activation in activations
                if activation.trace_id in complex_node.trace_ids
            ]
        )
        related_biases = _biases_for_complex(complex_node, biases)
        repetition_tendencies = unique_stable(
            list(complex_node.repetition_tendencies)
            + repetition_tendencies_from_biases(related_biases)
        )
        activation_results.append(
            MemoryComplexActivation(
                complex_id=complex_node.complex_id,
                public_label=complex_node.public_label,
                private_label=complex_node.private_label,
                source_trace_ids=list(complex_node.trace_ids),
                source_activation_trace_ids=source_activation_trace_ids,
                activation_score=score,
                charge=complex_node.charge,
                dominant_public_affects=list(complex_node.dominant_affects),
                preferred_defenses=list(complex_node.preferred_defenses),
                repetition_tendencies=repetition_tendencies,
                public_reason=_PUBLIC_REASON,
            )
        )
    return sorted(
        activation_results,
        key=lambda item: (-item.activation_score, -item.charge, item.public_label),
    )


def update_complexes_after_activation(
    *,
    complexes: list[ComplexNode],
    activations: list[MemoryComplexActivation],
    current_turn: int | None = None,
) -> list[ComplexNode]:
    activations_by_id = {activation.complex_id: activation for activation in activations}
    updated_complexes: list[ComplexNode] = []
    for complex_node in complexes:
        updated = complex_node.model_copy(deep=True)
        activation = activations_by_id.get(updated.complex_id)
        if activation is None:
            updated.charge = decay_complex_charge(updated.charge)
        else:
            updated.charge = clamp_01(max(updated.charge, activation.activation_score))
            updated.repetition_tendencies = unique_stable(
                updated.repetition_tendencies + activation.repetition_tendencies
            )
            if current_turn is not None:
                updated.last_activated_turn = current_turn
        updated_complexes.append(updated)
    return updated_complexes
