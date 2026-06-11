from psychodynamic_agent.memory.distortion_policy import should_defer_action
from psychodynamic_agent.memory.heuristics import clamp_01, sanitize_summary_text, unique_stable
from psychodynamic_agent.memory.similarity import list_overlap_score, signature_similarity
from psychodynamic_agent.schemas.memory import MemoryDeferredActionUpdate, MemoryTrace


def _similarity_score(old_trace: MemoryTrace, trigger_trace: MemoryTrace) -> float:
    affect = signature_similarity(old_trace.affective_signature, trigger_trace.affective_signature)
    desire = signature_similarity(old_trace.desire_signature, trigger_trace.desire_signature)
    threat = signature_similarity(old_trace.threat_signature, trigger_trace.threat_signature)
    symbol = list_overlap_score(old_trace.salient_symbols, trigger_trace.salient_symbols)
    obj = list_overlap_score(old_trace.object_targets, trigger_trace.object_targets)
    return clamp_01(
        (0.35 * affect) + (0.25 * desire) + (0.25 * threat) + (0.10 * symbol) + (0.05 * obj)
    )


def build_deferred_action_updates(
    *,
    traces: list[MemoryTrace],
    latest_trace: MemoryTrace | None = None,
    max_updates: int = 3,
) -> list[MemoryDeferredActionUpdate]:
    if not traces:
        return []
    trigger = latest_trace or max(traces, key=lambda trace: trace.created_turn)
    candidates: list[MemoryDeferredActionUpdate] = []
    for old_trace in traces:
        if old_trace.trace_id == trigger.trace_id or old_trace.created_turn >= trigger.created_turn:
            continue
        score = _similarity_score(old_trace, trigger)
        if not should_defer_action(
            old_trace=old_trace, trigger_trace=trigger, similarity_score=score
        ):
            continue
        symbols = unique_stable(
            list(set(old_trace.salient_symbols) & set(trigger.salient_symbols))
            + trigger.salient_symbols
            + old_trace.salient_symbols,
            limit=4,
        )
        objects = unique_stable(
            list(set(old_trace.object_targets) & set(trigger.object_targets)), limit=4
        )
        focus = sanitize_summary_text(" and ".join(symbols) if symbols else "symbolic pressure")
        candidates.append(
            MemoryDeferredActionUpdate(
                old_trace_id=old_trace.trace_id,
                trigger_trace_id=trigger.trace_id,
                old_created_turn=old_trace.created_turn,
                trigger_created_turn=trigger.created_turn,
                previous_meaning_version=old_trace.meaning_version,
                proposed_meaning_version=old_trace.meaning_version + 1,
                update_strength=score,
                public_update_summary=(
                    "A later trace retrospectively intensifies an earlier symbolic "
                    f"memory pattern around {focus}."
                ),
                private_update_summary=(
                    "Deferred-action candidate: trigger trace "
                    f"{trigger.trace_id} may reorganize old trace {old_trace.trace_id} "
                    f"around {focus}."
                ),
                supporting_symbols=symbols,
                supporting_object_targets=objects,
            )
        )
    return sorted(candidates, key=lambda item: (-item.update_strength, -item.old_created_turn))[
        : max(int(max_updates), 0)
    ]
