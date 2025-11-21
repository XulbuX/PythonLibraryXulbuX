"""
This module contains all custom exception classes used throughout the library.
"""

################################################## FILE ##################################################


class SameContentFileExistsError(FileExistsError):
    """Raised when attempting to create a file that already exists with identical content."""
    ...


################################################## PATH ##################################################


class PathNotFoundError(FileNotFoundError):
    """Raised when a file system path does not exist or cannot be accessed."""
    ...
