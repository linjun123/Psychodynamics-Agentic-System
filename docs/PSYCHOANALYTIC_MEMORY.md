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
