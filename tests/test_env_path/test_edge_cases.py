from pathlib import Path
from unittest.mock import MagicMock, patch
from xulbux import env_path
import pytest


def test_add_path_already_exists():
    path = "already"
    with patch("xulbux.env_path.has_path", return_value=True), patch("xulbux.env_path._persistent") as mock_pers:
        env_path.add_path(path)
        mock_pers.assert_not_called()


def test_remove_path_not_exists():
    path = "not_there"
    with patch("xulbux.env_path.has_path", return_value=False), patch("xulbux.env_path._persistent") as mock_pers:
        env_path.remove_path(path)
        mock_pers.assert_not_called()


def test_get_exceptions():
    with pytest.raises(ValueError, match="Both 'cwd' and 'base_dir' cannot be True"):
        env_path._get(cwd=True, base_dir=True)

    with pytest.raises(ValueError, match="No path provided"):
        env_path._get(None)


def test_get_cwd():
    with patch("xulbux.file_sys.get_cwd", return_value=Path(".")):
        assert env_path._get(cwd=True) == Path(".")


def test_persistent_windows_success(mock_os_windows: None):
    mock_winreg = MagicMock()
    with patch.dict("sys.modules", {"winreg": mock_winreg}):
        env_path._persistent(Path("test"))


def test_persistent_windows_error(mock_os_windows: None):
    mock_winreg = MagicMock()
    mock_winreg.OpenKey.side_effect = Exception("mocked error")
    with patch.dict("sys.modules", {"winreg": mock_winreg}), pytest.raises(RuntimeError):
        env_path._persistent(Path("test"))


def test_persistent_unix(mock_os_linux: None, mock_subprocess_run: MagicMock):
    with patch("xulbux.env_path.Path.home") as mock_home:
        mock_home.return_value = MagicMock()
        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("builtins.open") as mock_open,
            patch("xulbux.env_path.Path", return_value=MagicMock()),
        ):
            mock_file = MagicMock()
            mock_file.read.return_value = "export PATH=old"
            mock_open.return_value.__enter__.return_value = mock_file
            mock_path = MagicMock()
            env_path._persistent(mock_path)
            env_path._persistent(mock_path, remove=True)


def test_persistent_add_existing(mock_os_linux: None, mock_subprocess_run: MagicMock):
    with (
        patch("builtins.open"),
        patch("pathlib.Path.exists", return_value=True),
        patch("xulbux.env_path.Path.home", return_value=MagicMock()),
        patch("xulbux.env_path.Path", return_value=MagicMock()),
    ):
        current = env_path.paths(as_list=True)
        if current:
            env_path._persistent(current[0], remove=False)
