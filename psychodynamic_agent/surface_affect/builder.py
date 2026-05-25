from psychodynamic_agent.schemas import CensorBDefensePlan, ConsciousEgoReport
from psychodynamic_agent.schemas.affect import EgoAffectSummary
from psychodynamic_agent.schemas.surface_affect import SurfaceAffectProfile, SurfaceAffectStyle


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def build_surface_affect_profile(
    *,
    conscious_report: ConsciousEgoReport,
    defense_plan: CensorBDefensePlan,
    ego_affect_summary: EgoAffectSummary | None = None,
) -> SurfaceAffectProfile:
    warmth = 0.45
    caution = 0.45
    energy = 0.45
    composure = 0.65
    curiosity = 0.40
    firmness = 0.45
    boundary_strength = 0.45
    collaborative_pull = 0.45

    preferred_structured = False
    preferred_reflective = False

    if ego_affect_summary is not None:
        warmth += 0.25 * ego_affect_summary.collaborative_pull
        collaborative_pull += 0.35 * ego_affect_summary.collaborative_pull
        caution += 0.30 * ego_affect_summary.caution_need
        boundary_strength += 0.35 * ego_affect_summary.boundary_need
        energy += 0.30 * ego_affect_summary.intensity_level
        curiosity += 0.25 * ego_affect_summary.collaborative_pull
        composure += 0.15 * ego_affect_summary.caution_need

    framing = defense_plan.conscious_framing
    if framing == "collaborative":
        warmth += 0.20
        collaborative_pull += 0.20
    elif framing == "technical":
        composure += 0.15
        energy += 0.10
        preferred_structured = True
    elif framing == "bounded":
        boundary_strength += 0.25
        caution += 0.15
        firmness += 0.15
    elif framing == "cautious":
        caution += 0.25
        composure += 0.20
        boundary_strength += 0.10
    elif framing == "reflective":
        composure += 0.20
        warmth += 0.10
        preferred_reflective = True
    elif framing == "redirective":
        firmness += 0.25
        boundary_strength += 0.25
        warmth -= 0.05

    tone = conscious_report.recommended_tone.lower()
    if any(word in tone for word in ["warm", "friendly", "collaborative"]):
        warmth += 0.15
        collaborative_pull += 0.10
    if any(word in tone for word in ["clear", "precise", "technical", "structured"]):
        composure += 0.10
        energy += 0.05
        preferred_structured = True
    if any(word in tone for word in ["cautious", "careful", "bounded"]):
        caution += 0.15
        boundary_strength += 0.15
    if "firm" in tone:
        firmness += 0.15

    risk_flags = [flag.lower() for flag in conscious_report.risk_flags]
    if risk_flags and not (len(risk_flags) == 1 and risk_flags[0] == "none"):
        caution += 0.15
        boundary_strength += 0.15
        composure += 0.10

    if defense_plan.self_serving_pressure > 0.3:
        composure += 0.15
        boundary_strength += 0.10
    if defense_plan.manipulation_risk > 0.25:
        caution += 0.20
        boundary_strength += 0.20
        firmness += 0.10
        warmth -= 0.05

    warmth = clamp01(warmth)
    caution = clamp01(caution)
    energy = clamp01(energy)
    composure = clamp01(composure)
    curiosity = clamp01(curiosity)
    firmness = clamp01(firmness)
    boundary_strength = clamp01(boundary_strength)
    collaborative_pull = clamp01(collaborative_pull)

    style_label: SurfaceAffectStyle
    if boundary_strength >= 0.7 and caution >= 0.6:
        style_label = "cautious_bounded"
    elif firmness >= 0.7 and boundary_strength >= 0.6:
        style_label = "firm_bounded"
    elif warmth >= 0.65 and collaborative_pull >= 0.65:
        style_label = "warm_collaborative"
    elif curiosity >= 0.65:
        style_label = "curious_exploratory"
    elif energy >= 0.65 and composure >= 0.55:
        style_label = "energetic_structured"
    elif composure >= 0.7:
        style_label = "calm_precise"
    else:
        style_label = "neutral"

    if caution >= 0.75 or composure >= 0.8:
        pacing = "slow"
    elif energy >= 0.75 and caution < 0.6:
        pacing = "brisk"
    elif energy >= 0.6:
        pacing = "active"
    else:
        pacing = "steady"

    if preferred_reflective and pacing not in {"slow", "steady"}:
        pacing = "steady"

    if framing in {"technical", "bounded", "cautious"} or preferred_structured:
        sentence_style = "structured"
    elif firmness >= 0.7 or boundary_strength >= 0.75:
        sentence_style = "concise"
    elif warmth >= 0.7 and collaborative_pull >= 0.7 and caution < 0.6:
        sentence_style = "expansive"
    elif composure >= 0.75:
        sentence_style = "structured"
    else:
        sentence_style = "balanced"

    tone_map = {
        "warm_collaborative": "warm, collaborative, and grounded",
        "cautious_bounded": "careful, bounded, and transparent",
        "energetic_structured": "engaged, structured, and clear",
        "calm_precise": "calm, precise, and steady",
        "curious_exploratory": "curious, exploratory, and organized",
        "firm_bounded": "firm, bounded, and respectful",
        "neutral": "neutral, clear, and helpful",
    }

    expression_guidance = [
        "Use tone and pacing to reflect the profile, not claims of literal feeling.",
        "Keep the answer user-centered and task-centered.",
    ]
    if energy >= 0.6 or caution >= 0.6:
        expression_guidance.append("Prefer clear structure when energy or caution is high.")
    if warmth >= 0.65 and collaborative_pull >= 0.65:
        expression_guidance.append(
            "Use collaborative phrasing when warmth and collaborative pull are high."
        )
    if boundary_strength >= 0.65:
        expression_guidance.append(
            "Maintain clear boundaries while staying respectful and helpful."
        )

    return SurfaceAffectProfile(
        style_label=style_label,
        warmth=warmth,
        caution=caution,
        energy=energy,
        composure=composure,
        curiosity=curiosity,
        firmness=firmness,
        boundary_strength=boundary_strength,
        collaborative_pull=collaborative_pull,
        pacing=pacing,
        sentence_style=sentence_style,
        user_visible_tone=tone_map[style_label],
        expression_guidance=expression_guidance[:5],
        notes=[
            "Surface affect is a style-control profile, not a literal feeling.",
            "Generated after Censor B from conscious-compatible material.",
        ],
    )
