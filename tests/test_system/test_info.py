from collections.abc import Callable
from unittest.mock import MagicMock, patch
import xulbux.system as _system_module
import pytest


def test_is_elevated_windows_admin(mock_os_windows: None, mock_ctypes_windll: Callable[..., MagicMock]):
    mock_ctypes = mock_ctypes_windll()
    mock_ctypes.shell32.IsUserAnAdmin.return_value = 1
    assert _system_module.is_elevated() is True


def test_is_elevated_windows_non_admin(mock_os_windows: None, mock_ctypes_windll: Callable[..., MagicMock]):
    mock_ctypes = mock_ctypes_windll()
    mock_ctypes.shell32.IsUserAnAdmin.return_value = 0
    assert _system_module.is_elevated() is False


def test_is_elevated_windows_exception(mock_os_windows: None, mock_ctypes_windll: Callable[..., MagicMock]):
    mock_ctypes = mock_ctypes_windll()
    mock_ctypes.shell32.IsUserAnAdmin.side_effect = OSError("Access denied")
    assert _system_module.is_elevated() is False


def test_is_elevated_posix_root(mock_os_linux: None):
    with patch("xulbux.system._os.geteuid", create=True) as mock_geteuid:
        mock_geteuid.return_value = 0
        assert _system_module.is_elevated() is True


def test_is_elevated_posix_non_root(mock_os_linux: None):
    with patch("xulbux.system._os.geteuid", create=True) as mock_geteuid:
        mock_geteuid.return_value = 1000
        assert _system_module.is_elevated() is False


def test_is_elevated_posix_exception(mock_os_linux: None):
    with patch("xulbux.system._os.geteuid", create=True) as mock_geteuid:
        mock_geteuid.side_effect = OSError("Call failed")
        assert _system_module.is_elevated() is False


def test_is_elevated_unknown_os(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(_system_module._os, "name", "unknown_os")
    assert _system_module.is_elevated() is False


def test_is_win_detection(mock_os_windows: None):
    assert _system_module.is_win() is True


def test_is_win_false_on_linux(mock_os_linux: None):
    assert _system_module.is_win() is False


def test_is_linux_detection(mock_os_linux: None):
    assert _system_module.is_linux() is True


def test_is_linux_false_on_windows(mock_os_windows: None):
    assert _system_module.is_linux() is False


def test_is_mac_detection(mock_os_darwin: None):
    assert _system_module.is_mac() is True


def test_is_mac_false_on_windows(mock_os_windows: None):
    assert _system_module.is_mac() is False


def test_is_unix_detection(mock_os_linux: None):
    assert _system_module.is_unix() is True


def test_is_unix_false_on_windows(mock_os_windows: None):
    assert _system_module.is_unix() is False


def test_get_hostname_success_and_fallback():
    with patch("socket.gethostname", return_value="my_machine"):
        assert _system_module.get_hostname() == "my_machine"

    with patch("socket.gethostname", side_effect=OSError("Network error")):
        assert _system_module.get_hostname() == "unknown"


def test_get_username_success_and_fallbacks():
    with patch("getpass.getuser", return_value="current_user"):
        assert _system_module.get_username() == "current_user"

    with patch("getpass.getuser", side_effect=KeyError("No user")):
        with patch("os.getlogin", return_value="login_user"):
            assert _system_module.get_username() == "login_user"

        with patch("os.getlogin", side_effect=OSError("No login")):
            assert _system_module.get_username() == "unknown"


def test_get_os_information():
    with patch("platform.system", return_value="CustomOS"):
        assert _system_module.get_os_name() == "CustomOS"

    with patch("platform.version", return_value="10.0.1"):
        assert _system_module.get_os_version() == "10.0.1"

    with patch("platform.version", side_effect=RuntimeError("Version lookup failed")):
        assert _system_module.get_os_version() == "unknown"

    with patch("platform.machine", return_value="x86_64"):
        assert _system_module.get_architecture() == "x86_64"

    with patch("platform.python_version", return_value="3.14.0"):
        assert _system_module.get_python_version() == "3.14.0"


def test_get_cpu_count_with_fallbacks():
    with patch("multiprocessing.cpu_count", return_value=16):
        assert _system_module.get_cpu_count() == 16

    with patch("multiprocessing.cpu_count", side_effect=NotImplementedError):
        assert _system_module.get_cpu_count() == 1

    with patch("multiprocessing.cpu_count", side_effect=AttributeError):
        assert _system_module.get_cpu_count() == 1
