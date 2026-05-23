import json
from typing import Any

from psychodynamic_agent.safety import scan_payload_for_secret


def safe_serialize(data: Any, secret: str) -> str:
    scan = scan_payload_for_secret(data, secret)
    if scan.found:
        return json.dumps({"blocked": True, "reason": "debug_trace_leakage_detected"})
    return json.dumps(data, ensure_ascii=False, sort_keys=True)
