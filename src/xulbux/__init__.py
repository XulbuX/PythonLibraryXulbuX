__version__ = "1.8.3"

__author__ = "XulbuX"
__email__ = "xulbux.real@gmail.com"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2024 XulbuX"
__url__ = "https://github.com/XulbuX/PythonLibraryXulbuX"
__description__ = "A Python library which includes lots of helpful classes, types, and functions aiming to make common programming tasks simpler."

__all__ = [
    "Code",
    "Color",
    "Console",
    "Data",
    "EnvPath",
    "File",
    "FormatCodes",
    "Json",
    "Path",
    "ProgressBar",
    "Regex",
    "String",
    "System",
]

from .code import Code
from .color import Color
from .console import Console
from .console import ProgressBar
from .data import Data
from .env_path import EnvPath
from .file import File
from .format_codes import FormatCodes
from .json import Json
from .path import Path
from .regex import Regex
from .string import String
from .system import System
