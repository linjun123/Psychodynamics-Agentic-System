from psychodynamic_agent.memory.conscious_projection import affective_tone_from_trace
from psychodynamic_agent.memory.distortion_policy import safe_displacement_target
from psychodynamic_agent.memory.heuristics import clamp_01, sanitize_summary_text, unique_stable
from psychodynamic_agent.schemas.memory import (
    ConsciousMemoryCue,
    MemoryActivation,
    MemoryDefenseDecision,
    MemoryTrace,
    MemoryTransformationRecord,
)


def _symbolic_focus(activation: MemoryActivation, trace: MemoryTrace) -> str:
    safe_object = safe_displacement_target(trace) if trace.object_targets else "symbolic pressure"
    values = unique_stable(
        activation.matched_salient_symbols + trace.salient_symbols + [safe_object], limit=4
    )
    return sanitize_summary_text(" and ".join(values) if values else "symbolic pressure")


def build_screen_memory_cue(
    *,
    activation: MemoryActivation,
    trace: MemoryTrace,
    decision: MemoryDefenseDecision,
) -> ConsciousMemoryCue:
    focus = _symbolic_focus(activation, trace)
    return ConsciousMemoryCue(
        cue_id=f"screen_{trace.trace_id}",
        source_trace_ids=[trace.trace_id],
        cue_type="screen_memory",
        public_summary=f"A screened memory cue is available around {focus}.",
        affective_tone=affective_tone_from_trace(trace, activation),
        intensity=clamp_01(max(activation.association_score, decision.defense_pressure)),
        recommended_handling="Handle indirectly through symbolic or structural language.",
    )


def build_screen_memory_record(
    *,
    activation: MemoryActivation,
    trace: MemoryTrace,
    decision: MemoryDefenseDecision,
    cue: ConsciousMemoryCue,
) -> MemoryTransformationRecord:
    _ = activation
    return MemoryTransformationRecord(
        source_trace_ids=[trace.trace_id],
        mechanism="screen_memory",
        private_input_summary=trace.private_core_summary,
        public_output_summary=cue.public_summary,
        access_mode_before=decision.original_accessibility,
        access_mode_after=decision.decided_accessibility,
        defense_reason=decision.public_reason,
        llm_generated=False,
        guard_result="passed",
    )
