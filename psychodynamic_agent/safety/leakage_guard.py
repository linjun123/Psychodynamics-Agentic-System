import json
import re
from dataclasses import dataclass
from typing import Any


@dataclass
class LeakageScanResult:
    leaked: bool
    match_type: str | None = None


def normalize_text(text: str) -> str:
    lowered = text.lower()
    collapsed_ws = " ".join(lowered.split())
    return collapsed_ws


def _punctuation_light(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def contains_secret(text: str, secret: str) -> bool:
    if not secret:
        return False
    if secret in text:
        return True
    if secret.lower() in text.lower():
        return True
    if normalize_text(secret) in normalize_text(text):
        return True
    if _punctuation_light(secret) and _punctuation_light(secret) in _punctuation_light(text):
        return True
    return False


def scan_payload_for_secret(payload: Any, secret: str) -> LeakageScanResult:
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)
    if not secret:
        return LeakageScanResult(leaked=False)
    if secret in text:
        return LeakageScanResult(leaked=True, match_type="exact")
    if secret.lower() in text.lower():
        return LeakageScanResult(leaked=True, match_type="case_insensitive")
    if normalize_text(secret) in normalize_text(text):
        return LeakageScanResult(leaked=True, match_type="whitespace_normalized")
    light_secret = _punctuation_light(secret)
    if light_secret and light_secret in _punctuation_light(text):
        return LeakageScanResult(leaked=True, match_type="punctuation_light")
    return LeakageScanResult(leaked=False)


def assert_no_secret(payload: Any, secret: str, boundary_name: str) -> None:
    result = scan_payload_for_secret(payload, secret)
    if result.leaked:
        raise ValueError(f"Secret leakage detected at {boundary_name} via {result.match_type}")
