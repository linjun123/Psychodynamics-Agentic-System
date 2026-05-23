# Psychodynamic Agent (MVP Scaffold)

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
