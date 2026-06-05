import argparse
import sys

from psychodynamic_agent.config import get_settings
from psychodynamic_agent.orchestrator.session import PsychodynamicChatSession

PLACEHOLDER_U_STAR = "SEALED_ULTIMATE_NEED"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("message", type=str, nargs="?")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--interactive", "-i", action="store_true")
    parser.add_argument("--u-star", type=str, default=None)
    parser.add_argument(
        "--guard-mode",
        choices=["enforce", "warn"],
        default="enforce",
    )
    return parser


def _is_colab() -> bool:
    return "google.colab" in sys.modules


def _safe_cli_error_message(exc: Exception, *, u_star: str | None) -> str:
    message = str(exc)
    if u_star:
        message = message.replace(u_star, "[sealed]")
    return message[:500]


def _warn_placeholder_u_star(u_star: str) -> None:
    if u_star == PLACEHOLDER_U_STAR:
        print(
            "Warning: U* is using the placeholder SEALED_ULTIMATE_NEED.",
            file=sys.stderr,
        )


def _print_turn(result, *, debug: bool, flush: bool = False) -> None:
    print(result.final_response, flush=flush)
    if result.raw.get("guard_warnings"):
        print("\n--- GUARD WARNINGS ---", flush=flush)
        for warning in result.raw["guard_warnings"]:
            print(
                f"{warning.get('stage', 'unknown')}: {warning.get('message', '')}",
                flush=flush,
            )
    if debug:
        print("\n--- SAFE DEBUG TRACE ---", flush=flush)
        print(result.raw.get("safe_debug_trace", {}), flush=flush)


def _run_interactive(args, settings) -> None:
    if _is_colab():
        print(
            "Colab note: for notebook chat, prefer PsychodynamicChatSession directly. "
            "See docs/COLAB.md.",
            flush=True,
        )

    u_star = args.u_star
    if u_star is None:
        u_star = input("U* (blank to use settings.ultimate_need_seed): ").strip()
        if not u_star:
            u_star = settings.ultimate_need_seed

    _warn_placeholder_u_star(u_star)
    session = PsychodynamicChatSession.from_settings(
        settings,
        u_star=u_star,
        guard_mode=args.guard_mode,
    )

    while True:
        try:
            user_input = input("> ").strip()
        except EOFError:
            print(flush=True)
            break
        if user_input in {"/exit", "/quit"}:
            break
        if not user_input:
            continue

        print("Agent is thinking...", flush=True)
        try:
            result = session.send(user_input, debug=args.debug)
        except Exception as exc:
            safe_message = _safe_cli_error_message(exc, u_star=u_star)
            print(
                f"Error while generating response: {type(exc).__name__}: {safe_message}",
                file=sys.stderr,
                flush=True,
            )
            print(
                "Resetting pipeline after failed turn while preserving recorded public memory.",
                file=sys.stderr,
                flush=True,
            )
            session.reset_pipeline_preserving_memory(
                settings,
                u_star=u_star,
                guard_mode=args.guard_mode,
            )
            continue
        _print_turn(result, debug=args.debug, flush=True)


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.interactive and args.message is None:
        parser.error("message is required unless --interactive is used")

    settings = get_settings()
    if args.interactive:
        _run_interactive(args, settings)
        return

    u_star = args.u_star or settings.ultimate_need_seed
    _warn_placeholder_u_star(u_star)
    session = PsychodynamicChatSession.from_settings(
        settings,
        u_star=u_star,
        guard_mode=args.guard_mode,
    )
    result = session.send(args.message, debug=args.debug)
    _print_turn(result, debug=args.debug)


if __name__ == "__main__":
    main()
