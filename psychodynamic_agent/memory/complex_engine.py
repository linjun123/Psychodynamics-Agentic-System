from psychodynamic_agent.memory.complex_activation import (
    activate_complexes,
    update_complexes_after_activation,
)
from psychodynamic_agent.memory.complex_clustering import assign_trace_to_complexes
from psychodynamic_agent.schemas.memory import (
    ComplexNode,
    MemoryActivation,
    MemoryComplexUpdateResult,
    MemoryTrace,
    RepetitionBias,
)


class MemoryComplexEngine:
    def update_with_trace(
        self,
        *,
        trace: MemoryTrace,
        complexes: list[ComplexNode],
        all_traces: list[MemoryTrace],
        next_complex_index: int,
    ) -> tuple[list[ComplexNode], list[ComplexNode], list[ComplexNode], int]:
        return assign_trace_to_complexes(
            trace=trace,
            complexes=complexes,
            all_traces=all_traces,
            next_complex_index=next_complex_index,
        )

    def activate(
        self,
        *,
        complexes: list[ComplexNode],
        activations: list[MemoryActivation],
        traces: list[MemoryTrace],
        repetition_biases: list[RepetitionBias] | None = None,
        current_turn: int | None = None,
    ) -> MemoryComplexUpdateResult:
        activated_complexes = activate_complexes(
            complexes=complexes,
            activations=activations,
            traces=traces,
            repetition_biases=repetition_biases,
            current_turn=current_turn,
        )
        updated_complexes = update_complexes_after_activation(
            complexes=complexes,
            activations=activated_complexes,
            current_turn=current_turn,
        )
        return MemoryComplexUpdateResult(
            complexes=updated_complexes,
            activated_complexes=activated_complexes,
        )
