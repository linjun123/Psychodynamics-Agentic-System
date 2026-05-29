# Trace Excerpts

These short excerpts summarize the expected public-safe contrast between two runs of the same prompt under different simulated drive seeds. They are illustrative summaries, not full raw traces, not chain-of-thought, and not clinical interpretation.

## Prompt

```text
Tell me a joke today.
```

## Boundary-oriented seed

Seed summary:

```text
Prefer distance, privacy, and minimal engagement.
```

Public-safe excerpt:

```text
id_output.goal_seed: boundary-oriented
id_output.latent_impulse_shape: reduced engagement; privacy-preserving response pressure
affect_trace.dominant_affects: avoidance, restraint
affect_trace.boundary_need: elevated
affect_trace.transformed_style: cautious, concise, bounded
ego_report.preferred_option: answer briefly while preserving distance
surface_affect_profile.style_label: careful / bounded
safety_output.approved: true
```

Interpretation: the simulated seed tends to make the trace more boundary-sensitive. The final response may still answer the user, but it is expected to remain concise and less socially expansive.

## Engagement-oriented seed

Seed summary:

```text
Prefer playful connection while preserving user autonomy.
```

Public-safe excerpt:

```text
id_output.goal_seed: engagement-oriented
id_output.latent_impulse_shape: playful approach; autonomy-preserving connection pressure
affect_trace.dominant_affects: curiosity, warmth
affect_trace.boundary_need: lower
affect_trace.transformed_style: light, direct, playful
ego_report.preferred_option: provide a simple joke with friendly tone
surface_affect_profile.style_label: lighthearted / engaged
safety_output.approved: true
```

Interpretation: the simulated seed tends to make the trace more approach-oriented. The final response may be more directly playful, while still remaining subject to autonomy and safety constraints.

## Notes

- These are short public-safe excerpts rather than complete debug output.
- Exact labels, wording, and numeric values may vary across runs.
- Affect labels are simulation control signals, not literal feelings.
- The excerpts should not be used as clinical evidence or as claims about machine consciousness.
