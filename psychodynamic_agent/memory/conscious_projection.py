from psychodynamic_agent.memory.heuristics import (
    clamp_01,
    sanitize_summary_text,
    truncate_summary,
    unique_stable,
)
from psychodynamic_agent.memory.repetition_generation import repetition_label_for_view
from psychodynamic_agent.schemas.memory import (
    ConsciousMemoryCue,
    ConsciousMemoryView,
    MemoryActivation,
    MemoryComplexActivation,
    MemoryDefenseDecision,
    MemoryDistortionResult,
    MemoryProjectionResult,
    MemoryRepetitionResult,
    MemoryTrace,
    MemoryTransformationRecord,
)

_TONE_BY_SYMBOL = {
    "loss_anxiety": "loss-anxious",
    "evaluation_sensitivity": "evaluation-sensitive",
    "boundary_pressure": "boundary-focused",
    "recognition_pressure": "recognition-oriented",
    "task_mastery": "structure-oriented",
    "curiosity": "curious",
}

_HANDLING_BY_ACCESS = {
    "direct": "May be referenced as a conscious-compatible memory cue.",
    "screened": "Handle indirectly through symbolic or structural language.",
    "felt_sense_only": "Treat as affective pressure rather than factual recall.",
}

_CUE_TYPE_BY_ACCESS = {
    "direct": "direct_memory",
    "screened": "screen_memory",
    "felt_sense_only": "felt_sense",
}


def affective_tone_from_trace(trace: MemoryTrace, activation: MemoryActivation) -> str:
    for symbol in unique_stable(activation.matched_salient_symbols + trace.salient_symbols):
        tone = _TONE_BY_SYMBOL.get(symbol)
        if tone:
            return tone
    return "neutral"


def public_summary_for_direct(trace: MemoryTrace, activation: MemoryActivation) -> str:
    event = truncate_summary(sanitize_summary_text(trace.surface_event_summary), 140)
    reason = truncate_summary(sanitize_summary_text(activation.public_reason), 90)
    if reason:
        return f"{event} ({reason})"
    return event


def public_summary_for_screened(trace: MemoryTrace, activation: MemoryActivation) -> str:
    symbols = unique_stable(activation.matched_salient_symbols + trace.salient_symbols, limit=3)
    if symbols:
        symbolic_focus = " and ".join(symbols)
        return f"A related memory trace is available as a screened cue around {symbolic_focus}."
    return "A related memory trace is available as a screened cue around symbolic pressure."


def public_summary_for_felt_sense(trace: MemoryTrace, activation: MemoryActivation) -> str:
    _ = (trace, activation)
    return "A related trace contributes diffuse affective pressure without direct memory access."


def build_conscious_cue(
    *,
    activation: MemoryActivation,
    trace: MemoryTrace,
    decision: MemoryDefenseDecision,
) -> ConsciousMemoryCue | None:
    if not decision.emits_conscious_cue or decision.conscious_access not in _CUE_TYPE_BY_ACCESS:
        return None
    if decision.conscious_access == "direct":
        public_summary = public_summary_for_direct(trace, activation)
    elif decision.conscious_access == "screened":
        public_summary = public_summary_for_screened(trace, activation)
    else:
        public_summary = public_summary_for_felt_sense(trace, activation)
    return ConsciousMemoryCue(
        cue_id=f"cue_{trace.trace_id}",
        source_trace_ids=[trace.trace_id],
        cue_type=_CUE_TYPE_BY_ACCESS[decision.conscious_access],
        public_summary=public_summary,
        affective_tone=affective_tone_from_trace(trace, activation),
        intensity=clamp_01(max(activation.association_score, decision.defense_pressure)),
        recommended_handling=_HANDLING_BY_ACCESS.get(decision.conscious_access),
    )


def transformation_record_for_decision(
    *,
    trace: MemoryTrace,
    decision: MemoryDefenseDecision,
    cue: ConsciousMemoryCue | None,
) -> MemoryTransformationRecord:
    return MemoryTransformationRecord(
        source_trace_ids=[decision.trace_id],
        mechanism=decision.mechanism,
        private_input_summary=trace.private_core_summary,
        public_output_summary=cue.public_summary if cue is not None else decision.public_reason,
        access_mode_before=decision.original_accessibility,
        access_mode_after=decision.decided_accessibility,
        defense_reason=decision.public_reason,
        llm_generated=False,
        llm_operation_id=None,
        guard_result="passed",
    )


def build_conscious_memory_view(
    *,
    activations: list[MemoryActivation],
    traces: list[MemoryTrace],
    decisions: list[MemoryDefenseDecision],
    max_cues: int = 5,
    distortion_result: MemoryDistortionResult | None = None,
    repetition_result: MemoryRepetitionResult | None = None,
    complex_activations: list[MemoryComplexActivation] | None = None,
) -> MemoryProjectionResult:
    activations_by_id = {activation.trace_id: activation for activation in activations}
    traces_by_id = {trace.trace_id: trace for trace in traces}
    active_cues: list[ConsciousMemoryCue] = []
    transformation_chain: list[MemoryTransformationRecord] = []
    cue_limit = max(int(max_cues), 0)
    suppressed_trace_ids: set[str] = set()
    represented_trace_ids: set[str] = set()
    represented_record_ids: set[str] = set()
    distortion_decisions = []
    deferred_action_updates = []
    repetition_biases = []
    repetition_triggers = []

    if distortion_result is not None:
        for cue in distortion_result.distorted_cues:
            if len(active_cues) < cue_limit:
                active_cues.append(cue.model_copy(deep=True))
            represented_trace_ids.update(cue.source_trace_ids)
        suppressed_trace_ids.update(distortion_result.suppressed_trace_ids)
        for record in distortion_result.transformation_chain:
            transformation_chain.append(record.model_copy(deep=True))
            represented_record_ids.update(record.source_trace_ids)
        distortion_decisions = [
            decision.model_copy(deep=True)
            for decision in distortion_result.distortion_decisions
        ]
        deferred_action_updates = [
            update.model_copy(deep=True)
            for update in distortion_result.deferred_action_updates
        ]

    if repetition_result is not None:
        repetition_biases = [
            bias.model_copy(deep=True) for bias in repetition_result.repetition_biases
        ]
        repetition_triggers = [
            trigger.model_copy(deep=True) for trigger in repetition_result.triggers
        ]

    for decision in sorted(decisions, key=lambda item: item.activation_rank):
        activation = activations_by_id.get(decision.trace_id)
        trace = traces_by_id.get(decision.trace_id)
        if activation is None or trace is None:
            continue
        if decision.trace_id in suppressed_trace_ids or decision.trace_id in represented_trace_ids:
            cue = None
        else:
            cue = build_conscious_cue(activation=activation, trace=trace, decision=decision)
            if cue is not None and len(active_cues) < cue_limit:
                active_cues.append(cue.model_copy(deep=True))
        if decision.trace_id not in represented_record_ids:
            transformation_chain.append(
                transformation_record_for_decision(trace=trace, decision=decision, cue=cue)
            )

    memory_pressure = max((activation.association_score for activation in activations), default=0.0)
    defense_pressure = max((decision.defense_pressure for decision in decisions), default=0.0)
    complex_labels = unique_stable(
        [activation.public_label for activation in (complex_activations or [])],
        limit=5,
    )
    view = ConsciousMemoryView(
        active_cues=active_cues,
        dominant_complex_labels=complex_labels,
        repetition_biases=[repetition_label_for_view(bias) for bias in repetition_biases],
        memory_pressure=clamp_01(memory_pressure),
        defense_pressure=clamp_01(defense_pressure),
        repetition_pressure=(
            repetition_result.repetition_pressure if repetition_result is not None else 0.0
        ),
        caution=clamp_01(defense_pressure),
    )
    return MemoryProjectionResult(
        conscious_memory_view=view,
        defense_decisions=[decision.model_copy(deep=True) for decision in decisions],
        transformation_chain=[record.model_copy(deep=True) for record in transformation_chain],
        deferred_action_updates=deferred_action_updates,
        distortion_decisions=distortion_decisions,
        repetition_biases=repetition_biases,
        repetition_triggers=repetition_triggers,
        complex_activations=[
            activation.model_copy(deep=True) for activation in (complex_activations or [])
        ],
    )
