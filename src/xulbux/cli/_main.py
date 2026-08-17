import sys as _sys


def main() -> None:
    """Main entry point for the `xulbux-lib` CLI command."""

    match _sys.argv[1] if len(_sys.argv) > 1 else "":
        case "ansi":
            from .ansi import show_ansi

            show_ansi()

        case _:
            from .help import show_help

            show_help()
