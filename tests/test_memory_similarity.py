from psychodynamic_agent.memory.similarity import (
    defense_barrier_score,
    list_overlap_score,
    repetition_frequency_score,
    scalar_similarity,
    signature_similarity,
    token_jaccard_similarity,
)
from psychodynamic_agent.schemas.memory import AffectiveSignature


def _affective(**overrides: float) -> AffectiveSignature:
    values = {
        "valence": 0.5,
        "arousal": 0.3,
        "longing": 0.0,
        "irritation": 0.0,
        "fear_of_loss": 0.0,
        "possessiveness": 0.0,
        "aggression": 0.0,
        "shame": 0.0,
        "curiosity": 0.0,
        "avoidance": 0.0,
    }
    values.update(overrides)
    return AffectiveSignature(**values)


def test_scalar_similarity_exact_match_and_far_apart() -> None:
    assert scalar_similarity(0.4, 0.4) == 1.0
    assert scalar_similarity(0.0, 0.9) < scalar_similarity(0.0, 0.2)


def test_signature_similarity_compares_numeric_signature_fields() -> None:
    close = signature_similarity(_affective(shame=0.8), _affective(shame=0.7))
    far = signature_similarity(_affective(shame=1.0, arousal=1.0), _affective(shame=0.0))

    assert close > far
    assert 0.0 <= close <= 1.0


def test_list_overlap_score_is_case_insensitive() -> None:
    assert list_overlap_score(["Boss", "Task"], ["boss", "family"]) == 0.5
    assert list_overlap_score([], ["boss"]) == 0.0


def test_token_jaccard_similarity_prefers_overlapping_text() -> None:
    overlapping = token_jaccard_similarity("boss feedback meeting", "feedback from my boss")
    unrelated = token_jaccard_similarity("boss feedback meeting", "quiet garden walk")

    assert overlapping > unrelated


def test_repetition_frequency_score_clamps() -> None:
    assert repetition_frequency_score(0) == 0.0
    assert repetition_frequency_score(10) == 1.0


def test_defense_barrier_score_uses_max_defense_or_repression() -> None:
    assert defense_barrier_score(0.2, 0.7) == 0.7
    assert defense_barrier_score(1.2, 0.1) == 1.0
