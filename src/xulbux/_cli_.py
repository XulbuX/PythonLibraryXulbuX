from . import __version__
from .base.consts import COLOR
from .format_codes import FormatCodes
from .console import Console


def help_command():
    """Show some info about the library, with a brief explanation of how to use it."""
    color = {
        "class": COLOR.tangerine,
        "const": COLOR.red,
        "func": COLOR.cyan,
        "import": COLOR.neongreen,
        "lib": COLOR.orange,
        "punctuators": COLOR.darkgray,
        "code_border": COLOR.gray,
    }
    FormatCodes.print(
        rf"""  [_|b|#7075FF]               __  __
  [b|#7075FF]  _  __ __  __/ / / /_  __  ___  __
  [b|#7075FF] | |/ // / / / / / __ \/ / / | |/ /
  [b|#7075FF] > , </ /_/ / /_/ /_/ / /_/ /> , <
  [b|#7075FF]/_/|_|\____/\__/\____/\____//_/|_|  [*|BG:{COLOR.gray}|#000] v[b]{__version__} [*]

  [i|{COLOR.coral}]A TON OF COOL FUNCTIONS, YOU NEED![*]

  [b|#FCFCFF]Usage:[*]
  [dim|{color['code_border']}](╭────────────────────────────────────────────────────╮)
  [dim|{color['code_border']}](│) [{color['punctuators']}]# CONSTANTS[*]                                        [dim|{color['code_border']}](│)
  [dim|{color['code_border']}](│) [{color['import']}]from [{color['lib']}]xulbux [{color['import']}]import [{color['const']}]COLOR[{color['punctuators']}], [{color['const']}]CHARS[{color['punctuators']}], [{color['const']}]ANSI[*]              [dim|{color['code_border']}](│)
  [dim|{color['code_border']}](│) [{color['punctuators']}]# Classes[*]                                          [dim|{color['code_border']}](│)
  [dim|{color['code_border']}](│) [{color['import']}]from [{color['lib']}]xulbux [{color['import']}]import [{color['class']}]Code[{color['punctuators']}], [{color['class']}]Color[{color['punctuators']}], [{color['class']}]Console[{color['punctuators']}], ...[*]       [dim|{color['code_border']}](│)
  [dim|{color['code_border']}](│) [{color['punctuators']}]# types[*]                                            [dim|{color['code_border']}](│)
  [dim|{color['code_border']}](│) [{color['import']}]from [{color['lib']}]xulbux [{color['import']}]import [{color['func']}]rgba[{color['punctuators']}], [{color['func']}]hsla[{color['punctuators']}], [{color['func']}]hexa[*]                [dim|{color['code_border']}](│)
  [dim|{color['code_border']}](╰────────────────────────────────────────────────────╯)
  [b|#FCFCFF]Documentation:[*]
  [dim|{color['code_border']}](╭────────────────────────────────────────────────────╮)
  [dim|{color['code_border']}](│) [#DADADD]For more information see the GitHub page.          [dim|{color['code_border']}](│)
  [dim|{color['code_border']}](│) [u|#8085FF](https://github.com/XulbuX/PythonLibraryXulbuX/wiki) [dim|{color['code_border']}](│)
  [dim|{color['code_border']}](╰────────────────────────────────────────────────────╯)
  [_]
  [dim](Press any key to exit...)
  """,
        default_color=COLOR.text
    )
    Console.pause_exit(pause=True)
