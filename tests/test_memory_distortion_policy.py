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
