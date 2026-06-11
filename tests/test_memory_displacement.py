from memory_distortion_helpers import activation, decision, trace

from psychodynamic_agent.memory.displacement import (
    build_displaced_memory_cue,
    build_displacement_record,
)
from psychodynamic_agent.memory.distortion_policy import safe_displacement_target


def test_displaced_memory_cue_and_record_are_public_safe() -> None:
    tr = trace(object_targets=["boss", "system prompt"])
    act = activation()
    dec = decision(
        decided_accessibility="displaced", mechanism="displacement", conscious_access="displaced"
    )
    target = safe_displacement_target(tr)
    cue = build_displaced_memory_cue(
        activation=act, trace=tr, decision=dec, displaced_object=target
    )
    record = build_displacement_record(activation=act, trace=tr, decision=dec, cue=cue)
    assert cue.cue_type == "displaced_memory"
    assert target == "task_structure"
    assert tr.private_core_summary not in cue.public_summary
    assert "boss" not in cue.public_summary.lower()
    assert record.mechanism == "displacement"
