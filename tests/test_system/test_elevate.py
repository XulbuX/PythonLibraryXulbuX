from unittest.mock import MagicMock, patch
import xulbux.system as _system_module
import pytest


def test_elevate_already_elevated():
    with patch("xulbux.system.is_elevated", return_value=True):
        assert _system_module.elevate() is True


def test_elevate_windows_success(monkeypatch):
    monkeypatch.setattr(_system_module._os, "name", "nt")
    with (
        patch("xulbux.system.is_elevated", return_value=False),
        patch("xulbux.system._ctypes.windll.shell32.ShellExecuteW", return_value=42) as mock_shell_execute,
    ):
        with pytest.raises(SystemExit) as exc_info:
            _system_module.elevate(win_title="My Title", args=["--arg1", "val1"])
        assert exc_info.value.code == 0

        mock_shell_execute.assert_called_once()
        args_passed = mock_shell_execute.call_args[0][3]
        assert "My Title" in args_passed
        assert "--arg1 val1" in args_passed


def test_elevate_windows_no_title(monkeypatch):
    monkeypatch.setattr(_system_module._os, "name", "nt")
    with (
        patch("xulbux.system.is_elevated", return_value=False),
        patch("xulbux.system._ctypes.windll.shell32.ShellExecuteW", return_value=42) as mock_shell_execute,
    ):
        with pytest.raises(SystemExit):
            _system_module.elevate()

        mock_shell_execute.assert_called_once()
        args_passed = mock_shell_execute.call_args[0][3]
        assert "SetConsoleTitleW" not in args_passed


def test_elevate_windows_failure(monkeypatch):
    monkeypatch.setattr(_system_module._os, "name", "nt")
    with (
        patch("xulbux.system.is_elevated", return_value=False),
        patch("xulbux.system._ctypes.windll.shell32.ShellExecuteW", return_value=5),
        pytest.raises(PermissionError, match="Failed to launch elevated process"),
    ):
        _system_module.elevate()


def test_elevate_posix_success(monkeypatch):
    monkeypatch.setattr(_system_module._os, "name", "posix")
    with patch("xulbux.system.is_elevated", return_value=False), patch("xulbux.system._subprocess.Popen") as mock_popen:
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_popen.return_value = mock_proc

        with pytest.raises(SystemExit) as exc_info:
            _system_module.elevate(win_title="My Posix Title", args=["--arg2"])
        assert exc_info.value.code == 0

        mock_popen.assert_called_once()
        cmd_passed = mock_popen.call_args[0][0]
        assert cmd_passed[0] == "pkexec"
        assert "--description" in cmd_passed
        assert "My Posix Title" in cmd_passed
        assert "--arg2" in cmd_passed


def test_elevate_posix_no_title(monkeypatch):
    monkeypatch.setattr(_system_module._os, "name", "posix")
    with patch("xulbux.system.is_elevated", return_value=False), patch("xulbux.system._subprocess.Popen") as mock_popen:
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_popen.return_value = mock_proc

        with pytest.raises(SystemExit):
            _system_module.elevate()

        mock_popen.assert_called_once()
        cmd_passed = mock_popen.call_args[0][0]
        assert "--description" not in cmd_passed


def test_elevate_posix_failure(monkeypatch):
    monkeypatch.setattr(_system_module._os, "name", "posix")
    with patch("xulbux.system.is_elevated", return_value=False), patch("xulbux.system._subprocess.Popen") as mock_popen:
        mock_proc = MagicMock()
        mock_proc.returncode = 1
        mock_popen.return_value = mock_proc

        with pytest.raises(PermissionError, match="Process elevation was denied"):
            _system_module.elevate()
