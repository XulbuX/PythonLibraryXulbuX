"""
Provides utility decorators used throughout the library.

Includes decorators for caching properties, deprecating
functions, and marking MyPyC compatibility.
"""

import sys as _sys
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Final, LiteralString


class _SafeDeprecated:
    """Safe implementation of deprecated that emits warnings at runtime<br>
    but handles mypyc compiled functions gracefully without crashing.\n
    --------------------------------------------------------------------------------------------------
    *   `message` – A string message to display when the deprecated function is called.
    *   `**kwargs` – Additional keyword arguments to pass to the underlying `warnings.warn` function.
    --------------------------------------------------------------------------------------------------
    **Example usage:**
    ```python
    @deprecated("This function is deprecated. Use `new_function()` instead.")
    def old_function():
        ...
    ```"""

    __slots__: Final[tuple[str, ...]] = ("kwargs", "message")

    def __init__(self, message: LiteralString, **kwargs: Any) -> None:
        self.message: LiteralString = message
        self.kwargs: Any = kwargs

    def __call__(self, arg: Any, /) -> Any:
        if _sys.version_info >= (3, 13):
            from warnings import deprecated as _dep  # type: ignore[attr-defined]
        else:
            try:
                from typing_extensions import deprecated as _dep  # type: ignore[attr-defined]
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


deprecated: Final[type[_SafeDeprecated]] = _SafeDeprecated

if TYPE_CHECKING:
    import sys

    if sys.version_info >= (3, 13):
        from warnings import deprecated as deprecated  # type: ignore[assignment, attr-defined, no-redef]
    else:
        from typing_extensions import deprecated as deprecated  # type: ignore[assignment, attr-defined, no-redef]


def _noop_decorator[T](obj: T) -> T:
    """No-op decorator that returns the object unchanged."""

    return obj


def mypyc_attr[T](**kwargs: Any) -> Callable[[T], T]:
    """A custom decorator that wraps `mypy_extensions.mypyc_attr` when available,<br>
    or acts as a no-op decorator when `mypy_extensions` is not installed.\n
    This allows the use of `mypyc` compilation hints for compiling without making
    `mypy_extensions` a required dependency.\n
    -------------------------------------------------------------------------------------------
    *   `**kwargs` – Keyword arguments to pass to `mypy_extensions.mypyc_attr` if available.\n
    -------------------------------------------------------------------------------------------
    **Example usage:**
    ```python
    @mypyc_attr(native_class=False)
    class MyClass:
        ...
    ```"""

    try:
        from mypy_extensions import mypyc_attr as _mypyc_attr

        return _mypyc_attr(**kwargs)

    except ImportError:
        # If `mypy_extensions` is not installed, just return a no-op decorator.
        return _noop_decorator
