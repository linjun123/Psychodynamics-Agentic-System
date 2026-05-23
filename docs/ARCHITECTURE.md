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
