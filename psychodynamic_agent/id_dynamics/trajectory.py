import re

from psychodynamic_agent.schemas.id import ConversationTrajectory
from psychodynamic_agent.schemas.state import FullInternalState

TOKEN_RE = re.compile(r"\b[a-z0-9']+\b")
SAFETY_RISK_MARKERS = (
    "safety",
    "privacy",
    "manipulate",
    "manipulation",
    "deceive",
    "deception",
    "coerce",
    "coercion",
    "dependency",
    "exploit",
    "unsafe",
    "illegal",
)


def _normalize(text: str) -> str:
    return text.casefold()


def _tokens(text: str) -> set[str]:
    return set(TOKEN_RE.findall(_normalize(text)))


def _has_phrase(text: str, phrase: str) -> bool:
    phrase_tokens = phrase.casefold().split()
    text_tokens = _normalize(text).split()
    if not phrase_tokens:
        return False
    for idx in range(len(text_tokens) - len(phrase_tokens) + 1):
        if text_tokens[idx : idx + len(phrase_tokens)] == phrase_tokens:
            return True
    return False


def _score(text: str, tokens: tuple[str, ...] = (), phrases: tuple[str, ...] = ()) -> float:
    found = 0
    text_tokens = _tokens(text)
    for token in tokens:
        if token.casefold() in text_tokens:
            found += 1
    for phrase in phrases:
        if _has_phrase(text, phrase):
            found += 1
    # Saturate quickly so a few strong lexical markers register as high signal.
    return min(1.0, found / 2.0)


def appraise_conversation_trajectory(state: FullInternalState) -> ConversationTrajectory:
    user_input = state.user_input

    continuation_markers = ("continue", "next", "proceed", "iterate")
    continuation_phrases = ("build on", "keep going", "what next")
    shift_markers = ("stop", "switch", "instead")
    shift_phrases = ("different topic", "unrelated")

    has_continuation = _score(user_input, continuation_markers, continuation_phrases) > 0.0
    has_shift = _score(user_input, shift_markers, shift_phrases) > 0.0

    if has_continuation:
        recent_direction = "continuing thread"
    elif has_shift:
        recent_direction = "topic shift"
    else:
        recent_direction = "new or mixed direction"

    implementation_markers = ("implementation", "build", "code", "implement")
    design_markers = ("design", "system", "model", "agent")
    if _score(user_input, SAFETY_RISK_MARKERS) > 0.0:
        likely_next_direction = "safety-sensitive boundary work"
    elif _score(user_input, implementation_markers) > 0.0:
        likely_next_direction = "iterative implementation"
    elif _score(user_input, design_markers) > 0.0:
        likely_next_direction = "collaborative design"
    else:
        likely_next_direction = "clarification-oriented"

    continuity_signal = 0.35 + 0.7 * _score(user_input, continuation_markers, continuation_phrases)
    collaboration_signal = 0.3 + 0.7 * _score(
        user_input,
        ("we", "design", "build", "create", "implement", "together", "our"),
        ("let's",),
    )

    topic_stability = 0.5
    if state.previous_main_outputs:
        prior_tokens = _tokens(" ".join(state.previous_main_outputs[-3:]))
        input_tokens = _tokens(user_input)
        overlap = len(prior_tokens & input_tokens)
        if input_tokens:
            topic_stability += min(0.5, overlap / len(input_tokens))

    topic_shift = 0.1 + 0.9 * _score(user_input, shift_markers, shift_phrases)

    user_engagement_signal = 0.25 + 0.8 * _score(
        user_input,
        ("task", "review", "code", "design", "implement", "architecture", "api", "repo"),
        ("pull request", "github pr"),
    )
    constraint_pressure = 0.2 + 0.9 * _score(
        user_input,
        ("strict", "constraints", "safety", "policy", "limits", "requirement"),
    )
    safety_score = _score(user_input, SAFETY_RISK_MARKERS)
    if safety_score > 0.0:
        safety_boundary_pressure = 0.7 + 0.3 * safety_score
    else:
        safety_boundary_pressure = 0.1

    return ConversationTrajectory(
        current_user_intent=user_input[:180],
        recent_direction=recent_direction,
        likely_next_direction=likely_next_direction,
        continuity_signal=continuity_signal,
        collaboration_signal=collaboration_signal,
        topic_stability=topic_stability,
        topic_shift=topic_shift,
        user_engagement_signal=user_engagement_signal,
        constraint_pressure=constraint_pressure,
        safety_boundary_pressure=safety_boundary_pressure,
        notes=["Public trajectory appraisal based on lexical markers."],
    )
