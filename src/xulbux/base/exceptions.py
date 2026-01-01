"""
This module contains all custom exception classes used throughout the library.
"""

from mypy_extensions import mypyc_attr

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
