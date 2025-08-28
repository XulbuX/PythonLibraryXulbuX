from .. import __version__
from ..base.consts import COLOR
from ..format_codes import FormatCodes
from ..console import Console


CLR = {
    "class": COLOR.TANGERINE,
    "const": COLOR.RED,
    "func": COLOR.CYAN,
    "import": COLOR.NEON_GREEN,
    "lib": COLOR.ORANGE,
    "punctuators": COLOR.DARK_GRAY,
    "code_border": COLOR.GRAY,
}
HELP = FormatCodes.to_ansi(
    rf"""  [_|b|#7075FF]               __  __
  [b|#7075FF]  _  __ __  __/ / / /_  __  ___  __
  [b|#7075FF] | |/ // / / / / / __ \/ / / | |/ /
  [b|#7075FF] > , </ /_/ / /_/ /_/ / /_/ /> , <
  [b|#7075FF]/_/|_|\____/\__/\____/\____//_/|_|  [*|BG:{COLOR.GRAY}|#000] v[b]{__version__} [*]

  [i|{COLOR.CORAL}]A TON OF COOL FUNCTIONS, YOU NEED![*]

  [b|#FCFCFF]Usage:[*]
  [dim|{CLR['code_border']}](╭────────────────────────────────────────────────────╮)
  [dim|{CLR['code_border']}](│) [{CLR['punctuators']}]# LIBRARY CONSTANTS[*]                                [dim|{CLR['code_border']}](│)
  [dim|{CLR['code_border']}](│) [{CLR['import']}]from [{CLR['lib']}]xulbux[{CLR['punctuators']}].[{CLR['lib']}]base[{CLR['punctuators']}].[{CLR['lib']}]consts [{CLR['import']}]import [{CLR['const']}]COLOR[{CLR['punctuators']}], [{CLR['const']}]CHARS[{CLR['punctuators']}], [{CLR['const']}]ANSI[*]  [dim|{CLR['code_border']}](│)
  [dim|{CLR['code_border']}](│) [{CLR['punctuators']}]# Main Classes[*]                                     [dim|{CLR['code_border']}](│)
  [dim|{CLR['code_border']}](│) [{CLR['import']}]from [{CLR['lib']}]xulbux [{CLR['import']}]import [{CLR['class']}]Code[{CLR['punctuators']}], [{CLR['class']}]Color[{CLR['punctuators']}], [{CLR['class']}]Console[{CLR['punctuators']}], ...[*]       [dim|{CLR['code_border']}](│)
  [dim|{CLR['code_border']}](│) [{CLR['punctuators']}]# module specific imports[*]                          [dim|{CLR['code_border']}](│)
  [dim|{CLR['code_border']}](│) [{CLR['import']}]from [{CLR['lib']}]xulbux[{CLR['punctuators']}].[{CLR['lib']}]color [{CLR['import']}]import [{CLR['func']}]rgba[{CLR['punctuators']}], [{CLR['func']}]hsla[{CLR['punctuators']}], [{CLR['func']}]hexa[*]          [dim|{CLR['code_border']}](│)
  [dim|{CLR['code_border']}](╰────────────────────────────────────────────────────╯)
  [b|#FCFCFF]Documentation:[*]
  [dim|{CLR['code_border']}](╭────────────────────────────────────────────────────╮)
  [dim|{CLR['code_border']}](│) [#DADADD]For more information see the GitHub page.          [dim|{CLR['code_border']}](│)
  [dim|{CLR['code_border']}](│) [u|#8085FF](https://github.com/XulbuX/PythonLibraryXulbuX/wiki) [dim|{CLR['code_border']}](│)
  [dim|{CLR['code_border']}](╰────────────────────────────────────────────────────╯)
  [_]"""
)


def show_help() -> None:
    print(HELP)
    Console.pause_exit(pause=True, prompt="  [dim](Press any key to exit...)\n\n")
