from .. import __version__
from ..depr_format_codes import deprFormatCodes
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

CLI_COLORS = {
    "border": "dim|br:black",
    "class": "br:cyan",
    "cmd": "green",
    "const": "br:blue",
    "fn": "br:green",
    "heading": "br:white",
    "import": "magenta",
    "lib": "br:magenta",
    "link": "br:blue",
    "notice": "br:yellow",
    "punctuator": "br:black",
    "text": "white",
}
CLI_HELP = deprFormatCodes.to_ansi(
    rf"""[_]
  [b|#7075FF]               __  __
  [b|#7075FF]  _  __ __  __/ / / /_  __  ___  __
  [b|#7075FF] | |/ // / / / / / __ \/ / / | |/ /
  [b|#7075FF] > , </ /_/ / /_/ /_/ / /_/ /> , <
  [b|#7075FF]/_/|_|\____/\__/\____/\____//_/|_|  [*|#000|BG:#8085FF] v[b]{__version__} [*|dim|{CLI_COLORS["notice"]}]({"" if IS_LATEST_VERSION else " (newer available)"})[*]

  [i|#9095FF]Simplify common programming tasks![*]

  [b|{CLI_COLORS["heading"]}](Commands:)[*]
  [{CLI_COLORS["border"]}](╭───────────────────────────────────────────────────╮)[*]
  [{CLI_COLORS["border"]}](│) [{CLI_COLORS["cmd"]}]xulbux-lib[*]       [{CLI_COLORS["text"]}]Show library info and usage[*]      [{CLI_COLORS["border"]}](│)[*]
  [{CLI_COLORS["border"]}](│) [{CLI_COLORS["cmd"]}]xulbux-lib [b|{CLI_COLORS["fn"]}](fc)    [{CLI_COLORS["text"]}]Render a string's format codes[*]   [{CLI_COLORS["border"]}](│)[*]
  [{CLI_COLORS["border"]}](╰───────────────────────────────────────────────────╯)[*]
  [b|{CLI_COLORS["heading"]}](Usage:)[*]
  [{CLI_COLORS["border"]}](╭───────────────────────────────────────────────────╮)[*]
  [{CLI_COLORS["border"]}](│) [i|{CLI_COLORS["punctuator"]}](# LIBRARY CONSTANTS)[*]                               [{CLI_COLORS["border"]}](│)[*]
  [{CLI_COLORS["border"]}](│) [{CLI_COLORS["import"]}]from [{CLI_COLORS["lib"]}]xulbux[{CLI_COLORS["punctuator"]}].[{CLI_COLORS["lib"]}]base[{CLI_COLORS["punctuator"]}].[{CLI_COLORS["lib"]}]consts [{CLI_COLORS["import"]}]import [{CLI_COLORS["const"]}]COLOR[{CLI_COLORS["punctuator"]}], [{CLI_COLORS["const"]}]CHARS[{CLI_COLORS["punctuator"]}], [{CLI_COLORS["const"]}]ANSI[*] [{CLI_COLORS["border"]}](│)[*]
  [{CLI_COLORS["border"]}](│) [i|{CLI_COLORS["punctuator"]}](# Main Classes)[*]                                    [{CLI_COLORS["border"]}](│)[*]
  [{CLI_COLORS["border"]}](│) [{CLI_COLORS["import"]}]from [{CLI_COLORS["lib"]}]xulbux [{CLI_COLORS["import"]}]import [{CLI_COLORS["class"]}]Code[{CLI_COLORS["punctuator"]}], [{CLI_COLORS["class"]}]Color[{CLI_COLORS["punctuator"]}], [{CLI_COLORS["class"]}]Console[{CLI_COLORS["punctuator"]}], ...[*]      [{CLI_COLORS["border"]}](│)[*]
  [{CLI_COLORS["border"]}](│) [i|{CLI_COLORS["punctuator"]}](# module specific imports)[*]                         [{CLI_COLORS["border"]}](│)[*]
  [{CLI_COLORS["border"]}](│) [{CLI_COLORS["import"]}]from [{CLI_COLORS["lib"]}]xulbux[{CLI_COLORS["punctuator"]}].[{CLI_COLORS["lib"]}]color [{CLI_COLORS["import"]}]import [{CLI_COLORS["fn"]}]rgba[{CLI_COLORS["punctuator"]}], [{CLI_COLORS["fn"]}]hsla[{CLI_COLORS["punctuator"]}], [{CLI_COLORS["fn"]}]hexa[*]         [{CLI_COLORS["border"]}](│)
  [{CLI_COLORS["border"]}](╰───────────────────────────────────────────────────╯)[*]
  [b|{CLI_COLORS["heading"]}](Documentation:)[*]
  [{CLI_COLORS["border"]}](╭───────────────────────────────────────────────────╮)[*]
  [{CLI_COLORS["border"]}](│) [{CLI_COLORS["text"]}]For more information see the GitHub wiki page:    [{CLI_COLORS["border"]}](│)[*]
  [{CLI_COLORS["border"]}](│) [{CLI_COLORS["link"]}|link:https://github.com/xulbux/python-lib-xulbux/wiki](github.com/xulbux/python-lib-xulbux/wiki)          [{CLI_COLORS["border"]}](│)[*]
  [{CLI_COLORS["border"]}](╰───────────────────────────────────────────────────╯)[*]
  [_]"""
)


def show_help() -> None:
    """CLI command function for `xulbux-lib` command,<br>
    which shows some information about the library."""

    deprFormatCodes._config_terminal()
    print(CLI_HELP)
    Console.pause_exit("  [dim](Press any key to exit...)\n\n", pause=True)
