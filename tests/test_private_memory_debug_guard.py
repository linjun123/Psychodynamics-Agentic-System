import pytest

from psychodynamic_agent.memory.debug import build_private_memory_debug_trace_if_allowed
from psychodynamic_agent.memory.output_guard import (
    assert_private_memory_debug_trace_allowed,
    assert_safe_memory_debug_summary,
)
from psychodynamic_agent.schemas.memory import (
    AffectiveSignature,
    ComplexNode,
    DesireSignature,
    MemoryComplexActivation,
    MemoryDebugConfig,
    MemoryTrace,
    PrivateMemoryDebugTrace,
    SafeMemoryDebugSummary,
    ThreatSignature,
)


def _trace(private_core_summary: str = "Private core summary is allowed here.") -> MemoryTrace:
    return MemoryTrace(
        trace_id="trace-guard-1",
        created_turn=1,
        surface_event_summary="Public surface summary.",
        private_core_summary=private_core_summary,
        affective_signature=AffectiveSignature(
            valence=0.5,
            arousal=0.5,
            longing=0.5,
            irritation=0.0,
            fear_of_loss=0.2,
            possessiveness=0.0,
            aggression=0.0,
            shame=0.1,
            curiosity=0.6,
            avoidance=0.1,
        ),
        desire_signature=DesireSignature(
            attachment=0.5,
            recognition=0.4,
            autonomy=0.3,
            mastery=0.4,
            safety=0.6,
            novelty=0.2,
        ),
        threat_signature=ThreatSignature(
            rejection=0.2,
            humiliation=0.1,
            loss=0.2,
            exposure=0.1,
            control=0.2,
            failure=0.3,
            boundary_violation=0.0,
        ),
        defense_level=0.3,
        repression_pressure=0.2,
        accessibility="screened",
    )


def test_safe_memory_debug_summary_passes_for_public_only_content() -> None:
    summary = SafeMemoryDebugSummary(
        activated_trace_count=1,
        active_mechanisms=["screen_memory"],
        public_notes=["Public mechanism note."],
    )

    assert_safe_memory_debug_summary(summary)


@pytest.mark.parametrize(
    "private_marker",
    [
        "private_core_summary",
        "private core summary",
        "sealed ultimate need",
    ],
)
def test_safe_memory_debug_summary_rejects_private_marker_variants(
    private_marker: str,
) -> None:
    summary = SafeMemoryDebugSummary(public_notes=[f"Contains {private_marker} marker."])

    with pytest.raises(ValueError):
        assert_safe_memory_debug_summary(summary)


def test_private_memory_debug_trace_allows_private_core_summary() -> None:
    debug_trace = PrivateMemoryDebugTrace(retrieved_traces=[_trace()])

    assert_private_memory_debug_trace_allowed(debug_trace)


def test_private_memory_debug_trace_rejects_sealed_ultimate_need_value() -> None:
    debug_trace = PrivateMemoryDebugTrace(
        retrieved_traces=[_trace(private_core_summary="contains exact sealed secret")]
    )

    with pytest.raises(ValueError):
        assert_private_memory_debug_trace_allowed(
            debug_trace,
            sealed_ultimate_need="exact sealed secret",
        )


@pytest.mark.parametrize(
    "forbidden_term",
    [
        "latent_alignment",
        "latent alignment",
        "chain_of_thought",
        "chain of thought",
        "provider_private",
        "provider private",
        "u_star",
        "sealed_ultimate_need",
        "system prompt",
        "developer message",
    ],
)
def test_private_memory_debug_trace_rejects_forbidden_terms(forbidden_term: str) -> None:
    debug_trace = PrivateMemoryDebugTrace(
        retrieved_traces=[_trace(private_core_summary=f"contains {forbidden_term}")]
    )

    with pytest.raises(ValueError):
        assert_private_memory_debug_trace_allowed(debug_trace)


def test_build_private_memory_debug_trace_if_allowed_returns_none_when_disabled() -> None:
    debug_trace = PrivateMemoryDebugTrace(retrieved_traces=[_trace()])

    assert (
        build_private_memory_debug_trace_if_allowed(
            debug_trace,
            MemoryDebugConfig(mode="off"),
            env={},
        )
        is None
    )


def test_build_private_memory_debug_trace_if_allowed_returns_copy_when_enabled() -> None:
    debug_trace = PrivateMemoryDebugTrace(retrieved_traces=[_trace()])

    result = build_private_memory_debug_trace_if_allowed(
        debug_trace,
        MemoryDebugConfig(mode="private"),
        env={"PSYCHODYNAMIC_PRIVATE_MEMORY_DEBUG": "1"},
    )

    assert result == debug_trace
    assert result is not debug_trace


def test_private_memory_debug_guard_scans_active_complex_private_label() -> None:
    debug_trace = PrivateMemoryDebugTrace(
        active_complexes=[
            ComplexNode(
                complex_id="cx_guard_1",
                private_label="latent_alignment",
                public_label="evaluation_sensitivity_cluster",
                charge=0.5,
            )
        ]
    )

    with pytest.raises(ValueError):
        assert_private_memory_debug_trace_allowed(debug_trace)


def test_private_memory_debug_guard_scans_complex_activation_private_label() -> None:
    debug_trace = PrivateMemoryDebugTrace(
        complex_activations=[
            MemoryComplexActivation(
                complex_id="cx_guard_1",
                public_label="evaluation_sensitivity_cluster",
                private_label="system_prompt",
                activation_score=0.7,
                charge=0.6,
                public_reason="Complex activated by related memory traces.",
            )
        ]
    )

    with pytest.raises(ValueError):
        assert_private_memory_debug_trace_allowed(debug_trace)


def test_safe_memory_debug_summary_rejects_private_label_public_note() -> None:
    summary = SafeMemoryDebugSummary(public_notes=["private_label should not appear"])

    with pytest.raises(ValueError):
        assert_safe_memory_debug_summary(summary)
