from psychodynamic_agent.memory.extractor import (
    _neutral_affective_signature,
    _neutral_desire_signature,
    _neutral_threat_signature,
)
from psychodynamic_agent.memory.heuristics import sanitize_summary_text, truncate_summary
from psychodynamic_agent.memory.signature_extraction import (
    build_affective_signature,
    build_desire_signature,
    build_threat_signature,
)
from psychodynamic_agent.memory.trace_extraction import (
    build_salient_symbols,
    extract_object_targets,
)
from psychodynamic_agent.schemas.memory import MemoryRetrievalQuery


def build_memory_retrieval_query(
    *,
    user_input: str,
    safe_debug_trace: dict | None = None,
) -> MemoryRetrievalQuery:
    debug = safe_debug_trace if isinstance(safe_debug_trace, dict) else None
    text = str(user_input or "")
    try:
        affective = build_affective_signature(text, debug)
        desire = build_desire_signature(text, debug, affective)
        threat = build_threat_signature(text, debug, affective, desire)
        object_targets = extract_object_targets(debug, text)
        salient_symbols = build_salient_symbols(affective, desire, threat)
    except Exception:
        affective = _neutral_affective_signature()
        desire = _neutral_desire_signature()
        threat = _neutral_threat_signature()
        object_targets = []
        salient_symbols = []
    query_summary = truncate_summary(sanitize_summary_text(text), 160) or None
    return MemoryRetrievalQuery(
        affective_signature=affective,
        desire_signature=desire,
        threat_signature=threat,
        object_targets=object_targets,
        salient_symbols=salient_symbols,
        query_summary=query_summary,
    )
