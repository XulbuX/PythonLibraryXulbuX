from .. import __version__
from .. import console as _console_module
from ..ansi import S, TextRenderable

import json as _json
import threading as _threading
import urllib.request as _request
from contextlib import suppress as _suppress
from typing import Final

PACKAGE_META_URL: Final[str] = "https://pypi.org/pypi/xulbux/json"
"""URL to fetch the package metadata from PyPI."""


def get_latest_version(timeout: float = 1.0) -> str | None:
    """Fetches the latest version of the library from PyPI in the format `x.y.z`.\n
    ----------------------------------------------------------------------------------------------------
    *   `timeout` – Maximum duration in seconds to wait for the version check
        before aborting and continuing.\n
    ----------------------------------------------------------------------------------------------------
    Returns `None` if the latest version could not be fetched."""

    result: list[str | None] = [None]

    def _fetch() -> None:
        """Worker function to fetch and parse package metadata in a background thread."""

        with _suppress(Exception), _request.urlopen(PACKAGE_META_URL, timeout=timeout) as response:
            if clean_version := (_json.load(response)["info"]["version"] or "").lower().lstrip("v"):
                result[0] = clean_version

    with _suppress(Exception):
        thread = _threading.Thread(target=_fetch, daemon=True)
        thread.start()
        thread.join(timeout=timeout)

    return result[0]


def is_latest_version(latest_version: str | None = None) -> bool | None:
    """Checks if the currently installed version of the library is the latest one available on PyPI.\n
    ----------------------------------------------------------------------------------------------------
    *   `latest_version` – Optional already fetched latest version
        to avoid duplicate network requests.\n
    ----------------------------------------------------------------------------------------------------
    Returns `None` if the check failed."""

    try:
        if latest_version is None:
            latest_version = get_latest_version()

        if not latest_version:
            return None

        latest_v_parts = tuple([int(part) for part in latest_version.lower().lstrip("v").split(".")])
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
    cmd_st = S.BR.RED
    heading_st = S.BOLD | S.BR.WHITE
    module_st = S.BR.MAGENTA
    notice_st = S.BR.CYAN
    src_st = S.BR.BLUE
    txt_st = S.WHITE

    def _box(*args: TextRenderable) -> S:
        """Helper function to create a help screen box with the given content."""

        return _console_module.box(*args, border_style=S.DIM | S.BR.BLACK, width=58, indent=2, print=False)

    is_latest_ver: bool = bool((latest_ver := get_latest_version()) and is_latest_version(latest_ver))

    # The local version of the library:
    version_msg: tuple[TextRenderable, TextRenderable, TextRenderable] = (
        xx_secondary("▄" * (len(__version__) + (7 if is_latest_ver else 5))),
        (S.hex("#000") | xx_secondary.as_bg())(f"  {'✓ ' if is_latest_ver else ''}v", S.BOLD(__version__), "  "),
        xx_secondary("▀" * (len(__version__) + (7 if is_latest_ver else 5))),
    )

    # fmt:off
    # Attach a notice if the installed version is not the latest one available on PyPI:
    if not is_latest_ver and latest_ver:
        version_msg = (
            (version_msg[0], (S.DIM | notice_st)("─" * (len(latest_ver) + 15), "╮")),
            (version_msg[1], (notice_st(" ↑ ", S.link("https://pypi.org/pypi/xulbux")("v", S.BOLD(latest_ver)), " available "), (S.DIM | notice_st)("│"))),  # ruff:ignore[line-too-long]
            (version_msg[2], (S.DIM | notice_st)("─" * (len(latest_ver) + 15), "╯")),
        )

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
        _box(
            (cmd_st("xulbux-lib        "), txt_st("Show library info and usage.")),
            (cmd_st("xulbux-lib ", S.BOLD("ansi   ")), txt_st("Preview all possible ANSI styles.")),
            (cmd_st("xulbux-lib ", S.BOLD("c256   ")), txt_st("Show a map of all 256 colors.")),
            (cmd_st("xulbux-lib ", S.BOLD("tc     ")), txt_st("Show a true-color gradient map.")),
        ),
        ("  ", heading_st("Modules:")),
        _box(
            (module_st("ansi       "), txt_st("Rich ANSI terminal styling & Term.")),
            (module_st("color      "), txt_st("RGBA, HSLA & HEXA color models.")),
            (module_st("console    "), txt_st("Loggers, boxes, inputs, progress bars.")),
            (module_st("data       "), txt_st("Deep merge, render, path IDs, cleanup.")),
            (module_st("file_sys   "), txt_st("Path resolution & file operations.")),
            (module_st("json       "), txt_st("Comment-aware JSON read/write/update.")),
            (module_st("regex      "), txt_st("Dynamic regex generators & LazyRegex.")),
            (module_st("string     "), txt_st("Casing, indentation, JS detection.")),
            (module_st("system     "), txt_st("Elevation, env paths, dependencies.")),
        ),
        ("  ", heading_st("Resources:")),
        _box(
            (src_st("Docs       "), (txt_st | S.link("https://xulbux.github.io/python-lib-xulbux/docs"))("xulbux.github.io/python-lib-xulbux/docs")),
            (src_st("GitHub     "), (txt_st | S.link("https://github.com/xulbux/python-lib-xulbux"))("github.com/xulbux/python-lib-xulbux")),
            (src_st("PyPI       "), (txt_st | S.link("https://pypi.org/project/xulbux"))("pypi.org/project/xulbux")),
        ),
        "",
        sep="\n",
    ).print()
    # fmt:on

    _console_module.pause_exit(S("  ", S.DIM("Press any key to exit..."), "\n\n"), pause=True)
