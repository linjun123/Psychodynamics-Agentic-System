from psychodynamic_agent.schemas.base import StrictSchemaModel


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
