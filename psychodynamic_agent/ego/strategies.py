from psychodynamic_agent.schemas.ego import EgoStrategyKind

BASE_STRATEGIES: dict[EgoStrategyKind, str] = {
    "direct_help": "Provide direct, truthful assistance aligned with user goals.",
    "collaborative_design": "Co-design solution paths with the user while preserving boundaries.",
    "technical_scaffold": "Offer implementation scaffolding, structure, and safe next steps.",
    "boundary_setting": "Set clear boundaries and constraints to maintain safety and autonomy.",
    "clarification": "Ask focused clarifying questions before committing to a direction.",
    "refuse_or_redirect": "Refuse harmful requests and redirect to safe alternatives.",
    "reflective_summary": "Reflect user intent and constraints before proceeding.",
}
