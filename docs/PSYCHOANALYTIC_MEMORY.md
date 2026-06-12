# Psychoanalytic Memory Foundation

This PR is foundation-only. It adds schemas, debug-mode boundaries, guard helpers,
documentation, and tests for a future psychoanalytic memory system. It does not
wire memory into the runtime pipeline, alter final responses, or add memory
retrieval, storage, LLM interpretation, defense gating, distortion, repetition,
or complex activation behavior.

## Simulation scope

The psychoanalytic memory system is simulation-oriented. It is intended to model
fictional internal dynamics for an agent architecture, not to perform clinical
diagnosis, therapeutic assessment, or mental-health treatment.

## Future mechanisms

Future PRs may model memory association and transformation with psychoanalytic
mechanisms such as:

- affect/desire/threat-prioritized association
- defensive forgetting
- screen memory
- condensation
- displacement
- deferred action
- repetition bias
- complexes

This foundation only defines data contracts and safety boundaries for those
future mechanisms.

## Three-layer memory design

### `PrivateMemoryTrace`

The internal private layer is represented by `MemoryTrace`. It may include a
`private_core_summary`, affective/desire/threat signatures, object targets,
defense pressure, repression pressure, complex IDs, activation metadata, and an
accessibility mode. This layer is not downstream-safe and must not enter normal
final responses.

### `ConsciousMemoryView`

`ConsciousMemoryView` is the future defense-processed, conscious-compatible
projection. It may contain public cues, public complex labels, repetition bias
labels, and pressure levels. It must not include `private_core_summary` and is
the only future downstream-safe memory view intended for Ego/MainAI-style
consumption.

### `SafeMemoryDebugSummary`

`SafeMemoryDebugSummary` is a public-safe mechanism summary. It can show counts,
active mechanisms, pressure levels, public labels, and public notes. It cannot
expose private trace text, private core summaries, sealed drives, latent/private
alignment content, provider-private internals, or chain-of-thought-like text.

## Developer-only private debug

`PrivateMemoryDebugTrace` is a separate developer-only debug artifact. It may
expose private memory traces, transformation records, defense decisions, active
complexes, repetition biases, and the conscious memory view when explicitly
enabled by future runtime integration.

Even private memory debug must not expose sealed U*, latent/private alignment,
provider-private content, system/developer prompts, or chain-of-thought-like
text.

## Invariants

- `MemoryTrace` / the private trace layer must not enter a normal final response.
- `ConsciousMemoryView` is the only future downstream-safe view.
- `SafeMemoryDebugSummary` cannot expose private trace content.
- `PrivateMemoryDebugTrace` is developer-only and must be explicitly enabled.
- Future LLM-based memory operations may generate drafts, but deterministic code
  must own schema validation, boundary decisions, and guards.

## PR2: MemoryStore and heuristic trace extraction

PR2 adds a non-persistent `PsychoanalyticMemoryStore` and a deterministic
`HeuristicMemoryExtractor`. After each completed in-memory conversation turn, the
store can record a private `MemoryTrace` with a local ID such as `mem_000001`,
turn metadata, safe surface summary, private simulation summary,
affective/desire/threat signatures, object targets, symbolic labels, defense and
repression pressure, accessibility, and activation metadata.

The extraction path is heuristic-only in PR2. It uses the user turn text and
public-safe debug artifacts when available, such as raw affect, affect traces,
object cathexis, public affect dynamics, and ego affect summaries. It does not
call an LLM or OpenAI API, does not inspect sealed U*, latent/private alignment,
system prompts, provider-private internals, or chain-of-thought, and falls back
to neutral deterministic signatures when debug data is missing or malformed.

PR2 still does not perform retrieval, association ranking, defense gating,
distortion, repetition, complex clustering, screen memory, condensation,
displacement, deferred action, or runtime response influence. It only records
private traces for later phases to use.

`MemoryTrace` remains private to the memory store. It is not added to
`FullInternalState`, conversation history, previous Ego reports, previous MainAI
outputs, satisfaction history, safe debug traces, or final responses. Future LLM
memory interpretation remains out of scope for this PR.

## PR3: Affect-prioritized association retrieval

PR3 adds deterministic, store-level association retrieval for private
`MemoryTrace` records. Retrieval is modular and private: callers can build a
`MemoryRetrievalQuery`, score stored traces, and receive `MemoryActivation`
metadata from the memory store, but those activations are not wired into Ego,
MainAI, SafetyGate, the runtime pipeline, or final response generation.

Association retrieval intentionally prioritizes psychoanalytic-style similarity
over factual/topic overlap. The scoring components emphasize affective,
desire, and threat signatures first, then symbolic object overlap and salient
symbols. Repetition frequency contributes a small bounded signal, factual text
similarity remains deliberately low-weight, and defense/repression pressure
penalizes direct activation without deleting or mutating the underlying trace.

This PR does not add DefenseGate behavior, a `ConsciousMemoryView` projection,
screen memory, condensation, displacement, deferred action, repetition-bias
generation, complex clustering, LLM interpretation, API calls, or persistent
storage. Retrieval is read-only: it does not increment `activation_count` or
change stored `MemoryTrace` records.

## PR4: Defensive memory gate and conscious memory projection

PR4 adds a deterministic, store-level `MemoryDefenseGate` and
`ConsciousMemoryView` projection layer for retrieved private memory activations.
Retrieved `MemoryActivation` records are matched back to their private
`MemoryTrace` records, passed through a defensive access policy, and converted
into conscious-compatible cues only when the policy allows a cue to be emitted.

Defensive forgetting is modeled as access gating, not deletion. Private
`MemoryTrace` records remain stored privately even when defense or repression
pressure prevents them from entering the conscious view directly.

The PR4 access modes are intentionally minimal:

- Direct traces can become `direct_memory` conscious cues using sanitized public
  surface summaries.
- Screened traces can become symbolic `screen_memory` cues that avoid private
  core summaries and direct event detail.
- Felt-sense-only traces can become generic diffuse affective cues rather than
  factual recall.
- Blocked-action-only traces remain private and emit no conscious cue, while the
  private debug projection records the defensive block.

`ConsciousMemoryView` remains private/store-level only in this PR. It is not
added to `FullInternalState`, passed to Ego/MainAI, wired into the runtime
pipeline, or used to change final responses. This PR also does not add a full
memory distortion engine, repetition-bias generation, complex clustering,
condensation, displacement, deferred action, LLM memory interpretation, API
calls, or persistent storage.

## PR5: Memory distortion engine

PR5 adds a deterministic, store-level psychoanalytic memory distortion engine for private
inspection and debug projections. It does not wire distortion artifacts into the runtime
agent pipeline, Ego/MainAI response generation, or final responses.

The engine models distortion as defensive transformation rather than lying, deletion, or
historical rewriting:

- **Screen memory** converts screened traces into conscious-compatible symbolic substitute
  cues using public labels such as salient symbols, matched symbols, and safe structural
  targets. These cues do not expose `private_core_summary`.
- **Condensation** groups multiple activated traces with shared symbolic or affective
  overlap into a composite cue. Individual source cues can be suppressed when the
  condensed cue covers their conscious-compatible pressure.
- **Displacement** shifts a risky object focus, such as authority or parental targets,
  toward safer symbolic targets such as `task_structure`, `boundary`, `process`, or
  `communication_format` without claiming historical truth.
- **Deferred action** records candidate retrospective meaning updates when a newer trace
  strongly reactivates older traces. Candidate records describe possible reorganization
  without mutating old traces or incrementing stored `meaning_version` values.

Boundary notes:

- Distortion remains store-level/debug-level only.
- There is no pipeline wiring, no Id/Ego/Censor/MainAI/SafetyGate wiring, and no final
  response change.
- No memory objects are added to `FullInternalState`.
- No LLM interpreter or OpenAI API call is used.
- No persistent storage, repetition bias generation, complex clustering, or automatic
  historical trace mutation is introduced.

## PR6: Repetition bias generation

PR6 adds deterministic, modular repetition-bias generation for store-level and debug-level
memory inspection. It models the psychoanalytic idea that what is not directly remembered
may return as repeated action tendency or strategy pressure.

Blocked, felt-sense-only, screened, high-defense, repeatedly activated, deferred-action, or
condensed traces can produce `RepetitionBias` metadata such as `seek_reassurance`,
`avoid_topic`, `over_explain`, `test_boundary`, `intellectualize`, `ask_for_structure`,
`preempt_rejection`, or `control_uncertainty`. These artifacts are safe strategy metadata:
they can include source trace IDs for private developer inspection, compact tendency labels,
bounded intensity, safe handling hints, and prohibited expression notes, but they do not expose
`private_core_summary` or raw private summaries.

The repetition system is intentionally split into focused modules:

- `repetition_policy.py` contains deterministic thresholds, pressure scoring, tendency
  selection, safe hints, and prohibited-expression metadata.
- `repetition_generation.py` constructs public-safe triggers and `RepetitionBias` objects and
  merges duplicate tendencies.
- `repetition_engine.py` orchestrates per-trace triggers plus deferred-action and condensed
  pressure triggers.

Boundary notes:

- Repetition bias is not clinical diagnosis and does not claim historical truth.
- Repetition bias is not runtime behavior yet; it is store/debug metadata only.
- There is no Id/Ego/Censor/MainAI/SafetyGate or pipeline wiring in this PR.
- `FullInternalState` is not extended with repetition memory fields.
- No LLM interpreter or OpenAI API call is used.
- No complex clustering, persistent storage, `activation_count` mutation, or historical
  `meaning_version` mutation is introduced.
