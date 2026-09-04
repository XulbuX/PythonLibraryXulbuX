import subprocess
from unittest.mock import MagicMock, patch
import xulbux.system as _system_module
import pytest


def test_restart_negative_wait_raises_value_error() -> None:
    with pytest.raises(ValueError, match="must be non-negative"):
        _system_module.restart(wait=-1)


def test_restart_unsupported_system_raises_not_implemented() -> None:
    with (
        patch("platform.system", return_value="FreeBSD"),
        pytest.raises(NotImplementedError, match="Restart not implemented for 'freebsd' systems"),
    ):
        _system_module.restart()


def test_restart_windows_without_prompt(
    mock_subprocess_run: MagicMock, mock_subprocess_check_output: MagicMock, mock_os_windows: None
) -> None:
    mock_subprocess_check_output.return_value = b"Header1\nHeader2\nHeader3\n"
    _system_module.restart()
    mock_subprocess_run.assert_called_once_with(["shutdown", "/r", "/t", "0"])


def test_restart_windows_with_prompt_and_wait(
    mock_subprocess_run: MagicMock, mock_subprocess_check_output: MagicMock, mock_os_windows: None
) -> None:
    mock_subprocess_check_output.return_value = b"Header1\nHeader2\nHeader3\npython.exe\n"
    with patch("time.sleep") as mock_sleep, patch("builtins.print") as mock_print:
        _system_module.restart("Restart scheduled", wait=5, continue_program=True)
        mock_subprocess_run.assert_called_once_with(["shutdown", "/r", "/t", "5", "/c", "Restart scheduled"])
        mock_sleep.assert_called_once_with(5)
        mock_print.assert_called_once_with("Restarting in 5 seconds...")


def test_restart_windows_running_processes_prevent_restart(
    mock_subprocess_check_output: MagicMock, mock_os_windows: None
) -> None:
    mock_subprocess_check_output.return_value = b"1\n2\n3\nnotepad.exe\n"
    with pytest.raises(RuntimeError, match="Processes are still running"):
        _system_module.restart()


def test_restart_windows_force_bypasses_running_process_check(
    mock_subprocess_run: MagicMock, mock_subprocess_check_output: MagicMock, mock_os_windows: None
) -> None:
    _system_module.restart(force=True)
    mock_subprocess_check_output.assert_not_called()
    mock_subprocess_run.assert_called_once_with(["shutdown", "/r", "/t", "0"])


def test_restart_posix_with_prompt_and_notify_send(
    mock_subprocess_run: MagicMock,
    mock_subprocess_check_output: MagicMock,
    mock_subprocess_popen: MagicMock,
    mock_os_linux: None,
) -> None:
    with patch("xulbux.system._shutil.which", return_value=True):
        mock_subprocess_check_output.return_value = b"PID TTY TIME CMD\n 1234 ? 00:00:00 bash\n"
        with patch("time.sleep"):
            _system_module.restart("Rebooting now", wait=1)
            mock_subprocess_popen.assert_called_once_with(["notify-send", "System Restart", "Rebooting now"])
            mock_subprocess_run.assert_called_once_with(["sudo", "shutdown", "-r", "now"])


def test_restart_posix_with_prompt_fallback_console_info(
    mock_subprocess_run: MagicMock, mock_subprocess_check_output: MagicMock, mock_os_darwin: None
) -> None:
    with patch("xulbux.system._shutil.which", return_value=False):
        mock_subprocess_check_output.return_value = b"PID TTY TIME CMD\n 1234 ? 00:00:00 zsh\n"
        with patch("time.sleep"), patch("xulbux.console.info") as mock_info, patch("builtins.print") as mock_print:
            _system_module.restart("Rebooting now", wait=1, continue_program=True)
            mock_info.assert_called_once_with("System Restart: Rebooting now")
            mock_subprocess_run.assert_called_once_with(["sudo", "shutdown", "-r", "now"])
            mock_print.assert_called_once_with("Restarting in 1 seconds...")


def test_restart_posix_insufficient_privileges(
    mock_subprocess_run: MagicMock, mock_subprocess_check_output: MagicMock, mock_os_linux: None
) -> None:
    mock_subprocess_check_output.return_value = b"PID TTY TIME CMD\n"
    mock_subprocess_run.side_effect = subprocess.CalledProcessError(1, "sudo")
    with pytest.raises(PermissionError, match="insufficient privileges"):
        _system_module.restart()


def test_restart_check_processes_string_command(mock_subprocess_check_output: MagicMock) -> None:
    helper = _system_module._SystemRestartHelper("", wait=0, continue_program=False, force=False)
    mock_subprocess_check_output.return_value = b"cmd\npython\n"
    helper.check_running_processes("tasklist")
    mock_subprocess_check_output.assert_called_once_with("tasklist", shell=True)


def test_restart_check_processes_empty_lines_filtered(mock_subprocess_check_output: MagicMock) -> None:
    helper = _system_module._SystemRestartHelper("", wait=0, continue_program=False, force=False)
    mock_subprocess_check_output.return_value = b"cmd\n\n\npython\n"
    helper.check_running_processes(["ps", "-A"])
    mock_subprocess_check_output.assert_called_once_with(["ps", "-A"])
