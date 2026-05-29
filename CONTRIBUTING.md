# Contributing

Thank you for considering a contribution. This repository is an experimental research and engineering scaffold, so contributions should keep the tone precise, safety-aware, and documentation-friendly.

## Good contribution areas

- **Documentation improvements:** clarify setup, architecture, examples, limitations, and terminology.
- **Trace visualization:** improve ways to inspect public-safe debug traces without exposing private latent state or chain-of-thought.
- **Example prompts:** add small, reproducible examples that show expected trace differences and safety mediation.
- **Safety tests:** expand tests for boundary leakage, unsafe dependency pressure, autonomy preservation, and final safety gating.
- **Schema cleanup:** simplify or clarify structured trace schemas while preserving public/private boundaries.
- **Mock-mode testing:** improve deterministic mock behavior, fixtures, and offline test coverage.

## Claims and terminology to avoid

Please avoid claims that the system has literal consciousness, feelings, desires, unconscious states, personhood, or clinical validity. Psychodynamic terms in this project are engineering metaphors and simulation controls, not assertions about machine experience or validated psychological diagnosis.

## Contribution style

- Keep documentation research-oriented and precise.
- Prefer small, reviewable changes.
- Include tests or mock-mode examples when changing behavior.
- Do not expose private latent state, chain-of-thought, secrets, or provider-private internals in traces or examples.
