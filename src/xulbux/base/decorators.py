"""
This module contains custom decorators used throughout the library.
"""

import sys as _sys
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Final, LiteralString


class _SafeDeprecated:
    """Safe implementation of deprecated that emits warnings at runtime
    but handles mypyc compiled functions gracefully without crashing.\n
    Standard PEP 702 decorators crash when applying `__deprecated__` to
    mypyc `builtin_function_or_method` objects."""

    __slots__: Final[tuple[str, ...]] = ("kwargs", "message")

    def __init__(self, message: LiteralString, **kwargs: Any) -> None:
        self.message: LiteralString = message
        self.kwargs: Any = kwargs

    def __call__(self, arg: Any, /) -> Any:
        if _sys.version_info >= (3, 13):
            from warnings import deprecated as _dep
        else:
            try:
                from typing_extensions import deprecated as _dep
            except ImportError:
                from contextlib import suppress

                with suppress(AttributeError, TypeError):
                    arg.__deprecated__ = self.message
                return arg

        try:
            return _dep(self.message, **self.kwargs)(arg)

        except (AttributeError, TypeError):
            # Standard decorator failed to set `__deprecated__`.
            if callable(arg) and not isinstance(arg, type):
                import functools

                @functools.wraps(arg)
                def _mypyc_wrapper(*args: Any, **kw: Any) -> Any:
                    return arg(*args, **kw)

                return _dep(self.message, **self.kwargs)(_mypyc_wrapper)

            return arg  # If it's a class or something else, just return it.


deprecated = _SafeDeprecated


if TYPE_CHECKING:
    if _sys.version_info >= (3, 13):
        from warnings import deprecated as deprecated  # type: ignore[assignment]
    else:
        from typing_extensions import deprecated as deprecated  # type: ignore[assignment]


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
