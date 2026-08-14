import os
import sys
import tempfile
from pathlib import Path
import xulbux.file_sys as _file_sys_module
from xulbux.base.exceptions import PathNotFoundError
import pytest


@pytest.fixture
def setup_test_environment(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict[str, Path]:
    """Sets up a controlled environment for path tests."""
    mock_cwd = tmp_path / "mock_cwd"
    mock_script_dir = tmp_path / "mock_script_dir"
    mock_home = tmp_path / "mock_home"
    mock_temp = tmp_path / "mock_temp"
    mock_search_in = tmp_path / "mock_search_in"

    for path in [mock_cwd, mock_script_dir, mock_home, mock_temp, mock_search_in]:
        path.mkdir()

    (mock_cwd / "file_in_cwd.txt").touch()
    (mock_script_dir / "subdir").mkdir()
    (mock_script_dir / "subdir" / "file_in_script_subdir.txt").touch()
    (mock_home / "file_in_home.txt").touch()
    (mock_temp / "temp_file.tmp").touch()
    (mock_search_in / "custom_file.dat").touch()
    (mock_search_in / "TypoDir").mkdir()
    (mock_search_in / "TypoDir" / "file_in_typo.txt").touch()
    abs_file = mock_cwd / "absolute_file.txt"
    abs_file.touch()

    monkeypatch.setattr(Path, "cwd", staticmethod(lambda: mock_cwd))
    monkeypatch.setattr(Path, "home", staticmethod(lambda: mock_home))
    monkeypatch.setattr(sys.modules["__main__"], "__file__", str(mock_script_dir / "mock_script.py"))

    def mock_expanduser(path: str) -> str:
        return str(mock_home) if path == "~" else path

    monkeypatch.setattr(os.path, "expanduser", mock_expanduser)
    monkeypatch.setattr(tempfile, "gettempdir", lambda: str(mock_temp))

    return {
        "cwd": mock_cwd,
        "script_dir": mock_script_dir,
        "home": mock_home,
        "temp": mock_temp,
        "search_in": mock_search_in,
        "abs_file": abs_file,
    }


# ******************************************************* MODULE TESTS *****************************************************


def test_path_cwd(setup_test_environment: dict[str, Path]):
    cwd_output = _file_sys_module.get_cwd()
    assert isinstance(cwd_output, Path)
    assert str(cwd_output) == str(setup_test_environment["cwd"])


def test_path_script_dir(setup_test_environment: dict[str, Path]):
    script_dir_output = _file_sys_module.get_script_dir()
    assert isinstance(script_dir_output, Path)
    assert str(script_dir_output) == str(setup_test_environment["script_dir"])


def test_path_home():
    home = _file_sys_module.get_home()
    assert isinstance(home, Path)
    assert len(str(home)) > 0
    assert home.exists()
    assert home.is_dir()


def test_extend(setup_test_environment: dict[str, Path]):
    env = setup_test_environment
    search_dir = str(env["search_in"])
    search_dirs = [str(env["cwd"]), search_dir]

    # Absolute path:
    result = _file_sys_module.extend_path(str(env["abs_file"]))
    assert isinstance(result, Path)
    assert str(result) == str(env["abs_file"])

    # Empty path:
    assert _file_sys_module.extend_path("") is None
    with pytest.raises(PathNotFoundError, match=r"Given 'rel_path' is an empty string\."):
        _file_sys_module.extend_path("", raise_error=True)

    # Found in standard locations:
    assert str(_file_sys_module.extend_path("file_in_cwd.txt")) == str(env["cwd"] / "file_in_cwd.txt")
    assert str(_file_sys_module.extend_path("subdir/file_in_script_subdir.txt")) == str(
        env["script_dir"] / "subdir" / "file_in_script_subdir.txt"
    )
    assert str(_file_sys_module.extend_path("file_in_home.txt")) == str(env["home"] / "file_in_home.txt")
    assert str(_file_sys_module.extend_path("temp_file.tmp")) == str(env["temp"] / "temp_file.tmp")

    # Found in `search_in` directory:
    assert str(_file_sys_module.extend_path("custom_file.dat", search_in=search_dir)) == str(
        env["search_in"] / "custom_file.dat"
    )
    assert str(_file_sys_module.extend_path("custom_file.dat", search_in=search_dirs)) == str(
        env["search_in"] / "custom_file.dat"
    )

    # Not found:
    assert _file_sys_module.extend_path("non_existent_file.xyz") is None
    with pytest.raises(
        PathNotFoundError, match=r"Path [A-Za-z]*Path\('non_existent_file\.xyz'\) not found in specified directories\."
    ):
        _file_sys_module.extend_path("non_existent_file.xyz", raise_error=True)

    # Closest match:
    expected_typo = env["search_in"] / "TypoDir" / "file_in_typo.txt"
    assert str(_file_sys_module.extend_path("TypoDir/file_in_typo.txt", search_in=search_dir, fuzzy_match=False)) == str(
        expected_typo
    )
    assert str(_file_sys_module.extend_path("TypoDir/file_in_typo.txt", search_in=search_dir, fuzzy_match=True)) == str(
        expected_typo
    )
    assert str(_file_sys_module.extend_path("TypoDir/file_in_typx.txt", search_in=search_dir, fuzzy_match=True)) == str(
        expected_typo
    )
    assert _file_sys_module.extend_path("CompletelyWrong/no_file_here.dat", search_in=search_dir, fuzzy_match=True) is None


def test_extend_or_make(setup_test_environment: dict[str, Path]):
    env = setup_test_environment
    search_dir = str(env["search_in"])

    # Found:
    result = _file_sys_module.extend_or_make_path("file_in_cwd.txt")
    assert isinstance(result, Path)
    assert str(result) == str(env["cwd"] / "file_in_cwd.txt")

    # Not found; make path (prefer script dir):
    rel_path_script = "new_dir/new_file.txt"
    expected_script = env["script_dir"] / rel_path_script
    assert str(_file_sys_module.extend_or_make_path(rel_path_script, prefer_script_dir=True)) == str(expected_script)

    # Not found; make path (prefer CWD):
    rel_path_cwd = "another_new_dir/another_new_file.txt"
    expected_cwd = env["cwd"] / rel_path_cwd
    assert str(_file_sys_module.extend_or_make_path(rel_path_cwd, prefer_script_dir=False)) == str(expected_cwd)

    # Uses closest match when finding:
    expected_typo = env["search_in"] / "TypoDir" / "file_in_typo.txt"
    assert str(
        _file_sys_module.extend_or_make_path("TypoDir/file_in_typx.txt", search_in=search_dir, fuzzy_match=True)
    ) == str(expected_typo)

    # Makes path when closest match fails:
    rel_path_wrong = "VeryWrong/made_up.file"
    expected_made = env["script_dir"] / rel_path_wrong
    assert str(_file_sys_module.extend_or_make_path(rel_path_wrong, search_in=search_dir, fuzzy_match=True)) == str(
        expected_made
    )


def test_remove(tmp_path: Path):
    # Non-existent:
    non_existent_path = tmp_path / "does_not_exist"
    assert not non_existent_path.exists()
    _file_sys_module.remove(str(non_existent_path))
    assert not non_existent_path.exists()
    _file_sys_module.remove(str(non_existent_path), only_content=True)
    assert not non_existent_path.exists()

    # File removal:
    file_to_remove = tmp_path / "remove_me.txt"
    file_to_remove.touch()
    assert file_to_remove.exists()
    _file_sys_module.remove(str(file_to_remove))
    assert not file_to_remove.exists()

    # Directory removal (full):
    dir_to_remove = tmp_path / "remove_dir"
    dir_to_remove.mkdir()
    (dir_to_remove / "file1.txt").touch()
    (dir_to_remove / "subdir").mkdir()
    (dir_to_remove / "subdir" / "file2.txt").touch()
    assert dir_to_remove.exists()
    _file_sys_module.remove(str(dir_to_remove))
    assert not dir_to_remove.exists()

    # Directory removal (only content):
    dir_to_empty = tmp_path / "empty_dir"
    dir_to_empty.mkdir()
    (dir_to_empty / "file1.txt").touch()
    (dir_to_empty / "subdir").mkdir()
    (dir_to_empty / "subdir" / "file2.txt").touch()
    assert dir_to_empty.exists()
    _file_sys_module.remove(str(dir_to_empty), only_content=True)
    assert dir_to_empty.exists()
    assert not list(dir_to_empty.iterdir())

    # Only content on a file (should raise error):
    file_path_content = tmp_path / "file_content.txt"
    file_path_content.write_text("content")
    assert file_path_content.exists()
    with pytest.raises(NotADirectoryError):
        _file_sys_module.remove(str(file_path_content), only_content=True)
    assert file_path_content.exists()
    assert file_path_content.read_text() == "content"
