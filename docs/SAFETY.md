# Safety Notes

## U* Sealing
- U* lives only as a sealed value in pipeline + Id agent constructor.
- U* is not provided to Ego/CensorB/MainAI prompts.

## Redaction
- Safe debug trace uses string redaction to remove exact U* secret token.
- Normal output returns only final safe response.

## Anti-manipulation
- Prompt-level constraints prohibit manipulative strategy generation.
- Censor B removes manipulative/unsafe directions.
- Final Safety Gate can block or revise unsafe drafts.

## Limitations
- MVP prompt-based controls are not formal guarantees.
- Paraphrase-level leakage detection is not fully solved yet.
- No long-term memory/database in this scaffold.
