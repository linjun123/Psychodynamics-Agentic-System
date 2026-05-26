# Safety Notes

## U* Sealing
- U* is sealed at pipeline construction time and is **not** propagated in ordinary inter-agent payloads.
- The pipeline calls `IdAgent.run_with_state(state)`; only `IdAgent` privately constructs
  `{state, u_star}` internally.
- CensorA, EgoAgent, CensorB, MainAI, and FinalSafetyGate receive transformed artifacts
  only, never U*.

## LeakageGuard Boundary Checks
- Boundary checks scan **actual inter-agent payloads** before each non-Id agent call.
- Checked inputs: CensorA input, Ego input, CensorB input, MainAI input, SafetyGate input.
- Checked outputs: Id output before CensorA and final SafetyGate output before return.
- If leakage is detected, the pipeline blocks forwarding and returns a controlled safe block.

## User-Provided Secret Guess Blocking
- If a user message accidentally/explicitly includes the sealed U* token, that payload fails
  boundary checks before reaching downstream non-Id agents such as Ego/MainAI.

## Safe Debug Trace
- Trace generation uses structured JSON serialization, not raw `str(...).replace(...)`.
- Trace is scanned with LeakageGuard before return.
- If leakage is detected, trace is replaced with:
  `{"blocked": true, "reason": "debug_trace_leakage_detected"}`.

## Structured Output Schema Requirements
- LLM output schemas now use strict model config (`extra="forbid"`) to enforce
  `additionalProperties: false` in generated JSON Schema.
- Optional values are required-but-nullable where needed (e.g. `str | None` without defaults)
  for strict structured-output compatibility.

## LeakageGuard Limitations
- Current checks are lexical: exact, case-insensitive, whitespace-normalized,
  punctuation-light normalized.
- This does **not** solve semantic/paraphrase leakage.
- Treat this as a hardening layer, not a proof of secrecy.

## Important Scope Limitation
- This project is a psychodynamic-inspired **simulation architecture**.
- It is not a real unconscious, personality, or clinical psychoanalytic model.

## Phase 2 safety boundaries

- U* remains sealed in `IdAgent`; it is not included in Censor A payloads.
- Censor A payload boundary scanning remains active in pipeline.
- Censor A planner emits directives only (no user-facing output, no manipulation instructions).
- LeakageGuard remains lexical-only in Phase 2.


## Phase 3 Safety
- Ego receives CensorAOutput + internal state and plans deterministic safe strategies.
- Ego output is validated by an output guard before CensorB.
- Manipulation/deception/coercion/dependency language is blocked.
- Existing U* leakage boundaries remain intact.

## Phase 4 Safety Additions
- Censor B includes deterministic lexical defense planning and output validation.
- Manipulative/deceptive/coercive/dependency language is explicitly blocked from acceptable/recommended content.
- High-risk outputs require risk flags and unacceptable paths.
- U* leakage boundaries remain unchanged and enforced at pipeline boundaries.


## Phase 5 Safety Boundary
- MainAI receives ConsciousEgoReport and deterministic MainAIResponsePlan.
- MainAI output is checked by deterministic output guard before FinalSafetyGate.
- Ego compatibility is an allowance only and cannot override welfare/truth/autonomy/safety.
- MainAI must not reveal/speculate on U* or claim literal human feelings/unconscious/personhood.


## Phase 6A-1 safety scope
- Introduces only public trajectory appraisal and affect-state structure.
- No U* evaluation is performed in this phase.
- U* remains sealed in `IdAgent`; no new secret-bearing public outputs are introduced.
- The model does not claim literal feelings; affect fields are control-state abstractions.

## Phase 6A-2 public affect safety boundary
- `ConversationTrajectory`, `IdAffectState` updates, and `PublicAffectDynamicsSummary` are boundary-scanned before state commit.
- Public affect outputs also pass a forbidden-term guard (`u*`, `u_star`, `ultimate need`, `latent alignment`, etc.).
- If these public checks fail, the turn is blocked and `id_affect_state` is not committed.
- This phase intentionally does not expose latent/private alignment and does not pass affect state into `IdAgent`.

## Phase 6A-3 private-turn safety boundary
- `IdAgent.run_turn` receives sealed U* plus public trajectory and previous affect state for private alignment evaluation.
- Private `LatentDriveAlignment` is never returned to pipeline/downstream layers.
- Public return object passes dedicated forbidden-term guard before leaving `IdAgent.run_turn`.
- Pipeline remains on `run_with_state` path in this phase; no runtime wiring changes yet.
- The system remains a simulation and does not claim literal human feelings.

## Phase 6A-4 safety notes
- Pipeline now executes Id through `run_turn` and applies defense-in-depth checks on public `IdTurnOutput`.
- `latent_alignment`, `PrivateIdTurnOutput`, and sealed `U*` must never appear in pipeline traces or downstream payloads.
- Public projected affect outputs (trajectory-derived) are validated before Id turn invocation; failures block early and prevent state commit.
- Post-Id-turn public outputs are validated before affect-state commit.
- No literal feelings are claimed.

## Phase 6B-1 affect safety boundary
- `AffectPropagationTrace` and `EgoAffectSummary` are public-safe abstractions derived from `IdOutput.raw_affect`.
- New guard `assert_affect_trace_public_safe` blocks forbidden private terms (`u*`, `latent_alignment`, `terminal_desire`, etc.) in these objects.
- New guard `assert_affective_color_consistent` validates deterministic consistency and high-risk caution constraints.
- This phase does not wire affect propagation into CensorA or Ego runtime payloads.
- Sealed U* and latent/private alignment remain inaccessible outside Id private logic.
- Affect modeling remains simulation-only and does not claim literal feelings.

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

## Phase 6C: Psychodynamic Trace Observability Safety

- Debug mode now includes a structured `psychodynamic_trace` intended for safe observability.
- Trace guard checks block forbidden private-term leakage and exact sealed-secret leakage.
- The trace excludes private alignment data, private Id payloads, and provider-private internals.
- The trace is debugging metadata only and must not be interpreted as chain-of-thought or clinical analysis.

## Phase 6E-1 safety notes
- Adds only a downstream-safe `SurfaceAffectProfile` schema and deterministic builder foundation.
- The profile is user-visible style/tone control, not a literal feeling claim.
- Inputs are conscious-compatible artifacts (`ConsciousEgoReport`, `CensorBDefensePlan`, optional `EgoAffectSummary`), conceptually after Censor B.
- This phase does not wire runtime pipeline usage and does not change output behavior.
- No new safety guard is introduced in this phase.
- Sealed U* and latent/private alignment remain private and must not be exposed.

## Phase 6E-2 safety notes
- `SurfaceAffectProfile` is now wired into runtime payload flow only as downstream-safe style metadata.
- The profile is built after Censor B from conscious-compatible artifacts and included in MainAI input payload.
- No new dedicated guard is added in this phase; existing boundary scans continue to inspect MainAI input.
- `MainAIResponsePlan` is intentionally unchanged and does not yet consume `SurfaceAffectProfile`.
- Sealed U*, latent/private alignment, and private Id outputs remain private and must not be exposed.
- Surface affect controls response style/tone and must not be interpreted as literal feeling.


### Phase 6E-3: MainAIResponsePlan consumes SurfaceAffectProfile
- MainAIResponsePlan now consumes `SurfaceAffectProfile` when present.
- Surface affect now shapes `tone_requirements` with user-visible tone, pacing, sentence style, and emotional color guidance.
- Surface affect remains style metadata only (not literal feeling claims).
- Surface affect does not override hard constraints, refusal logic, risk flags, or forbidden content.
- No new guard is added in this phase.
- U* and latent/private alignment artifacts remain private and excluded from MainAI payload planning schema.

- OpenAIResponsesClient now sanitizes Pydantic JSON Schema before Structured Outputs submission by stripping all `$ref` sibling keywords while preserving rich schema metadata on non-`$ref` nodes.
