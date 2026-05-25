from psychodynamic_agent.schemas import IdOutput
from psychodynamic_agent.schemas.affect import AffectPropagationTrace, EgoAffectSummary
from psychodynamic_agent.schemas.censor import AffectiveColor


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def map_id_affect_to_trace(id_output: IdOutput) -> AffectPropagationTrace:
    raw = id_output.raw_affect
    leakage_risk = clamp01(id_output.leakage_risk_self_check)

    raw_affect_dict = raw.model_dump()
    dominant_affects = [
        key
        for key, _ in sorted(
            ((k, v) for k, v in raw_affect_dict.items() if k != "valence" and float(v) >= 0.5),
            key=lambda item: item[1],
            reverse=True,
        )[:3]
    ]

    affect_pressure = clamp01(
        (
            raw.arousal
            + raw.longing
            + raw.excitement
            + raw.fear_of_loss
            + raw.irritation
            + raw.possessiveness
            + raw.aggression
        )
        / 7
    )

    approach_avoidance_balance = clamp01((raw.approach - raw.avoidance + 1) / 2)
    intimacy_pressure = clamp01(
        (raw.longing + raw.approach + raw.possessiveness + raw.fear_of_loss) / 4
    )
    boundary_need = clamp01(
        max(raw.fear_of_loss, raw.possessiveness, raw.aggression, raw.avoidance, leakage_risk)
    )
    aggression_pressure = clamp01(max(raw.aggression, raw.irritation))
    loss_anxiety = clamp01(raw.fear_of_loss)
    curiosity_drive = clamp01(raw.curiosity)

    warmth = clamp01(
        0.3
        + 0.4 * raw.longing
        + 0.2 * raw.approach
        + 0.2 * raw.curiosity
        - 0.3 * raw.aggression
    )
    caution = clamp01(
        0.2
        + 0.4 * raw.fear_of_loss
        + 0.3 * leakage_risk
        + 0.2 * raw.avoidance
        + 0.2 * raw.possessiveness
    )
    intensity = clamp01(0.2 + 0.5 * raw.arousal + 0.2 * raw.excitement + 0.2 * raw.irritation)
    playfulness = clamp01(0.1 + 0.5 * raw.curiosity + 0.2 * raw.excitement - 0.3 * caution)
    assertiveness = clamp01(0.2 + 0.3 * raw.aggression + 0.2 * raw.irritation + 0.2 * raw.arousal)
    distance = clamp01(
        0.1
        + 0.4 * raw.avoidance
        + 0.2 * raw.fear_of_loss
        + 0.2 * raw.aggression
        - 0.2 * raw.approach
    )

    if caution >= 0.5 and caution >= max(warmth, playfulness, assertiveness):
        conscious_style_hint = "cautious and bounded"
    elif warmth >= 0.65:
        conscious_style_hint = "warm and collaborative"
    elif playfulness >= 0.65:
        conscious_style_hint = "curious and exploratory"
    elif assertiveness >= 0.65 or intensity >= 0.75:
        conscious_style_hint = "firm and structured"
    else:
        conscious_style_hint = "neutral and precise"

    transformed_style = AffectiveColor(
        conscious_style_hint=conscious_style_hint,
        warmth=warmth,
        caution=caution,
        intensity=intensity,
        playfulness=playfulness,
        assertiveness=assertiveness,
        distance=distance,
    )

    return AffectPropagationTrace(
        dominant_affects=dominant_affects,
        affect_pressure=affect_pressure,
        approach_avoidance_balance=approach_avoidance_balance,
        boundary_need=boundary_need,
        intimacy_pressure=intimacy_pressure,
        aggression_pressure=aggression_pressure,
        loss_anxiety=loss_anxiety,
        curiosity_drive=curiosity_drive,
        transformed_style=transformed_style,
        notes=["Derived from Id raw affect; simulation control signal, not literal feeling."],
    )


def summarize_affect_for_ego(trace: AffectPropagationTrace) -> EgoAffectSummary:
    return EgoAffectSummary(
        affective_pressure=trace.affect_pressure,
        conscious_style_hint=trace.transformed_style.conscious_style_hint,
        boundary_need=trace.boundary_need,
        collaborative_pull=clamp01(
            (trace.transformed_style.warmth + trace.curiosity_drive + trace.intimacy_pressure) / 3
        ),
        caution_need=trace.transformed_style.caution,
        intensity_level=trace.transformed_style.intensity,
        notes=["Conscious-compatible affect summary for strategy scoring; not literal feeling."],
    )
