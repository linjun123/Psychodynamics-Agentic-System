from collections.abc import Mapping

from psychodynamic_agent.memory.associator import MemoryAssociator
from psychodynamic_agent.memory.complex_engine import MemoryComplexEngine
from psychodynamic_agent.memory.conscious_projection import build_conscious_memory_view
from psychodynamic_agent.memory.debug import (
    build_private_memory_debug_trace_if_allowed,
    build_safe_memory_debug_summary,
)
from psychodynamic_agent.memory.defense_gate import MemoryDefenseGate
from psychodynamic_agent.memory.distortion_engine import MemoryDistortionEngine
from psychodynamic_agent.memory.extractor import HeuristicMemoryExtractor
from psychodynamic_agent.memory.heuristics import clamp_01, unique_stable
from psychodynamic_agent.memory.redaction import redact_private_memory_debug_trace
from psychodynamic_agent.memory.repetition_engine import MemoryRepetitionEngine
from psychodynamic_agent.memory.retrieval_query import build_memory_retrieval_query
from psychodynamic_agent.schemas.memory import (
    ComplexNode,
    ConsciousMemoryView,
    MemoryActivation,
    MemoryComplexActivation,
    MemoryDebugConfig,
    MemoryDefenseDecision,
    MemoryDeferredActionUpdate,
    MemoryDistortionDecision,
    MemoryRepetitionTrigger,
    MemoryTrace,
    MemoryTransformationRecord,
    PrivateMemoryDebugTrace,
    RepetitionBias,
    SafeMemoryDebugSummary,
)


class PsychoanalyticMemoryStore:
    def __init__(
        self,
        *,
        extractor: HeuristicMemoryExtractor | None = None,
        associator: MemoryAssociator | None = None,
        defense_gate: MemoryDefenseGate | None = None,
        distortion_engine: MemoryDistortionEngine | None = None,
        repetition_engine: MemoryRepetitionEngine | None = None,
        complex_engine: MemoryComplexEngine | None = None,
    ):
        self._extractor = extractor or HeuristicMemoryExtractor()
        self._associator = associator or MemoryAssociator()
        self._defense_gate = defense_gate or MemoryDefenseGate()
        self._distortion_engine = distortion_engine or MemoryDistortionEngine()
        self._repetition_engine = repetition_engine or MemoryRepetitionEngine()
        self._complex_engine = complex_engine or MemoryComplexEngine()
        self._traces: list[MemoryTrace] = []
        self._last_retrieval_activations: list[MemoryActivation] = []
        self._latest_conscious_memory_view: ConsciousMemoryView | None = None
        self._latest_defense_decisions: list[MemoryDefenseDecision] = []
        self._latest_transformation_chain: list[MemoryTransformationRecord] = []
        self._latest_distortion_decisions: list[MemoryDistortionDecision] = []
        self._latest_deferred_action_updates: list[MemoryDeferredActionUpdate] = []
        self._latest_repetition_triggers: list[MemoryRepetitionTrigger] = []
        self._latest_repetition_biases: list[RepetitionBias] = []
        self._complexes: list[ComplexNode] = []
        self._next_complex_index = 1
        self._latest_complex_activations: list[MemoryComplexActivation] = []
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
        stored_trace = trace.model_copy(deep=True)
        self._traces.append(stored_trace)
        try:
            (
                self._complexes,
                _,
                _,
                self._next_complex_index,
            ) = self._complex_engine.update_with_trace(
                trace=stored_trace,
                complexes=self._complexes,
                all_traces=self._traces,
                next_complex_index=self._next_complex_index,
            )
        except Exception:
            pass
        self._next_turn += 1
        return trace.model_copy(deep=True)

    def all_traces(self) -> list[MemoryTrace]:
        return [trace.model_copy(deep=True) for trace in self._traces]

    def latest_trace(self) -> MemoryTrace | None:
        if not self._traces:
            return None
        return self._traces[-1].model_copy(deep=True)

    def all_complexes(self) -> list[ComplexNode]:
        return [complex_node.model_copy(deep=True) for complex_node in self._complexes]

    def latest_complex_activations(self) -> list[MemoryComplexActivation]:
        return [
            activation.model_copy(deep=True)
            for activation in self._latest_complex_activations
        ]

    def clear(self) -> None:
        self._traces.clear()
        self._last_retrieval_activations.clear()
        self._latest_conscious_memory_view = None
        self._latest_defense_decisions.clear()
        self._latest_transformation_chain.clear()
        self._latest_distortion_decisions.clear()
        self._latest_deferred_action_updates.clear()
        self._latest_repetition_triggers.clear()
        self._latest_repetition_biases.clear()
        self._complexes.clear()
        self._next_complex_index = 1
        self._latest_complex_activations.clear()
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
        distortion_result = self._distortion_engine.build_distortion_result(
            activations=activations,
            traces=self._traces,
            decisions=decisions,
            latest_trace=self._traces[-1] if self._traces else None,
            max_cues=max_cues,
        )
        repetition_result = self._repetition_engine.build_repetition_result(
            activations=activations,
            traces=self._traces,
            decisions=decisions,
            distortion_decisions=distortion_result.distortion_decisions,
            deferred_action_updates=distortion_result.deferred_action_updates,
            max_biases=5,
        )
        complex_result = self._complex_engine.activate(
            complexes=self._complexes,
            activations=activations,
            traces=self._traces,
            repetition_biases=repetition_result.repetition_biases,
            current_turn=self._next_turn - 1,
        )
        self._complexes = [
            complex_node.model_copy(deep=True) for complex_node in complex_result.complexes
        ]
        self._latest_complex_activations = [
            activation.model_copy(deep=True)
            for activation in complex_result.activated_complexes
        ]
        projection = build_conscious_memory_view(
            activations=activations,
            traces=self._traces,
            decisions=decisions,
            max_cues=max_cues,
            distortion_result=distortion_result,
            repetition_result=repetition_result,
            complex_activations=self._latest_complex_activations,
        )
        self._latest_conscious_memory_view = projection.conscious_memory_view.model_copy(deep=True)
        self._latest_defense_decisions = [
            decision.model_copy(deep=True) for decision in projection.defense_decisions
        ]
        self._latest_transformation_chain = [
            record.model_copy(deep=True) for record in projection.transformation_chain
        ]
        self._latest_distortion_decisions = [
            decision.model_copy(deep=True) for decision in projection.distortion_decisions
        ]
        self._latest_deferred_action_updates = [
            update.model_copy(deep=True) for update in projection.deferred_action_updates
        ]
        self._latest_repetition_triggers = [
            trigger.model_copy(deep=True) for trigger in projection.repetition_triggers
        ]
        self._latest_repetition_biases = [
            bias.model_copy(deep=True) for bias in projection.repetition_biases
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

    def latest_distortion_decisions(self) -> list[MemoryDistortionDecision]:
        return [
            decision.model_copy(deep=True)
            for decision in self._latest_distortion_decisions
        ]

    def latest_deferred_action_updates(self) -> list[MemoryDeferredActionUpdate]:
        return [
            update.model_copy(deep=True)
            for update in self._latest_deferred_action_updates
        ]

    def latest_repetition_triggers(self) -> list[MemoryRepetitionTrigger]:
        return [
            trigger.model_copy(deep=True) for trigger in self._latest_repetition_triggers
        ]

    def latest_repetition_biases(self) -> list[RepetitionBias]:
        return [bias.model_copy(deep=True) for bias in self._latest_repetition_biases]

    def build_safe_summary(self) -> SafeMemoryDebugSummary:
        latest = self._traces[-1] if self._traces else None
        if self._traces:
            memory_pressure = max(trace.affective_signature.arousal for trace in self._traces)
        else:
            memory_pressure = 0.0
        active_mechanisms = []

        def append_unique(mechanism: str) -> None:
            if mechanism not in active_mechanisms:
                active_mechanisms.append(mechanism)

        for decision in self._latest_defense_decisions:
            append_unique(decision.mechanism)
        for decision in self._latest_distortion_decisions:
            append_unique(decision.mechanism)
        if self._latest_repetition_biases:
            append_unique("repetition_bias")
        if self._latest_complex_activations:
            append_unique("complex_activation")
            memory_pressure = max(
                memory_pressure,
                max(
                    activation.activation_score
                    for activation in self._latest_complex_activations
                ),
            )
        if not active_mechanisms and self._traces:
            active_mechanisms.append("direct")
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
        if self._latest_distortion_decisions:
            public_notes.append(
                "Memory distortion artifacts are available for private inspection "
                "but are not wired into response generation."
            )
        if self._latest_repetition_biases:
            public_notes.append(
                "Repetition-bias artifacts are available for private inspection "
                "but are not wired into response generation."
            )
        if self._latest_complex_activations:
            public_notes.append(
                "Complex activation artifacts are available for private inspection "
                "but are not wired into response generation."
            )
        return build_safe_memory_debug_summary(
            activated_trace_count=len(self._traces),
            activated_complex_count=len(self._latest_complex_activations),
            dominant_public_affects=unique_stable(
                (list(latest.salient_symbols) if latest else [])
                + [
                    affect
                    for activation in self._latest_complex_activations
                    for affect in activation.dominant_public_affects
                ]
            ),
            active_mechanisms=active_mechanisms,
            memory_pressure=clamp_01(memory_pressure),
            defense_pressure=latest.defense_level if latest else 0.0,
            repetition_pressure=clamp_01(
                max((bias.intensity for bias in self._latest_repetition_biases), default=0.0)
            ),
            public_notes=public_notes,
        )

    def _latest_active_complex_nodes(self) -> list[ComplexNode]:
        active_ids = {activation.complex_id for activation in self._latest_complex_activations}
        return [
            complex_node.model_copy(deep=True)
            for complex_node in self._complexes
            if complex_node.complex_id in active_ids
        ]

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
            distortion_decisions=self.latest_distortion_decisions(),
            deferred_action_updates=self.latest_deferred_action_updates(),
            active_complexes=self._latest_active_complex_nodes(),
            complex_activations=self.latest_complex_activations(),
            repetition_triggers=self.latest_repetition_triggers(),
            repetition_biases=self.latest_repetition_biases(),
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
