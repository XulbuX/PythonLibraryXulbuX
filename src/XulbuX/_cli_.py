from . import __version__
from ._consts_ import DEFAULT
from .xx_format_codes import *
from .xx_cmd import *


def help_command():
    """Show some info about the library, with a brief explanation of how to use it."""
    color = {
        "lib": DEFAULT.color["ice"],
        "import": DEFAULT.color["red"],
        "class": DEFAULT.color["lavender"],
        "types": DEFAULT.color["lightblue"],
        "punctuators": DEFAULT.color["darkgray"],
    }
    FormatCodes.print(
        rf"""  [_|b|#7075FF]               __  __              
  [b|#7075FF]  _  __ __  __/ / / /_  __  ___  __
  [b|#7075FF] | |/ // / / / / / __ \/ / / | |/ /
  [b|#7075FF] > , </ /_/ / /_/ /_/ / /_/ /> , < 
  [b|#7075FF]/_/|_|\____/\__/\____/\____//_/|_|  [*|BG:{DEFAULT.color['gray']}|#000] v[b]{__version__} [*]

  [i|{DEFAULT.color['coral']}]A TON OF COOL FUNCTIONS, YOU NEED![*]

  [b|#75A2FF]Usage:[*]
    [{color['punctuators']}]# GENERAL LIBRARY[*]
    [{color['import']}]import [{color['lib']}]XulbuX [{color['import']}]as [{color['lib']}]xx[*]
    [{color['punctuators']}]# CUSTOM TYPES[*]
    [{color['import']}]from [{color['lib']}]XulbuX [{color['import']}]import [{color['lib']}]rgba[{color['punctuators']}], [{color['lib']}]hsla[{color['punctuators']}], [{color['lib']}]hexa[*]

  [b|#75A2FF]Includes:[*]
    [dim](•) CUSTOM TYPES:
       [dim](•) [{color['class']}]rgba[{color['punctuators']}]/([i|{color['types']}]int[_|{color['punctuators']}],[i|{color['types']}]int[_|{color['punctuators']}],[i|{color['types']}]int[_|{color['punctuators']}],[i|{color['types']}]float[_|{color['punctuators']}])[*]
       [dim](•) [{color['class']}]hsla[{color['punctuators']}]/([i|{color['types']}]int[_|{color['punctuators']}],[i|{color['types']}]int[_|{color['punctuators']}],[i|{color['types']}]int[_|{color['punctuators']}],[i|{color['types']}]float[_|{color['punctuators']}])[*]
       [dim](•) [{color['class']}]hexa[{color['punctuators']}]/([i|{color['types']}]str[_|{color['punctuators']}])[*]
    [dim](•) PATH OPERATIONS          [{color['lib']}]xx[{color['punctuators']}].[{color['class']}]Path[*]
    [dim](•) FILE OPERATIONS          [{color['lib']}]xx[{color['punctuators']}].[{color['class']}]File[*]
    [dim](•) JSON FILE OPERATIONS     [{color['lib']}]xx[{color['punctuators']}].[{color['class']}]Json[*]
    [dim](•) SYSTEM ACTIONS           [{color['lib']}]xx[{color['punctuators']}].[{color['class']}]System[*]
    [dim](•) MANAGE ENVIRONMENT VARS  [{color['lib']}]xx[{color['punctuators']}].[{color['class']}]Env_vars[*]
    [dim](•) CMD LOG AND ACTIONS      [{color['lib']}]xx[{color['punctuators']}].[{color['class']}]Cmd[*]
    [dim](•) PRETTY PRINTING          [{color['lib']}]xx[{color['punctuators']}].[{color['class']}]FormatCodes[*]
    [dim](•) COLOR OPERATIONS         [{color['lib']}]xx[{color['punctuators']}].[{color['class']}]Color[*]
    [dim](•) DATA OPERATIONS          [{color['lib']}]xx[{color['punctuators']}].[{color['class']}]Data[*]
    [dim](•) STR OPERATIONS           [{color['lib']}]xx[{color['punctuators']}].[{color['class']}]String[*]
    [dim](•) CODE STRING OPERATIONS   [{color['lib']}]xx[{color['punctuators']}].[{color['class']}]Code[*]
    [dim](•) REGEX PATTERN TEMPLATES  [{color['lib']}]xx[{color['punctuators']}].[{color['class']}]Regex[*]
  [_]
  [dim](Press any key to exit...)
  """,
        DEFAULT.text_color,
    )
    Cmd.pause_exit(pause=True)
