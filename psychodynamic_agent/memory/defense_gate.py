from psychodynamic_agent.memory.defense_policy import (
    choose_defensive_access,
    defense_pressure_score,
    emits_conscious_cue,
    mechanism_for_access,
    public_defense_reason,
)
from psychodynamic_agent.schemas.memory import (
    MemoryActivation,
    MemoryDefenseDecision,
    MemoryTrace,
)


class MemoryDefenseGate:
    def decide(
        self,
        *,
        activation: MemoryActivation,
        trace: MemoryTrace,
    ) -> MemoryDefenseDecision:
        decided_access = choose_defensive_access(
            trace_accessibility=trace.accessibility,
            association_score=activation.association_score,
            defense_level=trace.defense_level,
            repression_pressure=trace.repression_pressure,
        )
        return MemoryDefenseDecision(
            trace_id=activation.trace_id,
            activation_rank=activation.activation_rank,
            association_score=activation.association_score,
            original_accessibility=trace.accessibility,
            decided_accessibility=decided_access,
            defense_level=trace.defense_level,
            repression_pressure=trace.repression_pressure,
            defense_pressure=defense_pressure_score(
                association_score=activation.association_score,
                defense_level=trace.defense_level,
                repression_pressure=trace.repression_pressure,
            ),
            conscious_access=decided_access,
            mechanism=mechanism_for_access(decided_access),
            emits_conscious_cue=emits_conscious_cue(decided_access),
            public_reason=public_defense_reason(decided_access),
        )

    def decide_many(
        self,
        *,
        activations: list[MemoryActivation],
        traces: list[MemoryTrace],
    ) -> list[MemoryDefenseDecision]:
        traces_by_id = {trace.trace_id: trace for trace in traces}
        decisions = [
            self.decide(activation=activation, trace=trace)
            for activation in activations
            if (trace := traces_by_id.get(activation.trace_id)) is not None
        ]
        return sorted(
            [decision.model_copy(deep=True) for decision in decisions],
            key=lambda decision: decision.activation_rank,
        )
