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
    del ego_reality_plan
    option_map = {o.option_name: o for o in ego_report.response_options}
    preferred = ego_report.ego_recommendation.preferred_option
    if preferred not in option_map:
        raise ValueError("Preferred option missing from response_options.")
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
        *ego_report.ego_recommendation.avoid,
    ]
    text = " ".join(fields).lower()
    if any(term in text for term in BLOCKED_TERMS):
        raise ValueError("Manipulative language detected.")
