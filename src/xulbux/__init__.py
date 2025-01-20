"""
 >>> import xulbux as xx
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  • CUSTOM TYPES:
     • rgba(int,int,int,float)
     • hsla(int,int,int,float)
     • hexa(str)
  • PATH OPERATIONS          xx.Path
  • FILE OPERATIONS          xx.File
  • JSON FILE OPERATIONS     xx.Json
  • SYSTEM ACTIONS           xx.System
  • MANAGE THE ENV PATH VAR  xx.EnvPath
  • CONSOLE LOG AND ACTIONS  xx.Console
  • EASY PRETTY PRINTING     xx.FormatCodes
  • WORKING WITH COLORS      xx.Color
  • DATA OPERATIONS          xx.Data
  • STRING OPERATIONS        xx.String
  • CODE STRING OPERATIONS   xx.Code
  • REGEX PATTERN TEMPLATES  xx.Regex
"""

__version__ = "1.6.2"
__author__ = "XulbuX"
__email__ = "xulbux.real@gmail.com"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2024 XulbuX"
__url__ = "https://github.com/XulbuX-dev/PythonLibraryXulbuX"
__description__ = "A library which includes a lot of really helpful functions."
__all__ = [
    "_consts_",
    "xx_console",
    "xx_code",
    "xx_color",
    "xx_data",
    "xx_env_path",
    "xx_file",
    "xx_format_codes",
    "xx_json",
    "xx_path",
    "xx_regex",
    "xx_string",
    "xx_system",
]

from ._consts_ import *
from .xx_code import *
from .xx_color import *
from .xx_console import *
from .xx_data import *
from .xx_env_path import *
from .xx_file import *
from .xx_format_codes import *
from .xx_json import *
from .xx_path import *
from .xx_regex import *
from .xx_string import *
from .xx_system import *
