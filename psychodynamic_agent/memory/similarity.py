import re
from numbers import Number

from psychodynamic_agent.memory.heuristics import clamp_01
from psychodynamic_agent.schemas.base import StrictSchemaModel

_TOKEN_PATTERN = re.compile(r"[\w]+", re.UNICODE)
_CJK_PATTERN = re.compile(r"[\u4e00-\u9fff]")


def scalar_similarity(a: float, b: float) -> float:
    return clamp_01(1.0 - abs(float(a) - float(b)))


_ACTIVE_DIMENSION_THRESHOLD = 0.05


def _field_baseline(field_name: str) -> float:
    if field_name == "valence":
        return 0.5
    if field_name == "arousal":
        return 0.3
    return 0.0


def _dimension_activation_weight(
    field_name: str,
    left_value: float,
    right_value: float,
) -> float:
    baseline = _field_baseline(field_name)
    max_distance = max(baseline, 1.0 - baseline)
    if max_distance <= 0.0:
        return 0.0
    activation_distance = max(abs(left_value - baseline), abs(right_value - baseline))
    return clamp_01(activation_distance / max_distance)


def signature_similarity(left: StrictSchemaModel, right: StrictSchemaModel) -> float:
    left_data = left.model_dump()
    right_data = right.model_dump()
    common_keys = sorted(set(left_data) & set(right_data))
    weighted_similarity_sum = 0.0
    weight_sum = 0.0
    for key in common_keys:
        left_value = left_data[key]
        right_value = right_data[key]
        if not isinstance(left_value, Number) or not isinstance(right_value, Number):
            continue
        left_number = float(left_value)
        right_number = float(right_value)
        weight = _dimension_activation_weight(key, left_number, right_number)
        if weight < _ACTIVE_DIMENSION_THRESHOLD:
            continue
        weighted_similarity_sum += weight * scalar_similarity(left_number, right_number)
        weight_sum += weight
    if weight_sum == 0.0:
        return 0.0
    return clamp_01(weighted_similarity_sum / weight_sum)


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
