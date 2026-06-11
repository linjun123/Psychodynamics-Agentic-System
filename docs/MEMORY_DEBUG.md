# Memory Debug Modes

This repository keeps public-safe debug output separate from developer-only
private memory debug output.

## Safe debug remains public-safe

Existing safe debug behavior must remain public-safe. `SafeMemoryDebugSummary`
can report mechanism-level metadata such as activated counts, active public
mechanisms, pressure levels, and public notes. It must not expose private memory
trace text, private core summaries, sealed U*, latent/private alignment content,
provider-private internals, or chain-of-thought-like text.

## Private memory debug is separate

`PrivateMemoryDebugTrace` is a future developer-only artifact for inspecting the
private psychoanalytic memory system. It may expose private memory traces,
including `private_core_summary`, plus transformation records, defense decisions,
complexes, repetition biases, safe summaries, and conscious memory views.

Private memory debug must still not expose:

- sealed U* values or fields
- latent alignment or private alignment content
- provider-private chain-of-thought or provider-private internals
- system prompts
- developer messages

## Proposed future usage

Future runtime wiring can request private memory debug with both explicit config
and an environment flag:

```python
MemoryDebugConfig(mode="private", include_private_trace_text=True)
```

```bash
PSYCHODYNAMIC_PRIVATE_MEMORY_DEBUG=1
```

The foundation helper requires `PSYCHODYNAMIC_PRIVATE_MEMORY_DEBUG=1` by default
when `mode="private"`. Tests may disable the environment requirement with
`require_env_flag=False` for deterministic unit coverage.

## Why safe and private traces must remain separate

`safe_debug_trace` and `private_memory_debug_trace` must remain separate because
they have different audiences and disclosure rules. Safe debug output is designed
for public-safe observability and can be surfaced without exposing private trace
content. Private memory debug is developer-only observability for future memory
internals and may include private trace fields, so it requires explicit gating
and a stricter guard against sealed U*, latent/private alignment,
provider-private internals, prompts, and chain-of-thought-like text.

## PR2 memory store debug output

PR2 allows `PsychoanalyticMemoryStore` to build memory debug artifacts through
`MemoryDebugConfig`. The normal safe summary remains mechanism-level and
public-safe: it can include trace counts, public symbolic labels, active public
mechanisms, pressure numbers, and public notes, but it must not include private
trace text or `private_core_summary` content.

Private debug traces are only returned when private mode is enabled and the
private debug guard allows the payload. By default this requires
`PSYCHODYNAMIC_PRIVATE_MEMORY_DEBUG=1`.

`include_private_trace_text` controls private trace redaction:

- `False`: retrieved `MemoryTrace` objects are included with
  `private_core_summary` redacted to `None`. Future private complex labels and
  private transformation input summaries are also redacted by the same helper.
- `True`: `private_core_summary` may be included, but only when private debug
  mode and the environment flag permit it, and only after the private debug guard
  checks the resulting payload.

Safe summaries and private traces remain separate. Safe output is suitable only
for public mechanism-level observability; private debug output is developer-only
and must continue to pass the stricter protected-content guard.

## PR3 retrieval activation debug output

PR3 allows developer-only private memory debug traces to include
`retrieval_activations` after store-level association retrieval has been run.
Each activation contains public-safe score metadata: trace ID, rank,
association score, component breakdowns, accessibility mode, matched public
object/symbol labels, and a compact public reason. It does not contain
`private_core_summary` or raw private trace text.

Safe debug remains public-safe. `SafeMemoryDebugSummary` may note that
association retrieval exists for private inspection, but it must not include
retrieval activation payloads, private trace text, private summaries, sealed
U*, latent/private alignment content, provider-private internals, system or
developer messages, or chain-of-thought-like text.

Private debug remains explicitly gated by `MemoryDebugConfig` and, by default,
`PSYCHODYNAMIC_PRIVATE_MEMORY_DEBUG=1`. When
`include_private_trace_text=False`, retrieved `MemoryTrace.private_core_summary`
continues to be redacted while retrieval activation score breakdowns are
preserved for developer inspection.

## PR4 defensive projection debug output

PR4 allows developer-only private memory debug traces to include defensive
projection artifacts after `project_conscious_view_for_turn` has been run:

- `defense_decisions` records the public-safe access decision for each retrieved
  activation, including mechanism, pressure, and a short public reason.
- `transformation_chain` records how each private trace activation became a
  direct cue, screened cue, felt-sense cue, or blocked cue.
- `conscious_memory_view` contains conscious-compatible public cues and pressure
  metadata.

Safe debug remains public-safe and mechanism-level only. It may mention that
private defensive projection is available for inspection, but it must not expose
private trace text, private transformation input summaries, defense decision
payloads, or transformation-chain private text.

When `include_private_trace_text=False`, private debug redaction removes both
`MemoryTrace.private_core_summary` and
`MemoryTransformationRecord.private_input_summary`. Retrieval activations,
defense decisions, and the conscious memory view are preserved because their
stored fields are public-safe. Defense decisions use public-safe reasons only.

`ConsciousMemoryView` is conscious-compatible, but it is not runtime-wired in
PR4. It is not passed to Ego/MainAI/SafetyGate and does not alter final
responses.
