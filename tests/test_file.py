from xulbux.xx_file import SameContentFileExistsError
from xulbux import File

import pytest
import os


@pytest.mark.parametrize(
    "input_file, new_extension, camel_case, full_extension, expected_output", [
        ("myfile.txt", ".log", False, False, "myfile.log"),
        ("my_file_name.data", ".csv", False, False, "my_file_name.csv"),
        ("another-file.json", ".xml", False, False, "another-file.xml"),
        ("path/to/myfile.txt", ".md", False, False, os.path.join("path", "to", "myfile.md")),
        ("my_file_name.data", ".csv", True, False, "MyFileName.csv"),
        ("another-file.json", ".xml", True, False, "AnotherFile.xml"),
        ("alreadyCamelCase.config", ".yaml", True, False, "AlreadyCamelCase.yaml"),
        (os.path.join("path", "to", "my_file.txt"), ".log", True, False, os.path.join("path", "to", "MyFile.log")),
        ("filename", ".ext", False, False, "filename.ext"),
        ("file_name", ".ext", True, False, "FileName.ext"),
        ("test_file.blade.php", ".vue", False, False, "test_file.blade.vue"),
        ("archive.tar.gz", ".zip", False, False, "archive.tar.zip"),
        ("my_archive.tar.gz", ".zip", True, False, "MyArchive.tar.zip"),
        ("test_file.blade.php", ".vue", False, True, "test_file.vue"),
        ("archive.tar.gz", ".zip", False, True, "archive.zip"),
        ("my_archive.tar.gz", ".zip", True, True, "MyArchive.zip"),
        (os.path.join("some", "dir", "file.config.yaml"), ".json", False, True, os.path.join("some", "dir", "file.json")),
        (
            os.path.join("some", "dir",
                         "file_name.config.yaml"), ".json", True, True, os.path.join("some", "dir", "FileName.json")
        ),
        ("nodotfile", ".txt", False, True, "nodotfile.txt"),
        ("no_dot_file", ".txt", True, True, "NoDotFile.txt"),
    ]
)
def test_rename_extension(input_file, new_extension, full_extension, camel_case, expected_output):
    expected_output = expected_output.replace("/", os.sep).replace("\\", os.sep)
    assert File.rename_extension(input_file, new_extension, full_extension, camel_case) == expected_output


def test_create_new_file(tmp_path):
    file_path = tmp_path / "new_file.txt"
    abs_path = File.create(str(file_path))
    assert os.path.exists(file_path)
    assert os.path.abspath(str(file_path)) == abs_path
    with open(file_path, "r", encoding="utf-8") as f:
        assert f.read() == ""


def test_create_file_with_content(tmp_path):
    file_path = tmp_path / "content_file.log"
    content = "This is the file content.\nWith multiple lines."
    abs_path = File.create(str(file_path), content=content)
    assert os.path.exists(file_path)
    assert os.path.abspath(str(file_path)) == abs_path
    with open(file_path, "r", encoding="utf-8") as f:
        assert f.read() == content


def test_create_file_exists_error(tmp_path):
    file_path = tmp_path / "existing_file.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("Initial content")
    with pytest.raises(FileExistsError, match="File already exists."):
        File.create(str(file_path), content="New content", force=False)


def test_create_file_same_content_exists_error(tmp_path):
    file_path = tmp_path / "same_content_file.data"
    content = "Identical content"
    File.create(str(file_path), content=content)
    with pytest.raises(SameContentFileExistsError, match="Already created this file. \\(nothing changed\\)"):
        File.create(str(file_path), content=content, force=False)


def test_create_file_force_overwrite_different_content(tmp_path):
    file_path = tmp_path / "overwrite_file.cfg"
    initial_content = "Old config"
    new_content = "New configuration values"

    File.create(str(file_path), content=initial_content)
    assert open(file_path, "r", encoding="utf-8").read() == initial_content

    abs_path = File.create(str(file_path), content=new_content, force=True)
    assert os.path.exists(file_path)
    assert os.path.abspath(str(file_path)) == abs_path
    with open(file_path, "r", encoding="utf-8") as f:
        assert f.read() == new_content


def test_create_file_force_overwrite_same_content(tmp_path):
    file_path = tmp_path / "overwrite_same_file.ini"
    content = "[Settings]\nValue=1"

    File.create(str(file_path), content=content)
    assert open(file_path, "r", encoding="utf-8").read() == content

    abs_path = File.create(str(file_path), content=content, force=True)
    assert os.path.exists(file_path)
    assert os.path.abspath(str(file_path)) == abs_path
    with open(file_path, "r", encoding="utf-8") as f:
        assert f.read() == content


def test_create_file_in_subdirectory(tmp_path):
    dir_path = tmp_path / "subdir"
    file_path = dir_path / "sub_file.txt"
    content = "Content in subdirectory"

    with pytest.raises(FileNotFoundError):
        File.create(str(file_path), content=content)

    os.makedirs(dir_path)
    abs_path = File.create(str(file_path), content=content)
    assert os.path.exists(file_path)
    assert os.path.abspath(str(file_path)) == abs_path
    with open(file_path, "r", encoding="utf-8") as f:
        assert f.read() == content
