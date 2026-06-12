from psychodynamic_agent.memory.condensation import (
    build_condensation_groups,
    build_condensation_record,
    build_condensed_memory_cue,
)
from psychodynamic_agent.memory.deferred_action import build_deferred_action_updates
from psychodynamic_agent.memory.displacement import (
    build_displaced_memory_cue,
    build_displacement_record,
)
from psychodynamic_agent.memory.distortion_policy import (
    safe_displacement_target,
    should_displace,
    should_screen_memory,
)
from psychodynamic_agent.memory.heuristics import clamp_01, unique_stable
from psychodynamic_agent.memory.screen_memory import (
    build_screen_memory_cue,
    build_screen_memory_record,
)
from psychodynamic_agent.schemas.memory import (
    MemoryActivation,
    MemoryDefenseDecision,
    MemoryDistortionDecision,
    MemoryDistortionResult,
    MemoryTrace,
)


class MemoryDistortionEngine:
    def build_distortion_result(
        self,
        *,
        activations: list[MemoryActivation],
        traces: list[MemoryTrace],
        decisions: list[MemoryDefenseDecision],
        latest_trace: MemoryTrace | None = None,
        max_cues: int = 5,
    ) -> MemoryDistortionResult:
        activations_by_id = {activation.trace_id: activation for activation in activations}
        traces_by_id = {trace.trace_id: trace for trace in traces}
        distorted_cues = []
        records = []
        distortion_decisions: list[MemoryDistortionDecision] = []
        already_distorted: set[str] = set()
        cue_limit = max(int(max_cues), 0)

        for decision in sorted(decisions, key=lambda item: item.activation_rank):
            activation = activations_by_id.get(decision.trace_id)
            trace = traces_by_id.get(decision.trace_id)
            if activation is None or trace is None or not should_displace(decision, trace):
                continue
            displaced_object = safe_displacement_target(trace)
            cue = build_displaced_memory_cue(
                activation=activation,
                trace=trace,
                decision=decision,
                displaced_object=displaced_object,
            )
            if len(distorted_cues) < cue_limit:
                distorted_cues.append(cue)
            records.append(
                build_displacement_record(
                    activation=activation, trace=trace, decision=decision, cue=cue
                )
            )
            already_distorted.add(trace.trace_id)
            distortion_decisions.append(
                MemoryDistortionDecision(
                    distortion_id=f"displacement_{trace.trace_id}",
                    source_trace_ids=[trace.trace_id],
                    source_activation_ranks=[decision.activation_rank],
                    mode="displacement",
                    mechanism="displacement",
                    should_emit_cue=True,
                    public_reason=(
                        "Risky object focus was shifted toward a safer symbolic target."
                    ),
                    intensity=clamp_01(
                        max(activation.association_score, decision.defense_pressure)
                    ),
                )
            )

        for decision in sorted(decisions, key=lambda item: item.activation_rank):
            if decision.trace_id in already_distorted:
                continue
            activation = activations_by_id.get(decision.trace_id)
            trace = traces_by_id.get(decision.trace_id)
            if activation is None or trace is None or not should_screen_memory(decision, trace):
                continue
            cue = build_screen_memory_cue(activation=activation, trace=trace, decision=decision)
            if len(distorted_cues) < cue_limit:
                distorted_cues.append(cue)
            records.append(
                build_screen_memory_record(
                    activation=activation, trace=trace, decision=decision, cue=cue
                )
            )
            already_distorted.add(trace.trace_id)
            distortion_decisions.append(
                MemoryDistortionDecision(
                    distortion_id=f"screen_{trace.trace_id}",
                    source_trace_ids=[trace.trace_id],
                    source_activation_ranks=[decision.activation_rank],
                    mode="screen_memory",
                    mechanism="screen_memory",
                    should_emit_cue=True,
                    public_reason="Screened trace was converted to a symbolic substitute cue.",
                    intensity=clamp_01(
                        max(activation.association_score, decision.defense_pressure)
                    ),
                )
            )

        remaining_decisions = [d for d in decisions if d.trace_id not in already_distorted]
        groups = build_condensation_groups(
            activations=activations, traces=traces, decisions=remaining_decisions
        )
        suppressed_trace_ids: list[str] = []
        for group in groups:
            cue = build_condensed_memory_cue(
                group_trace_ids=group,
                activations=activations,
                traces=traces,
                decisions=remaining_decisions,
            )
            if len(distorted_cues) < cue_limit:
                distorted_cues.append(cue)
            records.append(build_condensation_record(group_trace_ids=group, traces=traces, cue=cue))
            suppressed_trace_ids.extend(group)
            ranks = [activations_by_id[trace_id].activation_rank for trace_id in group]
            distortion_decisions.append(
                MemoryDistortionDecision(
                    distortion_id=cue.cue_id,
                    source_trace_ids=group,
                    source_activation_ranks=ranks,
                    mode="condensation",
                    mechanism="condensation",
                    should_emit_cue=True,
                    should_suppress_source_cues=True,
                    public_reason="Related traces were grouped into a composite symbolic cue.",
                    intensity=cue.intensity,
                )
            )

        deferred_updates = build_deferred_action_updates(
            traces=traces, latest_trace=latest_trace, max_updates=3
        )
        for update in deferred_updates:
            distortion_decisions.append(
                MemoryDistortionDecision(
                    distortion_id=f"deferred_{update.old_trace_id}_{update.trigger_trace_id}",
                    source_trace_ids=[update.old_trace_id, update.trigger_trace_id],
                    source_activation_ranks=[],
                    mode="deferred_action",
                    mechanism="deferred_action",
                    should_emit_cue=False,
                    public_reason="A later trace may retrospectively intensify an older pattern.",
                    intensity=update.update_strength,
                )
            )

        return MemoryDistortionResult(
            distortion_decisions=[item.model_copy(deep=True) for item in distortion_decisions],
            distorted_cues=[cue.model_copy(deep=True) for cue in distorted_cues[:cue_limit]],
            suppressed_trace_ids=unique_stable(suppressed_trace_ids),
            transformation_chain=[record.model_copy(deep=True) for record in records],
            deferred_action_updates=[item.model_copy(deep=True) for item in deferred_updates],
        )
