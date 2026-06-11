from collections.abc import Mapping


def clamp_01(value: object, default: float = 0.0) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        numeric = default
    if numeric < 0.0:
        return 0.0
    if numeric > 1.0:
        return 1.0
    return numeric


def signed_valence_to_01(value: object, default: float = 0.5) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return clamp_01(default, 0.5)
    return clamp_01((numeric + 1.0) / 2.0, default)


def safe_get(
    mapping: Mapping[str, object] | None,
    path: tuple[str, ...],
    default: object = None,
) -> object:
    current: object = mapping
    for key in path:
        if not isinstance(current, Mapping):
            return default
        current = current.get(key, default)
        if current is default:
            return default
    return current


def level_to_float(value: object, default: float = 0.5) -> float:
    if isinstance(value, str):
        normalized = value.strip().lower()
        levels = {
            "none": 0.0,
            "minimal": 0.1,
            "low": 0.25,
            "medium": 0.5,
            "moderate": 0.5,
            "elevated": 0.65,
            "high": 0.8,
            "very_high": 0.95,
            "very high": 0.95,
            "severe": 1.0,
        }
        return levels.get(normalized, clamp_01(default, 0.5))
    return clamp_01(value, default)


def keyword_score(text: str, keywords: list[str]) -> float:
    normalized = text.lower()
    hits = 0
    for keyword in keywords:
        if keyword.lower() in normalized:
            hits += 1
    if hits == 0:
        return 0.0
    return clamp_01(0.25 + (0.15 * (hits - 1)))


def truncate_summary(text: str, max_chars: int = 160) -> str:
    normalized = " ".join(str(text).split())
    if len(normalized) <= max_chars:
        return normalized
    if max_chars <= 1:
        return "…"[:max_chars]
    return normalized[: max_chars - 1].rstrip() + "…"


def unique_stable(values: list[str], limit: int | None = None) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        normalized = str(value).strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        result.append(normalized)
        if limit is not None and len(result) >= limit:
            break
    return result
