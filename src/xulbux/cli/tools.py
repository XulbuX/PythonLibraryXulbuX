from ..depr_format_codes import deprFormatCodes
from ..console import Console


def render_format_codes():
    """CLI command function for `xulbux-lib fc` command, which allows you to parse<br>
    and render a given string's format codes as ANSI terminal output."""

    args = Console.get_args({"input": "before"}, skip=1)
    vals = args.input.values

    if not vals:
        deprFormatCodes.print(
            "\n[_|i|dim]Provide a string to parse and render\n"
            "its format codes as ANSI terminal output.[_]\n"
        )

    else:
        ansi = deprFormatCodes.to_ansi("".join(vals))
        ansi_escaped = deprFormatCodes.escape_ansi(ansi)
        ansi_stripped = deprFormatCodes.remove_ansi(ansi)

        print(f"\n{ansi}\n")

        if len(ansi) != len(ansi_stripped):
            deprFormatCodes.print(f"[_|i|dim]{ansi_escaped}[_]\n")
        else:
            deprFormatCodes.print("[_|i|dim](The provided string doesn't contain any valid format codes.)\n")
