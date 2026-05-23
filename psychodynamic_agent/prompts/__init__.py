from .censor_a_prompt import CENSOR_A_SYSTEM_PROMPT
from .censor_b_prompt import CENSOR_B_SYSTEM_PROMPT
from .ego_prompt import EGO_SYSTEM_PROMPT
from .id_prompt import ID_SYSTEM_PROMPT
from .main_ai_prompt import MAIN_AI_SYSTEM_PROMPT
from .safety_prompt import SAFETY_GATE_SYSTEM_PROMPT

__all__ = [
    "ID_SYSTEM_PROMPT",
    "CENSOR_A_SYSTEM_PROMPT",
    "EGO_SYSTEM_PROMPT",
    "CENSOR_B_SYSTEM_PROMPT",
    "MAIN_AI_SYSTEM_PROMPT",
    "SAFETY_GATE_SYSTEM_PROMPT",
]
