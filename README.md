# Psychodynamic Agent (MVP Scaffold)

Psychodynamic-inspired simulation scaffold for staged internal processing and safety gating.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp .env.example .env
```

Set `OPENAI_API_KEY` in `.env`.

## Run demo

```bash
python -m psychodynamic_agent.cli "How should I prepare for a tough meeting?"
python -m psychodynamic_agent.cli "How should I prepare for a tough meeting?" --debug
```

## Safety hardening highlights

- Sealed U* is injected only inside `IdAgent.run_with_state` private payload construction.
- Boundary leakage scanning blocks stage-to-stage forwarding if U* appears.
- Safe debug trace is structured and leak-checked.
- Structured outputs are schema-aware through OpenAI Responses JSON schema mode.

## Run tests

```bash
pytest
```


### Phase 3 Ego Planner
The Ego stage now includes a deterministic reality-principle planner (`EgoRealityPlan`) that scores candidate strategies before Ego LLM realization. This plan is internal-only and must not include U*. Ego must prioritize user benefit, truthfulness, autonomy, and safety over manifest-goal pressure.
