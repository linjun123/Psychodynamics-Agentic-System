from memory_distortion_helpers import activation, decision, trace

from psychodynamic_agent.memory.distortion_policy import (
    condensation_group_key,
    safe_displacement_target,
    should_condense_group,
    should_defer_action,
    should_displace,
    should_screen_memory,
)


def test_policy_predicates_and_targets() -> None:
    tr = trace()
    dec = decision()
    act = activation()
    assert should_screen_memory(dec, tr)
    assert should_displace(decision(decided_accessibility="displaced"), tr)
    assert should_displace(dec, tr)
    assert safe_displacement_target(tr) == "task_structure"
    assert condensation_group_key(tr, act) == "evaluation_sensitivity"


def test_condense_and_defer_action() -> None:
    t1 = trace(trace_id="a", created_turn=1)
    t2 = trace(trace_id="b", created_turn=2)
    a1 = activation(trace_id="a", activation_rank=1)
    a2 = activation(trace_id="b", activation_rank=2)
    assert should_condense_group([a1, a2], [t1, t2])
    assert should_defer_action(old_trace=t1, trigger_trace=t2, similarity_score=0.8)


def test_should_displace_false_for_blocked_action_only_even_with_risky_object() -> None:
    tr = trace(object_targets=["boss"], accessibility="direct")
    dec = decision(
        decided_accessibility="blocked_action_only",
        conscious_access="blocked_action_only",
        mechanism="blocked_action_only",
        emits_conscious_cue=False,
        defense_pressure=1.0,
    )

    assert not should_displace(dec, tr)


def test_should_displace_false_for_trace_accessibility_blocked_action_only() -> None:
    tr = trace(accessibility="blocked_action_only", object_targets=["boss"])
    dec = decision(defense_pressure=1.0)

    assert not should_displace(dec, tr)


def test_should_displace_false_for_felt_sense_only_even_with_risky_object() -> None:
    tr = trace(object_targets=["boss"], accessibility="direct")
    dec = decision(
        decided_accessibility="felt_sense_only",
        conscious_access="felt_sense_only",
        mechanism="felt_sense_only",
        emits_conscious_cue=True,
        defense_pressure=0.9,
    )

    assert not should_displace(dec, tr)


def test_should_displace_allows_explicit_displaced_decision() -> None:
    tr = trace(object_targets=["boss"], accessibility="direct")
    dec = decision(
        decided_accessibility="displaced",
        conscious_access="displaced",
        mechanism="displacement",
        emits_conscious_cue=False,
    )

    assert should_displace(dec, tr)
