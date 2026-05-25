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
