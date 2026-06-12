from psychodynamic_agent.memory.heuristics import clamp_01, sanitize_summary_text, unique_stable
from psychodynamic_agent.memory.repetition_policy import (
    prohibited_expressions_for_tendency,
    repetition_pressure_score,
    safe_strategy_hint_for_tendency,
    should_generate_repetition_bias,
    tendency_from_trace,
    trigger_kind_from_decision,
)
from psychodynamic_agent.schemas.memory import (
    MemoryActivation,
    MemoryDefenseDecision,
    MemoryRepetitionTrigger,
    MemoryTrace,
    RepetitionBias,
)

_REASON_PREFIX = {
    "blocked_memory": "Blocked memory pressure",
    "felt_sense_memory": "Felt-sense memory pressure",
    "screened_memory": "Screened memory pressure",
    "deferred_action": "Deferred-action pressure",
    "condensed_pressure": "Condensed memory pressure",
    "high_defense_activation": "High-defense memory pressure",
}


def build_repetition_trigger(
    *,
    activation: MemoryActivation,
    trace: MemoryTrace,
    decision: MemoryDefenseDecision,
) -> MemoryRepetitionTrigger | None:
    if not should_generate_repetition_bias(activation=activation, trace=trace, decision=decision):
        return None
    trigger_kind = trigger_kind_from_decision(trace=trace, decision=decision)
    tendency = tendency_from_trace(trace=trace, activation=activation, decision=decision)
    public_reason = sanitize_summary_text(
        f"{_REASON_PREFIX[trigger_kind]} returned as a {tendency.replace('_', '-')} tendency."
    )
    return MemoryRepetitionTrigger(
        trigger_id=f"rep_trigger_{trace.trace_id}_{trigger_kind}",
        source_trace_ids=[trace.trace_id],
        source_activation_ranks=[activation.activation_rank],
        trigger_kind=trigger_kind,
        tendency=tendency,
        intensity=repetition_pressure_score(activation=activation, trace=trace, decision=decision),
        public_reason=public_reason,
    )


def build_repetition_bias_from_trigger(trigger: MemoryRepetitionTrigger) -> RepetitionBias:
    return RepetitionBias(
        bias_id=f"rep_bias_{trigger.trigger_id}",
        source_trace_ids=list(trigger.source_trace_ids),
        source_complex_id=None,
        tendency=trigger.tendency,
        intensity=trigger.intensity,
        safe_strategy_hint=safe_strategy_hint_for_tendency(trigger.tendency),
        prohibited_expression=prohibited_expressions_for_tendency(trigger.tendency),
    ).model_copy(deep=True)


def merge_repetition_biases(biases: list[RepetitionBias]) -> list[RepetitionBias]:
    grouped: dict[str, list[RepetitionBias]] = {}
    for bias in biases:
        grouped.setdefault(bias.tendency, []).append(bias.model_copy(deep=True))

    merged: list[RepetitionBias] = []
    for tendency, items in grouped.items():
        strongest = max(items, key=lambda item: item.intensity)
        source_trace_ids: list[str] = []
        prohibited: list[str] = []
        for item in items:
            source_trace_ids = unique_stable(source_trace_ids + item.source_trace_ids)
            prohibited = unique_stable(prohibited + item.prohibited_expression)
        merged.append(
            RepetitionBias(
                bias_id=f"rep_bias_{tendency}",
                source_trace_ids=source_trace_ids,
                source_complex_id=None,
                tendency=tendency,
                intensity=clamp_01(max(item.intensity for item in items)),
                safe_strategy_hint=strongest.safe_strategy_hint,
                prohibited_expression=prohibited,
            )
        )
    return sorted(merged, key=lambda item: (-item.intensity, item.tendency))


def repetition_label_for_view(bias: RepetitionBias) -> str:
    return sanitize_summary_text(f"{bias.tendency}:{bias.intensity:.2f}")
