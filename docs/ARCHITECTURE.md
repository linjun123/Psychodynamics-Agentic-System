# Architecture

Pipeline:
1. Build `FullInternalState` from in-memory context.
2. IdAgent reads full state plus sealed U* (read-only).
3. CensorA converts Id output to Manifest Goal + Affective Color.
4. EgoAgent evaluates options, risks, and recommendations.
5. CensorB produces Main-AI-compatible conscious report.
6. MainAI drafts user-facing response.
7. FinalSafetyGate approves/revises/blocks output.
8. Return final response and optional safe debug trace.

Design goals:
- Modular agents with isolated prompts + typed schemas.
- OpenAI Responses API integration through one wrapper.
- Deterministic mock LLM for test-only execution.
- TODO hook for post-draft Id/Ego reaction pass.
