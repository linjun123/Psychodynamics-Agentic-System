from collections.abc import Mapping

from psychodynamic_agent.memory.associator import MemoryAssociator
from psychodynamic_agent.memory.conscious_projection import build_conscious_memory_view
from psychodynamic_agent.memory.debug import (
    build_private_memory_debug_trace_if_allowed,
    build_safe_memory_debug_summary,
)
from psychodynamic_agent.memory.defense_gate import MemoryDefenseGate
from psychodynamic_agent.memory.extractor import HeuristicMemoryExtractor
from psychodynamic_agent.memory.heuristics import clamp_01
from psychodynamic_agent.memory.redaction import redact_private_memory_debug_trace
from psychodynamic_agent.memory.retrieval_query import build_memory_retrieval_query
from psychodynamic_agent.schemas.memory import (
    ConsciousMemoryView,
    MemoryActivation,
    MemoryDebugConfig,
    MemoryDefenseDecision,
    MemoryTrace,
    MemoryTransformationRecord,
    PrivateMemoryDebugTrace,
    SafeMemoryDebugSummary,
)


class PsychoanalyticMemoryStore:
    def __init__(
        self,
        *,
        extractor: HeuristicMemoryExtractor | None = None,
        associator: MemoryAssociator | None = None,
        defense_gate: MemoryDefenseGate | None = None,
    ):
        self._extractor = extractor or HeuristicMemoryExtractor()
        self._associator = associator or MemoryAssociator()
        self._defense_gate = defense_gate or MemoryDefenseGate()
        self._traces: list[MemoryTrace] = []
        self._last_retrieval_activations: list[MemoryActivation] = []
        self._latest_conscious_memory_view: ConsciousMemoryView | None = None
        self._latest_defense_decisions: list[MemoryDefenseDecision] = []
        self._latest_transformation_chain: list[MemoryTransformationRecord] = []
        self._next_turn = 1

    def record_turn(
        self,
        *,
        user_input: str,
        final_response: str,
        safe_debug_trace: dict | None = None,
    ) -> MemoryTrace:
        trace_id = f"mem_{self._next_turn:06d}"
        created_turn = self._next_turn
        trace = self._extractor.extract_turn_trace(
            trace_id=trace_id,
            created_turn=created_turn,
            user_input=user_input,
            final_response=final_response,
            safe_debug_trace=safe_debug_trace if isinstance(safe_debug_trace, dict) else None,
        )
        self._traces.append(trace.model_copy(deep=True))
        self._next_turn += 1
        return trace.model_copy(deep=True)

    def all_traces(self) -> list[MemoryTrace]:
        return [trace.model_copy(deep=True) for trace in self._traces]

    def latest_trace(self) -> MemoryTrace | None:
        if not self._traces:
            return None
        return self._traces[-1].model_copy(deep=True)

    def clear(self) -> None:
        self._traces.clear()
        self._last_retrieval_activations.clear()
        self._latest_conscious_memory_view = None
        self._latest_defense_decisions.clear()
        self._latest_transformation_chain.clear()
        self._next_turn = 1

    def trace_count(self) -> int:
        return len(self._traces)

    def retrieve_related_to_turn(
        self,
        *,
        user_input: str,
        safe_debug_trace: dict | None = None,
        top_k: int = 5,
        min_score: float = 0.0,
        include_blocked: bool = True,
    ) -> list[MemoryActivation]:
        query = build_memory_retrieval_query(
            user_input=user_input,
            safe_debug_trace=safe_debug_trace if isinstance(safe_debug_trace, dict) else None,
        )
        activations = self._associator.retrieve(
            query=query,
            traces=self._traces,
            top_k=top_k,
            min_score=min_score,
            include_blocked=include_blocked,
        )
        self._last_retrieval_activations = [
            activation.model_copy(deep=True) for activation in activations
        ]
        return self.latest_retrieval_activations()

    def latest_retrieval_activations(self) -> list[MemoryActivation]:
        return [activation.model_copy(deep=True) for activation in self._last_retrieval_activations]

    def project_conscious_view_for_turn(
        self,
        *,
        user_input: str,
        safe_debug_trace: dict | None = None,
        top_k: int = 5,
        min_score: float = 0.0,
        include_blocked: bool = True,
        max_cues: int = 5,
    ) -> ConsciousMemoryView:
        activations = self.retrieve_related_to_turn(
            user_input=user_input,
            safe_debug_trace=safe_debug_trace,
            top_k=top_k,
            min_score=min_score,
            include_blocked=include_blocked,
        )
        decisions = self._defense_gate.decide_many(activations=activations, traces=self._traces)
        projection = build_conscious_memory_view(
            activations=activations,
            traces=self._traces,
            decisions=decisions,
            max_cues=max_cues,
        )
        self._latest_conscious_memory_view = projection.conscious_memory_view.model_copy(deep=True)
        self._latest_defense_decisions = [
            decision.model_copy(deep=True) for decision in projection.defense_decisions
        ]
        self._latest_transformation_chain = [
            record.model_copy(deep=True) for record in projection.transformation_chain
        ]
        return self._latest_conscious_memory_view.model_copy(deep=True)

    def latest_conscious_memory_view(self) -> ConsciousMemoryView | None:
        if self._latest_conscious_memory_view is None:
            return None
        return self._latest_conscious_memory_view.model_copy(deep=True)

    def latest_defense_decisions(self) -> list[MemoryDefenseDecision]:
        return [decision.model_copy(deep=True) for decision in self._latest_defense_decisions]

    def latest_transformation_chain(self) -> list[MemoryTransformationRecord]:
        return [record.model_copy(deep=True) for record in self._latest_transformation_chain]

    def build_safe_summary(self) -> SafeMemoryDebugSummary:
        latest = self._traces[-1] if self._traces else None
        if self._traces:
            memory_pressure = max(trace.affective_signature.arousal for trace in self._traces)
        else:
            memory_pressure = 0.0
        active_mechanisms = ["direct"] if self._traces else []
        for decision in self._latest_defense_decisions:
            if decision.mechanism not in active_mechanisms:
                active_mechanisms.append(decision.mechanism)
        public_notes = [
            "Psychoanalytic memory store recorded traces.",
            (
                "Association retrieval is available for private memory inspection "
                "but is not wired into response generation."
            ),
        ]
        if self._latest_defense_decisions:
            public_notes.append(
                "Defensive memory projection is available for private inspection "
                "but is not wired into response generation."
            )
        return build_safe_memory_debug_summary(
            activated_trace_count=len(self._traces),
            activated_complex_count=0,
            dominant_public_affects=list(latest.salient_symbols) if latest else [],
            active_mechanisms=active_mechanisms,
            memory_pressure=clamp_01(memory_pressure),
            defense_pressure=latest.defense_level if latest else 0.0,
            repetition_pressure=0.0,
            public_notes=public_notes,
        )

    def build_private_debug_trace(
        self,
        *,
        config: MemoryDebugConfig,
        sealed_ultimate_need: str | None = None,
        env: Mapping[str, str] | None = None,
    ) -> PrivateMemoryDebugTrace | None:
        debug_trace = PrivateMemoryDebugTrace(
            current_turn_summary=(
                f"Psychoanalytic memory store contains {len(self._traces)} traces."
            ),
            retrieved_traces=self.all_traces(),
            retrieval_activations=self.latest_retrieval_activations(),
            defense_decisions=self.latest_defense_decisions(),
            transformation_chain=self.latest_transformation_chain(),
            conscious_memory_view=self.latest_conscious_memory_view(),
            safe_summary=self.build_safe_summary(),
        )
        if not config.include_private_trace_text:
            debug_trace = redact_private_memory_debug_trace(debug_trace)
        return build_private_memory_debug_trace_if_allowed(
            debug_trace,
            config,
            sealed_ultimate_need=sealed_ultimate_need,
            env=env,
        )
