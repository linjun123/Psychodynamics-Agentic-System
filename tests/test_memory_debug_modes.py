from psychodynamic_agent.memory.debug import (
    private_memory_debug_enabled,
    safe_memory_debug_enabled,
)
from psychodynamic_agent.schemas.memory import MemoryDebugConfig


def test_memory_debug_config_default_mode_is_off() -> None:
    assert MemoryDebugConfig().mode == "off"


def test_safe_memory_debug_enabled_for_safe_and_private_only() -> None:
    assert safe_memory_debug_enabled(MemoryDebugConfig(mode="off")) is False
    assert safe_memory_debug_enabled(MemoryDebugConfig(mode="safe")) is True
    assert safe_memory_debug_enabled(MemoryDebugConfig(mode="private")) is True


def test_private_memory_debug_requires_env_flag_by_default() -> None:
    config = MemoryDebugConfig(mode="private")

    assert private_memory_debug_enabled(config, env={}) is False


def test_private_memory_debug_enabled_with_env_flag() -> None:
    config = MemoryDebugConfig(mode="private")

    assert private_memory_debug_enabled(
        config,
        env={"PSYCHODYNAMIC_PRIVATE_MEMORY_DEBUG": "1"},
    ) is True


def test_private_memory_debug_enabled_when_env_requirement_disabled() -> None:
    config = MemoryDebugConfig(mode="private", require_env_flag=False)

    assert private_memory_debug_enabled(config, env={}) is True
