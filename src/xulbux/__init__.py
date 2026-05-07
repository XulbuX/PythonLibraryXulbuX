__package_name__ = "xulbux"
__version__ = "1.9.8"
__description__ = "A Python library to simplify common programming tasks."
__status__ = "Production/Stable"

__url__ = "https://github.com/xulbux/python-lib-xulbux"

__author__ = "XulbuX"
__email__ = "xulbux.real@gmail.com"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2024 XulbuX"

__requires_python__ = ">=3.10.0"
__dependencies__ = [
    "prompt_toolkit>=3.0.41",
    "regex>=2023.10.3",
]

__all__ = [
    "Code",
    "Color",
    "Console",
    "Data",
    "EnvPath",
    "File",
    "FileSys",
    "FormatCodes",
    "Json",
    "Regex",
    "String",
    "System",
]

from .code import Code
from .color import Color
from .console import Console
from .data import Data
from .env_path import EnvPath
from .file import File
from .file_sys import FileSys
from .format_codes import FormatCodes
from .json import Json
from .regex import Regex
from .string import String
from .system import System
