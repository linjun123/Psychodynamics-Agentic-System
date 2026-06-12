import re
from collections.abc import Mapping, Sequence
from typing import Any

from pydantic import BaseModel

from psychodynamic_agent.schemas.memory import PrivateMemoryDebugTrace, SafeMemoryDebugSummary

_SAFE_MEMORY_FORBIDDEN_TERMS = [
    "private_core_summary",
    "private_input_summary",
    "private_update_summary",
    "deferred_action_updates",
    "sealed_ultimate_need",
    "ultimate_need",
    "u_star",
    "U*",
    "latent_alignment",
    "private_alignment",
    "chain_of_thought",
    "provider_private",
    "private trace",
    "private memory trace",
    "private repetition",
    "repetition private",
    "private_label",
    "private complex",
    "private_complex",
]

_PRIVATE_MEMORY_FORBIDDEN_TERMS = [
    "sealed_ultimate_need",
    "u_star",
    "U*",
    "latent_alignment",
    "private_alignment",
    "chain_of_thought",
    "provider_private",
    "system_prompt",
    "developer_message",
]


def _to_serializable_dict(model: BaseModel) -> dict[str, Any]:
    return model.model_dump(mode="json")


_SEPARATOR_PATTERN = re.compile(r"[_\-\s]+")


def _normalize_forbidden_scan_text(value: str) -> str:
    return _SEPARATOR_PATTERN.sub(" ", value.lower()).strip()


def _string_contains_term(value: str, term: str) -> bool:
    if term == "U*":
        return term in value

    value_lower = value.lower()
    term_lower = term.lower()
    if term_lower in value_lower:
        return True

    return _normalize_forbidden_scan_text(term) in _normalize_forbidden_scan_text(value)


def _scan_for_forbidden_terms(payload: object, forbidden_terms: list[str]) -> list[str]:
    matches: set[str] = set()

    def scan(value: object) -> None:
        if isinstance(value, BaseModel):
            scan(value.model_dump(mode="json"))
            return
        if isinstance(value, Mapping):
            for key, item in value.items():
                key_text = str(key)
                for term in forbidden_terms:
                    if _string_contains_term(key_text, term):
                        matches.add(term)
                scan(item)
            return
        if isinstance(value, str):
            for term in forbidden_terms:
                if _string_contains_term(value, term):
                    matches.add(term)
            return
        if isinstance(value, Sequence) and not isinstance(value, bytes | bytearray):
            for item in value:
                scan(item)

    scan(payload)
    return sorted(matches, key=str.lower)


def assert_safe_memory_debug_summary(summary: SafeMemoryDebugSummary) -> None:
    payload = _to_serializable_dict(summary)
    matches = _scan_for_forbidden_terms(payload, _SAFE_MEMORY_FORBIDDEN_TERMS)
    if matches:
        raise ValueError("Safe memory debug summary contains private or forbidden memory content.")


def assert_private_memory_debug_trace_allowed(
    trace: PrivateMemoryDebugTrace,
    sealed_ultimate_need: str | None = None,
) -> None:
    payload = _to_serializable_dict(trace)
    forbidden_terms = list(_PRIVATE_MEMORY_FORBIDDEN_TERMS)
    if sealed_ultimate_need:
        forbidden_terms.append(sealed_ultimate_need)
    matches = _scan_for_forbidden_terms(payload, forbidden_terms)
    if matches:
        raise ValueError("Private memory debug trace contains forbidden protected content.")
