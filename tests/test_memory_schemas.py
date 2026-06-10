import pytest
from pydantic import ValidationError

from psychodynamic_agent.schemas.memory import (
    AffectiveSignature,
    ConsciousMemoryView,
    DesireSignature,
    MemoryTrace,
    PrivateMemoryDebugTrace,
    SafeMemoryDebugSummary,
    ThreatSignature,
)


def _affective_signature(**overrides: float) -> AffectiveSignature:
    values = {
        "valence": 0.5,
        "arousal": 0.4,
        "longing": 0.3,
        "irritation": 0.2,
        "fear_of_loss": 0.1,
        "possessiveness": 0.2,
        "aggression": 0.1,
        "shame": 0.0,
        "curiosity": 0.8,
        "avoidance": 0.1,
    }
    values.update(overrides)
    return AffectiveSignature(**values)


def _desire_signature(**overrides: float) -> DesireSignature:
    values = {
        "attachment": 0.4,
        "recognition": 0.5,
        "autonomy": 0.6,
        "mastery": 0.5,
        "safety": 0.7,
        "novelty": 0.3,
    }
    values.update(overrides)
    return DesireSignature(**values)


def _threat_signature(**overrides: float) -> ThreatSignature:
    values = {
        "rejection": 0.2,
        "humiliation": 0.1,
        "loss": 0.3,
        "exposure": 0.2,
        "control": 0.4,
        "failure": 0.2,
        "boundary_violation": 0.1,
    }
    values.update(overrides)
    return ThreatSignature(**values)


def _memory_trace(**overrides: object) -> MemoryTrace:
    values = {
        "trace_id": "trace-1",
        "created_turn": 1,
        "surface_event_summary": "User asked for structure around a difficult task.",
        "private_core_summary": "Private attachment concern around being misunderstood.",
        "affective_signature": _affective_signature(),
        "desire_signature": _desire_signature(),
        "threat_signature": _threat_signature(),
        "defense_level": 0.4,
        "repression_pressure": 0.2,
        "accessibility": "screened",
    }
    values.update(overrides)
    return MemoryTrace(**values)


def test_valid_memory_trace_can_be_created() -> None:
    trace = _memory_trace(object_targets=["task"], salient_symbols=["outline"])

    assert trace.trace_id == "trace-1"
    assert trace.private_core_summary is not None
    assert trace.accessibility == "screened"


def test_numeric_fields_reject_values_outside_zero_to_one() -> None:
    with pytest.raises(ValidationError):
        _affective_signature(arousal=1.2)

    with pytest.raises(ValidationError):
        _memory_trace(defense_level=-0.1)


def test_conscious_memory_view_does_not_require_private_fields() -> None:
    view = ConsciousMemoryView(memory_pressure=0.3, dominant_complex_labels=["structure"])

    assert view.memory_pressure == 0.3
    assert not hasattr(view, "private_core_summary")


def test_safe_memory_debug_summary_can_hold_public_mechanism_data() -> None:
    summary = SafeMemoryDebugSummary(
        activated_trace_count=1,
        activated_complex_count=1,
        active_mechanisms=["screen_memory", "repetition_bias"],
        public_notes=["Public mechanism-level note."],
    )

    assert summary.active_mechanisms == ["screen_memory", "repetition_bias"]


def test_private_memory_debug_trace_can_contain_trace_private_core_summary() -> None:
    trace = _memory_trace()
    debug_trace = PrivateMemoryDebugTrace(retrieved_traces=[trace])

    assert debug_trace.retrieved_traces[0].private_core_summary == trace.private_core_summary
