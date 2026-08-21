from typing import TYPE_CHECKING, Any, Final

__package_name__: Final[str] = "xulbux"
__version__: Final[str] = "2.0.0"
__description__: Final[str] = "A Python library to simplify common programming tasks."
__status__: Final[str] = "Production/Stable"

__url__: Final[str] = "https://xulbux.github.io/python-lib-xulbux"

__author__: Final[str] = "XulbuX"
__email__: Final[str] = "hi@xul.is"
__license__: Final[str] = "MIT"
__copyright__: Final[str] = "Copyright (c) 2024 XulbuX"

__requires_python__: Final[str] = ">=3.10.0"
__dependencies__: Final[list[str]] = [
    "prompt_toolkit>=3.0.41",
    "regex>=2023.10.3",
    "typing-extensions>=4.6.0; python_version < '3.13'",
]

if TYPE_CHECKING:
    from . import ansi, code, color, console, data, env_path, file, file_sys, json, regex, string, system
    from .ansi import S, StyledText, Term
    from .color import hexa, hsla, rgba
    from .console import ArgumentParser, ProgressBar, Throbber
    from .format_codes import FormatCodes
    from .regex import LazyRegex

__all__ = [
    "ArgumentParser",
    "FormatCodes",
    "LazyRegex",
    "ProgressBar",
    "S",
    "StyledText",
    "Term",
    "Throbber",
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
    "ansi",
    "code",
    "color",
    "console",
    "data",
    "env_path",
    "file",
    "file_sys",
    "hexa",
    "hsla",
    "json",
    "regex",
    "rgba",
    "string",
    "system",
]


def __getattr__(name: str) -> Any:
    if name in __all__:
        import importlib

        # Map specific exported objects to their submodules:
        submodules = {
            "S": "ansi",
            "StyledText": "ansi",
            "Term": "ansi",
            "hexa": "color",
            "hsla": "color",
            "rgba": "color",
            "ArgumentParser": "console",
            "ProgressBar": "console",
            "Throbber": "console",
            "FormatCodes": "format_codes",
            "LazyRegex": "regex",
        }

        if name in submodules:
            module = importlib.import_module(f".{submodules[name]}", package=__package__)
            return getattr(module, name)

        # Otherwise, it must be a top-level module (e.g., `console`, `string`, …).
        return importlib.import_module(f".{name}", package=__package__)

    raise AttributeError(f"Module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return __all__
