from pathlib import Path
from unittest.mock import MagicMock, patch
import xulbux.system as _system_module
import pytest


def test_paths_as_path_and_as_list() -> None:
    path_single = _system_module.get_env_path()
    paths_list = _system_module.get_env_path(as_list=True)

    assert isinstance(path_single, Path)
    assert isinstance(paths_list, list)
    assert all(isinstance(item, Path) for item in paths_list)


def test_has_path_detection() -> None:
    if current_paths := _system_module.get_env_path(as_list=True):
        assert _system_module.has_env_path(current_paths[0]) is True

    assert _system_module.has_env_path(Path("non_existent_folder_xyz_12345")) is False


def test_add_path_and_remove_path_lifecycle() -> None:
    sample_path = Path("custom_test_env_path_entry")

    with patch("xulbux.system.has_env_path") as mock_has_path, patch("xulbux.system._persistent_env_path") as mock_persistent:
        mock_has_path.return_value = False
        _system_module.add_env_path(sample_path)
        mock_persistent.assert_called_once_with(sample_path)

    with patch("xulbux.system.has_env_path") as mock_has_path, patch("xulbux.system._persistent_env_path") as mock_persistent:
        mock_has_path.return_value = True
        _system_module.add_env_path(sample_path)
        mock_persistent.assert_not_called()

    with patch("xulbux.system.has_env_path") as mock_has_path, patch("xulbux.system._persistent_env_path") as mock_persistent:
        mock_has_path.return_value = True
        _system_module.remove_env_path(sample_path)
        mock_persistent.assert_called_once_with(sample_path, remove=True)

    with patch("xulbux.system.has_env_path") as mock_has_path, patch("xulbux.system._persistent_env_path") as mock_persistent:
        mock_has_path.return_value = False
        _system_module.remove_env_path(sample_path)
        mock_persistent.assert_not_called()


def test_get_path_resolution_options() -> None:
    with patch("xulbux.file_sys.get_cwd", return_value=Path("/mock/cwd")):
        assert _system_module._get_env_path_target(cwd=True) == Path("/mock/cwd")

    with patch("xulbux.file_sys.get_script_dir", return_value=Path("/mock/script")):
        assert _system_module._get_env_path_target(base_dir=True) == Path("/mock/script")

    assert _system_module._get_env_path_target("some/str/path") == Path("some/str/path")
    assert _system_module._get_env_path_target(Path("some/path/obj")) == Path("some/path/obj")


def test_get_validation_errors() -> None:
    with pytest.raises(ValueError, match="Both 'cwd' and 'base_dir' cannot be True"):
        _system_module._get_env_path_target(cwd=True, base_dir=True)

    with pytest.raises(ValueError, match="No path provided"):
        _system_module._get_env_path_target(None)


def test_persistent_windows_success_and_failure(mock_os_windows: None) -> None:
    mock_winreg = MagicMock()
    with patch.dict("os.environ"), patch.dict("sys.modules", {"winreg": mock_winreg}):
        _system_module._persistent_env_path(Path("test_path"))
        mock_winreg.SetValueEx.assert_called_once()

    mock_winreg_err = MagicMock()
    mock_winreg_err.OpenKey.side_effect = OSError("Access denied")
    with (
        patch.dict("os.environ"),
        patch.dict("sys.modules", {"winreg": mock_winreg_err}),
        pytest.raises(RuntimeError, match="Failed to update PATH"),
    ):
        _system_module._persistent_env_path(Path("test_path"))


def test_persistent_unix_add_and_remove(mock_os_linux: None, mock_subprocess_run: MagicMock) -> None:
    sample_target = Path("test_bin_dir")

    with (
        patch.dict("os.environ"),
        patch("pathlib.Path.exists", return_value=True),
        patch("builtins.open") as mock_open,
        patch("xulbux.system.Path.home", return_value=Path(".")),
    ):
        file_handle = MagicMock()
        file_handle.read.return_value = 'export PATH="/usr/bin"\n'
        mock_open.return_value.__enter__.return_value = file_handle

        _system_module._persistent_env_path(sample_target, remove=False)
        _system_module._persistent_env_path(sample_target, remove=True)


def test_persistent_add_already_existing_path_in_list(mock_os_linux: None, mock_subprocess_run: MagicMock) -> None:
    if existing_paths := _system_module.get_env_path(as_list=True):
        with (
            patch.dict("os.environ"),
            patch("builtins.open"),
            patch("pathlib.Path.exists", return_value=True),
            patch("xulbux.system.Path.home", return_value=Path(".")),
        ):
            _system_module._persistent_env_path(existing_paths[0], remove=False)
