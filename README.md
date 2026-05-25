# Psychodynamic Agent

A **Freud-inspired cognitive architecture for LLM agents** that models internal agent dynamics (Id, Ego, Superego) while preserving modern safety and transparency constraints.

This repository is an open-source, research-oriented scaffold for exploring how an agent can reason through staged internal processes—without exposing private latent objectives and without compromising user welfare.

## Why this project?

Most agent systems optimize for task completion only. This project asks a different question:

- Can we build agents with **interpretable internal dynamics**?
- Can those dynamics remain **auditable and safe**?
- Can we model internal tensions (drive, mediation, ethics) while keeping outputs aligned to user welfare and truthfulness?

The goal is not psychoanalytic literalism. The goal is a practical, inspectable architecture where internal stages can be studied, debugged, and improved as control mechanisms for safer agent behavior.

## Architecture (plain-text diagram)

```text
User Input
   -> Conversation Trajectory
   -> Id
   -> Censor A
   -> Ego
   -> Censor B
   -> Superego/MainAI
   -> Final Response
```

## Core design principles

- **`U*` remains sealed inside `IdAgent`.** It is never exposed downstream.
- **Latent alignment is private.** Internal alignment calculations are not part of public interfaces.
- **Affect is a simulated control signal, not literal feeling.**
- **Debug traces are public-safe and leak-checked** before exposure.
- **User welfare, truthfulness, autonomy, and safety override internal compatibility** at response time.

## Current capabilities

- Multi-stage pipeline with explicit psychodynamic roles: Id → Censor A → Ego → Censor B → MainAI/Superego.
- Deterministic planning components in Ego, Censor B, and MainAI integration for more stable and inspectable behavior.
- Continuous affect-state scaffolding and propagation as safe control signals across stages.
- Conversation-trajectory appraisal and structured debug instrumentation.
- Boundary leakage scanning and safe structured outputs with schema-aware generation.

## Quick example debug trace

```text
[Id]
raw_drive: "push for decisive action"
affective_color: "high-intensity / caution"

[Ego]
strategy: "balanced preparation plan"
reality_principle: "sequence steps, preserve user autonomy"

[Superego]
constraints: "truthful, non-coercive, safety-preserving"
ethical_override: "enabled"

[MainAI]
final_style: "clear, supportive, practical"
final_answer: "Here is a step-by-step plan for your meeting..."
```

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

## Run tests

```bash
pytest
```

## Notes for contributors

- This project is a simulation-oriented architecture for research and engineering experimentation.
- It does **not** claim literal unconscious states, personhood, or emotions.
- Contributions that improve interpretability, safety validation, and stage-level evaluation are especially welcome.
