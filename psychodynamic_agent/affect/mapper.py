from psychodynamic_agent.schemas import AffectPropagationTrace, EgoAffectSummary, IdOutput
from psychodynamic_agent.schemas.censor import AffectiveColor


def c(v): return max(0.0,min(1.0,float(v)))

def map_id_affect_to_trace(id_output: IdOutput) -> AffectPropagationTrace:
    a=id_output.raw_affect
    vals={k:v for k,v in a.model_dump().items() if k!='valence'}
    dom=[k for k,v in sorted(vals.items(), key=lambda kv: kv[1], reverse=True) if v>=0.5][:3]
    leakage=c(id_output.leakage_risk_self_check)
    caution=c(0.2+0.4*a.fear_of_loss+0.3*leakage+0.2*a.avoidance+0.2*a.possessiveness)
    style=AffectiveColor(
      conscious_style_hint='neutral and precise',
      warmth=c(0.3+0.4*a.longing+0.2*a.approach+0.2*a.curiosity-0.3*a.aggression),
      caution=caution,
      intensity=c(0.2+0.5*a.arousal+0.2*a.excitement+0.2*a.irritation),
      playfulness=c(0.1+0.5*a.curiosity+0.2*a.excitement-0.3*caution),
      assertiveness=c(0.2+0.3*a.aggression+0.2*a.irritation+0.2*a.arousal),
      distance=c(0.1+0.4*a.avoidance+0.2*a.fear_of_loss+0.2*a.aggression-0.2*a.approach),
    )
    hint='neutral and precise'
    if style.caution>=max(style.warmth,style.playfulness,style.assertiveness): hint='cautious and bounded'
    elif style.warmth>=0.65: hint='warm and collaborative'
    elif style.playfulness>=0.65: hint='curious and exploratory'
    elif style.assertiveness>=0.65 or style.intensity>=0.75: hint='firm and structured'
    style.conscious_style_hint=hint
    return AffectPropagationTrace(dominant_affects=dom,affect_pressure=c((a.arousal+a.longing+a.excitement+a.fear_of_loss+a.irritation+a.possessiveness+a.aggression)/7),
      approach_avoidance_balance=c((a.approach-a.avoidance+1)/2), boundary_need=max(c(a.fear_of_loss),c(a.possessiveness),c(a.aggression),c(a.avoidance),leakage), intimacy_pressure=c((a.longing+a.approach+a.possessiveness+a.fear_of_loss)/4),
      aggression_pressure=max(c(a.aggression),c(a.irritation)), loss_anxiety=c(a.fear_of_loss), curiosity_drive=c(a.curiosity), transformed_style=style, notes=['Derived from Id raw affect.'])

def summarize_affect_for_ego(trace:AffectPropagationTrace)->EgoAffectSummary:
    return EgoAffectSummary(affective_pressure=trace.affect_pressure, conscious_style_hint=trace.transformed_style.conscious_style_hint,boundary_need=trace.boundary_need, collaborative_pull=c((trace.transformed_style.warmth+trace.curiosity_drive+trace.intimacy_pressure)/3), caution_need=trace.transformed_style.caution,intensity_level=trace.transformed_style.intensity,notes=['Conscious-safe affect summary for strategy scoring.'])
