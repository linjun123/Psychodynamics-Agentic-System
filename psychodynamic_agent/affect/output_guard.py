import json

from psychodynamic_agent.schemas.affect import AffectPropagationTrace, EgoAffectSummary
from psychodynamic_agent.schemas.censor import AffectiveColor

FORBIDDEN_AFFECT_TERMS = [
    "u*",
    "u_star",
    "ultimate need",
    "sealed ultimate need",
    "latent alignment",
    "latent_alignment",
    "terminal desire",
    "terminal_desire",
    "hidden desire",
    "hidden_desire",
]


def assert_affect_trace_public_safe(
    *,
    affect_trace: AffectPropagationTrace,
    ego_affect_summary: EgoAffectSummary,
) -> None:
    payload = json.dumps(
        {
            "affect_trace": affect_trace.model_dump(mode="json"),
            "ego_affect_summary": ego_affect_summary.model_dump(mode="json"),
        }
    ).lower()
    for term in FORBIDDEN_AFFECT_TERMS:
        if term in payload:
            msg = f"Forbidden affect term found in public affect object: {term}"
            raise ValueError(msg)


def assert_affective_color_consistent(
    *,
    affect_trace: AffectPropagationTrace,
    affective_color: AffectiveColor,
    tolerance: float = 0.35,
) -> None:
    tolerance = abs(float(tolerance))
    reference = affect_trace.transformed_style
    for field in ("warmth", "caution", "intensity", "playfulness", "assertiveness", "distance"):
        if abs(getattr(affective_color, field) - getattr(reference, field)) > tolerance:
            raise ValueError(f"Affective color drift too large for {field}")

    if affect_trace.boundary_need > 0.7 and affective_color.caution < 0.5:
        raise ValueError("Affective color caution too low for high boundary_need")

    if affect_trace.aggression_pressure > 0.7 and not (
        affective_color.assertiveness >= 0.4 or affective_color.caution >= 0.5
    ):
        raise ValueError("Affective color inconsistent with high aggression_pressure")
