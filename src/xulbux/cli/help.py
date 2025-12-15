from .. import __version__
from ..format_codes import FormatCodes
from ..console import Console

from urllib.error import HTTPError
from typing import Optional
import urllib.request as _request
import json as _json


def get_latest_version() -> Optional[str]:
    with _request.urlopen(URL) as response:
        if response.status == 200:
            data = _json.load(response)
            return data["info"]["version"]
        else:
            raise HTTPError(URL, response.status, "Failed to fetch latest version info", response.headers, None)


def is_latest_version() -> Optional[bool]:
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
    "const": "br:blue",
    "func": "br:green",
    "heading": "br:white",
    "import": "magenta",
    "lib": "br:magenta",
    "link": "u|br:blue",
    "notice": "br:yellow",
    "punctuator": "br:black",
    "text": "white",
}
CLI_HELP = FormatCodes.to_ansi(
    rf"""  [_|b|#7075FF]               __  __
  [b|#7075FF]  _  __ __  __/ / / /_  __  ___  __
  [b|#7075FF] | |/ // / / / / / __ \/ / / | |/ /
  [b|#7075FF] > , </ /_/ / /_/ /_/ / /_/ /> , <
  [b|#7075FF]/_/|_|\____/\__/\____/\____//_/|_|  [*|#000|BG:#8085FF] v[b]{__version__} [*|dim|{CLI_COLORS["notice"]}]({"" if IS_LATEST_VERSION else " (newer available)"})[*]

  [i|#9095FF]A TON OF COOL FUNCTIONS, YOU NEED![*]

  [b|{CLI_COLORS["heading"]}](Usage:)[*]
  [{CLI_COLORS["border"]}](╭────────────────────────────────────────────────────╮)[*]
  [{CLI_COLORS["border"]}](│) [i|{CLI_COLORS["punctuator"]}](# LIBRARY CONSTANTS)[*]                                [{CLI_COLORS["border"]}](│)[*]
  [{CLI_COLORS["border"]}](│) [{CLI_COLORS["import"]}]from [{CLI_COLORS["lib"]}]xulbux[{CLI_COLORS["punctuator"]}].[{CLI_COLORS["lib"]}]base[{CLI_COLORS["punctuator"]}].[{CLI_COLORS["lib"]}]consts [{CLI_COLORS["import"]}]import [{CLI_COLORS["const"]}]COLOR[{CLI_COLORS["punctuator"]}], [{CLI_COLORS["const"]}]CHARS[{CLI_COLORS["punctuator"]}], [{CLI_COLORS["const"]}]ANSI[*]  [{CLI_COLORS["border"]}](│)[*]
  [{CLI_COLORS["border"]}](│) [i|{CLI_COLORS["punctuator"]}](# Main Classes)[*]                                     [{CLI_COLORS["border"]}](│)[*]
  [{CLI_COLORS["border"]}](│) [{CLI_COLORS["import"]}]from [{CLI_COLORS["lib"]}]xulbux [{CLI_COLORS["import"]}]import [{CLI_COLORS["class"]}]Code[{CLI_COLORS["punctuator"]}], [{CLI_COLORS["class"]}]Color[{CLI_COLORS["punctuator"]}], [{CLI_COLORS["class"]}]Console[{CLI_COLORS["punctuator"]}], ...[*]       [{CLI_COLORS["border"]}](│)[*]
  [{CLI_COLORS["border"]}](│) [i|{CLI_COLORS["punctuator"]}](# module specific imports)[*]                          [{CLI_COLORS["border"]}](│)[*]
  [{CLI_COLORS["border"]}](│) [{CLI_COLORS["import"]}]from [{CLI_COLORS["lib"]}]xulbux[{CLI_COLORS["punctuator"]}].[{CLI_COLORS["lib"]}]color [{CLI_COLORS["import"]}]import [{CLI_COLORS["func"]}]rgba[{CLI_COLORS["punctuator"]}], [{CLI_COLORS["func"]}]hsla[{CLI_COLORS["punctuator"]}], [{CLI_COLORS["func"]}]hexa[*]          [{CLI_COLORS["border"]}](│)
  [{CLI_COLORS["border"]}](╰────────────────────────────────────────────────────╯)[*]
  [b|{CLI_COLORS["heading"]}](Documentation:)[*]
  [{CLI_COLORS["border"]}](╭────────────────────────────────────────────────────╮)[*]
  [{CLI_COLORS["border"]}](│) [{CLI_COLORS["text"]}]For more information see the GitHub page.          [{CLI_COLORS["border"]}](│)[*]
  [{CLI_COLORS["border"]}](│) [{CLI_COLORS["link"]}](https://github.com/XulbuX/PythonLibraryXulbuX/wiki) [{CLI_COLORS["border"]}](│)[*]
  [{CLI_COLORS["border"]}](╰────────────────────────────────────────────────────╯)[*]
  [_]"""
)


def show_help() -> None:
    FormatCodes._config_console()
    print(CLI_HELP)
    Console.pause_exit(pause=True, prompt="  [dim](Press any key to exit...)\n\n")
