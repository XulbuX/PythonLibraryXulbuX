# ruff:file-ignore[non-empty-init-module]
from __future__ import annotations

TYPE_CHECKING: bool = False
"""Flag indicating whether type checking is active during static analysis."""

if TYPE_CHECKING:
    from . import ansi, cli, color, console, data, file_sys, json, regex, string, system
    from .ansi import S, Term
    from .color import hexa, hsla, rgba
    from .console import ArgumentParser, ParsedArgData, ParsedArgs, ProgressBar, Throbber
    from .regex import LazyRegex

    from typing import Any, Final

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
    "typing-extensions>=4.10.0; python_version < '3.13'",
]

__all__ = [
    "ArgumentParser",
    "LazyRegex",
    "ParsedArgData",
    "ParsedArgs",
    "ProgressBar",
    "S",
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
    "cli",
    "color",
    "console",
    "data",
    "file_sys",
    "hexa",
    "hsla",
    "json",
    "regex",
    "rgba",
    "string",
    "system",
]

_SUBMODULES: Final[dict[str, str]] = {
    "S": "ansi",
    "Term": "ansi",
    "hexa": "color",
    "hsla": "color",
    "rgba": "color",
    "ArgumentParser": "console",
    "ParsedArgData": "console",
    "ParsedArgs": "console",
    "ProgressBar": "console",
    "Throbber": "console",
    "LazyRegex": "regex",
}
"""Mapping of top-level exported class names to their originating submodule for lazy-loading."""


def __getattr__(name: str) -> Any:
    """Lazy-loads submodules and submodule attributes when accessed.<br>
    This allows for faster initial import times and reduces memory usage.\n
    ----------------------------------------------------------------------------------------------------
    *   `name` – The name of the submodule or attribute to access."""

    if name in __all__:
        import importlib

        if name in _SUBMODULES:
            module = importlib.import_module(f".{_SUBMODULES[name]}", package=__package__)
            globals()[name] = (val := getattr(module, name))

            return val

        # Otherwise, it must be a top-level module (e.g., `console`, `string`, …):
        module = importlib.import_module(f".{name}", package=__package__)
        globals()[name] = module

        return module

    raise AttributeError(f"Module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    """Returns the list of attributes available in this module,<br>
    including submodules and submodule attributes."""

    return __all__
