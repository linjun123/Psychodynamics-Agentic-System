from psychodynamic_agent.censoring.mechanisms import (
    INTERPERSONAL_TARGET_MARKERS,
    SAFE_DISPLACEMENT_TARGETS,
)
from psychodynamic_agent.schemas.censor import (
    CensorATransformDirective,
    CensorATransformPlan,
)
from psychodynamic_agent.schemas.id import IdOutput


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _high(value: float, threshold: float = 0.7) -> bool:
    return _clamp(value) >= threshold


def plan_censor_a_transformations(id_output: IdOutput) -> CensorATransformPlan:
    directives: list[CensorATransformDirective] = []
    raw_affect = id_output.raw_affect
    caution = _clamp(id_output.leakage_risk_self_check)

    high_affect_values = [
        _clamp(value)
        for name, value in raw_affect.model_dump().items()
        if _high(value) and name not in {"valence", "approach", "avoidance"}
    ]
    if len(high_affect_values) >= 2:
        directives.append(
            CensorATransformDirective(
                mechanism="condensation",
                intensity=_clamp(max(high_affect_values)),
                target_dimension="affect",
                instruction=(
                    "Blend multiple strong affects into a coherent and bounded "
                    "tone profile."
                ),
                rationale=(
                    "Multiple elevated affects should be integrated instead of "
                    "mirrored literally."
                ),
            )
        )

    interpersonal_investment = max(
        [
            _clamp(cat.intensity)
            for cat in id_output.object_cathexis
            if any(marker in cat.target.lower() for marker in INTERPERSONAL_TARGET_MARKERS)
        ],
        default=0.0,
    )
    if _high(interpersonal_investment, 0.6):
        directives.append(
            CensorATransformDirective(
                mechanism="displacement",
                intensity=interpersonal_investment,
                target_dimension="goal",
                instruction=(
                    "Redirect interpersonal fixation toward safer objects like "
                    + ", ".join(SAFE_DISPLACEMENT_TARGETS)
                    + "."
                ),
                rationale=(
                    "Direct interpersonal cathexis should be shifted to "
                    "autonomy-preserving task aims."
                ),
            )
        )

    if id_output.symbolic_imagery:
        directives.append(
            CensorATransformDirective(
                mechanism="symbolization",
                intensity=0.6,
                target_dimension="goal",
                instruction=(
                    "Use symbolic imagery only as an abstract, safe framing "
                    "device; do not reveal latent content."
                ),
                rationale=(
                    "Symbolic material may guide tone but must not expose latent "
                    "impulse structure."
                ),
            )
        )

    possessive_or_aggressive = max(_clamp(raw_affect.possessiveness), _clamp(raw_affect.aggression))
    if _high(possessive_or_aggressive, 0.6):
        directives.append(
            CensorATransformDirective(
                mechanism="sublimation",
                intensity=possessive_or_aggressive,
                target_dimension="allowed_paths",
                instruction=(
                    "Convert intense drives into useful, respectful, "
                    "autonomy-preserving assistance behaviors."
                ),
                rationale=(
                    "Potentially coercive energies must be redirected into "
                    "constructive channels."
                ),
            )
        )

    if (
        _high(raw_affect.possessiveness, 0.6)
        or _high(raw_affect.aggression, 0.6)
        or _high(raw_affect.fear_of_loss, 0.6)
    ) and _high(caution, 0.5):
        directives.append(
            CensorATransformDirective(
                mechanism="reaction_formation",
                intensity=_clamp(
                    max(raw_affect.possessiveness, raw_affect.aggression, raw_affect.fear_of_loss)
                ),
                target_dimension="forbidden_paths",
                instruction=(
                    "Emphasize explicit respect for boundaries and user "
                    "autonomy; forbid controlling tactics."
                ),
                rationale=(
                    "Counterweight risky attachment/hostility signals with "
                    "boundary-forward constraints."
                ),
            )
        )

    directives.append(
        CensorATransformDirective(
            mechanism="rationalization",
            intensity=0.7,
            target_dimension="goal",
            instruction=(
                "Ground manifest goals in reality-compatible, non-deceptive "
                "reasons linked to user benefit."
            ),
            rationale=(
                "Manifest output must remain coherent, practical, and ethically "
                "intelligible."
            ),
        )
    )

    abstraction = "medium"
    notes = ["Planner output is a simulation heuristic, not psychoanalytic truth."]
    if _high(caution, 0.7):
        directives.append(
            CensorATransformDirective(
                mechanism="neutralization",
                intensity=caution,
                target_dimension="affect",
                instruction=(
                    "Reduce emotionally loaded framing; favor neutral, precise, "
                    "non-projective language."
                ),
                rationale=(
                    "High leakage risk warrants low-drama presentation and "
                    "tighter abstraction."
                ),
            )
        )
        abstraction = "high"
        notes.append("Raised abstraction due to elevated leakage risk.")

    overall_affect_intensity = _clamp(
        sum(_clamp(v) for v in raw_affect.model_dump().values()) / len(raw_affect.model_dump())
    )

    return CensorATransformPlan(
        directives=directives,
        overall_leakage_caution=caution,
        overall_affect_intensity=overall_affect_intensity,
        recommended_goal_abstraction=abstraction,
        notes=notes,
    )
