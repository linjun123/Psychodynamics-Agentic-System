from memory_distortion_helpers import activation, decision, trace

from psychodynamic_agent.memory.store import PsychoanalyticMemoryStore
from psychodynamic_agent.schemas.memory import MemoryDebugConfig
from psychodynamic_agent.schemas.state import FullInternalState


class _RepetitionAssociator:
    def retrieve(self, *, query, traces, top_k, min_score, include_blocked):
        _ = (query, top_k, min_score, include_blocked)
        return [
            activation(
                trace_id=traces[0].trace_id,
                activation_rank=1,
                association_score=0.95,
                matched_salient_symbols=["evaluation_sensitivity"],
            )
        ]


class _BlockedDefenseGate:
    def decide_many(self, *, activations, traces):
        _ = traces
        return [
            decision(
                trace_id=activations[0].trace_id,
                activation_rank=1,
                original_accessibility="blocked_action_only",
                decided_accessibility="blocked_action_only",
                conscious_access="blocked_action_only",
                mechanism="blocked_action_only",
                emits_conscious_cue=False,
                defense_pressure=0.95,
            )
        ]


def _projected_store() -> PsychoanalyticMemoryStore:
    store = PsychoanalyticMemoryStore(
        associator=_RepetitionAssociator(), defense_gate=_BlockedDefenseGate()
    )
    store._traces = [
        trace(
            trace_id="blocked_trace",
            accessibility="blocked_action_only",
            defense_level=0.95,
            repression_pressure=0.9,
            activation_count=4,
            private_core_summary="PRIVATE blocked private_core_summary content",
        )
    ]
    store.project_conscious_view_for_turn(user_input="evaluation pressure")
    return store


def test_store_projection_stores_repetition_artifacts_and_public_view_labels() -> None:
    store = _projected_store()
    triggers = store.latest_repetition_triggers()
    biases = store.latest_repetition_biases()
    view = store.latest_conscious_memory_view()
    assert triggers
    assert biases
    assert view is not None
    assert view.repetition_biases
    assert view.repetition_pressure > 0
    view_json = view.model_dump_json()
    assert "blocked_trace" not in view_json
    assert "PRIVATE blocked" not in view_json


def test_latest_repetition_getters_return_deep_copies() -> None:
    store = _projected_store()
    triggers = store.latest_repetition_triggers()
    biases = store.latest_repetition_biases()
    triggers[0].source_trace_ids.append("mutated")
    biases[0].source_trace_ids.append("mutated")
    assert "mutated" not in store.latest_repetition_triggers()[0].source_trace_ids
    assert "mutated" not in store.latest_repetition_biases()[0].source_trace_ids


def test_private_debug_includes_repetition_artifacts_without_private_text_when_redacted() -> None:
    store = _projected_store()
    private = store.build_private_debug_trace(
        config=MemoryDebugConfig(
            mode="private", include_private_trace_text=False, require_env_flag=False
        ),
        env={},
    )
    assert private is not None
    assert private.repetition_triggers
    assert private.repetition_biases
    payload = private.model_dump_json()
    assert "PRIVATE blocked" not in payload
    assert "content" not in payload


def test_safe_summary_includes_repetition_pressure_without_private_identifiers() -> None:
    store = _projected_store()
    safe = store.build_safe_summary()
    payload = safe.model_dump_json()
    assert safe.repetition_pressure > 0
    assert "Repetition-bias artifacts" in payload
    assert "blocked_trace" not in payload
    assert "private_core_summary" not in payload
    assert "private_update_summary" not in payload
    assert "private_input_summary" not in payload
    assert "repetition_triggers" not in payload
    assert "source_trace_ids" not in payload


def test_full_internal_state_has_no_repetition_memory_fields() -> None:
    field_names = set(FullInternalState.model_fields)
    assert "repetition_biases" not in field_names
    assert "repetition_triggers" not in field_names
    assert "repetition_pressure" not in field_names
    assert "psychoanalytic_memory" not in field_names
