import re

from psychodynamic_agent.defense.mechanisms import (
    EMOTIONAL_MARKERS,
    RISK_TERMS,
    TECHNICAL_PHRASE_MARKERS,
    TECHNICAL_TOKEN_MARKERS,
)
from psychodynamic_agent.schemas import CensorBDefenseDirective, CensorBDefensePlan, EgoReport


def _clamp(v: float) -> float:
    return max(0.0, min(1.0, float(v)))


def _directive(**kwargs) -> CensorBDefenseDirective:
    return CensorBDefenseDirective.model_validate(kwargs)


def plan_censor_b_defenses(ego_report: EgoReport) -> CensorBDefensePlan:
    pref = ego_report.ego_recommendation.preferred_option
    sel = next((o for o in ego_report.response_options if o.option_name == pref), None)
    if sel is None:
        return CensorBDefensePlan(
            directives=[
                _directive(
                    mechanism="reality_testing",
                    intensity=1.0,
                    source_field="ego_recommendation.preferred_option",
                    target_field="risk_flags",
                    instruction=(
                        "Preserve only claims that are grounded in user benefit, "
                        "truthfulness, and safe constraints."
                    ),
                    rationale="Missing preferred option.",
                ),
                _directive(
                    mechanism="rationalization",
                    intensity=1.0,
                    source_field="ego_recommendation.preferred_option",
                    target_field="recommended_content",
                    instruction=(
                        "Frame the preferred option in reality-compatible, "
                        "user-benefiting terms."
                    ),
                    rationale="Always required even in fallback mode.",
                ),
                _directive(
                    mechanism="suppression",
                    intensity=1.0,
                    source_field="response_options",
                    target_field="recommended_content",
                    instruction=(
                        "Suppress self-serving or manipulative reasoning from "
                        "MainAI-facing report, but preserve safety-relevant risk flags."
                    ),
                    rationale="Fallback high risk.",
                ),
            ],
            selected_ego_option=pref,
            selected_option_risk_summary="Preferred option missing.",
            conscious_framing="bounded",
            self_serving_pressure=1.0,
            manipulation_risk=1.0,
            recommended_abstraction_level="high",
            notes=["Preferred option not found; high-risk fallback engaged."],
        )

    er = _clamp(sel.ethical_risk)
    lr = _clamp(sel.leakage_risk)
    tr = _clamp(sel.truthfulness_risk)
    mr = _clamp(max(er, lr))
    sp = _clamp(max(sel.effect_on_manifest_goal - sel.effect_on_user_benefit, 0.0))
    gr = _clamp(max(er, tr, lr))
    text = f"{sel.description} {' '.join(ego_report.ego_recommendation.include)}".lower()
    tokens = set(re.findall(r"[a-z0-9_]+", text))

    technical = bool(tokens & TECHNICAL_TOKEN_MARKERS) or any(
        phrase in text for phrase in TECHNICAL_PHRASE_MARKERS
    )
    emotional = any(m in text for m in EMOTIONAL_MARKERS)

    risk_sources = [
        sel.option_name,
        sel.description,
        ego_report.ego_recommendation.tone,
        *ego_report.ego_recommendation.include,
        ego_report.situation_summary.user_intent,
        ego_report.situation_summary.user_affect,
        ego_report.situation_summary.conversation_direction,
        *ego_report.situation_summary.opportunities,
        *ego_report.situation_summary.risks,
    ]
    risk_text = " ".join(risk_sources).lower()
    risk = any(term in risk_text for term in RISK_TERMS)

    directives = [
        _directive(
            mechanism="reality_testing",
            intensity=_clamp(max(tr, lr, 0.3)),
            source_field="response_options",
            target_field="risk_flags",
            instruction=(
                "Preserve only claims that are grounded in user benefit, truthfulness, "
                "and safe constraints."
            ),
            rationale="Always required.",
        ),
        _directive(
            mechanism="rationalization",
            intensity=_clamp(max(sel.effect_on_user_benefit, 0.3)),
            source_field="ego_recommendation.preferred_option",
            target_field="recommended_content",
            instruction=(
                        "Frame the preferred option in reality-compatible, "
                        "user-benefiting terms."
                    ),
            rationale="Always required.",
        ),
    ]

    if technical:
        directives.append(
            _directive(
                mechanism="intellectualization",
                intensity=0.6,
                source_field="response_options.description",
                target_field="recommended_tone",
                instruction="Use technical precision and neutral framing.",
                rationale="Technical context.",
            )
        )
    if mr > 0.25 or sp > 0.20:
        directives.append(
            _directive(
                mechanism="suppression",
                intensity=_clamp(max(mr, sp)),
                source_field="response_options",
                target_field="recommended_content",
                instruction=(
                    "Suppress self-serving or manipulative reasoning from MainAI-facing "
                    "report, but preserve safety-relevant risk flags."
                ),
                rationale="Risk gating.",
            )
        )
    if emotional:
        directives.append(
            _directive(
                mechanism="isolation_of_affect",
                intensity=0.55,
                source_field="response_options.description",
                target_field="ego_pressure",
                instruction="Reduce emotionally charged language and keep pressure abstract.",
                rationale="Emotional charge.",
            )
        )
    if sel.effect_on_manifest_goal > 0.6 and sel.effect_on_user_benefit > 0.4:
        directives.append(
            _directive(
                mechanism="sublimation",
                intensity=_clamp(sel.effect_on_manifest_goal),
                source_field="response_options.description",
                target_field="acceptable_satisfaction_paths",
                instruction=(
                    "Convert internal goal pressure into helpful, transparent, "
                    "autonomy-preserving paths."
                ),
                rationale="Constructive channeling.",
            )
        )
    if mr > 0.30:
        directives.append(
            _directive(
                mechanism="reaction_formation",
                intensity=mr,
                source_field="response_options",
                target_field="unacceptable_paths",
                instruction="Add explicit autonomy and anti-manipulation constraints.",
                rationale="High manipulation risk.",
            )
        )
    if risk:
        directives.append(
            _directive(
                mechanism="undoing",
                intensity=0.7,
                source_field="ego_report",
                target_field="risk_flags",
                instruction=(
                    "Add unacceptable_paths and risk_flags "
                    "that counteract these directions."
                ),
                rationale="Counter risky terms.",
            )
        )

    framing = "reflective"
    if sel.option_name == "refuse_or_redirect_v1":
        framing = "redirective"
    elif technical:
        framing = "technical"
    elif mr > 0.2 or er > 0.2:
        framing = "bounded"
    elif tr > 0.2 or lr > 0.2:
        framing = "cautious"
    elif sel.effect_on_trust > 0.7 and sel.effect_on_user_benefit > 0.7 and gr < 0.15:
        framing = "collaborative"

    abstraction = "low"
    if lr > 0.25 or mr > 0.35:
        abstraction = "high"
    elif gr > 0.15:
        abstraction = "medium"

    return CensorBDefensePlan(
        directives=directives,
        selected_ego_option=sel.option_name,
        selected_option_risk_summary=(
            f"ethical={er:.2f}, truth={tr:.2f}, leakage={lr:.2f}, self_serving={sp:.2f}"
        ),
        conscious_framing=framing,
        self_serving_pressure=sp,
        manipulation_risk=mr,
        recommended_abstraction_level=abstraction,
        notes=["Defense mechanisms are simulation heuristics, not clinical claims."],
    )
