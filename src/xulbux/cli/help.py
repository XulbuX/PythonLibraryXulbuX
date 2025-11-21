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
        latest_v_parts = tuple(int(part) for part in (latest or "").lower().lstrip("v").split('.'))
        installed_v_parts = tuple(int(part) for part in __version__.lower().lstrip("v").split('.'))
        return latest_v_parts <= installed_v_parts
    except Exception:
        return None


URL = "https://pypi.org/pypi/xulbux/json"
IS_LATEST_VERSION = is_latest_version()
CLR = {
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
HELP = FormatCodes.to_ansi(
    rf"""  [_|b|#7075FF]               __  __
  [b|#7075FF]  _  __ __  __/ / / /_  __  ___  __
  [b|#7075FF] | |/ // / / / / / __ \/ / / | |/ /
  [b|#7075FF] > , </ /_/ / /_/ /_/ / /_/ /> , <
  [b|#7075FF]/_/|_|\____/\__/\____/\____//_/|_|  [*|#000|BG:#8085FF] v[b]{__version__} [*|dim|{CLR['notice']}]({'' if IS_LATEST_VERSION else ' (newer available)'})[*]

  [i|#9095FF]A TON OF COOL FUNCTIONS, YOU NEED![*]

  [b|{CLR['heading']}](Usage:)[*]
  [{CLR['border']}](╭────────────────────────────────────────────────────╮)[*]
  [{CLR['border']}](│) [i|{CLR['punctuator']}](# LIBRARY CONSTANTS)[*]                                [{CLR['border']}](│)[*]
  [{CLR['border']}](│) [{CLR['import']}]from [{CLR['lib']}]xulbux[{CLR['punctuator']}].[{CLR['lib']}]base[{CLR['punctuator']}].[{CLR['lib']}]consts [{CLR['import']}]import [{CLR['const']}]COLOR[{CLR['punctuator']}], [{CLR['const']}]CHARS[{CLR['punctuator']}], [{CLR['const']}]ANSI[*]  [{CLR['border']}](│)[*]
  [{CLR['border']}](│) [i|{CLR['punctuator']}](# Main Classes)[*]                                     [{CLR['border']}](│)[*]
  [{CLR['border']}](│) [{CLR['import']}]from [{CLR['lib']}]xulbux [{CLR['import']}]import [{CLR['class']}]Code[{CLR['punctuator']}], [{CLR['class']}]Color[{CLR['punctuator']}], [{CLR['class']}]Console[{CLR['punctuator']}], ...[*]       [{CLR['border']}](│)[*]
  [{CLR['border']}](│) [i|{CLR['punctuator']}](# module specific imports)[*]                          [{CLR['border']}](│)[*]
  [{CLR['border']}](│) [{CLR['import']}]from [{CLR['lib']}]xulbux[{CLR['punctuator']}].[{CLR['lib']}]color [{CLR['import']}]import [{CLR['func']}]rgba[{CLR['punctuator']}], [{CLR['func']}]hsla[{CLR['punctuator']}], [{CLR['func']}]hexa[*]          [{CLR['border']}](│)
  [{CLR['border']}](╰────────────────────────────────────────────────────╯)[*]
  [b|{CLR['heading']}](Documentation:)[*]
  [{CLR['border']}](╭────────────────────────────────────────────────────╮)[*]
  [{CLR['border']}](│) [{CLR['text']}]For more information see the GitHub page.          [{CLR['border']}](│)[*]
  [{CLR['border']}](│) [{CLR['link']}](https://github.com/XulbuX/PythonLibraryXulbuX/wiki) [{CLR['border']}](│)[*]
  [{CLR['border']}](╰────────────────────────────────────────────────────╯)[*]
  [_]"""
)


def show_help() -> None:
    print(HELP)
    Console.pause_exit(pause=True, prompt="  [dim](Press any key to exit...)\n\n")
