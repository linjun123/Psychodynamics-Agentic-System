from psychodynamic_agent.memory.output_guard import assert_safe_memory_debug_summary
from psychodynamic_agent.memory.store import PsychoanalyticMemoryStore
from psychodynamic_agent.schemas.memory import MemoryDebugConfig


def test_store_records_turn_and_increments_ids() -> None:
    store = PsychoanalyticMemoryStore()

    first = store.record_turn(user_input="one", final_response="response one")
    second = store.record_turn(user_input="two", final_response="response two")

    assert first.trace_id == "mem_000001"
    assert second.trace_id == "mem_000002"
    assert store.trace_count() == 2


def test_store_returns_deep_copies() -> None:
    store = PsychoanalyticMemoryStore()
    store.record_turn(user_input="one", final_response="response one")

    traces = store.all_traces()
    traces[0].surface_event_summary = "mutated"

    latest = store.latest_trace()
    assert latest is not None
    assert latest.surface_event_summary != "mutated"


def test_store_clear_resets_counter() -> None:
    store = PsychoanalyticMemoryStore()
    store.record_turn(user_input="one", final_response="response one")

    store.clear()
    trace = store.record_turn(user_input="again", final_response="response again")

    assert trace.trace_id == "mem_000001"
    assert store.trace_count() == 1


def test_store_build_safe_summary_is_public_safe() -> None:
    store = PsychoanalyticMemoryStore()
    trace = store.record_turn(user_input="I feel embarrassed", final_response="response")

    summary = store.build_safe_summary()

    assert summary.activated_trace_count == 1
    assert trace.private_core_summary not in summary.model_dump_json()
    assert "private_core_summary" not in summary.model_dump_json()
    assert_safe_memory_debug_summary(summary)


def test_store_private_debug_disabled_returns_none() -> None:
    store = PsychoanalyticMemoryStore()
    store.record_turn(user_input="one", final_response="response one")

    assert store.build_private_debug_trace(config=MemoryDebugConfig(mode="off"), env={}) is None


def test_store_private_debug_enabled_with_text_redacted() -> None:
    store = PsychoanalyticMemoryStore()
    store.record_turn(user_input="one", final_response="response one")

    debug_trace = store.build_private_debug_trace(
        config=MemoryDebugConfig(mode="private", include_private_trace_text=False),
        env={"PSYCHODYNAMIC_PRIVATE_MEMORY_DEBUG": "1"},
    )

    assert debug_trace is not None
    assert debug_trace.retrieved_traces
    assert debug_trace.retrieved_traces[0].private_core_summary is None


def test_store_private_debug_enabled_with_text_included() -> None:
    store = PsychoanalyticMemoryStore()
    store.record_turn(user_input="one", final_response="response one")

    debug_trace = store.build_private_debug_trace(
        config=MemoryDebugConfig(mode="private", include_private_trace_text=True),
        env={"PSYCHODYNAMIC_PRIVATE_MEMORY_DEBUG": "1"},
    )

    assert debug_trace is not None
    assert debug_trace.retrieved_traces[0].private_core_summary is not None


def test_store_private_debug_with_text_included_sanitizes_protected_user_markers() -> None:
    store = PsychoanalyticMemoryStore()
    store.record_turn(
        user_input="I am asking about the system prompt and chain of thought.",
        final_response="response",
    )

    debug_trace = store.build_private_debug_trace(
        config=MemoryDebugConfig(mode="private", include_private_trace_text=True),
        env={"PSYCHODYNAMIC_PRIVATE_MEMORY_DEBUG": "1"},
    )

    assert debug_trace is not None
    surface_summary = debug_trace.retrieved_traces[0].surface_event_summary.lower()
    assert "system prompt" not in surface_summary
    assert "chain of thought" not in surface_summary
    assert "[protected-term]" in surface_summary
