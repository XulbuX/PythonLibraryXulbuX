from pathlib import Path
from unittest.mock import patch
import xulbux.file_sys as _file_sys_module
import pytest


def test_remove_non_existent_path(tmp_path: Path) -> None:
    non_existent = tmp_path / "does_not_exist"
    _file_sys_module.remove(str(non_existent))
    _file_sys_module.remove(str(non_existent), only_content=True)
    assert not non_existent.exists()


def test_remove_single_file(tmp_path: Path) -> None:
    target_file = tmp_path / "target_to_remove.txt"
    target_file.touch()
    assert target_file.exists()

    _file_sys_module.remove(str(target_file))
    assert not target_file.exists()


def test_remove_entire_directory(tmp_path: Path) -> None:
    dir_to_remove = tmp_path / "directory_to_remove"
    dir_to_remove.mkdir()
    (dir_to_remove / "nested_file.txt").touch()
    (dir_to_remove / "nested_dir").mkdir()

    assert dir_to_remove.exists()
    _file_sys_module.remove(str(dir_to_remove))
    assert not dir_to_remove.exists()


def test_remove_directory_only_content(tmp_path: Path) -> None:
    dir_to_empty = tmp_path / "directory_to_empty"
    dir_to_empty.mkdir()
    (dir_to_empty / "file1.txt").touch()
    (dir_to_empty / "subdir").mkdir()
    (dir_to_empty / "subdir" / "file2.txt").touch()

    _file_sys_module.remove(str(dir_to_empty), only_content=True)
    assert dir_to_empty.exists()
    assert list(dir_to_empty.iterdir()) == []


def test_remove_only_content_on_file_raises_not_a_directory_error(tmp_path: Path) -> None:
    regular_file = tmp_path / "regular_file.txt"
    regular_file.write_text("sample content")

    with pytest.raises(NotADirectoryError, match="Cannot remove only_content of non-directory"):
        _file_sys_module.remove(str(regular_file), only_content=True)


def test_remove_custom_path_neither_file_nor_dir() -> None:
    class CustomNonFileDirItem:
        def exists(self) -> bool:
            return True

        def is_file(self) -> bool:
            return False

        def is_symlink(self) -> bool:
            return False

        def is_dir(self) -> bool:
            return False

    with patch("xulbux.file_sys.Path", return_value=CustomNonFileDirItem()):
        _file_sys_module.remove("fake_item")


def test_remove_failure_raises_runtime_error() -> None:
    class UnlinkFailingPath:
        def exists(self) -> bool:
            return True

        def is_file(self) -> bool:
            return True

        def is_symlink(self) -> bool:
            return False

        def is_dir(self) -> bool:
            return False

        def unlink(self) -> None:
            raise PermissionError("Access is denied")

    with (
        patch("xulbux.file_sys.Path", return_value=UnlinkFailingPath()),
        pytest.raises(RuntimeError, match="Failed to delete"),
    ):
        _file_sys_module.remove("fake_path")
