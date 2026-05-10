"""
This module contains custom decorators used throughout the library.
"""

from typing import Callable, TypeVar, Any


T = TypeVar("T")


def _noop_decorator(obj: T) -> T:
    """No-op decorator that returns the object unchanged."""
    return obj


def mypyc_attr(**kwargs: Any) -> Callable[[T], T]:
    """A custom decorator that wraps `mypy_extensions.mypyc_attr` when available,<br>
    or acts as a no-op decorator when `mypy_extensions` is not installed.\n
    This allows the use of `mypyc` compilation hints for compiling without making
    `mypy_extensions` a required dependency.\n
    -------------------------------------------------------------------------------------------
    *   `**kwargs` – keyword arguments to pass to `mypy_extensions.mypyc_attr` if available"""

    try:
        from mypy_extensions import mypyc_attr as _mypyc_attr
        return _mypyc_attr(**kwargs)
    except ImportError:
        # IF 'mypy_extensions' IS NOT INSTALLED, JUST RETURN A NO-OP DECORATOR
        return _noop_decorator
