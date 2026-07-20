from typing import Final


__package_name__: Final[str] = "xulbux"
__version__: Final[str] = "1.9.8"
__description__: Final[str] = "A Python library to simplify common programming tasks."
__status__: Final[str] = "Production/Stable"

__url__: Final[str] = "https://github.com/xulbux/python-lib-xulbux"

__author__: Final[str] = "XulbuX"
__email__: Final[str] = "xulbux.real@gmail.com"
__license__: Final[str] = "MIT"
__copyright__: Final[str] = "Copyright (c) 2024 XulbuX"

__requires_python__: Final[str] = ">=3.10.0"
__dependencies__: Final[list[str]] = [
    "prompt_toolkit>=3.0.41",
    "regex>=2023.10.3",
    "typing-extensions>=4.6.0; python_version < '3.13'",
]

__all__ = [
    "__author__",
    "__copyright__",
    "__dependencies__",
    "__description__",
    "__email__",
    "__license__",
    "__package_name__",
    "__requires_python__",
    "__status__",
    "__url__",
    "__version__",
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
    "S",
    "String",
    "StyledText",
    "System",
    "Term",
]

from .ansi import StyledText, Term, S
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
