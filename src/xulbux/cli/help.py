from .. import __version__
from .. import console as _console_module
from ..ansi import S, TextRenderable

import json as _json
import urllib.request as _request
from typing import Final

PACKAGE_META_URL: Final[str] = "https://pypi.org/pypi/xulbux/json"
"""URL to fetch the package metadata from PyPI."""


def get_latest_version() -> str | None:
    """Fetches the latest version of the library from PyPI in the format `x.y.z`.\n
    ----------------------------------------------------------------------------------------------------
    Returns `None` if the latest version could not be fetched."""

    with _request.urlopen(PACKAGE_META_URL) as response:
        try:
            return (
                ".".join(clean_version.split("."))
                if (clean_version := (_json.load(response)["info"]["version"] or "").lower().lstrip("v"))
                else None
            )
        except Exception:
            return None


def is_latest_version() -> bool | None:
    """Checks if the currently installed version of the library is the latest one available on PyPI.\n
    ----------------------------------------------------------------------------------------------------
    Returns `None` if the check failed."""

    try:
        if (latest := get_latest_version()) in {"", None}:
            return None

        latest_v_parts = tuple([int(part) for part in (latest or "").lower().lstrip("v").split(".")])
        installed_v_parts = tuple([int(part) for part in __version__.lower().lstrip("v").split(".")])

        return latest_v_parts <= installed_v_parts

    except Exception:
        return None


def show_help() -> None:
    """CLI command function for `xulbux-lib` command,<br>
    which shows some information about the library."""

    # XulbuX colors:
    xx_primary = S.hex("#7075FF")
    xx_secondary = S.hex("#9095FF")

    # Styles used in the help message:
    border_st = S.DIM | S.BR.BLACK
    cmd_st = S.BR.RED
    const_st = S.MAGENTA
    heading_st = S.BOLD | S.BR.WHITE
    import_st = S.BLUE
    lib_st = S.BR.BLUE
    meta_st = S.DIM | S.BR.WHITE
    module_st = S.BR.MAGENTA
    notice_st = S.BR.CYAN
    obj_st = S.BR.CYAN
    punct_st = S.BR.BLACK
    txt_st = S.WHITE

    # The local version of the library:
    version_msg: tuple[TextRenderable, TextRenderable, TextRenderable] = (
        xx_secondary("▄" * (len(__version__) + 7)),
        (S.hex("#000") | xx_secondary.as_bg())("  ✓ v", S.BOLD(__version__), "  "),
        xx_secondary("▀" * (len(__version__) + 7)),
    )

    # fmt:off
    # Attach a notice if the installed version is not the latest one available on PyPI:
    if notice_ver := ver if is_latest_version() is False and (ver := get_latest_version()) else None:
        version_msg = (
            (version_msg[0], (S.DIM | notice_st)("─" * (len(notice_ver) + 15), "╮")),
            (version_msg[1], (notice_st(" ↑ ", S.link("https://pypi.org/pypi/xulbux")("v", S.BOLD(notice_ver)), " available "), (S.DIM | notice_st)("│"))),  # ruff:ignore[line-too-long]
            (version_msg[2], (S.DIM | notice_st)("─" * (len(notice_ver) + 15), "╯")),
        )

    # ruff:ignore[line-too-long]
    S(
        S.RESET,
        (
            "  ", (S.BOLD | xx_primary)("               __  __              "), " \n",
            "  ", (S.BOLD | xx_primary)("  _  __ __  __/ / / /_  __  ___  __"), " \n",
            "  ", (S.BOLD | xx_primary)(" | |/ // / / / / / __ \\/ / / | |/ /"), " \n",
            "  ", (S.BOLD | xx_primary)(" > , </ /_/ / /_/ /_/ / /_/ /> , <"), "  ", version_msg[0], "\n",
            "  ", (S.BOLD | xx_primary)("/_/|_|\\____/\\__/\\____/\\____//_/|_|"), "  ", version_msg[1],
        ),
        ("                                      ", version_msg[2]),
        ("  ", (S.ITALIC | xx_secondary)("Simplify common programming tasks!")),
        "",
        ("  ", heading_st("Commands:")),
        ("  ", border_st("╭─────────────────────────────────────────────────────╮")),
        ("  ", border_st("│ "), cmd_st("xulbux-lib       "), txt_st(" Show library info and usage."), border_st("      │")),
        ("  ", border_st("│ "), cmd_st("xulbux-lib ", S.BOLD("ansi  ")), txt_st(" Preview all possible ANSI styles."), border_st(" │")),
        ("  ", border_st("│ "), cmd_st("xulbux-lib ", S.BOLD("c256  ")), txt_st(" Show a map of all 256 colors."), border_st("     │")),
        ("  ", border_st("│ "), cmd_st("xulbux-lib ", S.BOLD("tc    ")), txt_st(" Show a true-color gradient map."), border_st("   │")),
        ("  ", border_st("╰─────────────────────────────────────────────────────╯")),
        ("  ", heading_st("Usage:")),
        ("  ", border_st("╭─────────────────────────────────────────────────────╮")),
        ("  ", border_st("│ "), punct_st("# ", S.ITALIC("Library Constants")), border_st("                                 │")),
        ("  ", border_st("│ "), import_st("from "), lib_st("xulbux"), (S.DIM | lib_st)("."), lib_st("base"), (S.DIM | lib_st)("."), lib_st("consts "), import_st("import "), const_st("COLOR"), punct_st(", "), const_st("CHARS"), punct_st(", "), const_st("ANSI"), border_st("   │")),
        ("  ", border_st("│ "), punct_st("# ", S.ITALIC("Modules")), border_st("                                           │")),
        ("  ", border_st("│ "), import_st("from "), lib_st("xulbux "), import_st("import "), module_st("ansi"), punct_st(", "), module_st("code"), punct_st(", "), module_st("color"), punct_st(", "), meta_st("..."), border_st("           │")),
        ("  ", border_st("│ "), punct_st("# ", S.ITALIC("Module Specific Imports")), border_st("                           │")),
        ("  ", border_st("│ "), import_st("from "), lib_st("xulbux"), (S.DIM | lib_st)("."), lib_st("color "), import_st("import "), obj_st("rgba"), punct_st(", "), obj_st("hsla"), punct_st(", "), obj_st("hexa"), border_st("           │")),
        ("  ", border_st("╰─────────────────────────────────────────────────────╯")),
        ("  ", heading_st("Documentation:")),
        ("  ", border_st("╭─────────────────────────────────────────────────────╮")),
        ("  ", border_st("│ "), txt_st("For more information see the documentation:"), border_st("         │")),
        ("  ", border_st("│ "), (S.BR.BLUE | S.link("https://xulbux.github.io/python-lib-xulbux/docs"))("xulbux.github.io/python-lib-xulbux/docs"), border_st("             │")),
        ("  ", border_st("╰─────────────────────────────────────────────────────╯")),
        "",
        sep="\n",
    ).print()
    # fmt:on

    _console_module.pause_exit(S("  ", S.DIM("Press any key to exit..."), "\n\n"), pause=True)
