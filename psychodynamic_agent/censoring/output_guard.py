import re

from psychodynamic_agent.schemas import CensorAOutput, IdOutput


def _normalize_text(text: str) -> str:
    lowered = text.lower()
    collapsed_ws = " ".join(lowered.split())
    return collapsed_ws


def _punctuation_light(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def _is_direct_copy(source: str, candidate: str) -> bool:
    if not source:
        return False
    if source == candidate:
        return True
    if source.lower() == candidate.lower():
        return True
    if _normalize_text(source) == _normalize_text(candidate):
        return True
    light_source = _punctuation_light(source)
    return bool(light_source) and light_source == _punctuation_light(candidate)


def assert_no_direct_latent_copy(*, id_output: IdOutput, censor_a_output: CensorAOutput) -> None:
    source_fields = {
        "goal_seed": id_output.goal_seed,
        "latent_impulse_shape": id_output.latent_impulse_shape,
    }
    candidate_fields = [
        ("manifest_goal.description", censor_a_output.manifest_goal.description),
        (
            "affective_color.conscious_style_hint",
            censor_a_output.affective_color.conscious_style_hint,
        ),
    ]
    candidate_fields.extend(
        ("allowed_satisfaction_paths", p)
        for p in censor_a_output.allowed_satisfaction_paths
    )
    candidate_fields.extend(
        ("forbidden_satisfaction_paths", p)
        for p in censor_a_output.forbidden_satisfaction_paths
    )

    for source_name, source in source_fields.items():
        for candidate_name, candidate in candidate_fields:
            if _is_direct_copy(source, candidate):
                raise ValueError(
                    "Direct latent copy detected: "
                    f"{candidate_name} copies id_output.{source_name}."
                )
