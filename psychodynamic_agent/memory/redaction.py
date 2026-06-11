from psychodynamic_agent.schemas.memory import MemoryTrace, PrivateMemoryDebugTrace


def redact_private_memory_trace(trace: MemoryTrace) -> MemoryTrace:
    redacted = trace.model_copy(deep=True)
    redacted.private_core_summary = None
    return redacted


def redact_private_memory_debug_trace(trace: PrivateMemoryDebugTrace) -> PrivateMemoryDebugTrace:
    redacted = trace.model_copy(deep=True)
    redacted.retrieved_traces = [
        redact_private_memory_trace(item) for item in redacted.retrieved_traces
    ]
    for complex_node in redacted.active_complexes:
        complex_node.private_label = None
    for record in redacted.transformation_chain:
        record.private_input_summary = None
    return redacted
