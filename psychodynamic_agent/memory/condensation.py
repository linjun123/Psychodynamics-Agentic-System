import hashlib

from psychodynamic_agent.memory.conscious_projection import affective_tone_from_trace
from psychodynamic_agent.memory.distortion_policy import (
    condensation_group_key,
    safe_displacement_target,
    should_condense_group,
)
from psychodynamic_agent.memory.heuristics import clamp_01, sanitize_summary_text, unique_stable
from psychodynamic_agent.schemas.memory import (
    ConsciousMemoryCue,
    MemoryActivation,
    MemoryDefenseDecision,
    MemoryTrace,
    MemoryTransformationRecord,
)


def _by_id(items: list[MemoryTrace] | list[MemoryActivation] | list[MemoryDefenseDecision]):
    return {item.trace_id: item for item in items}


def _group_key(
    trace: MemoryTrace,
    activation: MemoryActivation,
    decision: MemoryDefenseDecision,
) -> str | None:
    if decision.decided_accessibility == "blocked_action_only":
        return None
    key = condensation_group_key(trace, activation)
    if key is None:
        return None
    if decision.decided_accessibility == "displaced" or trace.accessibility == "displaced":
        return f"{key}:{safe_displacement_target(trace)}"
    return key


def build_condensation_groups(
    *,
    activations: list[MemoryActivation],
    traces: list[MemoryTrace],
    decisions: list[MemoryDefenseDecision],
) -> list[list[str]]:
    activations_by_id = _by_id(activations)
    decisions_by_id = _by_id(decisions)
    buckets: dict[str, list[str]] = {}
    for trace in traces:
        activation = activations_by_id.get(trace.trace_id)
        decision = decisions_by_id.get(trace.trace_id)
        if activation is None or decision is None:
            continue
        key = _group_key(trace, activation, decision)
        if key:
            buckets.setdefault(key, []).append(trace.trace_id)
    groups: list[list[str]] = []
    traces_by_id = _by_id(traces)
    for trace_ids in buckets.values():
        if len(trace_ids) < 2:
            continue
        group_activations = [activations_by_id[item] for item in trace_ids]
        group_traces = [traces_by_id[item] for item in trace_ids]
        if should_condense_group(group_activations, group_traces):
            groups.append(sorted(trace_ids))
    return sorted(groups, key=lambda group: (len(group), group), reverse=True)


def _symbols_for_group(
    group_trace_ids: list[str],
    activations_by_id: dict[str, MemoryActivation],
    traces_by_id: dict[str, MemoryTrace],
) -> list[str]:
    collected: list[str] = []
    for trace_id in group_trace_ids:
        activation = activations_by_id[trace_id]
        trace = traces_by_id[trace_id]
        collected.extend(activation.matched_salient_symbols + trace.salient_symbols)
    return unique_stable(collected, limit=4)


def build_condensed_memory_cue(
    *,
    group_trace_ids: list[str],
    activations: list[MemoryActivation],
    traces: list[MemoryTrace],
    decisions: list[MemoryDefenseDecision],
) -> ConsciousMemoryCue:
    _ = decisions
    activations_by_id = _by_id(activations)
    traces_by_id = _by_id(traces)
    symbols = _symbols_for_group(group_trace_ids, activations_by_id, traces_by_id)
    focus = sanitize_summary_text(" and ".join(symbols) if symbols else "shared symbolic pressure")
    suffix = hashlib.sha1("|".join(sorted(group_trace_ids)).encode()).hexdigest()[:10]
    first_trace = traces_by_id[group_trace_ids[0]]
    first_activation = activations_by_id[group_trace_ids[0]]
    intensity = max(activations_by_id[item].association_score for item in group_trace_ids)
    return ConsciousMemoryCue(
        cue_id=f"condensed_{suffix}",
        source_trace_ids=list(group_trace_ids),
        cue_type="condensed_memory",
        public_summary=(
            "Multiple related memory traces condense into a composite cue "
            f"around {focus}."
        ),
        affective_tone=affective_tone_from_trace(first_trace, first_activation),
        intensity=clamp_01(intensity),
        recommended_handling="Treat as a composite cue rather than a single factual memory.",
    )


def build_condensation_record(
    *,
    group_trace_ids: list[str],
    traces: list[MemoryTrace],
    cue: ConsciousMemoryCue,
) -> MemoryTransformationRecord:
    traces_by_id = _by_id(traces)
    private_summaries = [
        traces_by_id[trace_id].private_core_summary
        for trace_id in group_trace_ids
        if traces_by_id[trace_id].private_core_summary
    ]
    return MemoryTransformationRecord(
        source_trace_ids=list(group_trace_ids),
        mechanism="condensation",
        private_input_summary="; ".join(private_summaries) if private_summaries else None,
        public_output_summary=cue.public_summary,
        access_mode_before=None,
        access_mode_after="condensed",
        defense_reason="Shared symbolic or affective overlap produced a composite cue.",
        llm_generated=False,
        guard_result="passed",
    )
