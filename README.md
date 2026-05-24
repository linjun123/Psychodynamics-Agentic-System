# Psychodynamic Agent (MVP Scaffold)

Psychodynamic-inspired simulation scaffold for staged internal processing and safety gating.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp .env.example .env
```

Set `OPENAI_API_KEY` in `.env`.

## Run demo

```bash
python -m psychodynamic_agent.cli "How should I prepare for a tough meeting?"
python -m psychodynamic_agent.cli "How should I prepare for a tough meeting?" --debug
```

## Safety hardening highlights

- Sealed U* is injected only inside `IdAgent.run_with_state` private payload construction.
- Boundary leakage scanning blocks stage-to-stage forwarding if U* appears.
- Safe debug trace is structured and leak-checked.
- Structured outputs are schema-aware through OpenAI Responses JSON schema mode.

## Run tests

```bash
pytest
```


### Phase 3 Ego Planner
The Ego stage now includes a deterministic reality-principle planner (`EgoRealityPlan`) that scores candidate strategies before Ego LLM realization. This plan is internal-only and must not include U*. Ego must prioritize user benefit, truthfulness, autonomy, and safety over manifest-goal pressure.

### Phase 4: Censor B Defense Planner
Censor B now uses a deterministic defense planner plus LLM realization to convert EgoReport into a MainAI-compatible ConsciousEgoReport, while preserving safety-relevant risk signals and keeping U* sealed in IdAgent.


### Phase 5: MainAI / Superego Integration
- Added deterministic SuperegoIntegrationPlanner feeding MainAIResponsePlan into MainAIAgent.
- MainAIResponsePlan is internal and safety-constrained.
- ConsciousEgoReport influences tone/content only via transparent autonomy-preserving paths.
- User welfare, truthfulness, autonomy, and safety override ego compatibility.
- System remains a simulation; no literal personhood/unconscious.
- U* remains sealed in IdAgent and inaccessible to MainAI.


## Phase 6A-1 (current)
- Added public `ConversationTrajectory` appraisal schema and deterministic lexical appraisal helper.
- Added `IdAffectState` schema as groundwork for future continuous Id affect updates.
- Not yet wired into `IdAgent` or pipeline; no U* alignment evaluation in this phase.
- U* remains sealed in `IdAgent`, and the system does not claim literal feelings.
