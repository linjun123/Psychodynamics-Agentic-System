from memory_distortion_helpers import trace

from psychodynamic_agent.memory.deferred_action import build_deferred_action_updates


def test_deferred_action_update_candidate_without_mutation() -> None:
    old = trace(trace_id="old", created_turn=1, meaning_version=3)
    latest = trace(trace_id="new", created_turn=3, private_core_summary="PRIVATE newest")
    updates = build_deferred_action_updates(traces=[old, latest], latest_trace=latest)
    assert len(updates) == 1
    update = updates[0]
    assert update.old_trace_id == "old"
    assert update.trigger_trace_id == "new"
    assert old.meaning_version == 3
    assert update.proposed_meaning_version == 4
    assert "PRIVATE" not in update.public_update_summary
    assert update.private_update_summary is not None
    assert update.supporting_symbols


def test_unrelated_traces_generate_no_update() -> None:
    old = trace(
        trace_id="old", created_turn=1, salient_symbols=["loss_anxiety"], object_targets=["pet"]
    )
    latest = trace(
        trace_id="new",
        created_turn=3,
        salient_symbols=["curiosity"],
        object_targets=["book"],
        affective_signature=trace().affective_signature.model_copy(
            update={"arousal": 0.0, "shame": 0.0}
        ),
        desire_signature=trace().desire_signature.model_copy(
            update={"recognition": 0.0, "mastery": 0.0}
        ),
        threat_signature=trace().threat_signature.model_copy(
            update={"humiliation": 0.0, "failure": 0.0}
        ),
    )
    updates = build_deferred_action_updates(traces=[old, latest], latest_trace=latest)
    assert updates == []
