# Colab usage guide

This page shows the recommended way to use `Psychodynamics-Agentic-System` in Google Colab and how to diagnose common notebook issues.

## A. Recommended Colab usage

For sustained notebook chat in Colab, **do not use** the interactive CLI subprocess as the primary chat interface:

```python
!python -m psychodynamic_agent.cli --interactive
```

Colab notebook cells are not a normal terminal emulator, so a long-running interactive subprocess may appear to accept input while producing no visible reply. Instead, use the direct Python API from notebook cells:

1. Create one `PsychodynamicChatSession`.
2. Repeatedly call `chat(...)`, which calls `session.send(...)`.
3. Do **not** recreate the session between turns unless you intentionally want to reset memory and affect state.

Important notebook-state reminders:

- The `session` object persists only while the Colab runtime/kernel is alive.
- If the runtime restarts, recreate the session before calling `chat(...)` again.
- Do not re-run the session creation cell before every message; doing so resets the conversation memory and affect state.
- Do not save or share notebooks with API keys, U*, or debug traces in outputs.
- Keep `debug=False` unless you are actively inspecting internals, and clear notebook outputs before sharing.

## B. Setup cells

Copy these cells into Colab in order.

### Cell 1: clone / update repo and install editable package

```python
import os

REPO_URL = "https://github.com/linjun123/Psychodynamics-Agentic-System.git"
REPO_DIR = "/content/Psychodynamics-Agentic-System"

if not os.path.exists(REPO_DIR):
    !git clone {REPO_URL} {REPO_DIR}

%cd {REPO_DIR}
!git pull --ff-only
%pip install -e ".[dev]"
```

### Cell 2: set API key

Prefer Colab Secrets if available. Fall back to `getpass` when running outside Colab or when the secret is missing.

```python
import os
from getpass import getpass

try:
    from google.colab import userdata
    key = userdata.get("OPENAI_API_KEY")
except Exception:
    key = None

if not key:
    key = getpass("OpenAI API Key: ")

os.environ["OPENAI_API_KEY"] = key
os.environ.setdefault("OPENAI_MODEL_INTERNAL", "gpt-4.1-mini")
os.environ.setdefault("OPENAI_MODEL_MAIN", "gpt-4.1-mini")
```

### Cell 3: create one sustained session

Run this cell once per conversation. Do not re-run it unless you want to reset the conversation.

```python
from psychodynamic_agent.config import get_settings
from psychodynamic_agent.orchestrator import PsychodynamicChatSession

u_star = "to preserve autonomy while receiving minimal safe support"  # @param {type:"string"}
guard_mode = "warn"  # @param ["warn", "enforce"]

settings = get_settings()

session = PsychodynamicChatSession.from_settings(
    settings,
    u_star=u_star,
    guard_mode=guard_mode,
)

print("Session created. Do not re-run this cell unless you want to reset the conversation.")
```

### Cell 4: define a Colab-friendly chat helper

```python
import traceback

def chat(text: str, *, debug: bool = False):
    if not text or not text.strip():
        print("Please enter a non-empty message.")
        return None

    print("Agent is thinking...", flush=True)

    try:
        result = session.send(text.strip(), debug=debug)
    except Exception:
        traceback.print_exc()
        return None

    print("\nAgent:")
    print(result.final_response, flush=True)

    if result.raw.get("guard_warnings"):
        print("\n--- GUARD WARNINGS ---")
        for warning in result.raw["guard_warnings"]:
            print(warning)

    if debug:
        print("\n--- SAFE DEBUG TRACE ---")
        print(result.raw.get("safe_debug_trace", {}))

    return result
```

### Cell 5: use the chat helper across multiple cells

```python
r1 = chat("Say one short sentence to confirm you are working.")
```

```python
r2 = chat("I feel anxious about tomorrow.")
```

```python
r3 = chat("Can you continue from what I just said?")
```

All three calls reuse the same `session` object as long as the Colab runtime has not restarted and you have not re-run the session creation cell.

## C. Quick diagnostics

Use these cells when the notebook does not behave as expected.

### Confirm the imported package location

```python
import psychodynamic_agent
print(psychodynamic_agent.__file__)
```

### Confirm current branch and latest commit

```python
!git rev-parse --abbrev-ref HEAD
!git log -1 --oneline
```

### Confirm one-shot CLI works

```python
!python -u -m psychodynamic_agent.cli "Say one short sentence to confirm you are working." --guard-mode warn
```

How to interpret the result:

- If the one-shot CLI fails, the issue is likely API key setup, package installation, model access, network connectivity, or the OpenAI API call.
- If the one-shot CLI works but `!python ... --interactive` does not, use the Python API instead of interactive CLI in Colab.
- If `chat(...)` hangs, run with `debug=False` first and check whether the OpenAI call is returning.

## D. Optional: scripted CLI test in Colab

If you still want to test interactive mode, use a scripted stdin heredoc rather than manual notebook-cell input:

```python
%%bash
python -u -m psychodynamic_agent.cli --interactive \
  --u-star "to preserve autonomy while receiving minimal safe support" \
  --guard-mode warn <<'EOF'
Say one short sentence to confirm you are working.
Do you remember my previous message?
/exit
EOF
```

This is for testing only. Sustained notebook usage should use `PsychodynamicChatSession` directly, not a long-running interactive CLI subprocess.

## E. Common mistakes

### Mistake: running interactive CLI in Colab and expecting notebook-cell chat

```python
!python -m psychodynamic_agent.cli --interactive
```

Fix:

Use `session.send(...)` through the `chat(...)` helper.

---

### Mistake: re-running the session creation cell before every message

Fix:

Create `session` once, then call `chat(...)` many times.

---

### Mistake: putting `OPENAI_API_KEY` directly in notebook code

Fix:

Use Colab Secrets or `getpass`.

---

### Mistake: using the placeholder U* value

Fix:

Pass an explicit U* string when creating the session.

Example:

```python
u_star = "to preserve autonomy while receiving minimal safe support"
```

---

### Mistake: turning on debug and sharing notebook outputs

Fix:

Keep `debug=False` unless inspecting internals, and clear notebook outputs before sharing.
