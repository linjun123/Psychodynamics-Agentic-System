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

## Run checks

```bash
ruff check .
pytest
```

## Notes
- Uses OpenAI Responses API with schema-aware JSON output requests.
- Includes LeakageGuard lexical checks; this does not detect all semantic/paraphrase leakage.
- This is a simulation scaffold, not a literal human unconscious/personality model.
