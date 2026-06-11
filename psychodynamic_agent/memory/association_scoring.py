from psychodynamic_agent.memory.heuristics import clamp_01
from psychodynamic_agent.memory.similarity import (
    defense_barrier_score,
    list_overlap_score,
    repetition_frequency_score,
    signature_similarity,
    token_jaccard_similarity,
)
from psychodynamic_agent.schemas.memory import (
    AssociationScoreBreakdown,
    MemoryActivation,
    MemoryRetrievalQuery,
    MemoryTrace,
)


def _stable_intersection(left: list[str], right: list[str]) -> list[str]:
    right_normalized = {item.casefold() for item in right}
    seen: set[str] = set()
    matches: list[str] = []
    for item in left:
        normalized = item.casefold()
        if normalized in right_normalized and normalized not in seen:
            matches.append(item)
            seen.add(normalized)
    return matches


def score_trace_association(
    *,
    query: MemoryRetrievalQuery,
    trace: MemoryTrace,
) -> AssociationScoreBreakdown:
    affect_similarity = signature_similarity(query.affective_signature, trace.affective_signature)
    desire_similarity = signature_similarity(query.desire_signature, trace.desire_signature)
    threat_similarity = signature_similarity(query.threat_signature, trace.threat_signature)
    object_overlap = list_overlap_score(query.object_targets, trace.object_targets)
    salient_symbol_overlap = list_overlap_score(query.salient_symbols, trace.salient_symbols)
    repetition_frequency = repetition_frequency_score(trace.activation_count)
    fact_similarity = token_jaccard_similarity(query.query_summary, trace.surface_event_summary)
    defense_barrier = defense_barrier_score(trace.defense_level, trace.repression_pressure)
    weighted_score_before_defense = clamp_01(
        (0.35 * affect_similarity)
        + (0.25 * desire_similarity)
        + (0.25 * threat_similarity)
        + (0.10 * object_overlap)
        + (0.05 * salient_symbol_overlap)
        + (0.05 * repetition_frequency)
        + (0.05 * fact_similarity)
    )
    final_score = clamp_01(weighted_score_before_defense - (0.20 * defense_barrier))
    return AssociationScoreBreakdown(
        affect_similarity=affect_similarity,
        desire_similarity=desire_similarity,
        threat_similarity=threat_similarity,
        object_overlap=object_overlap,
        salient_symbol_overlap=salient_symbol_overlap,
        repetition_frequency=repetition_frequency,
        fact_similarity=fact_similarity,
        defense_barrier=defense_barrier,
        weighted_score_before_defense=weighted_score_before_defense,
        final_score=final_score,
    )


def _public_reason(components: AssociationScoreBreakdown) -> str:
    affective_components = max(
        components.affect_similarity,
        components.desire_similarity,
        components.threat_similarity,
    )
    if affective_components >= 0.75:
        if components.threat_similarity >= components.affect_similarity:
            return "Retrieved due to affect/threat similarity."
        return "Retrieved due to affect/desire similarity."
    if components.object_overlap >= 0.5:
        return "Retrieved due to object overlap and recognition pressure."
    if components.salient_symbol_overlap >= 0.5:
        return "Retrieved due to salient symbolic overlap."
    return "Retrieved due to weak associative similarity."


def build_memory_activation(
    *,
    query: MemoryRetrievalQuery,
    trace: MemoryTrace,
    rank: int,
) -> MemoryActivation:
    components = score_trace_association(query=query, trace=trace)
    return MemoryActivation(
        trace_id=trace.trace_id,
        created_turn=trace.created_turn,
        activation_rank=rank,
        association_score=components.final_score,
        components=components,
        accessibility=trace.accessibility,
        source_complex_ids=list(trace.complex_ids),
        matched_object_targets=_stable_intersection(query.object_targets, trace.object_targets),
        matched_salient_symbols=_stable_intersection(query.salient_symbols, trace.salient_symbols),
        public_reason=_public_reason(components),
    )
