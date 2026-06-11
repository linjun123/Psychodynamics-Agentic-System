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
