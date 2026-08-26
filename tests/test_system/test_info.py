from unittest.mock import patch
import xulbux.system as _system_module


def test_system_is_elevated_windows(monkeypatch):
    monkeypatch.setattr(_system_module._os, "name", "nt")
    with patch("xulbux.system._ctypes") as mock_ctypes:
        mock_ctypes.windll.shell32.IsUserAnAdmin.return_value = 1
        assert _system_module.is_elevated() is True

        mock_ctypes.windll.shell32.IsUserAnAdmin.return_value = 0
        assert _system_module.is_elevated() is False

        mock_ctypes.windll.shell32.IsUserAnAdmin.side_effect = Exception("test")
        assert _system_module.is_elevated() is False


def test_system_is_elevated_posix(monkeypatch):
    monkeypatch.setattr(_system_module._os, "name", "posix")
    with patch("xulbux.system._os.geteuid", create=True) as mock_geteuid:
        mock_geteuid.return_value = 0
        assert _system_module.is_elevated() is True

        mock_geteuid.return_value = 1000
        assert _system_module.is_elevated() is False

        mock_geteuid.side_effect = Exception("test")
        assert _system_module.is_elevated() is False


def test_system_is_elevated_unknown(monkeypatch):
    monkeypatch.setattr(_system_module._os, "name", "java")
    assert _system_module.is_elevated() is False


def test_system_is_win():
    with patch("platform.system", return_value="Windows"):
        assert _system_module.is_win() is True
    with patch("platform.system", return_value="Linux"):
        assert _system_module.is_win() is False


def test_system_is_linux():
    with patch("platform.system", return_value="Linux"):
        assert _system_module.is_linux() is True
    with patch("platform.system", return_value="Windows"):
        assert _system_module.is_linux() is False


def test_system_is_mac():
    with patch("platform.system", return_value="Darwin"):
        assert _system_module.is_mac() is True
    with patch("platform.system", return_value="Windows"):
        assert _system_module.is_mac() is False


def test_system_is_unix(monkeypatch):
    monkeypatch.setattr(_system_module._os, "name", "posix")
    assert _system_module.is_unix() is True

    monkeypatch.setattr(_system_module._os, "name", "nt")
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
