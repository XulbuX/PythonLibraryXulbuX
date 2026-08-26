from pathlib import Path
from unittest.mock import MagicMock, patch
from xulbux import env_path
import pytest


def test_paths_as_path_and_as_list():
    path_single = env_path.paths()
    paths_list = env_path.paths(as_list=True)

    assert isinstance(path_single, Path)
    assert isinstance(paths_list, list)
    assert all(isinstance(item, Path) for item in paths_list)


def test_has_path_detection():
    current_paths = env_path.paths(as_list=True)
    if current_paths:
        assert env_path.has_path(current_paths[0]) is True

    assert env_path.has_path(Path("non_existent_folder_xyz_12345")) is False


def test_add_path_and_remove_path_lifecycle():
    sample_path = Path("custom_test_env_path_entry")

    with patch("xulbux.env_path.has_path") as mock_has_path, patch("xulbux.env_path._persistent") as mock_persistent:
        mock_has_path.return_value = False
        env_path.add_path(sample_path)
        mock_persistent.assert_called_once_with(sample_path)

    with patch("xulbux.env_path.has_path") as mock_has_path, patch("xulbux.env_path._persistent") as mock_persistent:
        mock_has_path.return_value = True
        env_path.add_path(sample_path)
        mock_persistent.assert_not_called()

    with patch("xulbux.env_path.has_path") as mock_has_path, patch("xulbux.env_path._persistent") as mock_persistent:
        mock_has_path.return_value = True
        env_path.remove_path(sample_path)
        mock_persistent.assert_called_once_with(sample_path, remove=True)

    with patch("xulbux.env_path.has_path") as mock_has_path, patch("xulbux.env_path._persistent") as mock_persistent:
        mock_has_path.return_value = False
        env_path.remove_path(sample_path)
        mock_persistent.assert_not_called()


def test_get_path_resolution_options():
    with patch("xulbux.file_sys.get_cwd", return_value=Path("/mock/cwd")):
        assert env_path._get(cwd=True) == Path("/mock/cwd")

    with patch("xulbux.file_sys.get_script_dir", return_value=Path("/mock/script")):
        assert env_path._get(base_dir=True) == Path("/mock/script")

    assert env_path._get("some/str/path") == Path("some/str/path")
    assert env_path._get(Path("some/path/obj")) == Path("some/path/obj")


def test_get_validation_errors():
    with pytest.raises(ValueError, match="Both 'cwd' and 'base_dir' cannot be True"):
        env_path._get(cwd=True, base_dir=True)

    with pytest.raises(ValueError, match="No path provided"):
        env_path._get(None)


def test_persistent_windows_success_and_failure(mock_os_windows: None):
    mock_winreg = MagicMock()
    with patch.dict("sys.modules", {"winreg": mock_winreg}):
        env_path._persistent(Path("test_path"))
        mock_winreg.SetValueEx.assert_called_once()

    mock_winreg_err = MagicMock()
    mock_winreg_err.OpenKey.side_effect = OSError("Access denied")
    with patch.dict("sys.modules", {"winreg": mock_winreg_err}), pytest.raises(RuntimeError, match="Failed to update PATH"):
        env_path._persistent(Path("test_path"))


def test_persistent_unix_add_and_remove(monkeypatch: pytest.MonkeyPatch, mock_subprocess_run: MagicMock):
    monkeypatch.setattr("sys.platform", "linux")
    sample_target = Path("test_bin_dir")

    with (
        patch("pathlib.Path.exists", return_value=True),
        patch("builtins.open") as mock_open,
        patch("xulbux.env_path.Path.home", return_value=Path(".")),
    ):
        file_handle = MagicMock()
        file_handle.read.return_value = 'export PATH="/usr/bin"\n'
        mock_open.return_value.__enter__.return_value = file_handle

        env_path._persistent(sample_target, remove=False)
        env_path._persistent(sample_target, remove=True)


def test_persistent_add_already_existing_path_in_list(monkeypatch: pytest.MonkeyPatch, mock_subprocess_run: MagicMock):
    monkeypatch.setattr("sys.platform", "linux")
    existing_paths = env_path.paths(as_list=True)
    if existing_paths:
        with (
            patch("builtins.open"),
            patch("pathlib.Path.exists", return_value=True),
            patch("xulbux.env_path.Path.home", return_value=Path(".")),
        ):
            env_path._persistent(existing_paths[0], remove=False)
