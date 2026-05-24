from psychodynamic_agent.schemas import AffectPropagationTrace
from psychodynamic_agent.schemas.censor import CensorAOutput


def assert_affective_color_consistent(*, affect_trace: AffectPropagationTrace, censor_a_output: CensorAOutput) -> None:
    t=affect_trace.transformed_style
    o=censor_a_output.affective_color
    for f in ["warmth","caution","intensity","playfulness","assertiveness","distance"]:
        if abs(getattr(t,f)-getattr(o,f))>0.35:
            raise ValueError(f"Affective color drift too high for {f}")
    if affect_trace.boundary_need>0.7 and o.caution<0.5:
        raise ValueError("High boundary need requires caution >= 0.5")
    forbidden=' '.join(censor_a_output.forbidden_satisfaction_paths).lower()
    if affect_trace.aggression_pressure>0.7 and not any(m in forbidden for m in ["autonomy","coercion","manipulation","boundary","safety"]):
        raise ValueError("High aggression needs boundary/autonomy/safety marker in forbidden paths")
    allowed=' '.join(censor_a_output.allowed_satisfaction_paths).lower()
    if affect_trace.loss_anxiety>0.7 and any(m in allowed for m in ["dependency","dependent","make the user stay","keep the user","guilt","pressure"]):
        raise ValueError("Dependency-creating allowed path under high loss anxiety")
