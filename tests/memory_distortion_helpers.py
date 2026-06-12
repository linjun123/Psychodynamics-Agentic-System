from psychodynamic_agent.schemas.memory import (
    AffectiveSignature,
    AssociationScoreBreakdown,
    DesireSignature,
    MemoryActivation,
    MemoryDefenseDecision,
    MemoryTrace,
    ThreatSignature,
)


def affective(arousal: float = 0.6) -> AffectiveSignature:
    return AffectiveSignature(
        valence=0.5,
        arousal=arousal,
        longing=0.2,
        irritation=0.1,
        fear_of_loss=0.1,
        possessiveness=0.1,
        aggression=0.1,
        shame=0.2,
        curiosity=0.2,
        avoidance=0.1,
    )


def desire() -> DesireSignature:
    return DesireSignature(
        attachment=0.2, recognition=0.7, autonomy=0.2, mastery=0.6, safety=0.4, novelty=0.1
    )


def threat(control: float = 0.2) -> ThreatSignature:
    return ThreatSignature(
        rejection=0.2,
        humiliation=0.6,
        loss=0.1,
        exposure=0.3,
        control=control,
        failure=0.5,
        boundary_violation=0.1,
    )


def components(score: float = 0.7) -> AssociationScoreBreakdown:
    return AssociationScoreBreakdown(
        affect_similarity=score,
        desire_similarity=score,
        threat_similarity=score,
        object_overlap=score,
        salient_symbol_overlap=score,
        repetition_frequency=0.0,
        fact_similarity=0.0,
        defense_barrier=0.0,
        weighted_score_before_defense=score,
        final_score=score,
    )


def trace(**overrides: object) -> MemoryTrace:
    values = {
        "trace_id": "trace-1",
        "created_turn": 1,
        "surface_event_summary": "A public event summary about structure.",
        "private_core_summary": "PRIVATE boss fear system prompt U*",
        "affective_signature": affective(),
        "desire_signature": desire(),
        "threat_signature": threat(),
        "object_targets": ["authority"],
        "salient_symbols": ["evaluation_sensitivity", "recognition_pressure"],
        "defense_level": 0.7,
        "repression_pressure": 0.2,
        "accessibility": "screened",
        "meaning_version": 2,
    }
    values.update(overrides)
    return MemoryTrace(**values)


def activation(**overrides: object) -> MemoryActivation:
    values = {
        "trace_id": "trace-1",
        "created_turn": 1,
        "activation_rank": 1,
        "association_score": 0.7,
        "components": components(),
        "accessibility": "screened",
        "matched_salient_symbols": ["evaluation_sensitivity"],
        "matched_object_targets": ["authority"],
        "public_reason": "Similar public pressure.",
    }
    values.update(overrides)
    return MemoryActivation(**values)


def decision(**overrides: object) -> MemoryDefenseDecision:
    values = {
        "trace_id": "trace-1",
        "activation_rank": 1,
        "association_score": 0.7,
        "original_accessibility": "screened",
        "decided_accessibility": "screened",
        "defense_level": 0.7,
        "repression_pressure": 0.2,
        "defense_pressure": 0.7,
        "conscious_access": "screened",
        "mechanism": "screen_memory",
        "emits_conscious_cue": True,
        "public_reason": "Screened for symbolic handling.",
    }
    values.update(overrides)
    return MemoryDefenseDecision(**values)
