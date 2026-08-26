from xulbux.base.exceptions import PathNotFoundError, SameContentFileExistsError
import pytest


def test_same_content_file_exists_error_inheritance():
    with pytest.raises(FileExistsError):
        raise SameContentFileExistsError("File already has identical content")


def test_path_not_found_error_inheritance():
    with pytest.raises(FileNotFoundError):
        raise PathNotFoundError("File or directory not found")
