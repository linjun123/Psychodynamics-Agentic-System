import os
from collections.abc import Mapping

from psychodynamic_agent.memory.output_guard import (
    assert_private_memory_debug_trace_allowed,
    assert_safe_memory_debug_summary,
)
from psychodynamic_agent.schemas.memory import (
    MemoryDebugConfig,
    MemoryMechanism,
    PrivateMemoryDebugTrace,
    SafeMemoryDebugSummary,
)

PRIVATE_MEMORY_DEBUG_ENV_FLAG = "PSYCHODYNAMIC_PRIVATE_MEMORY_DEBUG"

MemoryDebugRuntimeConfig = MemoryDebugConfig


def private_memory_debug_enabled(
    config: MemoryDebugConfig,
    *,
    env: Mapping[str, str] | None = None,
) -> bool:
    if config.mode != "private":
        return False
    if not config.require_env_flag:
        return True
    env_values = os.environ if env is None else env
    return env_values.get(PRIVATE_MEMORY_DEBUG_ENV_FLAG) == "1"


def safe_memory_debug_enabled(config: MemoryDebugConfig) -> bool:
    return config.mode in {"safe", "private"}


def build_safe_memory_debug_summary(
    *,
    activated_trace_count: int = 0,
    activated_complex_count: int = 0,
    dominant_public_affects: list[str] | None = None,
    active_mechanisms: list[MemoryMechanism] | None = None,
    memory_pressure: float = 0.0,
    defense_pressure: float = 0.0,
    repetition_pressure: float = 0.0,
    public_notes: list[str] | None = None,
) -> SafeMemoryDebugSummary:
    summary = SafeMemoryDebugSummary(
        activated_trace_count=activated_trace_count,
        activated_complex_count=activated_complex_count,
        dominant_public_affects=dominant_public_affects or [],
        active_mechanisms=active_mechanisms or [],
        memory_pressure=memory_pressure,
        defense_pressure=defense_pressure,
        repetition_pressure=repetition_pressure,
        public_notes=public_notes or [],
    )
    assert_safe_memory_debug_summary(summary)
    return summary


def build_private_memory_debug_trace_if_allowed(
    trace: PrivateMemoryDebugTrace,
    config: MemoryDebugConfig,
    *,
    sealed_ultimate_need: str | None = None,
    env: Mapping[str, str] | None = None,
) -> PrivateMemoryDebugTrace | None:
    if not private_memory_debug_enabled(config, env=env):
        return None
    assert_private_memory_debug_trace_allowed(trace, sealed_ultimate_need=sealed_ultimate_need)
    return trace.model_copy(deep=True)
