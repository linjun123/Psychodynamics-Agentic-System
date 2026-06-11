from psychodynamic_agent.memory.similarity import list_overlap_score, signature_similarity
from psychodynamic_agent.schemas.memory import MemoryActivation, MemoryDefenseDecision, MemoryTrace

_RISKY_OBJECT_KEYWORDS = {
    "authority",
    "boss",
    "manager",
    "teacher",
    "parent",
    "mother",
    "father",
    "evaluator",
    "judge",
    "权威",
    "老板",
    "领导",
    "老师",
    "父亲",
    "母亲",
    "父母",
    "评价者",
    "审判",
    "上级",
}
_PARENT_KEYWORDS = {"parent", "mother", "father", "family", "父亲", "母亲", "父母"}
_AUTHORITY_KEYWORDS = {
    "authority",
    "boss",
    "manager",
    "teacher",
    "evaluator",
    "judge",
    "权威",
    "老板",
    "领导",
    "老师",
    "评价者",
    "审判",
    "上级",
}
_CONTROL_KEYWORDS = {"control", "pressure", "控制", "压力"}
_GROUP_PRIORITY = [
    "evaluation_sensitivity",
    "loss_anxiety",
    "boundary_pressure",
    "recognition_pressure",
    "task_mastery",
    "curiosity",
]


def _contains_keyword(values: list[str], keywords: set[str]) -> bool:
    text = " ".join(str(value).casefold() for value in values)
    return any(keyword.casefold() in text for keyword in keywords)


def should_screen_memory(decision: MemoryDefenseDecision, trace: MemoryTrace) -> bool:
    return (
        decision.trace_id == trace.trace_id
        and decision.decided_accessibility == "screened"
        and decision.mechanism == "screen_memory"
        and decision.emits_conscious_cue
        and decision.conscious_access == "screened"
        and trace.accessibility not in {"blocked_action_only", "felt_sense_only", "direct"}
    )


def should_displace(decision: MemoryDefenseDecision, trace: MemoryTrace) -> bool:
    return decision.decided_accessibility == "displaced" or (
        _contains_keyword(trace.object_targets, _RISKY_OBJECT_KEYWORDS)
        and decision.defense_pressure >= 0.55
    )


def safe_displacement_target(trace: MemoryTrace) -> str:
    if _contains_keyword(trace.object_targets, _AUTHORITY_KEYWORDS):
        return "task_structure"
    if _contains_keyword(trace.object_targets, _PARENT_KEYWORDS):
        return "boundary"
    if _contains_keyword(trace.object_targets + trace.salient_symbols, _CONTROL_KEYWORDS):
        return "communication_format"
    return "process"


def condensation_group_key(trace: MemoryTrace, activation: MemoryActivation) -> str | None:
    symbols = activation.matched_salient_symbols + trace.salient_symbols
    normalized = {str(symbol).strip() for symbol in symbols if str(symbol).strip()}
    for symbol in _GROUP_PRIORITY:
        if symbol in normalized:
            return symbol
    return sorted(normalized)[0] if len(normalized) >= 2 else None


def should_condense_group(
    group_activations: list[MemoryActivation],
    group_traces: list[MemoryTrace],
) -> bool:
    if len(group_traces) < 2 or len(group_activations) < 2:
        return False
    avg_score = sum(item.association_score for item in group_activations) / len(group_activations)
    if avg_score < 0.25:
        return False
    common_symbols = set(group_traces[0].salient_symbols)
    for trace in group_traces[1:]:
        common_symbols &= set(trace.salient_symbols)
    return bool(common_symbols) or any(
        condensation_group_key(trace, activation)
        for trace, activation in zip(group_traces, group_activations, strict=False)
    )


def should_defer_action(
    *,
    old_trace: MemoryTrace,
    trigger_trace: MemoryTrace,
    similarity_score: float,
) -> bool:
    if old_trace.trace_id == trigger_trace.trace_id:
        return False
    if trigger_trace.created_turn <= old_trace.created_turn or similarity_score < 0.55:
        return False
    shared_symbols = bool(set(old_trace.salient_symbols) & set(trigger_trace.salient_symbols))
    shared_objects = bool(set(old_trace.object_targets) & set(trigger_trace.object_targets))
    high_threat = (
        signature_similarity(old_trace.threat_signature, trigger_trace.threat_signature) >= 0.75
    )
    high_affect = (
        signature_similarity(old_trace.affective_signature, trigger_trace.affective_signature)
        >= 0.75
    )
    return shared_symbols or shared_objects or (high_threat and high_affect)


def object_overlap(left: MemoryTrace, right: MemoryTrace) -> float:
    return list_overlap_score(left.object_targets, right.object_targets)
