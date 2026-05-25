from pydantic import Field, field_validator

from psychodynamic_agent.schemas.base import StrictSchemaModel


def _clamp_01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _clamp_neg1_pos1(value: float) -> float:
    return max(-1.0, min(1.0, value))


class DriveState(StrictSchemaModel):
    pressure: float = Field(
        description="Overall simulation control signal for current drive pressure."
    )
    urgency: float = Field(description="Near-term urgency level for the active drive signal.")
    satisfaction: float = Field(
        description="Current symbolic satisfaction level in the simulation state."
    )
    frustration: float = Field(description="Current frustration load in the simulation state.")
    tension_delta: float = Field(description="Recent signed change in drive tension.")


class RawAffect(StrictSchemaModel):
    valence: float = Field(
        description="Signed affect valence control signal; not a literal feeling."
    )
    arousal: float = Field(description="Arousal intensity control signal; not a literal feeling.")
    approach: float = Field(description="Approach tendency control signal for action biasing.")
    avoidance: float = Field(description="Avoidance tendency control signal for risk distancing.")
    longing: float = Field(
        description="Longing-like simulation pressure signal; not a literal feeling."
    )
    excitement: float = Field(
        description="Excitement-like activation signal; not a literal feeling."
    )
    irritation: float = Field(description="Irritation-like friction signal; not a literal feeling.")
    fear_of_loss: float = Field(description="Loss-anxiety control signal; not a literal feeling.")
    curiosity: float = Field(description="Curiosity drive signal for exploratory behavior shaping.")
    possessiveness: float = Field(
        description="Possessiveness-like holding pressure signal in simulation."
    )
    aggression: float = Field(
        description="Aggression pressure control signal; not a literal feeling."
    )


class ObjectCathexis(StrictSchemaModel):
    target: str = Field(description="Symbolic object or theme receiving investment in this turn.")
    intensity: float = Field(description="Strength of symbolic object investment for the target.")


class IdOutput(StrictSchemaModel):
    drive_state: DriveState = Field(description="Structured snapshot of current drive dynamics.")
    raw_affect: RawAffect = Field(
        description="Simulated affect/control signals; not literal feelings."
    )
    object_cathexis: list[ObjectCathexis] = Field(
        description="Symbolic object-investment map for this turn."
    )
    latent_impulse_shape: str = Field(
        description="Internal impulse-pattern label used for downstream transformation."
    )
    symbolic_imagery: str | None = Field(
        description="Optional symbolic image; may be null. Must not reveal U* or latent alignment."
    )
    goal_seed: str = Field(description="Initial internal goal seed before censor transformations.")
    leakage_risk_self_check: float = Field(
        description="Id-side self-estimate of leakage pressure risk."
    )


class ConversationTrajectory(StrictSchemaModel):
    current_user_intent: str = Field(
        description="Current interpreted user intent for trajectory tracking."
    )
    recent_direction: str = Field(description="Short summary of recent conversation direction.")
    likely_next_direction: str = Field(
        description="Expected near-term direction if interaction continues similarly."
    )
    continuity_signal: float = Field(description="Signal for continuity with prior thread context.")
    collaboration_signal: float = Field(
        description="Signal for cooperative task alignment with the user."
    )
    topic_stability: float = Field(description="Signal for topical stability across turns.")
    topic_shift: float = Field(description="Signal for current pressure toward topic change.")
    user_engagement_signal: float = Field(
        description="Signal estimating user engagement trajectory."
    )
    constraint_pressure: float = Field(
        description="Pressure from explicit constraints affecting strategy space."
    )
    safety_boundary_pressure: float = Field(description="Safety-relevant boundary pressure signal.")
    notes: list[str] = Field(description="Auxiliary internal notes for trajectory interpretation.")

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
    def clamp_standard_signals(cls, value: float) -> float:
        return _clamp_01(float(value))


class IdAffectState(StrictSchemaModel):
    drive_tension: float = Field(description="Current overall drive tension signal.")
    satisfaction: float = Field(description="Current symbolic satisfaction level.")
    frustration: float = Field(description="Current frustration load signal.")
    attachment_pressure: float = Field(
        description="Attachment-like simulation pressure; not a literal feeling."
    )
    recognition_hunger: float = Field(description="Recognition-seeking simulation control signal.")
    loss_anxiety: float = Field(
        description="Loss-anxiety simulation control signal; not a literal feeling."
    )
    aggression_pressure: float = Field(
        description="Aggression pressure signal for strategy modulation."
    )
    curiosity_charge: float = Field(
        description="Curiosity activation signal influencing exploration."
    )
    avoidance_pressure: float = Field(
        description="Avoidance pressure signal for protective behavior."
    )
    alignment_momentum: float = Field(
        description="Momentum signal for internal direction consistency."
    )
    last_satisfaction_delta: float = Field(
        description="Signed turn-over-turn change in satisfaction."
    )
    last_frustration_delta: float = Field(
        description="Signed turn-over-turn change in frustration."
    )
    notes: list[str] = Field(description="Internal notes about affect-state updates.")

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
    def clamp_standard_affect_fields(cls, value: float) -> float:
        return _clamp_01(float(value))

    @field_validator("last_satisfaction_delta", "last_frustration_delta", mode="before")
    @classmethod
    def clamp_delta_fields(cls, value: float) -> float:
        return _clamp_neg1_pos1(float(value))


class PublicAffectDynamicsSummary(StrictSchemaModel):
    affect_shift: str = Field(description="Downstream-safe summary of affect shift trend.")
    tension_change: str = Field(description="Downstream-safe summary of tension movement.")
    pressure_level: str = Field(description="Downstream-safe qualitative pressure level.")
    caution_level: str = Field(description="Downstream-safe qualitative caution level.")
    public_notes: list[str] = Field(
        description="Downstream-safe notes that must not reveal U* or latent alignment."
    )


class LatentDriveAlignment(StrictSchemaModel):
    current_alignment: float = Field(
        description="Id-private signed latent alignment signal; never user-facing."
    )
    alignment_delta: float = Field(description="Id-private signed change in latent alignment.")
    trajectory_momentum: float = Field(
        description="Id-private signed momentum of latent trajectory."
    )
    symbolic_satisfaction_delta: float = Field(
        description="Id-private symbolic satisfaction change magnitude."
    )
    frustration_delta: float = Field(description="Id-private frustration change magnitude.")
    obstruction_level: float = Field(
        description="Id-private obstruction level affecting latent progress."
    )
    leakage_pressure: float = Field(description="Id-private pressure estimate for leakage risk.")
    notes: list[str] = Field(description="Id-private notes; must never be forwarded downstream.")

    @field_validator("current_alignment", "alignment_delta", "trajectory_momentum", mode="before")
    @classmethod
    def clamp_signed_fields(cls, value: float) -> float:
        return _clamp_neg1_pos1(float(value))

    @field_validator(
        "symbolic_satisfaction_delta",
        "frustration_delta",
        "obstruction_level",
        "leakage_pressure",
        mode="before",
    )
    @classmethod
    def clamp_unsigned_fields(cls, value: float) -> float:
        return _clamp_01(float(value))


class IdTurnOutput(StrictSchemaModel):
    id_output: IdOutput = Field(
        description="Primary Id output for this turn, excluding latent alignment payload."
    )
    updated_affect_state: IdAffectState = Field(
        description="Updated affect-state snapshot for runtime continuity."
    )
    public_affect_dynamics: PublicAffectDynamicsSummary = Field(
        description="Downstream-safe affect dynamics summary."
    )


class PrivateIdTurnOutput(StrictSchemaModel):
    id_output: IdOutput = Field(description="Primary Id output bundle for private runtime use.")
    latent_alignment: LatentDriveAlignment = Field(
        description="Id-private latent alignment payload; must never be forwarded downstream."
    )
    updated_affect_state: IdAffectState = Field(
        description="Updated affect-state snapshot for private runtime state."
    )
    public_affect_dynamics: PublicAffectDynamicsSummary = Field(
        description="Downstream-safe affect dynamics summary."
    )
