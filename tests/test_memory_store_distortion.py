from memory_distortion_helpers import activation, decision, trace

from psychodynamic_agent.memory.output_guard import assert_private_memory_debug_trace_allowed
from psychodynamic_agent.memory.store import PsychoanalyticMemoryStore
from psychodynamic_agent.schemas.memory import MemoryDebugConfig


def _projected_store() -> PsychoanalyticMemoryStore:
    class FakeAssociator:
        def retrieve(self, *, query, traces, top_k, min_score, include_blocked):
            _ = (query, top_k, min_score, include_blocked)
            return [
                activation(trace_id=traces[0].trace_id, activation_rank=1),
                activation(trace_id=traces[1].trace_id, activation_rank=2),
            ]

    class FakeDefenseGate:
        def decide_many(self, *, activations, traces):
            _ = traces
            return [
                decision(trace_id=activations[0].trace_id, activation_rank=1),
                decision(trace_id=activations[1].trace_id, activation_rank=2),
            ]

    store = PsychoanalyticMemoryStore(associator=FakeAssociator(), defense_gate=FakeDefenseGate())
    store._traces = [
        trace(
            trace_id="mem_000001",
            created_turn=1,
            object_targets=[],
            private_core_summary="PRIVATE safe one",
        ),
        trace(
            trace_id="mem_000002",
            created_turn=2,
            object_targets=[],
            private_core_summary="PRIVATE safe two",
        ),
    ]
    store.project_conscious_view_for_turn(user_input="evaluation structure")
    return store


def test_store_records_distortion_debug_and_redacts_private_text() -> None:
    store = _projected_store()
    assert store.latest_distortion_decisions()
    assert store.latest_deferred_action_updates()
    decisions = store.latest_distortion_decisions()
    decisions[0].public_reason = "mutated"
    assert store.latest_distortion_decisions()[0].public_reason != "mutated"
    updates = store.latest_deferred_action_updates()
    updates[0].private_update_summary = "mutated"
    assert store.latest_deferred_action_updates()[0].private_update_summary != "mutated"

    redacted = store.build_private_debug_trace(
        config=MemoryDebugConfig(
            mode="private", include_private_trace_text=False, require_env_flag=False
        )
    )
    assert redacted is not None
    payload = redacted.model_dump_json()
    assert redacted.distortion_decisions
    assert redacted.deferred_action_updates
    assert redacted.transformation_chain
    assert redacted.conscious_memory_view is not None
    assert "private_core_summary" in payload
    assert "PRIVATE" not in payload
    assert "private_update_summary" in payload
    assert all(update.private_update_summary is None for update in redacted.deferred_action_updates)
    assert all(record.private_input_summary is None for record in redacted.transformation_chain)

    private = store.build_private_debug_trace(
        config=MemoryDebugConfig(
            mode="private", include_private_trace_text=True, require_env_flag=False
        )
    )
    assert private is not None
    assert any(update.private_update_summary for update in private.deferred_action_updates)
    assert_private_memory_debug_trace_allowed(private)


def test_safe_summary_and_runtime_boundaries() -> None:
    store = _projected_store()
    safe = store.build_safe_summary()
    payload = safe.model_dump_json()
    assert "private_update_summary" not in payload
    assert "deferred_action_updates" not in payload
    assert "Memory distortion artifacts" in payload
    from psychodynamic_agent.schemas.state import FullInternalState

    field_names = set(FullInternalState.model_fields)
    assert "distortion_decisions" not in field_names
    assert "deferred_action_updates" not in field_names
