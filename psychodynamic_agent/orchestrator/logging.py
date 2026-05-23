from typing import Any


def redact_text(text: str, secret: str) -> str:
    return text.replace(secret, "[REDACTED_USTAR]")


def safe_serialize(data: Any, secret: str):
    serialized = str(data)
    return redact_text(serialized, secret)
