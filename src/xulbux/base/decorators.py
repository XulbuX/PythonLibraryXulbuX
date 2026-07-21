"""
This module contains custom decorators used throughout the library.
"""

import sys as _sys
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, LiteralString

if TYPE_CHECKING:
    if _sys.version_info >= (3, 13):
        from warnings import deprecated as deprecated  # type: ignore[attr-defined]
    else:
        from typing_extensions import deprecated as deprecated


class _DeprecatedWrapper:
    """Internal, callable class that wraps the `deprecated` decorator from either<br>
    `warnings` or `typing_extensions` depending on the Python version."""

    def __init__(self, message: LiteralString, **kwargs: Any) -> None:
        self.message: LiteralString = message
        self.kwargs: Any = kwargs

    def __call__[T](self, obj: T) -> T:
        try:
            if _sys.version_info >= (3, 13):
                from warnings import deprecated as _dep  # type: ignore[attr-defined]
            else:
                try:
                    from typing_extensions import deprecated as _dep
                except ImportError:
                    return obj

            return _dep(self.message, **self.kwargs)(obj)

        except (AttributeError, TypeError):
            return obj


def _deprecated_runtime(message: LiteralString, **kwargs: Any) -> _DeprecatedWrapper:
    """A decorator that marks a function or class as deprecated at runtime, using the `deprecated`<br>
    decorator from either `warnings` or `typing_extensions` depending on the Python version.<br>
    If neither is available, it will return the object unchanged.\n
    ---------------------------------------------------------------------------------------------------
    *   `message` – A string message to display when the deprecated function or class is called.
    *   `**kwargs` – Additional keyword arguments to pass to the `deprecated` decorator.
    ---------------------------------------------------------------------------------------------------
    Returns a callable that can be used as a decorator for functions or classes."""

    return _DeprecatedWrapper(message, **kwargs)


# Only use the custom decorator during runtime to keep
# the IDE functionality for the `@deprecated` decorator:
if not TYPE_CHECKING:
    deprecated = _deprecated_runtime


def _noop_decorator[T](obj: T) -> T:
    """No-op decorator that returns the object unchanged."""

    return obj


def mypyc_attr[T](**kwargs: Any) -> Callable[[T], T]:
    """A custom decorator that wraps `mypy_extensions.mypyc_attr` when available,<br>
    or acts as a no-op decorator when `mypy_extensions` is not installed.\n
    This allows the use of `mypyc` compilation hints for compiling without making
    `mypy_extensions` a required dependency.\n
    --------------------------------------------------------------------------------------------
    *   `**kwargs` – Keyword arguments to pass to `mypy_extensions.mypyc_attr` if available."""

    try:
        from mypy_extensions import mypyc_attr as _mypyc_attr

        return _mypyc_attr(**kwargs)

    except ImportError:
        # If `mypy_extensions` is not installed, just return a no-op decorator.
        return _noop_decorator
