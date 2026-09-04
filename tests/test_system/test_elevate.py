from collections.abc import Callable
from unittest.mock import MagicMock, patch
import xulbux.system as _system_module
import pytest


def test_elevate_already_elevated_returns_true() -> None:
    with patch("xulbux.system.is_elevated", return_value=True):
        assert _system_module.elevate() is True


def test_elevate_windows_success(mock_os_windows: None, mock_ctypes_windll: Callable[..., MagicMock]) -> None:
    with patch("xulbux.system.is_elevated", return_value=False):
        mock_windll = mock_ctypes_windll(42)
        with pytest.raises(SystemExit) as exc_info:
            _system_module.elevate(win_title="Elevated Window", args=["--flag", "value"])
        assert exc_info.value.code == 0

        mock_windll.shell32.ShellExecuteW.assert_called_once()
        args_passed = mock_windll.shell32.ShellExecuteW.call_args[0][3]
        assert "Elevated Window" in args_passed
        assert "--flag value" in args_passed


def test_elevate_windows_without_title(mock_os_windows: None, mock_ctypes_windll: Callable[..., MagicMock]) -> None:
    with patch("xulbux.system.is_elevated", return_value=False):
        mock_windll = mock_ctypes_windll(42)
        with pytest.raises(SystemExit) as exc_info:
            _system_module.elevate()
        assert exc_info.value.code == 0

        mock_windll.shell32.ShellExecuteW.assert_called_once()
        args_passed = mock_windll.shell32.ShellExecuteW.call_args[0][3]
        assert "SetConsoleTitleW" not in args_passed


def test_elevate_windows_failure_raises_permission_error(
    mock_os_windows: None, mock_ctypes_windll: Callable[..., MagicMock]
) -> None:
    with (
        patch("xulbux.system.is_elevated", return_value=False),
        pytest.raises(PermissionError, match="Failed to launch elevated process"),
    ):
        mock_ctypes_windll(5)
        _system_module.elevate()


def test_elevate_posix_success(mock_os_linux: None, mock_subprocess_popen: MagicMock) -> None:
    with patch("xulbux.system.is_elevated", return_value=False):
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_subprocess_popen.return_value = mock_proc

        with pytest.raises(SystemExit) as exc_info:
            _system_module.elevate(win_title="Posix Prompt", args=["--opt"])
        assert exc_info.value.code == 0

        mock_subprocess_popen.assert_called_once()
        cmd_args = mock_subprocess_popen.call_args[0][0]
        assert cmd_args[0] == "pkexec"
        assert "--description" in cmd_args
        assert "Posix Prompt" in cmd_args


def test_elevate_posix_without_title(mock_os_linux: None, mock_subprocess_popen: MagicMock) -> None:
    with patch("xulbux.system.is_elevated", return_value=False):
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_subprocess_popen.return_value = mock_proc

        with pytest.raises(SystemExit) as exc_info:
            _system_module.elevate()
        assert exc_info.value.code == 0

        cmd_args = mock_subprocess_popen.call_args[0][0]
        assert "--description" not in cmd_args


def test_elevate_posix_denied_raises_permission_error(mock_os_linux: None, mock_subprocess_popen: MagicMock) -> None:
    with patch("xulbux.system.is_elevated", return_value=False):
        mock_proc = MagicMock()
        mock_proc.returncode = 1
        mock_subprocess_popen.return_value = mock_proc

        with pytest.raises(PermissionError, match="Process elevation was denied"):
            _system_module.elevate()
