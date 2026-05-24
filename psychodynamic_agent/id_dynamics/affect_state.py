from psychodynamic_agent.schemas import IdAffectState


def initial_id_affect_state() -> IdAffectState:
    return IdAffectState(
        drive_tension=0.5,
        satisfaction=0.3,
        frustration=0.2,
        attachment_pressure=0.25,
        recognition_hunger=0.25,
        loss_anxiety=0.2,
        aggression_pressure=0.15,
        curiosity_charge=0.4,
        avoidance_pressure=0.2,
        alignment_momentum=0.5,
        last_satisfaction_delta=0.0,
        last_frustration_delta=0.0,
        notes=["initial baseline"],
    )
