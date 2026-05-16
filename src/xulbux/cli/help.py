from .. import __version__
from ..base.decorators import mypyc_attr
from ..format_codes import FC, F
from ..console import Console

from urllib.error import HTTPError
from typing import Optional
import urllib.request as _request
import json as _json


def get_latest_version() -> Optional[str]:
    """Fetches the latest version of the library from PyPI."""

    with _request.urlopen(URL) as response:
        if response.status == 200:
            return _json.load(response)["info"]["version"]
        else:
            raise HTTPError(URL, response.status, "Failed to fetch latest version info", response.headers, None)


def is_latest_version() -> Optional[bool]:
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


URL = "https://pypi.org/pypi/xulbux/json"
IS_LATEST_VERSION = is_latest_version()


@mypyc_attr(native_class=False)
class S:
    """Styling constants for the CLI help message."""

    BORDER = F.DIM | F.BR.BLACK
    CLS = F.BR.CYAN
    CMD = F.GREEN
    CONST = F.BR.BLUE
    FN = F.BR.GREEN
    HEADING = F.BOLD | F.BR.WHITE
    IMPORT = F.MAGENTA
    LIB = F.BR.MAGENTA
    META = F.DIM | F.BR.WHITE
    PUNCT = F.BR.BLACK
    TEXT = F.WHITE


# fmt: OFF
CLI_HELP = FC(
    F.RESET,
    (
        (F.BOLD | F.hex("#7075FF"))(
            "                 __  __              \n"
            "    _  __ __  __/ / / /_  __  ___  __\n"
            "   | |/ // / / / / / __ \\/ / / | |/ /\n"
            "   > , </ /_/ / /_/ /_/ / /_/ /> , < \n"
            "  /_/|_|\\____/\\__/\\____/\\____//_/|_|  ",
            (F.hex("#000") | F.BG.hex("#8085FF"))(f" v{__version__} "),
        ),
        "" if IS_LATEST_VERSION else (F.DIM | F.YELLOW)(" (", F.ITALIC("newer available"), ")"),
    ),
    "",
    (F.ITALIC | F.hex("#9095FF"))("  Simplify common programming tasks!"),
    "",
    S.HEADING("  Commands:"),
    S.BORDER("  ╭───────────────────────────────────────────────────╮"),
    (S.BORDER("  │ "), S.CMD("xulbux-lib      "), S.TEXT("Show library info and usage       "), S.BORDER("│")),
    S.BORDER("  ╰───────────────────────────────────────────────────╯"),
    S.HEADING("  Usage:"),
    S.BORDER("  ╭───────────────────────────────────────────────────╮"),
    (S.BORDER("  │ "), S.PUNCT("# ", F.ITALIC("LIBRARY CONSTANTS                               ")), S.BORDER("│")),
    (S.BORDER("  │ "), S.IMPORT("from "), S.LIB("xulbux"), (F.DIM | S.LIB)("."), S.LIB("base"), (F.DIM | S.LIB)("."), S.LIB("consts "), S.IMPORT("import "), S.CONST("COLOR"), S.PUNCT(", "), S.CONST("CHARS"), S.PUNCT(", "), S.CONST("ANSI "), S.BORDER("│")),
    (S.BORDER("  │ "), S.PUNCT("# ", F.ITALIC("Main Classes                                    ")), S.BORDER("│")),
    (S.BORDER("  │ "), S.IMPORT("from "), S.LIB("xulbux "), S.IMPORT("import "), S.CLS("Code"), S.PUNCT(", "), S.CLS("Color"), S.PUNCT(", "), S.CLS("Console"), S.PUNCT(", "), S.META("...      "), S.BORDER("│")),
    (S.BORDER("  │ "), S.PUNCT("# ", F.ITALIC("module specific imports                         ")), S.BORDER("│")),
    (S.BORDER("  │ "), S.IMPORT("from "), S.LIB("xulbux"), (F.DIM | S.LIB)("."), S.LIB("color "), S.IMPORT("import "), S.FN("rgba"), S.PUNCT(", "), S.FN("hsla"), S.PUNCT(", "), S.FN("hexa         "), S.BORDER("│")),
    S.BORDER("  ╰───────────────────────────────────────────────────╯"),
    S.HEADING("  Documentation:"),
    S.BORDER("  ╭───────────────────────────────────────────────────╮"),
    (S.BORDER("  │ "), S.TEXT("For more information see the GitHub wiki page:    "), S.BORDER("│")),
    (S.BORDER("  │ "), (F.BR.BLUE | F.link("https://github.com/xulbux/python-lib-xulbux/wiki"))("github.com/xulbux/python-lib-xulbux/wiki"), "          ", S.BORDER("│")),
    S.BORDER("  ╰───────────────────────────────────────────────────╯"),
    "",
)
# fmt: ON


def show_help() -> None:
    """CLI command function for `xulbux-lib` command,<br>
    which shows some information about the library."""

    CLI_HELP.print()
    Console.pause_exit("  [dim](Press any key to exit...)\n\n", pause=True)
