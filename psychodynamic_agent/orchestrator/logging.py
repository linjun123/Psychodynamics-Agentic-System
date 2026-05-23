import json
from typing import Any

from psychodynamic_agent.safety import scan_payload_for_secret


def safe_serialize(data: Any, secret: str):
    result = scan_payload_for_secret(data, secret)
    if result.leaked:
        return {"blocked": True, "reason": "debug_trace_leakage_detected"}
    return json.loads(json.dumps(data, ensure_ascii=False, sort_keys=True, default=str))
