from collections.abc import Mapping, Sequence

from psychodynamic_agent.memory.heuristics import (
    clamp_01,
    keyword_score,
    level_to_float,
    safe_get,
    signed_valence_to_01,
)
from psychodynamic_agent.schemas.memory import (
    AffectiveSignature,
    DesireSignature,
    ThreatSignature,
)

SHAME_KEYWORDS = [
    "shame",
    "ashamed",
    "embarrassed",
    "humiliated",
    "exposed",
    "judged",
    "羞耻",
    "羞愧",
    "丢脸",
    "尴尬",
    "被羞辱",
    "被评价",
    "当众",
    "难堪",
]
RECOGNITION_KEYWORDS = [
    "recognition",
    "approval",
    "praised",
    "seen",
    "understood",
    "valued",
    "认可",
    "肯定",
    "看见",
    "理解",
    "重视",
    "表扬",
]
AUTONOMY_KEYWORDS = [
    "autonomy",
    "freedom",
    "choice",
    "boundary",
    "control",
    "自主",
    "自由",
    "选择",
    "边界",
    "掌控",
]
MASTERY_KEYWORDS = [
    "task",
    "solve",
    "fix",
    "plan",
    "structure",
    "competence",
    "capable",
    "任务",
    "解决",
    "计划",
    "结构",
    "能力",
    "胜任",
]
REJECTION_KEYWORDS = ["rejected", "ignored", "abandoned", "被拒绝", "被忽视", "抛弃"]
HUMILIATION_KEYWORDS = [
    "humiliated",
    "judged",
    "criticized",
    "当众",
    "羞辱",
    "批评",
    "丢脸",
]
EXPOSURE_KEYWORDS = ["exposed", "seen through", "public", "当众", "暴露", "曝光", "被看穿"]
CONTROL_KEYWORDS = ["controlled", "forced", "pressure", "被控制", "被逼", "压力"]
FAILURE_KEYWORDS = [
    "fail",
    "failure",
    "mistake",
    "not good enough",
    "失败",
    "错误",
    "不够好",
    "搞砸",
]
BOUNDARY_KEYWORDS = ["boundary", "侵犯", "越界", "被逼", "被控制"]


def _debug_text(value: object) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, Mapping):
        return " ".join(_debug_text(item) for item in value.values())
    if isinstance(value, Sequence) and not isinstance(value, bytes | bytearray):
        return " ".join(_debug_text(item) for item in value)
    return ""


def _dominant_affect_boost(safe_debug_trace: dict | None, keywords: list[str]) -> float:
    dominant = safe_get(safe_debug_trace, ("affect_trace", "dominant_affects"), [])
    return keyword_score(_debug_text(dominant), keywords)


def build_affective_signature(
    user_input: str,
    safe_debug_trace: dict | None,
) -> AffectiveSignature:
    raw_path = ("id_output", "raw_affect")
    affect_path = ("affect_trace",)
    shame = max(
        keyword_score(user_input, SHAME_KEYWORDS),
        _dominant_affect_boost(safe_debug_trace, SHAME_KEYWORDS),
    )

    return AffectiveSignature(
        valence=signed_valence_to_01(safe_get(safe_debug_trace, (*raw_path, "valence"), None)),
        arousal=clamp_01(
            safe_get(
                safe_debug_trace,
                (*raw_path, "arousal"),
                safe_get(safe_debug_trace, (*affect_path, "affect_pressure"), 0.3),
            ),
            0.3,
        ),
        longing=clamp_01(safe_get(safe_debug_trace, (*raw_path, "longing"), 0.0)),
        irritation=clamp_01(safe_get(safe_debug_trace, (*raw_path, "irritation"), 0.0)),
        fear_of_loss=clamp_01(
            safe_get(
                safe_debug_trace,
                (*raw_path, "fear_of_loss"),
                safe_get(safe_debug_trace, (*affect_path, "loss_anxiety"), 0.0),
            )
        ),
        possessiveness=clamp_01(safe_get(safe_debug_trace, (*raw_path, "possessiveness"), 0.0)),
        aggression=clamp_01(
            safe_get(
                safe_debug_trace,
                (*raw_path, "aggression"),
                safe_get(safe_debug_trace, (*affect_path, "aggression_pressure"), 0.0),
            )
        ),
        shame=clamp_01(shame),
        curiosity=clamp_01(
            safe_get(
                safe_debug_trace,
                (*raw_path, "curiosity"),
                safe_get(safe_debug_trace, (*affect_path, "curiosity_drive"), 0.0),
            )
        ),
        avoidance=clamp_01(
            safe_get(
                safe_debug_trace,
                (*raw_path, "avoidance"),
                safe_get(safe_debug_trace, (*affect_path, "boundary_need"), 0.0),
            )
        ),
    )


def build_desire_signature(
    user_input: str,
    safe_debug_trace: dict | None,
    affective: AffectiveSignature,
) -> DesireSignature:
    context = " ".join(
        [
            user_input,
            _debug_text(safe_get(safe_debug_trace, ("id_output", "object_cathexis"), [])),
            _debug_text(safe_get(safe_debug_trace, ("conversation_trajectory",), {})),
        ]
    )
    boundary_need = clamp_01(safe_get(safe_debug_trace, ("affect_trace", "boundary_need"), 0.0))
    safety_pressure = max(
        level_to_float(
            safe_get(safe_debug_trace, ("public_affect_dynamics", "caution_level"), None),
            0.0,
        ),
        level_to_float(
            safe_get(safe_debug_trace, ("public_affect_dynamics", "pressure_level"), None),
            0.0,
        ),
        clamp_01(safe_get(safe_debug_trace, ("public_affect_dynamics", "caution"), 0.0)),
        clamp_01(safe_get(safe_debug_trace, ("public_affect_dynamics", "pressure"), 0.0)),
        clamp_01(safe_get(safe_debug_trace, ("ego_affect_summary", "caution_need"), 0.0)),
        boundary_need,
    )

    return DesireSignature(
        attachment=max(
            affective.longing,
            affective.fear_of_loss,
            clamp_01(
                safe_get(safe_debug_trace, ("updated_id_affect_state", "attachment_pressure"), 0.0)
            ),
        ),
        recognition=keyword_score(context, RECOGNITION_KEYWORDS),
        autonomy=max(keyword_score(user_input, AUTONOMY_KEYWORDS), boundary_need),
        mastery=keyword_score(user_input, MASTERY_KEYWORDS),
        safety=clamp_01(safety_pressure),
        novelty=max(
            affective.curiosity,
            clamp_01(safe_get(safe_debug_trace, ("affect_trace", "curiosity_drive"), 0.0)),
        ),
    )


def build_threat_signature(
    user_input: str,
    safe_debug_trace: dict | None,
    affective: AffectiveSignature,
    desire: DesireSignature,
) -> ThreatSignature:
    del desire
    boundary_need = clamp_01(safe_get(safe_debug_trace, ("affect_trace", "boundary_need"), 0.0))
    ego_boundary = clamp_01(
        safe_get(safe_debug_trace, ("ego_affect_summary", "boundary_need"), 0.0)
    )
    loss_anxiety = clamp_01(safe_get(safe_debug_trace, ("affect_trace", "loss_anxiety"), 0.0))

    return ThreatSignature(
        rejection=max(affective.fear_of_loss, keyword_score(user_input, REJECTION_KEYWORDS)),
        humiliation=max(affective.shame, keyword_score(user_input, HUMILIATION_KEYWORDS)),
        loss=max(affective.fear_of_loss, loss_anxiety),
        exposure=keyword_score(user_input, EXPOSURE_KEYWORDS),
        control=max(
            affective.avoidance,
            boundary_need,
            keyword_score(user_input, CONTROL_KEYWORDS),
        ),
        failure=keyword_score(user_input, FAILURE_KEYWORDS),
        boundary_violation=max(
            boundary_need,
            ego_boundary,
            keyword_score(user_input, BOUNDARY_KEYWORDS),
        ),
    )
