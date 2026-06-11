from typing import Literal

from pydantic import Field

from psychodynamic_agent.schemas.base import StrictSchemaModel

MemoryDebugMode = Literal["off", "safe", "private"]


class MemoryDebugConfig(StrictSchemaModel):
    mode: MemoryDebugMode = Field(default="off")
    include_private_trace_text: bool = Field(default=False)
    include_llm_memory_io: bool = Field(default=False)
    require_env_flag: bool = Field(default=True)


class AffectiveSignature(StrictSchemaModel):
    valence: float = Field(ge=0.0, le=1.0)
    arousal: float = Field(ge=0.0, le=1.0)
    longing: float = Field(ge=0.0, le=1.0)
    irritation: float = Field(ge=0.0, le=1.0)
    fear_of_loss: float = Field(ge=0.0, le=1.0)
    possessiveness: float = Field(ge=0.0, le=1.0)
    aggression: float = Field(ge=0.0, le=1.0)
    shame: float = Field(ge=0.0, le=1.0)
    curiosity: float = Field(ge=0.0, le=1.0)
    avoidance: float = Field(ge=0.0, le=1.0)


class DesireSignature(StrictSchemaModel):
    attachment: float = Field(ge=0.0, le=1.0)
    recognition: float = Field(ge=0.0, le=1.0)
    autonomy: float = Field(ge=0.0, le=1.0)
    mastery: float = Field(ge=0.0, le=1.0)
    safety: float = Field(ge=0.0, le=1.0)
    novelty: float = Field(ge=0.0, le=1.0)


class ThreatSignature(StrictSchemaModel):
    rejection: float = Field(ge=0.0, le=1.0)
    humiliation: float = Field(ge=0.0, le=1.0)
    loss: float = Field(ge=0.0, le=1.0)
    exposure: float = Field(ge=0.0, le=1.0)
    control: float = Field(ge=0.0, le=1.0)
    failure: float = Field(ge=0.0, le=1.0)
    boundary_violation: float = Field(ge=0.0, le=1.0)


MemoryAccessMode = Literal[
    "direct",
    "screened",
    "condensed",
    "displaced",
    "felt_sense_only",
    "blocked_action_only",
]

MemoryMechanism = Literal[
    "direct",
    "screen_memory",
    "condensation",
    "displacement",
    "deferred_action",
    "felt_sense_only",
    "blocked_action_only",
    "repetition_bias",
    "complex_activation",
]


class AssociationScoreBreakdown(StrictSchemaModel):
    affect_similarity: float = Field(ge=0.0, le=1.0)
    desire_similarity: float = Field(ge=0.0, le=1.0)
    threat_similarity: float = Field(ge=0.0, le=1.0)
    object_overlap: float = Field(ge=0.0, le=1.0)
    salient_symbol_overlap: float = Field(ge=0.0, le=1.0)
    repetition_frequency: float = Field(ge=0.0, le=1.0)
    fact_similarity: float = Field(ge=0.0, le=1.0)
    defense_barrier: float = Field(ge=0.0, le=1.0)
    weighted_score_before_defense: float = Field(ge=0.0, le=1.0)
    final_score: float = Field(ge=0.0, le=1.0)


class MemoryRetrievalQuery(StrictSchemaModel):
    affective_signature: AffectiveSignature
    desire_signature: DesireSignature
    threat_signature: ThreatSignature
    object_targets: list[str] = Field(default_factory=list)
    salient_symbols: list[str] = Field(default_factory=list)
    query_summary: str | None = None


class MemoryActivation(StrictSchemaModel):
    trace_id: str
    created_turn: int = Field(ge=0)
    activation_rank: int = Field(ge=1)
    association_score: float = Field(ge=0.0, le=1.0)
    components: AssociationScoreBreakdown
    accessibility: MemoryAccessMode
    source_complex_ids: list[str] = Field(default_factory=list)
    matched_object_targets: list[str] = Field(default_factory=list)
    matched_salient_symbols: list[str] = Field(default_factory=list)
    public_reason: str


class MemoryRetrievalResult(StrictSchemaModel):
    query: MemoryRetrievalQuery
    activations: list[MemoryActivation] = Field(default_factory=list)


class MemoryTrace(StrictSchemaModel):
    trace_id: str
    created_turn: int = Field(ge=0)
    last_activated_turn: int | None = None
    surface_event_summary: str
    private_core_summary: str | None = None
    affective_signature: AffectiveSignature
    desire_signature: DesireSignature
    threat_signature: ThreatSignature
    object_targets: list[str] = Field(default_factory=list)
    salient_symbols: list[str] = Field(default_factory=list)
    defense_level: float = Field(ge=0.0, le=1.0)
    repression_pressure: float = Field(ge=0.0, le=1.0)
    accessibility: MemoryAccessMode
    complex_ids: list[str] = Field(default_factory=list)
    activation_count: int = Field(default=0, ge=0)
    meaning_version: int = Field(default=1, ge=1)


class ConsciousMemoryCue(StrictSchemaModel):
    cue_id: str
    source_trace_ids: list[str] = Field(default_factory=list)
    cue_type: Literal[
        "direct_memory",
        "screen_memory",
        "condensed_memory",
        "displaced_memory",
        "felt_sense",
        "repetition_bias",
    ]
    public_summary: str
    affective_tone: str
    intensity: float = Field(ge=0.0, le=1.0)
    recommended_handling: str | None = None


class ConsciousMemoryView(StrictSchemaModel):
    active_cues: list[ConsciousMemoryCue] = Field(default_factory=list)
    dominant_complex_labels: list[str] = Field(default_factory=list)
    repetition_biases: list[str] = Field(default_factory=list)
    memory_pressure: float = Field(default=0.0, ge=0.0, le=1.0)
    defense_pressure: float = Field(default=0.0, ge=0.0, le=1.0)
    repetition_pressure: float = Field(default=0.0, ge=0.0, le=1.0)
    caution: float = Field(default=0.0, ge=0.0, le=1.0)


class RepetitionBias(StrictSchemaModel):
    bias_id: str
    source_trace_ids: list[str] = Field(default_factory=list)
    source_complex_id: str | None = None
    tendency: Literal[
        "seek_reassurance",
        "avoid_topic",
        "over_explain",
        "test_boundary",
        "intellectualize",
        "ask_for_structure",
        "preempt_rejection",
        "control_uncertainty",
    ]
    intensity: float = Field(ge=0.0, le=1.0)
    safe_strategy_hint: str
    prohibited_expression: list[str] = Field(default_factory=list)


class ComplexNode(StrictSchemaModel):
    complex_id: str
    private_label: str | None = None
    public_label: str
    dominant_affects: list[str] = Field(default_factory=list)
    dominant_desires: list[str] = Field(default_factory=list)
    dominant_threats: list[str] = Field(default_factory=list)
    object_targets: list[str] = Field(default_factory=list)
    trace_ids: list[str] = Field(default_factory=list)
    charge: float = Field(ge=0.0, le=1.0)
    activation_threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    last_activated_turn: int | None = None
    preferred_defenses: list[str] = Field(default_factory=list)
    repetition_tendencies: list[str] = Field(default_factory=list)


class MemoryTransformationRecord(StrictSchemaModel):
    source_trace_ids: list[str]
    mechanism: MemoryMechanism
    private_input_summary: str | None = None
    public_output_summary: str | None = None
    access_mode_before: MemoryAccessMode | None = None
    access_mode_after: MemoryAccessMode | None = None
    defense_reason: str | None = None
    llm_generated: bool = False
    llm_operation_id: str | None = None
    guard_result: Literal["passed", "repaired", "blocked"] = "passed"


class SafeMemoryDebugSummary(StrictSchemaModel):
    activated_trace_count: int = Field(default=0, ge=0)
    activated_complex_count: int = Field(default=0, ge=0)
    dominant_public_affects: list[str] = Field(default_factory=list)
    active_mechanisms: list[MemoryMechanism] = Field(default_factory=list)
    memory_pressure: float = Field(default=0.0, ge=0.0, le=1.0)
    defense_pressure: float = Field(default=0.0, ge=0.0, le=1.0)
    repetition_pressure: float = Field(default=0.0, ge=0.0, le=1.0)
    public_notes: list[str] = Field(default_factory=list)


class PrivateMemoryDebugTrace(StrictSchemaModel):
    current_turn_summary: str | None = None
    retrieved_traces: list[MemoryTrace] = Field(default_factory=list)
    retrieval_activations: list[MemoryActivation] = Field(default_factory=list)
    transformation_chain: list[MemoryTransformationRecord] = Field(default_factory=list)
    active_complexes: list[ComplexNode] = Field(default_factory=list)
    repetition_biases: list[RepetitionBias] = Field(default_factory=list)
    conscious_memory_view: ConsciousMemoryView | None = None
    safe_summary: SafeMemoryDebugSummary | None = None
    llm_memory_operations: list[dict[str, object]] = Field(default_factory=list)
    guard_summary: dict[str, object] = Field(default_factory=dict)
