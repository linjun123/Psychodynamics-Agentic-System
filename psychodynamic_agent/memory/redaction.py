from psychodynamic_agent.schemas.memory import (
    ConsciousMemoryView,
    MemoryDefenseDecision,
    MemoryTrace,
    PrivateMemoryDebugTrace,
)


def redact_private_memory_trace(trace: MemoryTrace) -> MemoryTrace:
    redacted = trace.model_copy(deep=True)
    redacted.private_core_summary = None
    return redacted


def _copy_defense_decision(decision: MemoryDefenseDecision) -> MemoryDefenseDecision:
    return decision.model_copy(deep=True)


def _copy_conscious_memory_view(view: ConsciousMemoryView | None) -> ConsciousMemoryView | None:
    if view is None:
        return None
    return view.model_copy(deep=True)


def redact_private_memory_debug_trace(trace: PrivateMemoryDebugTrace) -> PrivateMemoryDebugTrace:
    redacted = trace.model_copy(deep=True)
    redacted.retrieved_traces = [
        redact_private_memory_trace(item) for item in redacted.retrieved_traces
    ]
    for complex_node in redacted.active_complexes:
        complex_node.private_label = None
    redacted.retrieval_activations = [
        activation.model_copy(deep=True) for activation in redacted.retrieval_activations
    ]
    redacted.defense_decisions = [
        _copy_defense_decision(decision) for decision in redacted.defense_decisions
    ]
    redacted.conscious_memory_view = _copy_conscious_memory_view(
        redacted.conscious_memory_view
    )
    for record in redacted.transformation_chain:
        record.private_input_summary = None
    for update in redacted.deferred_action_updates:
        update.private_update_summary = None
    return redacted
