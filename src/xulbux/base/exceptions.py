"""
Provides custom exception classes used throughout the library.

Includes exceptions for missing dependencies,
execution failures, and formatting errors.
"""

from .decorators import mypyc_attr

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
