from collections.abc import Callable
from unittest.mock import MagicMock, patch
import xulbux.system as _system_module
import pytest


def test_system_is_elevated_windows_admin(mock_os_windows: None, mock_ctypes_windll: Callable[..., MagicMock]):
    mock_ctypes = mock_ctypes_windll()
    mock_ctypes.shell32.IsUserAnAdmin.return_value = 1
    assert _system_module.is_elevated() is True


def test_system_is_elevated_windows_not_admin(mock_os_windows: None, mock_ctypes_windll: Callable[..., MagicMock]):
    mock_ctypes = mock_ctypes_windll()
    mock_ctypes.shell32.IsUserAnAdmin.return_value = 0
    assert _system_module.is_elevated() is False


def test_system_is_elevated_windows_exception(mock_os_windows: None, mock_ctypes_windll: Callable[..., MagicMock]):
    mock_ctypes = mock_ctypes_windll()
    mock_ctypes.shell32.IsUserAnAdmin.side_effect = Exception("test")
    assert _system_module.is_elevated() is False


def test_system_is_elevated_posix_root(mock_os_linux: None):
    with patch("xulbux.system._os.geteuid", create=True) as mock_geteuid:
        mock_geteuid.return_value = 0
        assert _system_module.is_elevated() is True


def test_system_is_elevated_posix_not_root(mock_os_linux: None):
    with patch("xulbux.system._os.geteuid", create=True) as mock_geteuid:
        mock_geteuid.return_value = 1000
        assert _system_module.is_elevated() is False


def test_system_is_elevated_posix_exception(mock_os_linux: None):
    with patch("xulbux.system._os.geteuid", create=True) as mock_geteuid:
        mock_geteuid.side_effect = Exception("test")
        assert _system_module.is_elevated() is False


def test_system_is_elevated_unknown(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(_system_module._os, "name", "java")
    assert _system_module.is_elevated() is False


def test_system_is_win_true(mock_os_windows: None):
    assert _system_module.is_win() is True


def test_system_is_win_false(mock_os_linux: None):
    assert _system_module.is_win() is False


def test_system_is_linux_true(mock_os_linux: None):
    assert _system_module.is_linux() is True


def test_system_is_linux_false(mock_os_windows: None):
    assert _system_module.is_linux() is False


def test_system_is_mac_true(mock_os_darwin: None):
    assert _system_module.is_mac() is True


def test_system_is_mac_false(mock_os_windows: None):
    assert _system_module.is_mac() is False


def test_system_is_unix_true(mock_os_linux: None):
    assert _system_module.is_unix() is True


def test_system_is_unix_false(mock_os_windows: None):
    assert _system_module.is_unix() is False


def test_system_hostname():
    with patch("socket.gethostname", return_value="myhost"):
        assert _system_module.get_hostname() == "myhost"

    with patch("socket.gethostname", side_effect=Exception("error")):
        assert _system_module.get_hostname() == "unknown"


def test_system_username():
    with patch("getpass.getuser", return_value="myuser"):
        assert _system_module.get_username() == "myuser"

    with patch("getpass.getuser", side_effect=Exception("error")):
        with patch("os.getlogin", return_value="mylogin"):
            assert _system_module.get_username() == "mylogin"

        with patch("os.getlogin", side_effect=Exception("error")):
            assert _system_module.get_username() == "unknown"


def test_system_os_info():
    with patch("platform.system", return_value="TestOS"):
        assert _system_module.get_os_name() == "TestOS"

    with patch("platform.version", return_value="1.0"):
        assert _system_module.get_os_version() == "1.0"

    with patch("platform.version", side_effect=Exception("error")):
        assert _system_module.get_os_version() == "unknown"


def test_system_architecture():
    with patch("platform.machine", return_value="x86_64"):
        assert _system_module.get_architecture() == "x86_64"


def test_system_cpu_count():
    with patch("multiprocessing.cpu_count", return_value=8):
        assert _system_module.get_cpu_count() == 8

    with patch("multiprocessing.cpu_count", side_effect=NotImplementedError()):
        assert _system_module.get_cpu_count() == 1

    with patch("multiprocessing.cpu_count", side_effect=AttributeError()):
        assert _system_module.get_cpu_count() == 1


def test_system_python_version():
    with patch("platform.python_version", return_value="3.11.0"):
        assert _system_module.get_python_version() == "3.11.0"
