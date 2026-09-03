import sys as _sys


def main() -> None:
    """Main entry point for the `xulbux-lib` CLI command."""

    match _sys.argv[1] if len(_sys.argv) > 1 else "":
        case "ansi":
            from .ansi import show_ansi

            show_ansi()

        case "c256":
            from .color256 import show_color256

            show_color256()

        case "tc":
            from .true_color import show_true_color

            show_true_color(_sys.argv[2] if len(_sys.argv) > 2 else None)

        case _:
            from .help import show_help

            show_help()
