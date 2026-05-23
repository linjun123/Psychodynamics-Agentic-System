# Safety Notes

## U* Sealing
- U* is injected only inside `IdAgent.build_private_payload` and accessed via `IdAgent.run_with_state`.
- The pipeline no longer constructs a normal shared dict containing U*.
- U* is never forwarded to Censor A, Ego, Censor B, Main AI, or Safety Gate payloads.

## LeakageGuard
- `psychodynamic_agent.safety.leakage_guard` scans payload boundaries for potential U* leakage.
- Detection modes in this phase: exact, case-insensitive, whitespace-normalized, punctuation-light.
- This does **not** solve semantic/paraphrase leakage; deeper model-based checks are a future phase.

## Boundary Enforcement
- The pipeline performs boundary checks after each stage and before forwarding to next stage.
- On detection, pipeline raises `PipelineSafetyError` and blocks forwarding.

## Safe Debug Trace
- Debug traces are JSON-serialized structurally.
- If leakage is detected, trace is replaced with:
  `{"blocked": true, "reason": "debug_trace_leakage_detected"}`.

## Limitations
- Prompt controls and lexical scans are defense-in-depth, not formal guarantees.
- This project is a simulation scaffold, not a real unconscious or personality.
