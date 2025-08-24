from xulbux.path import PathNotFoundError, Path

import tempfile
import pytest
import sys
import os


@pytest.fixture
def setup_test_environment(tmp_path, monkeypatch):
    """Sets up a controlled environment for path tests."""
    mock_cwd = tmp_path / "mock_cwd"
    mock_script_dir = tmp_path / "mock_script_dir"
    mock_home = tmp_path / "mock_home"
    mock_temp = tmp_path / "mock_temp"
    mock_search_in = tmp_path / "mock_search_in"

    for p in [mock_cwd, mock_script_dir, mock_home, mock_temp, mock_search_in]:
        p.mkdir()

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

    monkeypatch.setattr(os, "getcwd", lambda: str(mock_cwd))
    monkeypatch.setattr(sys.modules["__main__"], "__file__", str(mock_script_dir / "mock_script.py"))
    monkeypatch.setattr(os.path, "expanduser", lambda path: str(mock_home) if path == "~" else path)
    monkeypatch.setattr(tempfile, "gettempdir", lambda: str(mock_temp))

    return {
        "cwd": mock_cwd,
        "script_dir": mock_script_dir,
        "home": mock_home,
        "temp": mock_temp,
        "search_in": mock_search_in,
        "abs_file": abs_file,
    }


def test_path_properties(setup_test_environment):
    assert Path.cwd == str(setup_test_environment["cwd"])
    assert Path.script_dir == str(setup_test_environment["script_dir"])


def test_extend(setup_test_environment):
    env = setup_test_environment
    search_dir = str(env["search_in"])
    search_dirs = [str(env["cwd"]), search_dir]

    # ABSOLUTE PATH
    assert Path.extend(str(env["abs_file"])) == str(env["abs_file"])

    # EMPTY PATH
    assert Path.extend("") is None
    assert Path.extend(None) is None  # type: ignore[assignment]
    with pytest.raises(PathNotFoundError, match="Path is empty."):
        Path.extend("", raise_error=True)

    # FOUND IN STANDARD LOCATIONS
    assert Path.extend("file_in_cwd.txt") == str(env["cwd"] / "file_in_cwd.txt")
    assert Path.extend("subdir/file_in_script_subdir.txt") == str(env["script_dir"] / "subdir" / "file_in_script_subdir.txt")
    assert Path.extend("file_in_home.txt") == str(env["home"] / "file_in_home.txt")
    assert Path.extend("temp_file.tmp") == str(env["temp"] / "temp_file.tmp")

    # FOUND IN search_in
    assert Path.extend("custom_file.dat", search_in=search_dir) == str(env["search_in"] / "custom_file.dat")
    assert Path.extend("custom_file.dat", search_in=search_dirs) == str(env["search_in"] / "custom_file.dat")

    # NOT FOUND
    assert Path.extend("non_existent_file.xyz") is None
    with pytest.raises(PathNotFoundError, match="'non_existent_file.xyz' not found"):
        Path.extend("non_existent_file.xyz", raise_error=True)

    # CLOSEST MATCH
    expected_typo = env["search_in"] / "TypoDir" / "file_in_typo.txt"
    assert Path.extend("TypoDir/file_in_typo.txt", search_in=search_dir, use_closest_match=False) == str(expected_typo)
    assert Path.extend("TypoDir/file_in_typo.txt", search_in=search_dir, use_closest_match=True) == str(expected_typo)
    assert Path.extend("TypoDir/file_in_typx.txt", search_in=search_dir, use_closest_match=True) == str(expected_typo)
    assert Path.extend("CompletelyWrong/no_file_here.dat", search_in=search_dir, use_closest_match=True) is None


def test_extend_or_make(setup_test_environment):
    env = setup_test_environment
    search_dir = str(env["search_in"])

    # FOUND
    assert Path.extend_or_make("file_in_cwd.txt") == str(env["cwd"] / "file_in_cwd.txt")

    # NOT FOUND - MAKE PATH (PREFER SCRIPT DIR)
    rel_path_script = "new_dir/new_file.txt"
    expected_script = env["script_dir"] / rel_path_script
    assert Path.extend_or_make(rel_path_script, prefer_script_dir=True) == str(expected_script)

    # NOT FOUND - MAKE PATH (PREFER CWD)
    rel_path_cwd = "another_new_dir/another_new_file.txt"
    expected_cwd = env["cwd"] / rel_path_cwd
    assert Path.extend_or_make(rel_path_cwd, prefer_script_dir=False) == str(expected_cwd)

    # USES CLOSEST MATCH WHEN FINDING
    expected_typo = env["search_in"] / "TypoDir" / "file_in_typo.txt"
    assert Path.extend_or_make("TypoDir/file_in_typx.txt", search_in=search_dir, use_closest_match=True) == str(expected_typo)

    # MAKES PATH WHEN CLOSEST MATCH FAILS
    rel_path_wrong = "VeryWrong/made_up.file"
    expected_made = env["script_dir"] / rel_path_wrong
    assert Path.extend_or_make(rel_path_wrong, search_in=search_dir, use_closest_match=True) == str(expected_made)


def test_remove(tmp_path):
    # NON-EXISTENT
    non_existent_path = tmp_path / "does_not_exist"
    assert not non_existent_path.exists()
    Path.remove(str(non_existent_path))
    assert not non_existent_path.exists()
    Path.remove(str(non_existent_path), only_content=True)
    assert not non_existent_path.exists()

    # FILE REMOVAL
    file_to_remove = tmp_path / "remove_me.txt"
    file_to_remove.touch()
    assert file_to_remove.exists()
    Path.remove(str(file_to_remove))
    assert not file_to_remove.exists()

    # DIRECTORY REMOVAL (FULL)
    dir_to_remove = tmp_path / "remove_dir"
    dir_to_remove.mkdir()
    (dir_to_remove / "file1.txt").touch()
    (dir_to_remove / "subdir").mkdir()
    (dir_to_remove / "subdir" / "file2.txt").touch()
    assert dir_to_remove.exists()
    Path.remove(str(dir_to_remove))
    assert not dir_to_remove.exists()

    # DIRECTORY REMOVAL (ONLY CONTENT)
    dir_to_empty = tmp_path / "empty_dir"
    dir_to_empty.mkdir()
    (dir_to_empty / "file1.txt").touch()
    (dir_to_empty / "subdir").mkdir()
    (dir_to_empty / "subdir" / "file2.txt").touch()
    assert dir_to_empty.exists()
    Path.remove(str(dir_to_empty), only_content=True)
    assert dir_to_empty.exists()
    assert not list(dir_to_empty.iterdir())

    # ONLY CONTENT ON A FILE (SHOULD DO NOTHING)
    file_path_content = tmp_path / "file_content.txt"
    file_path_content.write_text("content")
    assert file_path_content.exists()
    Path.remove(str(file_path_content), only_content=True)
    assert file_path_content.exists()
    assert file_path_content.read_text() == "content"
