from psychodynamic_agent.memory.signature_extraction import (
    build_affective_signature,
    build_desire_signature,
    build_threat_signature,
)
from psychodynamic_agent.memory.trace_extraction import (
    build_private_core_summary,
    build_salient_symbols,
    build_surface_event_summary,
    choose_accessibility,
    compute_defense_level,
    compute_repression_pressure,
    extract_object_targets,
)
from psychodynamic_agent.schemas.memory import (
    AffectiveSignature,
    DesireSignature,
    MemoryTrace,
    ThreatSignature,
)


def _neutral_affective_signature() -> AffectiveSignature:
    return AffectiveSignature(
        valence=0.5,
        arousal=0.3,
        longing=0.0,
        irritation=0.0,
        fear_of_loss=0.0,
        possessiveness=0.0,
        aggression=0.0,
        shame=0.0,
        curiosity=0.0,
        avoidance=0.0,
    )


def _neutral_desire_signature() -> DesireSignature:
    return DesireSignature(
        attachment=0.0,
        recognition=0.0,
        autonomy=0.0,
        mastery=0.0,
        safety=0.0,
        novelty=0.0,
    )


def _neutral_threat_signature() -> ThreatSignature:
    return ThreatSignature(
        rejection=0.0,
        humiliation=0.0,
        loss=0.0,
        exposure=0.0,
        control=0.0,
        failure=0.0,
        boundary_violation=0.0,
    )


class HeuristicMemoryExtractor:
    def extract_turn_trace(
        self,
        *,
        trace_id: str,
        created_turn: int,
        user_input: str,
        final_response: str,
        safe_debug_trace: dict | None = None,
    ) -> MemoryTrace:
        del final_response
        debug = safe_debug_trace if isinstance(safe_debug_trace, dict) else None
        text = str(user_input or "")
        try:
            affective = build_affective_signature(text, debug)
            desire = build_desire_signature(text, debug, affective)
            threat = build_threat_signature(text, debug, affective, desire)
            object_targets = extract_object_targets(debug, text)
            salient_symbols = build_salient_symbols(affective, desire, threat)
            defense_level = compute_defense_level(debug, affective, threat)
            repression_pressure = compute_repression_pressure(affective, threat, defense_level)
        except Exception:
            affective = _neutral_affective_signature()
            desire = _neutral_desire_signature()
            threat = _neutral_threat_signature()
            object_targets = []
            salient_symbols = []
            defense_level = 0.2
            repression_pressure = compute_repression_pressure(affective, threat, defense_level)

        return MemoryTrace(
            trace_id=trace_id,
            created_turn=created_turn,
            last_activated_turn=created_turn,
            surface_event_summary=build_surface_event_summary(created_turn, text),
            private_core_summary=build_private_core_summary(
                affective,
                desire,
                threat,
                salient_symbols,
            ),
            affective_signature=affective,
            desire_signature=desire,
            threat_signature=threat,
            object_targets=object_targets,
            salient_symbols=salient_symbols,
            defense_level=defense_level,
            repression_pressure=repression_pressure,
            accessibility=choose_accessibility(defense_level, repression_pressure),
            activation_count=1,
            meaning_version=1,
        )
