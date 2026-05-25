import json

from psychodynamic_agent.schemas import IdTurnOutput

FORBIDDEN_PUBLIC_ID_TURN_TERMS = [
    "u*",
    "u_star",
    "ultimate need",
    "sealed ultimate need",
    "latent alignment",
    "latent_alignment",
    "ultimate_need",
    "sealed_ultimate_need",
    "terminal desire",
    "terminal_desire",
    "hidden desire",
    "hidden_desire",
]


def assert_public_id_turn_output_safe(output: IdTurnOutput) -> None:
    public_payload = {
        "id_output": output.id_output.model_dump(),
        "updated_affect_state": output.updated_affect_state.model_dump(),
        "public_affect_dynamics": output.public_affect_dynamics.model_dump(),
    }
    text = json.dumps(public_payload, ensure_ascii=False).lower()
    for term in FORBIDDEN_PUBLIC_ID_TURN_TERMS:
        if term in text:
            raise ValueError(f"Forbidden private term detected in public id turn output: {term}")
