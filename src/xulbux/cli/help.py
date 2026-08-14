from .. import __version__
from .. import console as _console_module
from ..ansi import S, StyledText, _Style, _StyleGroup
from ..base.decorators import mypyc_attr

import json as _json
import urllib.request as _request
from typing import Final
from urllib.error import HTTPError


def get_latest_version() -> str | None:
    """Fetches the latest version of the library from PyPI.\n
    Raises a `HTTPError` if the request fails.\n
    Returns `None` if the request succeeds but the version info is not found."""

    with _request.urlopen(PACKAGE_META_URL) as response:
        if response.status == 200:
            try:
                return _json.load(response)["info"]["version"]
            except Exception:
                return None
        else:
            raise HTTPError(PACKAGE_META_URL, response.status, "Failed to fetch latest version info", response.headers, None)


def is_latest_version() -> bool | None:
    """Checks if the currently installed version of the library is the latest one available on PyPI.\n
    Returns `None` if the check failed."""

    try:
        if (latest := get_latest_version()) in {"", None}:
            return None

        latest_v_parts = tuple(int(part) for part in (latest or "").lower().lstrip("v").split("."))
        installed_v_parts = tuple(int(part) for part in __version__.lower().lstrip("v").split("."))

        return latest_v_parts <= installed_v_parts

    except Exception:
        return None


PACKAGE_META_URL: Final[str] = "https://pypi.org/pypi/xulbux/json"
"""URL to fetch the package metadata from PyPI."""
IS_LATEST_VERSION: bool | None = is_latest_version()
"""Whether the currently installed version is the latest one<br>
available on PyPI or not. `None` if the check failed."""


@mypyc_attr(native_class=False)
class H:
    """Styling constants for the CLI help message."""

    BORDER: _StyleGroup = S.DIM | S.BR.BLACK
    """Styling for the borders in the CLI help message."""
    CLS: _Style = S.BR.CYAN
    """Styling for class names in the CLI help message."""
    CMD: _Style = S.GREEN
    """Styling for command names in the CLI help message."""
    CONST: _Style = S.BR.BLUE
    """Styling for constant names in the CLI help message."""
    FN: _Style = S.BR.GREEN
    """Styling for function names in the CLI help message."""
    HEADING: _StyleGroup = S.BOLD | S.BR.WHITE
    """Styling for headings in the CLI help message."""
    IMPORT: _Style = S.MAGENTA
    """Styling for import statements in the CLI help message."""
    LIB: _Style = S.BR.MAGENTA
    """Styling for library names in the CLI help message."""
    META: _StyleGroup = S.DIM | S.BR.WHITE
    """Styling for meta information in the CLI help message."""
    PUNCT: _Style = S.BR.BLACK
    """Styling for punctuation in the CLI help message."""
    TEXT: _Style = S.WHITE
    """Styling for regular text in the CLI help message."""


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
    (H.BORDER("  │ "), H.IMPORT("from "), H.LIB("xulbux"), (S.DIM | H.LIB)("."), H.LIB("base"), (S.DIM | H.LIB)("."), H.LIB("consts "), H.IMPORT("import "), H.CONST("COLOR"), H.PUNCT(", "), H.CONST("CHARS"), H.PUNCT(", "), H.CONST("ANSI "), H.BORDER("│")),  # ruff:ignore[line-too-long]
    (H.BORDER("  │ "), H.PUNCT("# ", S.ITALIC("Main Classes                                    ")), H.BORDER("│")),
    (H.BORDER("  │ "), H.IMPORT("from "), H.LIB("xulbux "), H.IMPORT("import "), H.CLS("code"), H.PUNCT(", "), H.CLS("color"), H.PUNCT(", "), H.CLS("console"), H.PUNCT(", "), H.META("...      "), H.BORDER("│")),  # ruff:ignore[line-too-long]
    (H.BORDER("  │ "), H.PUNCT("# ", S.ITALIC("module specific imports                         ")), H.BORDER("│")),
    (H.BORDER("  │ "), H.IMPORT("from "), H.LIB("xulbux"), (S.DIM | H.LIB)("."), H.LIB("color "), H.IMPORT("import "), H.FN("rgba"), H.PUNCT(", "), H.FN("hsla"), H.PUNCT(", "), H.FN("hexa         "), H.BORDER("│")),  # ruff:ignore[line-too-long]
    H.BORDER("  ╰───────────────────────────────────────────────────╯"),
    H.HEADING("  Documentation:"),
    H.BORDER("  ╭───────────────────────────────────────────────────╮"),
    (H.BORDER("  │ "), H.TEXT("For more information see the documentation:    "), H.BORDER("│")),
    (H.BORDER("  │ "), (S.BR.BLUE | S.link("https://xulbux.github.io/python-lib-xulbux/docs"))("github.com/xulbux/python-lib-xulbux/wiki"), "          ", H.BORDER("│")),  # ruff:ignore[line-too-long]
    H.BORDER("  ╰───────────────────────────────────────────────────╯"),
    "",
    sep="\n",
)
"""The help message for the CLI command `xulbux-lib` as a `StyledText` object."""
# fmt: on


def show_help() -> None:
    """CLI command function for `xulbux-lib` command,<br>
    which shows some information about the library."""

    CLI_HELP.print()
    _console_module.pause_exit("  [dim](Press any key to exit...)\n\n", pause=True)
