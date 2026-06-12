from psychodynamic_agent.memory.heuristics import clamp_01, sanitize_summary_text, unique_stable
from psychodynamic_agent.memory.repetition_generation import (
    build_repetition_bias_from_trigger,
    build_repetition_trigger,
    merge_repetition_biases,
)
from psychodynamic_agent.schemas.memory import (
    MemoryActivation,
    MemoryDefenseDecision,
    MemoryDeferredActionUpdate,
    MemoryDistortionDecision,
    MemoryRepetitionResult,
    MemoryRepetitionTendency,
    MemoryRepetitionTrigger,
    MemoryTrace,
)


def _tendency_from_symbols(symbols: list[str]) -> MemoryRepetitionTendency:
    symbol_set = set(symbols)
    if "evaluation_sensitivity" in symbol_set or "recognition_pressure" in symbol_set:
        return "over_explain"
    if "loss_anxiety" in symbol_set:
        return "seek_reassurance"
    if "boundary_pressure" in symbol_set:
        return "control_uncertainty"
    if "task_mastery" in symbol_set or "task_structure" in symbol_set:
        return "ask_for_structure"
    return "intellectualize"


class MemoryRepetitionEngine:
    def build_repetition_result(
        self,
        *,
        activations: list[MemoryActivation],
        traces: list[MemoryTrace],
        decisions: list[MemoryDefenseDecision],
        distortion_decisions: list[MemoryDistortionDecision] | None = None,
        deferred_action_updates: list[MemoryDeferredActionUpdate] | None = None,
        max_biases: int = 5,
    ) -> MemoryRepetitionResult:
        activations_by_id = {activation.trace_id: activation for activation in activations}
        traces_by_id = {trace.trace_id: trace for trace in traces}
        triggers: list[MemoryRepetitionTrigger] = []

        for decision in sorted(decisions, key=lambda item: item.activation_rank):
            activation = activations_by_id.get(decision.trace_id)
            trace = traces_by_id.get(decision.trace_id)
            if activation is None or trace is None:
                continue
            trigger = build_repetition_trigger(
                activation=activation, trace=trace, decision=decision
            )
            if trigger is not None:
                triggers.append(trigger.model_copy(deep=True))

        for update in deferred_action_updates or []:
            if update.update_strength < 0.55:
                continue
            source_trace_ids = unique_stable([update.old_trace_id, update.trigger_trace_id])
            triggers.append(
                MemoryRepetitionTrigger(
                    trigger_id=f"rep_trigger_deferred_{update.old_trace_id}_{update.trigger_trace_id}",
                    source_trace_ids=source_trace_ids,
                    source_activation_ranks=[],
                    trigger_kind="deferred_action",
                    tendency=_tendency_from_symbols(update.supporting_symbols),
                    intensity=clamp_01(update.update_strength),
                    public_reason=sanitize_summary_text(
                        "Deferred-action pressure returned as a repeated strategy tendency."
                    ),
                )
            )

        for decision in distortion_decisions or []:
            if decision.mode != "condensation" or decision.intensity < 0.55:
                continue
            symbols: list[str] = []
            reason = decision.public_reason.lower()
            if "evaluation" in reason or "recognition" in reason:
                symbols.append("evaluation_sensitivity")
            for trace_id in decision.source_trace_ids:
                trace = traces_by_id.get(trace_id)
                if trace is not None:
                    symbols.extend(trace.salient_symbols)
            triggers.append(
                MemoryRepetitionTrigger(
                    trigger_id=f"rep_trigger_condensed_{'_'.join(decision.source_trace_ids)}",
                    source_trace_ids=unique_stable(decision.source_trace_ids),
                    source_activation_ranks=list(decision.source_activation_ranks),
                    trigger_kind="condensed_pressure",
                    tendency=_tendency_from_symbols(symbols),
                    intensity=clamp_01(decision.intensity),
                    public_reason=sanitize_summary_text(
                        "Condensed memory pressure returned as a composite repetition tendency."
                    ),
                )
            )

        biases = [build_repetition_bias_from_trigger(trigger) for trigger in triggers]
        limit = max(int(max_biases), 0)
        merged_biases = merge_repetition_biases(biases)[:limit]
        pressure = max((bias.intensity for bias in merged_biases), default=0.0)
        return MemoryRepetitionResult(
            triggers=[trigger.model_copy(deep=True) for trigger in triggers],
            repetition_biases=[bias.model_copy(deep=True) for bias in merged_biases],
            repetition_pressure=clamp_01(pressure),
        )
