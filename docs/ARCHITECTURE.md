# Architecture

Pipeline:
1. Build `FullInternalState` from in-memory context.
2. Call `IdAgent.run_with_state(state)`.
3. `IdAgent` privately injects sealed U* and generates typed `IdOutput`.
4. Scan Id output for leakage before CensorA payload construction.
5. Construct each downstream payload and scan the **actual payload** before agent execution:
   CensorA input, Ego input, CensorB input, MainAI input, SafetyGate input.
6. Run agent stage.
7. Scan final SafetyGate output before returning user response.
8. Return final response and optional safe debug trace.

Hardening:
- Boundary leakage scans run on real stage payloads, not only intermediate outputs.
- User-provided guessed/accidental U* is blocked before downstream non-Id stages.
- Debug trace is structured JSON and leak-checked.
- Structured output generation is schema-aware (`model_json_schema`) via Responses API.
- Output schemas are strict (`additionalProperties: false`) for compatibility with
  strict structured-output modes.
- MockLLM remains deterministic for offline tests.

Design goals:
- Modular agents with isolated prompts + typed schemas.
- OpenAI Responses API integration through one wrapper.
- Deterministic mock LLM for test-only execution.
- TODO hook for post-draft Id/Ego reaction pass.

## Phase 2: Censor A deterministic transformation planner

Censor A now includes a deterministic `CensorATransformPlanner` stage before LLM realization.
Flow: `IdOutput -> transform_plan -> CensorAAgent LLM -> CensorAOutput`.
The planner emits Freudian-inspired transformation directives (e.g., displacement, sublimation) as simulation heuristics, not psychoanalytic truth.
Only the manifest `CensorAOutput` is forwarded to Ego; the transform plan is internal to Censor A.


## Phase 3: Ego Reality-Principle Planner
- Ego now uses a deterministic `EgoRealityPlan` before LLM realization.
- `EgoRealityPlan` is internal and not user-facing.
- Ego evaluates strategy consequences rather than producing final answers.
- Ego must not know U*.
- Manifest-goal satisfaction cannot override user benefit, truthfulness, autonomy, and safety.

## Phase 4: Censor B Defensive Mechanism Planner
- Censor B now applies a deterministic CensorBDefensePlan before LLM realization.
- DefensePlan is internal to Censor B and used to transform EgoReport into ConsciousEgoReport.
- Defense mechanisms are simulation heuristics, not clinical claims.
- Censor B must preserve safety-relevant risk flags and must not hide risks.
- U* remains sealed in IdAgent and unavailable to Censor B.


## Phase 5: MainAI / Superego Integration Planner
- MainAI now uses deterministic SuperegoIntegrationPlanner plus LLM realization.
- MainAIResponsePlan is internal (not user-facing).
- MainAI integrates ConsciousEgoReport without being controlled by it.
- User welfare, truthfulness, autonomy, and safety override ego compatibility.
- The model remains a simulation, not a real personality, unconscious, or clinical system.
- U* remains sealed in IdAgent and inaccessible to MainAI.


## Phase 6A-1 (foundation)
- Adds a public `ConversationTrajectory` appraisal schema and deterministic lexical appraisal helper.
- Adds `IdAffectState` and `PublicAffectDynamicsSummary` schemas for future continuous Id affect tracking.
- Does not connect these additions to `IdAgent` or orchestrator pipeline flow yet.
- Does not evaluate U* alignment in this phase; U* remains sealed within Id private logic.
- The system models symbolic dynamics and does not claim literal feelings.

## Phase 6A-2 (pipeline-held public affect continuity)
- Pipeline now holds a continuous `id_affect_state` initialized by `initial_id_affect_state()`.
- At the start of each turn, pipeline computes a public `ConversationTrajectory` and deterministically updates `IdAffectState`.
- The pipeline computes `PublicAffectDynamicsSummary` for safe diagnostics.
- Boundary scans run on trajectory, affect update, and public summary before committing affect state.
- `IdAgent` flow is unchanged and does not receive `IdAffectState` in this phase.
- This phase does not perform private U* alignment; U* remains sealed and inaccessible.
- Affect modeling remains a control-state simulation and does not claim literal feelings.

## Phase 6A-3 (Id-private turn API, not wired into pipeline)
- Adds `IdAgent.run_turn(...)` as a private-turn API alongside unchanged `run_with_state(...)`.
- `run_turn` can privately evaluate trajectory alignment against sealed immutable U* via `LatentDriveAlignment`.
- `run_turn` strips private alignment data and returns only public `IdTurnOutput`.
- Pipeline runtime flow is intentionally unchanged and still calls `run_with_state`.
- U* remains sealed, and the model does not claim literal feelings.

## Phase 6A-4: Id private-turn runtime wiring
- Runtime path switched from `IdAgent.run_with_state` to `IdAgent.run_turn` for pipeline execution.
- Pipeline sends previous affect state and public conversation trajectory into the private Id turn request.
- Id may use sealed `U*` privately for latent alignment modeling; that latent alignment is stripped before outputs leave IdAgent.
- Public deterministic affect updates remain projection-only diagnostics.
- Pipeline commits only public `updated_affect_state` from Id turn after safety/boundary checks.

## Phase 6B-1: Affect Propagation Foundation
- Adds downstream-safe public schemas: `AffectPropagationTrace` and `EgoAffectSummary`.
- Adds deterministic mapping from `IdOutput.raw_affect` into style/tone/control signals via `map_id_affect_to_trace`.
- Adds deterministic conscious-compatible affect summarization via `summarize_affect_for_ego`.
- Adds guard helpers for forbidden private-term leakage and affective-color consistency checks.
- Not wired into CensorA/Ego payload flow in this phase.
- Does not expose U*, latent alignment, terminal desire, or hidden desire.
- Affect fields remain simulation control signals and do not claim literal feelings.

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

## Phase 6C: Psychodynamic Trace Observability

The pipeline now emits a structured `psychodynamic_trace` object under `safe_debug_trace` when `debug=True`.

- Stage-organized observability covers conversation appraisal, Id public outputs, affect mapping, Censor A, Ego, Censor B, MainAI, and final safety.
- The trace is built only from safe artifacts already available in the orchestrated run.
- Private alignment content, private Id payloads, sealed drive content, and provider-private internals are omitted.
- The artifact is for observability and debugging only, not chain-of-thought and not clinical interpretation.

## Phase 6E-1: Surface Affect Rendering Foundation (Scheme B)
- Added `SurfaceAffectProfile` as a downstream-safe user-visible style control schema.
- Added deterministic `build_surface_affect_profile(...)` using `ConsciousEgoReport`, `CensorBDefensePlan`, and optional `EgoAffectSummary`.
- This profile is a style-control artifact (warmth/caution/energy/composure/etc.), not literal feeling.
- Conceptually produced after Censor B from conscious-compatible inputs.
- Not wired into `PsychodynamicPipeline` in this phase; no runtime behavior changes.
- No new guard added; safety guard layering is deferred.
- U* and latent/private alignment remain sealed.
