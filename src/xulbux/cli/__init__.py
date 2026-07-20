import sys


def main() -> None:
    """Main entry point for the `xulbux-lib` CLI command."""

    match sys.argv[1] if len(sys.argv) > 1 else "":
        case _:
            from .help import show_help

            show_help()
