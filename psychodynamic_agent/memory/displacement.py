from psychodynamic_agent.memory.conscious_projection import affective_tone_from_trace
from psychodynamic_agent.memory.heuristics import clamp_01, sanitize_summary_text
from psychodynamic_agent.schemas.memory import (
    ConsciousMemoryCue,
    MemoryActivation,
    MemoryDefenseDecision,
    MemoryTrace,
    MemoryTransformationRecord,
)


def build_displaced_memory_cue(
    *,
    activation: MemoryActivation,
    trace: MemoryTrace,
    decision: MemoryDefenseDecision,
    displaced_object: str,
) -> ConsciousMemoryCue:
    target = sanitize_summary_text(displaced_object)
    return ConsciousMemoryCue(
        cue_id=f"displaced_{trace.trace_id}",
        source_trace_ids=[trace.trace_id],
        cue_type="displaced_memory",
        public_summary=(
            "A related memory trace is displaced from a risky object focus "
            f"toward {target}."
        ),
        affective_tone=affective_tone_from_trace(trace, activation),
        intensity=clamp_01(max(activation.association_score, decision.defense_pressure)),
        recommended_handling=(
            "Use the safer symbolic target rather than direct object interpretation."
        ),
    )


def build_displacement_record(
    *,
    activation: MemoryActivation,
    trace: MemoryTrace,
    decision: MemoryDefenseDecision,
    cue: ConsciousMemoryCue,
) -> MemoryTransformationRecord:
    _ = activation
    return MemoryTransformationRecord(
        source_trace_ids=[trace.trace_id],
        mechanism="displacement",
        private_input_summary=trace.private_core_summary,
        public_output_summary=cue.public_summary,
        access_mode_before=decision.original_accessibility,
        access_mode_after="displaced",
        defense_reason=decision.public_reason,
        llm_generated=False,
        guard_result="passed",
    )
