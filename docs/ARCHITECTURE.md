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
