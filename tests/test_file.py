from pathlib import Path
import xulbux.file as _file_module
from xulbux.base.exceptions import SameContentFileExistsError
import pytest

#
####################################################### File TESTS #######################################################


@pytest.mark.parametrize(
    "input_file, new_extension, camel_case, full_extension, expected_output",
    [
        ("myfile.txt", ".log", False, False, "myfile.log"),
        ("my_file_name.data", ".csv", False, False, "my_file_name.csv"),
        ("another-file.json", ".xml", False, False, "another-file.xml"),
        ("path/to/myfile.txt", ".md", False, False, str(Path("path") / "to" / "myfile.md")),
        ("my_file_name.data", ".csv", True, False, "MyFileName.csv"),
        ("another-file.json", ".xml", True, False, "AnotherFile.xml"),
        ("alreadyCamelCase.config", ".yaml", True, False, "AlreadyCamelCase.yaml"),
        (Path("path") / "to" / "my_file.txt", ".log", True, False, str(Path("path") / "to" / "MyFile.log")),
        ("filename", ".ext", False, False, "filename.ext"),
        ("file_name", ".ext", True, False, "FileName.ext"),
        ("test_file.blade.php", ".vue", False, False, "test_file.blade.vue"),
        ("archive.tar.gz", ".zip", False, False, "archive.tar.zip"),
        ("my_archive.tar.gz", ".zip", True, False, "MyArchive.tar.zip"),
        ("test_file.blade.php", ".vue", False, True, "test_file.vue"),
        ("archive.tar.gz", ".zip", False, True, "archive.zip"),
        ("my_archive.tar.gz", ".zip", True, True, "MyArchive.zip"),
        (Path("some") / "dir" / "file.config.yaml", ".json", False, True, str(Path("some") / "dir" / "file.json")),
        (Path("some") / "dir" / "file_name.config.yaml", ".json", True, True, str(Path("some") / "dir" / "FileName.json")),
        ("nodotfile", ".txt", False, True, "nodotfile.txt"),
        ("no_dot_file", ".txt", True, True, "NoDotFile.txt"),
    ],
)
def test_rename_extension(
    input_file: str | Path, new_extension: str, full_extension: bool, camel_case: bool, expected_output: str
):
    result = _file_module.rename_extension(
        input_file, new_extension, full_extension=full_extension, camel_case_filename=camel_case
    )
    assert isinstance(result, Path)
    assert str(result) == expected_output


def test_create_new_file(tmp_path: Path):
    file_path = tmp_path / "new_file.txt"
    abs_path = _file_module.create(str(file_path))
    assert isinstance(abs_path, Path)
    assert file_path.exists()
    assert abs_path.resolve() == file_path.resolve()
    with open(file_path, encoding="utf-8") as file:
        assert file.read() == ""


def test_create_file_with_content(tmp_path: Path):
    file_path = tmp_path / "content_file.log"
    content = "This is the file content.\nWith multiple lines."
    abs_path = _file_module.create(str(file_path), content)
    assert isinstance(abs_path, Path)
    assert file_path.exists()
    assert abs_path.resolve() == file_path.resolve()
    with open(file_path, encoding="utf-8") as file:
        assert file.read() == content


def test_create_file_exists_error(tmp_path: Path):
    file_path = tmp_path / "existing_file.txt"
    with open(file_path, "w", encoding="utf-8") as file:
        file.write("Initial content")
    with pytest.raises(FileExistsError):
        _file_module.create(str(file_path), "New content", force=False)


def test_create_file_same_content_exists_error(tmp_path: Path):
    file_path = tmp_path / "same_content_file.data"
    content = "Identical content"
    _file_module.create(str(file_path), content)
    with pytest.raises(SameContentFileExistsError):
        _file_module.create(str(file_path), content, force=False)


def test_create_file_force_overwrite_different_content(tmp_path: Path):
    file_path = tmp_path / "overwrite_file.cfg"
    initial_content = "Old config"
    new_content = "New configuration values"

    _file_module.create(str(file_path), initial_content)
    assert file_path.read_text(encoding="utf-8") == initial_content

    abs_path = _file_module.create(str(file_path), new_content, force=True)
    assert isinstance(abs_path, Path)
    assert file_path.exists()
    assert abs_path.resolve() == file_path.resolve()
    with open(file_path, encoding="utf-8") as file:
        assert file.read() == new_content


def test_create_file_force_overwrite_same_content(tmp_path: Path):
    file_path = tmp_path / "overwrite_same_file.ini"
    content = "[Settings]\nValue=1"

    _file_module.create(str(file_path), content)
    assert file_path.read_text(encoding="utf-8") == content

    abs_path = _file_module.create(str(file_path), content, force=True)
    assert isinstance(abs_path, Path)
    assert file_path.exists()
    assert abs_path.resolve() == file_path.resolve()
    with open(file_path, encoding="utf-8") as file:
        assert file.read() == content


def test_create_file_in_subdirectory(tmp_path: Path):
    dir_path = tmp_path / "subdir"
    file_path = dir_path / "sub_file.txt"
    content = "Content in subdirectory"

    with pytest.raises(FileNotFoundError):
        _file_module.create(str(file_path), content)

    dir_path.mkdir()
    abs_path = _file_module.create(str(file_path), content)
    assert isinstance(abs_path, Path)
    assert file_path.exists()
    assert abs_path.resolve() == file_path.resolve()
    with open(file_path, encoding="utf-8") as file:
        assert file.read() == content
