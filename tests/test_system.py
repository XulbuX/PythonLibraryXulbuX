import os
import platform
from unittest.mock import MagicMock, patch
from xulbux.system import System
import pytest

#
###################################################### System TESTS ######################################################


def test_system_is_elevated():
    result = System.is_elevated
    assert isinstance(result, bool)


def test_system_is_win():
    result = System.is_win
    assert isinstance(result, bool)
    assert result == (platform.system() == "Windows")


def test_system_is_linux():
    result = System.is_linux
    assert isinstance(result, bool)
    assert result == (platform.system() == "Linux")


def test_system_is_mac():
    result = System.is_mac
    assert isinstance(result, bool)
    assert result == (platform.system() == "Darwin")


def test_system_is_unix():
    result = System.is_unix
    assert isinstance(result, bool)
    current_system = platform.system()
    expected = current_system in ["Linux", "Darwin"] or "BSD" in current_system
    assert result == expected


def test_system_hostname():
    hostname = System.hostname
    assert isinstance(hostname, str)
    assert hostname != ""


def test_system_username():
    username = System.username
    assert isinstance(username, str)
    assert username != ""


def test_system_os_info():
    """Test OS name and version properties"""
    os_name = System.os_name
    assert isinstance(os_name, str)
    assert os_name != ""
    assert os_name in ["Windows", "Linux", "Darwin"] or os_name != ""

    os_version = System.os_version
    assert isinstance(os_version, str)
    assert os_version != ""


def test_system_architecture():
    architecture = System.architecture
    assert isinstance(architecture, str)
    assert architecture != ""
    assert any(arch in architecture.lower() for arch in ["x86", "amd64", "arm", "aarch", "i386", "i686"])


def test_system_cpu_count():
    cpu_count = System.cpu_count
    assert isinstance(cpu_count, int)
    assert cpu_count >= 1


def test_system_python_version():
    python_version = System.python_version
    assert isinstance(python_version, str)
    assert python_version != ""
    parts = python_version.split(".")
    assert len(parts) >= 2
    assert all(part.isdigit() for part in parts[:2])


def test_check_libs_existing_modules():
    """Test check_libs with existing modules"""
    result = System.check_libs(["os", "sys", "json"])
    assert result is None


def test_check_libs_nonexistent_module():
    """Test check_libs with nonexistent module returns list"""
    result = System.check_libs(["nonexistent_module_12345"], install_missing=False)
    assert isinstance(result, list)
    assert "nonexistent_module_12345" in result


@patch("xulbux.system._subprocess.check_call")
@patch("xulbux.console.Console.confirm", return_value=False)  # Decline installation.
def test_check_libs_decline_install(mock_confirm: MagicMock, mock_subprocess: MagicMock):
    """Test check_libs when user declines installation"""
    result = System.check_libs(["nonexistent_module_12345"], install_missing=True)
    assert isinstance(result, list)
    assert "nonexistent_module_12345" in result
    mock_subprocess.assert_not_called()


@patch("xulbux.system._platform.system")
@patch("xulbux.system._subprocess.check_output")
@patch("xulbux.system._subprocess.run")
def test_restart_windows_simple(mock_subprocess_run: MagicMock, mock_check_output: MagicMock, mock_platform: MagicMock):
    """Test simple restart on Windows"""
    mock_platform.return_value = "Windows"
    mock_check_output.return_value = b"minimal\nprocess\nlist\n"
    System.restart()
    mock_subprocess_run.assert_called_once_with(["shutdown", "/r", "/t", "0"])


@patch("xulbux.system._platform.system")
@patch("xulbux.system._subprocess.check_output")
def test_restart_too_many_processes(mock_subprocess: MagicMock, mock_platform: MagicMock):
    """Test restart fails when too many processes running"""
    mock_platform.return_value = "Windows"
    mock_subprocess.return_value = b"many\nprocess\nlines\nhere\nmore\nprocesses\neven\nmore\n"
    with pytest.raises(RuntimeError, match="Processes are still running"):
        System.restart()


@patch("xulbux.system._platform.system")
@patch("xulbux.system._subprocess.check_output")
def test_restart_unsupported_system(mock_subprocess: MagicMock, mock_platform: MagicMock):
    """Test restart on unsupported system"""
    mock_platform.return_value = "Unknown"
    mock_subprocess.return_value = b"some output"
    with pytest.raises(NotImplementedError, match="Restart not implemented for 'unknown' systems."):
        System.restart()


@pytest.mark.skipif(os.name != "nt", reason="Windows-specific test")
@patch("xulbux.system._ctypes")
def test_elevate_windows_already_elevated(mock_ctypes: MagicMock):
    """Test elevate on WINDOWS when already elevated"""
    # Setup the mock to return true for `IsUserAnAdmin`:
    mock_ctypes.windll.shell32.IsUserAnAdmin.return_value = 1

    result = System.elevate()
    assert result is True


@pytest.mark.skipif(os.name == "nt", reason="POSIX-specific test")
@patch("xulbux.system._os.geteuid")
def test_elevate_posix_already_elevated(mock_geteuid: MagicMock):
    """Test elevate on POSIX when already elevated"""
    mock_geteuid.return_value = 0
    result = System.elevate()
    assert result is True
