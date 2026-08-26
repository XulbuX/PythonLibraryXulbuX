import contextlib
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import PropertyMock, patch
import xulbux.file_sys as _file_sys_module
from xulbux.base.exceptions import PathNotFoundError
from xulbux.file_sys import _ExtendPathHelper
import pytest


@pytest.fixture
def setup_test_environment(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict[str, Path]:
    mock_cwd = tmp_path / "mock_cwd"
    mock_script_dir = tmp_path / "mock_script_dir"
    mock_home = tmp_path / "mock_home"
    mock_temp = tmp_path / "mock_temp"
    mock_search_in = tmp_path / "mock_search_in"

    for path_item in [mock_cwd, mock_script_dir, mock_home, mock_temp, mock_search_in]:
        path_item.mkdir()

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

    def mock_expanduser(path_str: str) -> str:
        return str(mock_home) if path_str == "~" else path_str

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


def test_get_cwd(setup_test_environment: dict[str, Path]):
    cwd_output = _file_sys_module.get_cwd()
    assert isinstance(cwd_output, Path)
    assert str(cwd_output) == str(setup_test_environment["cwd"])


def test_get_home():
    home = _file_sys_module.get_home()
    assert isinstance(home, Path)
    assert home.exists()
    assert home.is_dir()


def test_get_script_dir(setup_test_environment: dict[str, Path]):
    script_dir_output = _file_sys_module.get_script_dir()
    assert isinstance(script_dir_output, Path)
    assert str(script_dir_output) == str(setup_test_environment["script_dir"])


def test_get_script_dir_frozen_environment():
    with patch.object(sys, "frozen", True, create=True), patch.object(sys, "executable", "mocked_app.exe"):
        script_dir = _file_sys_module.get_script_dir()
        assert script_dir == Path("mocked_app.exe").parent


def test_get_script_dir_spec_fallback():
    class CustomSpec:
        origin = "mocked_spec_origin.py"

    class CustomMainModule:
        __spec__ = CustomSpec()

    with patch.dict(sys.modules, {"__main__": CustomMainModule()}):
        script_dir = _file_sys_module.get_script_dir()
        assert script_dir == Path("mocked_spec_origin.py").resolve().parent


def test_get_script_dir_missing_file_and_spec_raises_runtime_error():
    class IncompleteMainModule:
        __spec__ = None

    with (
        patch.dict(sys.modules, {"__main__": IncompleteMainModule()}),
        pytest.raises(RuntimeError, match="Can only get base directory"),
    ):
        _file_sys_module.get_script_dir()


def test_extend_path_standard_locations(setup_test_environment: dict[str, Path]):
    env = setup_test_environment
    search_dir = str(env["search_in"])
    search_dirs = [str(env["cwd"]), search_dir]

    assert str(_file_sys_module.extend_path(Path(str(env["abs_file"])))) == str(env["abs_file"])
    assert str(_file_sys_module.extend_path(str(env["abs_file"]))) == str(env["abs_file"])
    assert _file_sys_module.extend_path("") is None

    with pytest.raises(PathNotFoundError, match="Given 'rel_path' is an empty string"):
        _file_sys_module.extend_path("", raise_error=True)

    assert str(_file_sys_module.extend_path("file_in_cwd.txt")) == str(env["cwd"] / "file_in_cwd.txt")
    assert str(_file_sys_module.extend_path("subdir/file_in_script_subdir.txt")) == str(
        env["script_dir"] / "subdir" / "file_in_script_subdir.txt"
    )
    assert str(_file_sys_module.extend_path("file_in_home.txt")) == str(env["home"] / "file_in_home.txt")
    assert str(_file_sys_module.extend_path("temp_file.tmp")) == str(env["temp"] / "temp_file.tmp")

    assert str(_file_sys_module.extend_path("custom_file.dat", search_in=search_dir)) == str(
        env["search_in"] / "custom_file.dat"
    )
    assert str(_file_sys_module.extend_path("custom_file.dat", search_in=search_dirs)) == str(
        env["search_in"] / "custom_file.dat"
    )


def test_extend_path_missing_paths(setup_test_environment: dict[str, Path]):
    assert _file_sys_module.extend_path("non_existent_file.xyz") is None
    with pytest.raises(PathNotFoundError, match="not found in specified directories"):
        _file_sys_module.extend_path("non_existent_file.xyz", raise_error=True)


def test_extend_path_fuzzy_matching(setup_test_environment: dict[str, Path]):
    env = setup_test_environment
    search_dir = str(env["search_in"])
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


def test_extend_or_make_path(setup_test_environment: dict[str, Path]):
    env = setup_test_environment

    assert str(_file_sys_module.extend_or_make_path("file_in_cwd.txt")) == str(env["cwd"] / "file_in_cwd.txt")

    rel_script = "new_dir/new_file.txt"
    assert str(_file_sys_module.extend_or_make_path(rel_script, prefer_script_dir=True)) == str(env["script_dir"] / rel_script)

    rel_cwd = "another_dir/another_file.txt"
    assert str(_file_sys_module.extend_or_make_path(rel_cwd, prefer_script_dir=False)) == str(env["cwd"] / rel_cwd)


def test_extend_path_env_vars_and_absolute_handling():
    with patch.dict(os.environ, {"TEST_ENV_ROOT": "C:\\" if os.name == "nt" else "/"}):
        env_pattern = "%TEST_ENV_ROOT%sample_file" if os.name == "nt" else "$TEST_ENV_ROOT/sample_file"
        _file_sys_module.extend_path(env_pattern)

    with (
        patch("pathlib.Path.is_absolute", return_value=True),
        patch("pathlib.Path.drive", new_callable=PropertyMock, return_value=""),
    ):
        helper = _ExtendPathHelper(Path("dummy_path"), search_dirs=[], fuzzy_match=False, raise_error=False)
        with contextlib.suppress(Exception):
            helper()


def test_find_path_traversal_when_parent_is_file(tmp_path: Path):
    file_path = tmp_path / "sample_file.txt"
    file_path.touch()
    helper = _ExtendPathHelper(Path("sample_file.txt/nested"), search_dirs=[tmp_path], fuzzy_match=True, raise_error=False)
    assert helper() == file_path


def test_get_closest_match_permission_error():
    with patch.object(Path, "iterdir", side_effect=PermissionError("Mocked access error")):
        assert _ExtendPathHelper.get_closest_match(Path("."), "target_name") is None
