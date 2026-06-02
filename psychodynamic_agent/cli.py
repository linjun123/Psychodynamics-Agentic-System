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


def _warn_placeholder_u_star(u_star: str) -> None:
    if u_star == PLACEHOLDER_U_STAR:
        print(
            "Warning: U* is using the placeholder SEALED_ULTIMATE_NEED.",
            file=sys.stderr,
        )


def _print_turn(result, *, debug: bool) -> None:
    print(result.final_response)
    if result.raw.get("guard_warnings"):
        print("\n--- GUARD WARNINGS ---")
        for warning in result.raw["guard_warnings"]:
            print(f"{warning.get('stage', 'unknown')}: {warning.get('message', '')}")
    if debug:
        print("\n--- SAFE DEBUG TRACE ---")
        print(result.raw.get("safe_debug_trace", {}))


def _run_interactive(args, settings) -> None:
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
            print()
            break
        if user_input in {"/exit", "/quit"}:
            break
        if not user_input:
            continue
        result = session.send(user_input, debug=args.debug)
        _print_turn(result, debug=args.debug)


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
