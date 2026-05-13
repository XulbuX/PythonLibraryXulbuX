from ..format_codes import FormatCodes
from ..console import Console


def render_format_codes():
    """CLI command function for `xulbux-lib fc` command, which allows you to parse<br>
    and render a given string's format codes as ANSI terminal output."""

    args = Console.get_args({"input": "before"}, skip=1)
    vals = args.input.values

    if not vals:
        FormatCodes.print(
            "\n[_|i|dim]Provide a string to parse and render\n"
            "its format codes as ANSI terminal output.[_]\n"
        )

    else:
        ansi = FormatCodes.to_ansi("".join(vals))
        ansi_escaped = FormatCodes.escape_ansi(ansi)
        ansi_stripped = FormatCodes.remove_ansi(ansi)

        print(f"\n{ansi}\n")

        if len(ansi) != len(ansi_stripped):
            FormatCodes.print(f"[_|i|dim]{ansi_escaped}[_]\n")
        else:
            FormatCodes.print("[_|i|dim](The provided string doesn't contain any valid format codes.)\n")
