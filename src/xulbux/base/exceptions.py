"""
This module contains all custom exception classes used throughout the library.
"""

try:
    from mypy_extensions import mypyc_attr  # type: ignore[import]
except ImportError:

    def __mypyc_attr_decorator(cls):
        return cls

    def mypyc_attr(*args, **kwargs):  # type: ignore[misc]
        return __mypyc_attr_decorator


#
################################################## FILE ##################################################


@mypyc_attr(native_class=False)
class SameContentFileExistsError(FileExistsError):
    """Raised when attempting to create a file that already exists with identical content."""
    ...


################################################## PATH ##################################################


@mypyc_attr(native_class=False)
class PathNotFoundError(FileNotFoundError):
    """Raised when a file system path does not exist or cannot be accessed."""
    ...
