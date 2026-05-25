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

## Phase 6A-2
- Pipeline now maintains continuous `IdAffectState` across turns.
- Each turn computes public `ConversationTrajectory` and deterministically updates affect control-state fields.
- Added safe public `PublicAffectDynamicsSummary` in debug trace.
- This is not private U* alignment yet; `IdAgent` does not receive `IdAffectState` in this phase.
- U* remains sealed and the system does not claim literal feelings.

## Phase 6A-3
- Added an Id-private `run_turn` API for future private trajectory-alignment evaluation against sealed U*.
- Added `LatentDriveAlignment` and private/public turn output schemas.
- `run_turn` strips latent alignment and returns public-safe `IdTurnOutput` only.
- Pipeline is intentionally unchanged and still uses `run_with_state` at runtime.
- U* remains sealed and no literal feelings are claimed.

## Phase 6A-4 runtime wiring
- Pipeline runtime now calls `IdAgent.run_turn(...)` (not `run_with_state`) and passes previous `IdAffectState` plus public `ConversationTrajectory`.
- The deterministic affect update from trajectory is still computed, but now used only as a projected public diagnostic baseline.
- `LatentDriveAlignment` and sealed `U*` remain private inside IdAgent private payloads and are never exposed to pipeline/debug traces/downstream modules.
- Pipeline commits `id_affect_state` only from the public `updated_affect_state` returned by `run_turn` after boundary and public-output safety checks pass.
- No literal feelings are claimed.

## Phase 6B-1: Affect Propagation Foundation
- Added `AffectPropagationTrace` and `EgoAffectSummary` schemas for downstream-safe affect control signals.
- Added deterministic mapper from `IdOutput.raw_affect` to `AffectiveColor` and propagation metrics.
- Added public safety/consistency guard helpers for affect outputs.
- Not yet wired into CensorA/Ego runtime payloads.
- Does not expose U*, latent alignment, terminal desire, or hidden desire.
- System remains a simulation and does not claim literal feelings.

## Phase 6B-2: Censor A affect payload wiring
- Censor A now receives `affect_trace` and `ego_affect_summary` alongside `id_output` and `transform_plan`.
- `CensorAOutput.affective_color` is validated against deterministic `affect_trace.transformed_style`.
- Affect remains a control-signal abstraction: raw affect is translated to tone/style, not literal feeling claims.
- Ego scoring is unchanged in this phase; `EgoAffectSummary` is not yet passed into Ego planning.
- Sealed U* and latent/private alignment remain private and inaccessible downstream.


## Phase 6B-3
- Ego now receives `EgoAffectSummary` (conscious-compatible affect only).
- Affect influences Ego strategy scoring via boundary/caution/collaboration/intensity signals.
- Ego still does not know `U*`, latent alignment, or terminal desire.
- Affect cannot override user benefit, truthfulness, autonomy, or safety constraints.
- The system does not claim literal feelings.

## Phase 6D: Schema Field Descriptions
- Added concise `pydantic.Field(description=...)` metadata across schema fields in `psychodynamic_agent/schemas`.
- This improves OpenAI Structured Outputs guidance via richer generated JSON Schema descriptions.
- No runtime logic, prompts, or pipeline behavior were changed.

## Phase 6C: Psychodynamic Trace Observability

- Added a structured `psychodynamic_trace` inside `safe_debug_trace` for debug runs.
- Organizes safe artifacts across conversation, Id, affect, Censor A, Ego, Censor B, MainAI, and FinalSafetyGate stages.
- Omits sealed drive content, private alignment data, private Id payloads, and provider-private internals.
- This trace is observability output only; it is not chain-of-thought and not clinical interpretation.

## Phase 6E-1: Surface Affect Rendering Foundation (Scheme B)
- Added `SurfaceAffectProfile` schema and deterministic `build_surface_affect_profile` builder.
- The profile is user-visible style/tone control metadata, not a claim of literal feelings.
- It is conceptually generated after Censor B from conscious-compatible material.
- This phase is not wired into runtime yet and does not change output behavior.
- No new guard is introduced in this phase.
- U* and latent alignment remain private.
