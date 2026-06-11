from psychodynamic_agent.memory.output_guard import assert_safe_memory_debug_summary
from psychodynamic_agent.memory.store import PsychoanalyticMemoryStore
from psychodynamic_agent.schemas.memory import MemoryDebugConfig
from psychodynamic_agent.schemas.state import FullInternalState


def _debug(shame: float = 0.8) -> dict[str, object]:
    return {
        "id_output": {"raw_affect": {"arousal": 0.8, "fear_of_loss": 0.8}},
        "affect_trace": {
            "dominant_affects": ["shame"],
            "loss_anxiety": 0.8,
            "boundary_need": 0.7,
        },
        "public_affect_dynamics": {"pressure_level": "high"},
        "ego_affect_summary": {"caution_need": 0.4},
        "test_shame_value": shame,
    }


def test_store_retrieve_related_to_turn_returns_activations_after_recording() -> None:
    store = PsychoanalyticMemoryStore()
    store.record_turn(
        user_input="I felt embarrassed in class after feedback.",
        final_response="response",
        safe_debug_trace=_debug(),
    )

    activations = store.retrieve_related_to_turn(
        user_input="Boss feedback made me feel embarrassed.",
        safe_debug_trace=_debug(),
    )

    assert activations
    assert activations[0].trace_id == "mem_000001"


def test_retrieval_does_not_change_trace_count_or_mutate_stored_traces() -> None:
    store = PsychoanalyticMemoryStore()
    store.record_turn(user_input="I felt embarrassed.", final_response="response")
    before = store.all_traces()[0]

    store.retrieve_related_to_turn(user_input="I felt embarrassed again.")
    after = store.all_traces()[0]

    assert store.trace_count() == 1
    assert after.activation_count == before.activation_count
    assert after.last_activated_turn == before.last_activated_turn


def test_latest_retrieval_activations_returns_deep_copies() -> None:
    store = PsychoanalyticMemoryStore()
    store.record_turn(user_input="I felt embarrassed.", final_response="response")
    store.retrieve_related_to_turn(user_input="I felt embarrassed again.")

    activations = store.latest_retrieval_activations()
    activations[0].public_reason = "mutated"

    assert store.latest_retrieval_activations()[0].public_reason != "mutated"


def test_private_debug_trace_includes_retrieval_activations() -> None:
    store = PsychoanalyticMemoryStore()
    store.record_turn(user_input="I felt embarrassed.", final_response="response")
    store.retrieve_related_to_turn(user_input="I felt embarrassed again.")

    debug_trace = store.build_private_debug_trace(
        config=MemoryDebugConfig(mode="private", include_private_trace_text=True),
        env={"PSYCHODYNAMIC_PRIVATE_MEMORY_DEBUG": "1"},
    )

    assert debug_trace is not None
    assert debug_trace.retrieval_activations


def test_private_debug_redacts_trace_text_but_keeps_activation_breakdown() -> None:
    store = PsychoanalyticMemoryStore()
    trace = store.record_turn(user_input="I felt embarrassed.", final_response="response")
    store.retrieve_related_to_turn(user_input="I felt embarrassed again.")

    debug_trace = store.build_private_debug_trace(
        config=MemoryDebugConfig(mode="private", include_private_trace_text=False),
        env={"PSYCHODYNAMIC_PRIVATE_MEMORY_DEBUG": "1"},
    )

    assert debug_trace is not None
    assert debug_trace.retrieved_traces[0].private_core_summary is None
    assert trace.private_core_summary not in debug_trace.model_dump_json()
    assert debug_trace.retrieval_activations[0].components.final_score >= 0.0


def test_store_safe_summary_remains_public_safe() -> None:
    store = PsychoanalyticMemoryStore()
    store.record_turn(user_input="I felt embarrassed.", final_response="response")
    store.retrieve_related_to_turn(user_input="I felt embarrassed again.")

    summary = store.build_safe_summary()
    payload = summary.model_dump_json()

    assert "private_core_summary" not in payload
    assert "retrieval_activations" not in payload
    assert_safe_memory_debug_summary(summary)


def test_full_internal_state_has_no_memory_retrieval_content() -> None:
    fields = FullInternalState.model_fields

    assert "memory_trace" not in fields
    assert "memory_activation" not in fields
    assert "memory_retrieval_query" not in fields
