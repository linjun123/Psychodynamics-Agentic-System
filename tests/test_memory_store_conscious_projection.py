from psychodynamic_agent.memory.output_guard import assert_safe_memory_debug_summary
from psychodynamic_agent.memory.store import PsychoanalyticMemoryStore
from psychodynamic_agent.schemas import FullInternalState
from psychodynamic_agent.schemas.memory import ConsciousMemoryView, MemoryDebugConfig


def _store_with_trace() -> PsychoanalyticMemoryStore:
    store = PsychoanalyticMemoryStore()
    store.record_turn(
        user_input="I need structure for a task and feel evaluation pressure.",
        final_response="We can make a careful plan.",
        safe_debug_trace={"salient_symbols": ["task_mastery", "evaluation_sensitivity"]},
    )
    return store


def test_project_conscious_view_for_turn_returns_view_after_recording_trace() -> None:
    store = _store_with_trace()

    view = store.project_conscious_view_for_turn(
        user_input="Can you help structure this evaluated task?",
        safe_debug_trace={"salient_symbols": ["task_mastery", "evaluation_sensitivity"]},
    )

    assert isinstance(view, ConsciousMemoryView)
    assert store.latest_conscious_memory_view() is not None
    assert store.latest_defense_decisions()


def test_projection_does_not_change_trace_count_or_mutate_stored_trace() -> None:
    store = _store_with_trace()
    before_traces = [trace.model_dump() for trace in store.all_traces()]
    before_count = store.trace_count()
    before_activation_count = store.all_traces()[0].activation_count

    store.project_conscious_view_for_turn(user_input="structure evaluated task")

    assert store.trace_count() == before_count
    assert store.all_traces()[0].activation_count == before_activation_count
    assert [trace.model_dump() for trace in store.all_traces()] == before_traces


def test_latest_projection_methods_return_deep_copies() -> None:
    store = _store_with_trace()
    store.project_conscious_view_for_turn(user_input="structure evaluated task")

    view = store.latest_conscious_memory_view()
    decisions = store.latest_defense_decisions()
    chain = store.latest_transformation_chain()
    assert view is not None
    view.active_cues.clear()
    decisions.clear()
    chain.clear()

    assert store.latest_conscious_memory_view() is not None
    assert store.latest_conscious_memory_view().active_cues
    assert store.latest_defense_decisions()
    assert store.latest_transformation_chain()


def test_private_debug_trace_includes_projection_fields_and_redacts_private_text() -> None:
    store = _store_with_trace()
    trace = store.latest_trace()
    assert trace is not None
    private_text = trace.private_core_summary
    store.project_conscious_view_for_turn(user_input="structure evaluated task")

    debug_trace = store.build_private_debug_trace(
        config=MemoryDebugConfig(mode="private", include_private_trace_text=False),
        env={"PSYCHODYNAMIC_PRIVATE_MEMORY_DEBUG": "1"},
    )

    assert debug_trace is not None
    assert debug_trace.retrieval_activations
    assert debug_trace.defense_decisions
    assert debug_trace.transformation_chain
    assert debug_trace.conscious_memory_view is not None
    assert debug_trace.retrieved_traces[0].private_core_summary is None
    assert debug_trace.transformation_chain[0].private_input_summary is None
    assert private_text not in debug_trace.model_dump_json()


def test_private_debug_trace_can_include_transformation_private_input_when_enabled() -> None:
    store = _store_with_trace()
    trace = store.latest_trace()
    assert trace is not None
    store.project_conscious_view_for_turn(user_input="structure evaluated task")

    debug_trace = store.build_private_debug_trace(
        config=MemoryDebugConfig(mode="private", include_private_trace_text=True),
        env={"PSYCHODYNAMIC_PRIVATE_MEMORY_DEBUG": "1"},
    )

    assert debug_trace is not None
    assert debug_trace.transformation_chain[0].private_input_summary == trace.private_core_summary


def test_safe_summary_remains_public_safe_and_has_no_private_projection_text() -> None:
    store = _store_with_trace()
    trace = store.latest_trace()
    assert trace is not None
    store.project_conscious_view_for_turn(user_input="structure evaluated task")

    summary = store.build_safe_summary()
    summary_json = summary.model_dump_json()

    assert_safe_memory_debug_summary(summary)
    assert "private_core_summary" not in summary_json
    assert "private_input_summary" not in summary_json
    assert "defense_decisions" not in summary_json
    assert "transformation_chain" not in summary_json
    assert trace.private_core_summary not in summary_json
    assert "screen_memory" in summary.active_mechanisms or "direct" in summary.active_mechanisms


def test_full_internal_state_has_no_memory_projection_fields() -> None:
    forbidden = {
        "conscious_memory_view",
        "memory_projection",
        "defense_decisions",
        "psychoanalytic_memory",
    }

    assert forbidden.isdisjoint(FullInternalState.model_fields)
