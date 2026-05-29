# Launch Notes

## Project pitch

Psychodynamic Agent is a simulation-oriented research scaffold for exploring how staged, psychodynamic-style control signals can shape public-safe LLM agent traces and final responses.

## Same-prompt two-seed demo summary

The same-prompt two-seed demo runs one user request with two different simulated drive seeds: a boundary-oriented seed that tends to produce more cautious, bounded trace signals, and an engagement-oriented seed that tends to produce more direct or playful trace signals. The demo is intended to compare public-safe intermediate artifacts such as affect labels, boundary need, ego recommendations, surface style, and final safety approval, not to expose private latent state or chain-of-thought.

See the detailed demo: [Trace Contrast Demo](examples/TRACE_CONTRAST_DEMO.md).

## What this project is

- A research and engineering scaffold for psychodynamic-style LLM agent architecture.
- A staged simulation pipeline for impulse proposal, censorship, reality-principle planning, affect-style rendering, final integration, and safety gating.
- A public-safe observability experiment for comparing how simulated internal control signals affect traces and final responses.
- A mock-mode-friendly codebase for repeatable tests and documentation examples.

## What this project is not

- It is not evidence that LLMs have literal unconscious states, consciousness, feelings, drives, or personhood.
- It is not a clinical model, diagnostic tool, therapeutic system, or validated psychological theory.
- It is not a claim that trace artifacts reveal hidden mental states.
- It is not intended for high-stakes decision-making or clinical interpretation.

## Suggested citation or description text

> Psychodynamic Agent is an experimental research scaffold for staged, psychodynamic-style LLM agent architecture and public-safe trace observability. It uses simulated control signals for affect, boundary pressure, planning, tone, and safety mediation, without claiming literal machine consciousness, feelings, or clinical validity.

## Related documentation

- [README](../README.md)
- [Trace Contrast Demo](examples/TRACE_CONTRAST_DEMO.md)
