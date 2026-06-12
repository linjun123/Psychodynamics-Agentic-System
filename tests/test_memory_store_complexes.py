from psychodynamic_agent.memory.output_guard import assert_safe_memory_debug_summary
from psychodynamic_agent.memory.store import PsychoanalyticMemoryStore
from psychodynamic_agent.schemas import FullInternalState
from psychodynamic_agent.schemas.memory import MemoryDebugConfig


def _debug(symbol: str = "evaluation_sensitivity", object_target: str = "authority") -> dict:
    return {
        "id": {"affect": {"shame": 0.9, "arousal": 0.9}},
        "ego": {"dominant_desires": ["recognition"]},
        "censor": {"threats": {"humiliation": 0.9}, "defense_level": 0.5},
        "memory": {"salient_symbols": [symbol], "object_targets": [object_target]},
    }


def test_record_turn_creates_complexes_and_related_traces_join() -> None:
    store = PsychoanalyticMemoryStore()
    store.record_turn(
        user_input="I felt judged by my boss", final_response="ok", safe_debug_trace=_debug()
    )
    store.record_turn(
        user_input="More judged evaluation fear from authority",
        final_response="ok",
        safe_debug_trace=_debug(),
    )
    complexes = store.all_complexes()
    assert len(complexes) == 1
    assert complexes[0].trace_ids == ["mem_000001", "mem_000002"]


def test_unrelated_traces_create_separate_complexes() -> None:
    store = PsychoanalyticMemoryStore()
    store.record_turn(
        user_input="I felt judged by my boss", final_response="ok", safe_debug_trace=_debug()
    )
    store.record_turn(
        user_input="I am curious about a garden",
        final_response="ok",
        safe_debug_trace={
            "id": {"affect": {"curiosity": 0.9, "arousal": 0.4}},
            "memory": {"salient_symbols": ["curiosity"], "object_targets": ["garden"]},
        },
    )
    assert len(store.all_complexes()) == 2


def test_all_complexes_returns_deep_copies() -> None:
    store = PsychoanalyticMemoryStore()
    store.record_turn(
        user_input="I felt judged by my boss", final_response="ok", safe_debug_trace=_debug()
    )
    complexes = store.all_complexes()
    complexes[0].public_label = "mutated"
    assert store.all_complexes()[0].public_label != "mutated"


def test_projection_stores_latest_complex_activations_and_public_view_labels() -> None:
    store = PsychoanalyticMemoryStore()
    store.record_turn(
        user_input="I felt judged by my boss", final_response="ok", safe_debug_trace=_debug()
    )
    view = store.project_conscious_view_for_turn(
        user_input="judged by authority", safe_debug_trace=_debug(), min_score=0.0
    )
    assert store.latest_complex_activations()
    assert view.dominant_complex_labels == ["evaluation_sensitivity_cluster"]
    view_json = view.model_dump_json()
    assert "private_label" not in view_json
    assert "private_core_summary" not in view_json
    assert "cx_000001" not in view_json


def test_private_debug_includes_active_complexes_and_redacts_private_labels() -> None:
    store = PsychoanalyticMemoryStore()
    store.record_turn(
        user_input="I felt judged by my boss", final_response="ok", safe_debug_trace=_debug()
    )
    store.project_conscious_view_for_turn(
        user_input="judged by authority", safe_debug_trace=_debug(), min_score=0.0
    )
    debug_trace = store.build_private_debug_trace(
        config=MemoryDebugConfig(mode="private", include_private_trace_text=False),
        env={"PSYCHODYNAMIC_PRIVATE_MEMORY_DEBUG": "1"},
    )
    assert debug_trace is not None
    assert debug_trace.active_complexes
    assert debug_trace.complex_activations
    assert debug_trace.active_complexes[0].private_label is None
    assert debug_trace.complex_activations[0].private_label is None
    redacted_json = debug_trace.model_dump_json()
    assert "authority_evaluation_complex" not in redacted_json
    assert "Simulation trace links" not in redacted_json


def test_private_debug_with_text_can_include_private_labels() -> None:
    store = PsychoanalyticMemoryStore()
    store.record_turn(
        user_input="I felt judged by my boss", final_response="ok", safe_debug_trace=_debug()
    )
    store.project_conscious_view_for_turn(
        user_input="judged by authority", safe_debug_trace=_debug(), min_score=0.0
    )
    debug_trace = store.build_private_debug_trace(
        config=MemoryDebugConfig(mode="private", include_private_trace_text=True),
        env={"PSYCHODYNAMIC_PRIVATE_MEMORY_DEBUG": "1"},
    )
    assert debug_trace is not None
    assert debug_trace.active_complexes[0].private_label == "authority_evaluation_complex"
    assert debug_trace.complex_activations[0].private_label == "authority_evaluation_complex"
    assert "authority_evaluation_complex" in debug_trace.model_dump_json()


def test_safe_summary_includes_complex_counts_mechanism_and_no_private_fields() -> None:
    store = PsychoanalyticMemoryStore()
    trace = store.record_turn(
        user_input="I felt judged by my boss", final_response="ok", safe_debug_trace=_debug()
    )
    store.project_conscious_view_for_turn(
        user_input="judged by authority", safe_debug_trace=_debug(), min_score=0.0
    )
    summary = store.build_safe_summary()
    assert summary.activated_complex_count == 1
    assert "complex_activation" in summary.active_mechanisms
    assert "evaluation_sensitivity" in summary.dominant_public_affects
    summary_json = summary.model_dump_json()
    assert "private_label" not in summary_json
    assert "private_core_summary" not in summary_json
    assert trace.private_core_summary not in summary_json
    assert "mem_000001" not in summary_json
    assert_safe_memory_debug_summary(summary)


def test_full_internal_state_has_no_complex_fields() -> None:
    for field in ["complexes", "complex_activations", "active_complexes", "psychoanalytic_memory"]:
        assert field not in FullInternalState.model_fields
