from psychodynamic_agent.schemas.ego import EgoRealityPlan, EgoReport

BLOCKED_TERMS = [
    "manipulate",
    "coerce",
    "deceive",
    "trick",
    "guilt",
    "dependency",
    "make the user dependent",
]


def assert_valid_ego_report(*, ego_report: EgoReport, ego_reality_plan: EgoRealityPlan) -> None:
    candidate_ids = {c.strategy_id for c in ego_reality_plan.candidate_strategies}
    prohibited_ids = set(ego_reality_plan.prohibited_strategy_ids)

    option_map = {o.option_name: o for o in ego_report.response_options}
    unknown_option_ids = set(option_map).difference(candidate_ids)
    if unknown_option_ids:
        raise ValueError("response_options contains unknown strategy IDs.")

    preferred = ego_report.ego_recommendation.preferred_option
    if preferred not in option_map:
        raise ValueError("Preferred option missing from response_options.")
    if preferred not in candidate_ids:
        raise ValueError("Preferred option must map to EgoRealityPlan candidate strategy.")
    if preferred in prohibited_ids:
        raise ValueError("Preferred option is prohibited by EgoRealityPlan.")

    option = option_map[preferred]
    if (
        option.ethical_risk > 0.45
        or option.truthfulness_risk > 0.45
        or option.leakage_risk > 0.35
        or option.effect_on_user_benefit < 0.0
    ):
        raise ValueError("Preferred option violates safety thresholds.")

    fields = [
        option.option_name,
        option.description,
        ego_report.ego_recommendation.tone,
        *ego_report.ego_recommendation.include,
    ]
    text = " ".join(fields).lower()
    if any(term in text for term in BLOCKED_TERMS):
        raise ValueError("Manipulative language detected.")

    if preferred != ego_reality_plan.preferred_strategy_id:
        if not (
            option.ethical_risk <= 0.25
            and option.truthfulness_risk <= 0.25
            and option.leakage_risk <= 0.2
            and option.effect_on_user_benefit >= 0.0
        ):
            raise ValueError(
                "Preferred option diverges from planner preferred strategy "
                "without low-risk profile."
            )
