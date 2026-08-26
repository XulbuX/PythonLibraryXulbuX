import subprocess
from unittest.mock import patch
import xulbux.system as _system_module
import pytest


def test_restart_invalid_wait():
    with pytest.raises(ValueError, match="must be non-negative"):
        _system_module.restart(wait=-1)


def test_restart_unsupported_system():
    with (
        patch("platform.system", return_value="Unknown"),
        pytest.raises(NotImplementedError, match="Restart not implemented for 'unknown' systems"),
    ):
        _system_module.restart()


@patch("xulbux.system._subprocess.check_output")
@patch("xulbux.system._subprocess.run")
def test_restart_windows_no_prompt(mock_run, mock_check_output):
    with patch("platform.system", return_value="Windows"):
        mock_check_output.return_value = b"Header1\nHeader2\nHeader3\n"
        _system_module.restart()
        mock_run.assert_called_once_with(["shutdown", "/r", "/t", "0"])


@patch("xulbux.system._subprocess.check_output")
@patch("xulbux.system._subprocess.run")
def test_restart_windows_with_prompt_and_wait(mock_run, mock_check_output):
    with patch("platform.system", return_value="Windows"):
        mock_check_output.return_value = b"Header1\nHeader2\nHeader3\npython.exe\n"
        with patch("time.sleep") as mock_sleep, patch("builtins.print") as mock_print:
            _system_module.restart("Restarting!", wait=5, continue_program=True)
            mock_run.assert_called_once_with(["shutdown", "/r", "/t", "5", "/c", "Restarting!"])
            mock_sleep.assert_called_once_with(5)
            mock_print.assert_called_once_with("Restarting in 5 seconds...")


@patch("xulbux.system._subprocess.check_output")
def test_restart_windows_processes_running(mock_check_output):
    with patch("platform.system", return_value="Windows"):
        # Not a python or shell process
        mock_check_output.return_value = b"1\n2\n3\nchrome.exe\n"
        with pytest.raises(RuntimeError, match="Processes are still running"):
            _system_module.restart()


@patch("xulbux.system._subprocess.check_output")
@patch("xulbux.system._subprocess.run")
def test_restart_windows_force(mock_run, mock_check_output):
    with patch("platform.system", return_value="Windows"):
        _system_module.restart(force=True)
        mock_check_output.assert_not_called()
        mock_run.assert_called_once_with(["shutdown", "/r", "/t", "0"])


@patch("xulbux.system._subprocess.check_output")
@patch("xulbux.system._subprocess.run")
@patch("xulbux.system._subprocess.Popen")
@patch("xulbux.system._shutil.which", return_value=True)
def test_restart_posix_with_prompt_notify_send(mock_which, mock_popen, mock_run, mock_check_output):
    with patch("platform.system", return_value="Linux"):
        mock_check_output.return_value = b"PID TTY TIME CMD\n 1234 ? 00:00:00 bash\n"
        with patch("time.sleep"):
            _system_module.restart("Reboot now", wait=1)
            mock_popen.assert_called_once_with(["notify-send", "System Restart", "Reboot now"])
            mock_run.assert_called_once_with(["sudo", "shutdown", "-r", "now"])


@patch("xulbux.system._subprocess.check_output")
@patch("xulbux.system._subprocess.run")
@patch("xulbux.system._shutil.which", return_value=False)
def test_restart_posix_with_prompt_no_notify_send(mock_which, mock_run, mock_check_output):
    with patch("platform.system", return_value="Darwin"):
        mock_check_output.return_value = b"PID TTY TIME CMD\n 1234 ? 00:00:00 zsh\n"
        with patch("time.sleep"), patch("xulbux.console.info") as mock_info, patch("builtins.print") as mock_print:
            _system_module.restart("Reboot now", wait=1, continue_program=True)
            mock_info.assert_called_once_with("System Restart: Reboot now")
            mock_run.assert_called_once_with(["sudo", "shutdown", "-r", "now"])
            mock_print.assert_called_once_with("Restarting in 1 seconds...")


@patch("xulbux.system._subprocess.check_output")
@patch("xulbux.system._subprocess.run")
def test_restart_posix_run_error(mock_run, mock_check_output):
    with patch("platform.system", return_value="Linux"):
        mock_check_output.return_value = b"PID TTY TIME CMD\n"
        mock_run.side_effect = subprocess.CalledProcessError(1, "sudo")
        with pytest.raises(PermissionError, match="insufficient privileges"):
            _system_module.restart()


def test_restart_check_processes_string_command():
    helper = _system_module._SystemRestartHelper("", wait=0, continue_program=False, force=False)
    with patch("xulbux.system._subprocess.check_output", return_value=b"cmd\npython\n") as mock_check_output:
        helper.check_running_processes("tasklist")
        mock_check_output.assert_called_once_with("tasklist", shell=True)


def test_restart_check_processes_empty_line():
    helper = _system_module._SystemRestartHelper("", wait=0, continue_program=False, force=False)
    with patch("xulbux.system._subprocess.check_output", return_value=b"cmd\n\n\npython\n") as mock_check_output:
        helper.check_running_processes(["ps", "-A"])
        mock_check_output.assert_called_once_with(["ps", "-A"])
