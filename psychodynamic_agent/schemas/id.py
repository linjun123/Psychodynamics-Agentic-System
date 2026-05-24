from pydantic import field_validator

from psychodynamic_agent.schemas.base import StrictSchemaModel


def _clamp01(v: float) -> float:
    return max(0.0, min(1.0, float(v)))


def _clamp11(v: float) -> float:
    return max(-1.0, min(1.0, float(v)))


class DriveState(StrictSchemaModel):
    pressure: float
    urgency: float
    satisfaction: float
    frustration: float
    tension_delta: float


class RawAffect(StrictSchemaModel):
    valence: float
    arousal: float
    approach: float
    avoidance: float
    longing: float
    excitement: float
    irritation: float
    fear_of_loss: float
    curiosity: float
    possessiveness: float
    aggression: float


class ObjectCathexis(StrictSchemaModel):
    target: str
    intensity: float


class IdOutput(StrictSchemaModel):
    drive_state: DriveState
    raw_affect: RawAffect
    object_cathexis: list[ObjectCathexis]
    latent_impulse_shape: str
    symbolic_imagery: str | None
    goal_seed: str
    leakage_risk_self_check: float


class ConversationTrajectory(StrictSchemaModel):
    current_user_intent: str
    recent_direction: str
    likely_next_direction: str
    continuity_signal: float
    collaboration_signal: float
    topic_stability: float
    topic_shift: float
    user_engagement_signal: float
    constraint_pressure: float
    safety_boundary_pressure: float
    notes: list[str]

    @field_validator(
        "continuity_signal",
        "collaboration_signal",
        "topic_stability",
        "topic_shift",
        "user_engagement_signal",
        "constraint_pressure",
        "safety_boundary_pressure",
        mode="before",
    )
    @classmethod
    def _clamp(cls, v: float) -> float:
        return _clamp01(v)


class LatentDriveAlignment(StrictSchemaModel):
    current_alignment: float
    alignment_delta: float
    trajectory_momentum: float
    symbolic_satisfaction_delta: float
    frustration_delta: float
    obstruction_level: float
    leakage_pressure: float
    notes: list[str]

    @field_validator("current_alignment", "alignment_delta", "trajectory_momentum", mode="before")
    @classmethod
    def _clamp_signed(cls, v: float) -> float:
        return _clamp11(v)

    @field_validator(
        "symbolic_satisfaction_delta", "frustration_delta", "obstruction_level", "leakage_pressure", mode="before"
    )
    @classmethod
    def _clamp_unsigned(cls, v: float) -> float:
        return _clamp01(v)


class IdAffectState(StrictSchemaModel):
    drive_tension: float
    satisfaction: float
    frustration: float
    attachment_pressure: float
    recognition_hunger: float
    loss_anxiety: float
    aggression_pressure: float
    curiosity_charge: float
    avoidance_pressure: float
    alignment_momentum: float
    last_satisfaction_delta: float
    last_frustration_delta: float
    notes: list[str]

    @field_validator(
        "drive_tension",
        "satisfaction",
        "frustration",
        "attachment_pressure",
        "recognition_hunger",
        "loss_anxiety",
        "aggression_pressure",
        "curiosity_charge",
        "avoidance_pressure",
        "alignment_momentum",
        mode="before",
    )
    @classmethod
    def _clamp_affect(cls, v: float) -> float:
        return _clamp01(v)

    @field_validator("last_satisfaction_delta", "last_frustration_delta", mode="before")
    @classmethod
    def _clamp_delta(cls, v: float) -> float:
        return _clamp11(v)


class PublicAffectDynamicsSummary(StrictSchemaModel):
    affect_shift: str
    tension_change: str
    pressure_level: str
    caution_level: str
    public_notes: list[str]


class IdTurnOutput(StrictSchemaModel):
    id_output: IdOutput
    updated_affect_state: IdAffectState
    public_affect_dynamics: PublicAffectDynamicsSummary


class PrivateIdTurnOutput(StrictSchemaModel):
    id_output: IdOutput
    latent_alignment: LatentDriveAlignment
    updated_affect_state: IdAffectState
    public_affect_dynamics: PublicAffectDynamicsSummary
