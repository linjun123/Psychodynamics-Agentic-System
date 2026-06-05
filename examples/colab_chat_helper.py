"""Pure-Python helpers for notebook or Colab chat sessions.

This module intentionally avoids notebook magics and shell commands. Install the
package and configure environment variables, including OPENAI_API_KEY, before
using these helpers.
"""

from psychodynamic_agent.config import get_settings
from psychodynamic_agent.orchestrator import PsychodynamicChatSession


def create_session(u_star: str, guard_mode: str = "warn") -> PsychodynamicChatSession:
    """Create one sustained chat session for repeated notebook calls."""
    settings = get_settings()
    return PsychodynamicChatSession.from_settings(
        settings,
        u_star=u_star,
        guard_mode=guard_mode,
    )


def chat(session: PsychodynamicChatSession, text: str, debug: bool = False):
    """Send one message through an existing sustained session and print the reply."""
    if not text or not text.strip():
        print("Please enter a non-empty message.")
        return None

    print("Agent is thinking...", flush=True)
    result = session.send(text.strip(), debug=debug)

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
