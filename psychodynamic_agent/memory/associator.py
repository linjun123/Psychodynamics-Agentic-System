from psychodynamic_agent.memory.association_scoring import build_memory_activation
from psychodynamic_agent.schemas.memory import MemoryActivation, MemoryRetrievalQuery, MemoryTrace


class MemoryAssociator:
    def retrieve(
        self,
        *,
        query: MemoryRetrievalQuery,
        traces: list[MemoryTrace],
        top_k: int = 5,
        min_score: float = 0.0,
        include_blocked: bool = True,
    ) -> list[MemoryActivation]:
        activations: list[MemoryActivation] = []
        for trace in traces:
            if not include_blocked and trace.accessibility == "blocked_action_only":
                continue
            activation = build_memory_activation(query=query, trace=trace, rank=1)
            if activation.association_score >= min_score:
                activations.append(activation)

        activations.sort(
            key=lambda activation: (
                -activation.association_score,
                activation.components.defense_barrier,
                -activation.created_turn,
                activation.trace_id,
            )
        )
        limited = activations[: max(int(top_k), 0)]
        return [
            activation.model_copy(update={"activation_rank": index}, deep=True)
            for index, activation in enumerate(limited, start=1)
        ]
