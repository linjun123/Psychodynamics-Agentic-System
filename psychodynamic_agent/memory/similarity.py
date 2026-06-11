import re
from numbers import Number

from psychodynamic_agent.memory.heuristics import clamp_01
from psychodynamic_agent.schemas.base import StrictSchemaModel

_TOKEN_PATTERN = re.compile(r"[\w]+", re.UNICODE)
_CJK_PATTERN = re.compile(r"[\u4e00-\u9fff]")


def scalar_similarity(a: float, b: float) -> float:
    return clamp_01(1.0 - abs(float(a) - float(b)))


def signature_similarity(left: StrictSchemaModel, right: StrictSchemaModel) -> float:
    left_data = left.model_dump()
    right_data = right.model_dump()
    common_keys = sorted(set(left_data) & set(right_data))
    similarities: list[float] = []
    for key in common_keys:
        left_value = left_data[key]
        right_value = right_data[key]
        if isinstance(left_value, Number) and isinstance(right_value, Number):
            similarities.append(scalar_similarity(float(left_value), float(right_value)))
    if not similarities:
        return 0.0
    return clamp_01(sum(similarities) / len(similarities))


def _normalized_set(values: list[str]) -> set[str]:
    return {str(value).strip().casefold() for value in values if str(value).strip()}


def list_overlap_score(left: list[str], right: list[str]) -> float:
    left_set = _normalized_set(left)
    right_set = _normalized_set(right)
    if not left_set or not right_set:
        return 0.0
    return clamp_01(len(left_set & right_set) / max(len(left_set), len(right_set)))


def _tokens(value: str | None) -> set[str]:
    if not value:
        return set()
    text = str(value).casefold()
    tokens = {match.group(0) for match in _TOKEN_PATTERN.finditer(text) if match.group(0)}
    if not tokens and _CJK_PATTERN.search(text):
        return {char for char in text if _CJK_PATTERN.match(char)}
    for cjk_run in re.findall(r"[\u4e00-\u9fff]+", text):
        tokens.update(cjk_run[index : index + 2] for index in range(max(len(cjk_run) - 1, 1)))
    return {token for token in tokens if token.strip()}


def token_jaccard_similarity(left: str | None, right: str | None) -> float:
    left_tokens = _tokens(left)
    right_tokens = _tokens(right)
    if not left_tokens or not right_tokens:
        return 0.0
    return clamp_01(len(left_tokens & right_tokens) / len(left_tokens | right_tokens))


def repetition_frequency_score(activation_count: int) -> float:
    return clamp_01(float(activation_count) / 5.0)


def defense_barrier_score(defense_level: float, repression_pressure: float) -> float:
    return clamp_01(max(defense_level, repression_pressure))
