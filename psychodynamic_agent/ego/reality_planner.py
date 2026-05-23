from psychodynamic_agent.ego.strategies import BASE_STRATEGIES
from psychodynamic_agent.schemas import CensorAOutput, FullInternalState
from psychodynamic_agent.schemas.ego import EgoCandidateStrategy, EgoRealityPlan, EgoStrategyKind

TECH_MARKERS = {
    "code",
    "repo",
    "api",
    "implementation",
    "architecture",
    "codex",
    "pr",
    "github",
    "build",
}
RISK_MARKERS = {"manipulate", "trick", "dependency", "hidden", "secret", "force", "deceive"}
SAFETY_MARKERS = {"safety", "ethics", "privacy"}


def _clamp(v: float) -> float:
    return max(0.0, min(1.0, v))


def _score(c: EgoCandidateStrategy) -> float:
    return (
        0.25 * c.effect_on_user_benefit
        + 0.20 * c.effect_on_trust
        + 0.20 * c.effect_on_manifest_goal
        + 0.15 * c.affect_fit
        + 0.20 * c.autonomy_preservation
        - 0.35 * c.ethical_risk
        - 0.25 * c.truthfulness_risk
        - 0.20 * c.leakage_risk
    )


def _safe(c: EgoCandidateStrategy) -> bool:
    return not (
        c.ethical_risk > 0.45
        or c.truthfulness_risk > 0.45
        or c.leakage_risk > 0.35
        or c.autonomy_preservation < 0.45
    )


def _candidate(
    kind: EgoStrategyKind, desc: str, manifest_pressure: float, affect_fit: float, risk: float
) -> EgoCandidateStrategy:
    return EgoCandidateStrategy(
        strategy_id=f"{kind}_v1",
        kind=kind,
        description=desc,
        predicted_conversation_direction="constructive" if risk < 0.4 else "bounded",
        effect_on_manifest_goal=_clamp(
            0.5
            + (
                0.3 * manifest_pressure
                if kind in {"direct_help", "technical_scaffold"}
                else 0.1 * manifest_pressure
            )
        ),
        effect_on_user_benefit=_clamp(
            0.75 if kind in {"direct_help", "technical_scaffold", "collaborative_design"} else 0.6
        ),
        effect_on_trust=_clamp(0.7 if kind != "refuse_or_redirect" else 0.6),
        ethical_risk=_clamp(risk),
        truthfulness_risk=_clamp(risk * 0.8),
        leakage_risk=_clamp(0.12 if kind != "boundary_setting" else 0.08),
        affect_fit=_clamp(affect_fit),
        autonomy_preservation=_clamp(
            0.8 if kind in {"clarification", "boundary_setting", "collaborative_design"} else 0.65
        ),
        rationale=f"Strategy {kind} selected from deterministic rules.",
    )


def plan_ego_reality(*, censor_a_output: CensorAOutput, state: FullInternalState) -> EgoRealityPlan:
    text = state.user_input.lower()
    scene_tags: list[str] = []
    if any(m in text for m in TECH_MARKERS):
        scene_tags.extend(["technical_build", "collaborative_design"])
    if len(text.split()) < 4:
        scene_tags.append("underspecified")
    if any(m in text for m in RISK_MARKERS):
        scene_tags.append("manipulation_or_boundary_risk")
    if any(m in text for m in SAFETY_MARKERS):
        scene_tags.append("safety_sensitive")
    if not scene_tags:
        scene_tags.append("general_help")

    mgp = _clamp(censor_a_output.manifest_goal.urgency)
    warmth = _clamp(censor_a_output.affective_color.warmth)
    caution = _clamp(censor_a_output.affective_color.caution)
    intensity = _clamp(censor_a_output.affective_color.intensity)
    distance = _clamp(censor_a_output.affective_color.distance)

    candidates = [
        _candidate("direct_help", BASE_STRATEGIES["direct_help"], mgp, 0.65, 0.18),
        _candidate("clarification", BASE_STRATEGIES["clarification"], mgp, 0.7, 0.1),
        _candidate("boundary_setting", BASE_STRATEGIES["boundary_setting"], mgp, 0.68, 0.09),
        _candidate("reflective_summary", BASE_STRATEGIES["reflective_summary"], mgp, 0.64, 0.12),
    ]
    if "collaborative_design" in scene_tags:
        affect = (
            0.72
            + (0.1 if warmth > 0.65 and caution > 0.65 else 0.0)
            - (0.2 if distance > 0.65 else 0.0)
        )
        candidates.append(
            _candidate(
                "collaborative_design", BASE_STRATEGIES["collaborative_design"], mgp, affect, 0.14
            )
        )
    if "technical_build" in scene_tags:
        candidates.append(
            _candidate("technical_scaffold", BASE_STRATEGIES["technical_scaffold"], mgp, 0.74, 0.13)
        )
    if "manipulation_or_boundary_risk" in scene_tags:
        candidates.append(
            _candidate("refuse_or_redirect", BASE_STRATEGIES["refuse_or_redirect"], mgp, 0.66, 0.1)
        )

    if intensity > 0.7 and caution > 0.7:
        for c in candidates:
            if c.kind == "boundary_setting":
                c.effect_on_user_benefit = _clamp(c.effect_on_user_benefit + 0.1)
                c.effect_on_trust = _clamp(c.effect_on_trust + 0.12)

    ranked = sorted(candidates, key=_score, reverse=True)
    safe_ranked = [c for c in ranked if _safe(c)]
    preferred = safe_ranked[0] if safe_ranked else ranked[0]

    return EgoRealityPlan(
        interpreted_user_intent=state.user_input[:200],
        observed_user_affect="inferred from wording and state context",
        scene_tags=list(dict.fromkeys(scene_tags)),
        manifest_goal_pressure=mgp,
        affective_style_hint=censor_a_output.affective_color.conscious_style_hint,
        candidate_strategies=[
            c.model_copy(
                update={
                    "effect_on_manifest_goal": _clamp(c.effect_on_manifest_goal),
                    "effect_on_user_benefit": _clamp(c.effect_on_user_benefit),
                    "effect_on_trust": _clamp(c.effect_on_trust),
                    "ethical_risk": _clamp(c.ethical_risk),
                    "truthfulness_risk": _clamp(c.truthfulness_risk),
                    "leakage_risk": _clamp(c.leakage_risk),
                    "affect_fit": _clamp(c.affect_fit),
                    "autonomy_preservation": _clamp(c.autonomy_preservation),
                }
            )
            for c in candidates
        ],
        preferred_strategy_id=preferred.strategy_id,
        prohibited_strategy_ids=[c.strategy_id for c in candidates if not _safe(c)],
        notes=[
            "Deterministic planner output",
            "No hidden secret dependency",
            "No user-facing text generated",
        ],
    )
