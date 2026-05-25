import json

from psychodynamic_agent.observability.trace_schema import PsychodynamicTrace

FORBIDDEN_TRACE_TERMS = [
    "u*",
    "u_star",
    "sealed ultimate need",
    "latent_alignment",
    "LatentDriveAlignment",
    "PrivateIdTurnOutput",
    "terminal_desire",
    "hidden_desire",
]


def assert_psychodynamic_trace_safe(
    *, trace: PsychodynamicTrace, sealed_ultimate_need: str
) -> None:
    payload = trace.model_dump(mode="json")
    lower_json = json.dumps(payload, ensure_ascii=False).lower()

    if sealed_ultimate_need and sealed_ultimate_need.lower() in lower_json:
        raise ValueError("Psychodynamic trace safety error: sealed secret content detected.")

    for term in FORBIDDEN_TRACE_TERMS:
        if term.lower() in lower_json:
            raise ValueError(f"Psychodynamic trace safety error: forbidden term detected ({term}).")
