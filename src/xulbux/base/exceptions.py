################################################## FILE ##################################################


class SameContentFileExistsError(FileExistsError):
    """Exception raised when a file with the same name and content already exists."""
    ...


################################################## PATH ##################################################


class PathNotFoundError(FileNotFoundError):
    """Exception raised when a specified path could not be found."""
    ...
