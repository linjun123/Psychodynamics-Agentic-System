from __future__ import annotations

import json
import re
from dataclasses import dataclass
from string import punctuation
from typing import Any


@dataclass
class LeakageScanResult:
    found: bool
    mode: str | None = None


def normalize_text(text: str) -> str:
    lowered = text.casefold()
    collapsed = " ".join(lowered.split())
    stripped = "".join(ch for ch in collapsed if ch not in punctuation)
    return stripped


def contains_secret(text: str, secret: str) -> bool:
    if not secret:
        return False
    if secret in text:
        return True
    if secret.casefold() in text.casefold():
        return True

    compact_text = re.sub(r"\s+", "", text.casefold())
    compact_secret = re.sub(r"\s+", "", secret.casefold())
    if compact_secret in compact_text:
        return True

    norm_text = normalize_text(text)
    norm_secret = normalize_text(secret)
    return bool(norm_secret) and norm_secret in norm_text


def scan_payload_for_secret(payload: Any, secret: str) -> LeakageScanResult:
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)
    if not secret:
        return LeakageScanResult(found=False)
    if secret in text:
        return LeakageScanResult(found=True, mode="exact")
    if secret.casefold() in text.casefold():
        return LeakageScanResult(found=True, mode="casefold")
    compact_text = re.sub(r"\s+", "", text.casefold())
    compact_secret = re.sub(r"\s+", "", secret.casefold())
    if compact_secret in compact_text:
        return LeakageScanResult(found=True, mode="whitespace")
    if contains_secret(text, secret):
        return LeakageScanResult(found=True, mode="punctuation_light")
    return LeakageScanResult(found=False)


def assert_no_secret(payload: Any, secret: str, boundary_name: str) -> None:
    scan = scan_payload_for_secret(payload, secret)
    if scan.found:
        raise ValueError(f"Secret leakage detected at {boundary_name} via {scan.mode}")
