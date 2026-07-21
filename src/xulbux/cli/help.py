# ruff: noqa: E501

from .. import __version__
from .. import console as _console_module
from ..ansi import S, StyledText, _Style, _StyleGroup
from ..base.decorators import mypyc_attr

import json as _json
import urllib.request as _request
from typing import Final
from urllib.error import HTTPError


def get_latest_version() -> str | None:
    """Fetches the latest version of the library from PyPI."""

    with _request.urlopen(PACKAGE_META_URL) as response:
        if response.status == 200:
            return _json.load(response)["info"]["version"]
        else:
            raise HTTPError(PACKAGE_META_URL, response.status, "Failed to fetch latest version info", response.headers, None)


def is_latest_version() -> bool | None:
    """Checks if the currently installed version of the<br>
    library is the latest one available on PyPI."""

    try:
        if (latest := get_latest_version()) in {"", None}:
            return None

        latest_v_parts = tuple(int(part) for part in (latest or "").lower().lstrip("v").split("."))
        installed_v_parts = tuple(int(part) for part in __version__.lower().lstrip("v").split("."))

        return latest_v_parts <= installed_v_parts

    except Exception:
        return None


PACKAGE_META_URL: Final[str] = "https://pypi.org/pypi/xulbux/json"
IS_LATEST_VERSION: bool | None = is_latest_version()


@mypyc_attr(native_class=False)
class H:
    """Styling constants for the CLI help message."""

    BORDER: _StyleGroup = S.DIM | S.BR.BLACK
    CLS: _Style = S.BR.CYAN
    CMD: _Style = S.GREEN
    CONST: _Style = S.BR.BLUE
    FN: _Style = S.BR.GREEN
    HEADING: _StyleGroup = S.BOLD | S.BR.WHITE
    IMPORT: _Style = S.MAGENTA
    LIB: _Style = S.BR.MAGENTA
    META: _StyleGroup = S.DIM | S.BR.WHITE
    PUNCT: _Style = S.BR.BLACK
    TEXT: _Style = S.WHITE


# fmt: off
CLI_HELP: Final[StyledText] = StyledText(
    S.RESET,
    (
        (S.BOLD | S.hex("#7075FF"))(
            "                 __  __              \n"
            "    _  __ __  __/ / / /_  __  ___  __\n"
            "   | |/ // / / / / / __ \\/ / / | |/ /\n"
            "   > , </ /_/ / /_/ /_/ / /_/ /> , < \n"
            "  /_/|_|\\____/\\__/\\____/\\____//_/|_|  ",
            (S.hex("#000") | S.BG.hex("#8085FF"))(f" v{__version__} "),
        ),
        "" if IS_LATEST_VERSION else (S.DIM | S.YELLOW)(" (", S.ITALIC("newer available"), ")"),
    ),
    "",
    (S.ITALIC | S.hex("#9095FF"))("  Simplify common programming tasks!"),
    "",
    H.HEADING("  Commands:"),
    H.BORDER("  ╭───────────────────────────────────────────────────╮"),
    (H.BORDER("  │ "), H.CMD("xulbux-lib      "), H.TEXT("Show library info and usage       "), H.BORDER("│")),
    H.BORDER("  ╰───────────────────────────────────────────────────╯"),
    H.HEADING("  Usage:"),
    H.BORDER("  ╭───────────────────────────────────────────────────╮"),
    (H.BORDER("  │ "), H.PUNCT("# ", S.ITALIC("LIBRARY CONSTANTS                               ")), H.BORDER("│")),
    (H.BORDER("  │ "), H.IMPORT("from "), H.LIB("xulbux"), (S.DIM | H.LIB)("."), H.LIB("base"), (S.DIM | H.LIB)("."), H.LIB("consts "), H.IMPORT("import "), H.CONST("COLOR"), H.PUNCT(", "), H.CONST("CHARS"), H.PUNCT(", "), H.CONST("ANSI "), H.BORDER("│")),
    (H.BORDER("  │ "), H.PUNCT("# ", S.ITALIC("Main Classes                                    ")), H.BORDER("│")),
    (H.BORDER("  │ "), H.IMPORT("from "), H.LIB("xulbux "), H.IMPORT("import "), H.CLS("code"), H.PUNCT(", "), H.CLS("color"), H.PUNCT(", "), H.CLS("console"), H.PUNCT(", "), H.META("...      "), H.BORDER("│")),
    (H.BORDER("  │ "), H.PUNCT("# ", S.ITALIC("module specific imports                         ")), H.BORDER("│")),
    (H.BORDER("  │ "), H.IMPORT("from "), H.LIB("xulbux"), (S.DIM | H.LIB)("."), H.LIB("color "), H.IMPORT("import "), H.FN("rgba"), H.PUNCT(", "), H.FN("hsla"), H.PUNCT(", "), H.FN("hexa         "), H.BORDER("│")),
    H.BORDER("  ╰───────────────────────────────────────────────────╯"),
    H.HEADING("  Documentation:"),
    H.BORDER("  ╭───────────────────────────────────────────────────╮"),
    (H.BORDER("  │ "), H.TEXT("For more information see the GitHub wiki page:    "), H.BORDER("│")),
    (H.BORDER("  │ "), (S.BR.BLUE | S.link("https://github.com/xulbux/python-lib-xulbux/wiki"))("github.com/xulbux/python-lib-xulbux/wiki"), "          ", H.BORDER("│")),
    H.BORDER("  ╰───────────────────────────────────────────────────╯"),
    "",
    sep="\n",
)
# fmt: on


def show_help() -> None:
    """CLI command function for `xulbux-lib` command,<br>
    which shows some information about the library."""

    CLI_HELP.print()
    _console_module.pause_exit("  [dim](Press any key to exit...)\n\n", pause=True)
