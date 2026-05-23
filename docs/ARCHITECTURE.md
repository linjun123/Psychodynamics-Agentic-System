# Architecture

Pipeline:
1. Build `FullInternalState` from in-memory context.
2. `IdAgent.run_with_state(state)` constructs a **private** Id payload including sealed U*.
3. CensorA converts Id output to Manifest Goal + Affective Color.
4. EgoAgent evaluates options, risks, and recommendations.
5. CensorB produces Main-AI-compatible conscious report.
6. MainAI drafts user-facing response.
7. FinalSafetyGate approves/revises/blocks output.
8. Return final response and optional safe debug trace.

Hardening notes:
- Boundary leakage checks run between every stage.
- Structured schema-aware output is requested via OpenAI Responses JSON schema mode.
- Deterministic mock LLM enables offline tests.

Scope note:
- This system simulates psychodynamic roles for experimentation; it is not a claim of real human-like unconscious processes.
