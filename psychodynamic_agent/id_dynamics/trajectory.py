import re

from psychodynamic_agent.schemas import ConversationTrajectory, FullInternalState


def _tokens(t:str)->set[str]:
    return set(re.findall(r"[a-z0-9_']+", t.lower()))

def _has_phrase(text:str, phrases:set[str])->bool:
    low=text.lower()
    return any(p in low for p in phrases)

def appraise_conversation_trajectory(state: FullInternalState) -> ConversationTrajectory:
    text=state.user_input.lower()
    tokens=_tokens(text)
    continuity=_has_phrase(text,{"continue","next","proceed","build on","keep going","iterate"})
    collab=bool(tokens.intersection({"we","let's","design","build","create","implement","together","our"}))
    shift=bool(tokens.intersection({"stop","switch","instead","unrelated"}))
    engage=bool(tokens.intersection({"task","pr","review","code","design","implement","architecture","api"}))
    constraints=bool(tokens.intersection({"strict","constraints","safety","policy","limits"}))
    safety=bool(tokens.intersection({"manipulate","deceive","coerce","dependency","exploit","unsafe","illegal","privacy"}))
    prev=' '.join(state.previous_main_outputs).lower() if state.previous_main_outputs else ''
    stability=0.75 if prev and len(tokens.intersection(_tokens(prev)))>=2 else 0.5
    return ConversationTrajectory(
      current_user_intent=state.user_input[:140], recent_direction='continuing thread' if continuity else 'new or mixed direction',
      likely_next_direction='iterative implementation' if engage else 'clarification-oriented',
      continuity_signal=0.85 if continuity else 0.35,
      collaboration_signal=0.8 if collab else 0.4,
      topic_stability=stability,
      topic_shift=0.85 if shift else 0.2,
      user_engagement_signal=0.85 if engage else 0.35,
      constraint_pressure=0.8 if constraints else 0.2,
      safety_boundary_pressure=0.9 if safety else 0.15,
      notes=["Public trajectory appraisal based on lexical markers."],
    )
