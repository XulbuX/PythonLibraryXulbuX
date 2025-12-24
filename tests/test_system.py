from xulbux.system import System

from unittest.mock import patch
import platform
import pytest
import os

#
################################################## System TESTS ##################################################


def test_system_is_elevated():
    result = System.is_elevated
    assert isinstance(result, bool)


def test_system_is_win():
    result = System.is_win
    assert isinstance(result, bool)
    assert result == (platform.system() == "Windows")


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
@patch("xulbux.console.Console.confirm", return_value=False)  # DECLINE INSTALLATION
def test_check_libs_decline_install(mock_confirm, mock_subprocess):
    """Test check_libs when user declines installation"""
    result = System.check_libs(["nonexistent_module_12345"], install_missing=True)
    assert isinstance(result, list)
    assert "nonexistent_module_12345" in result
    mock_subprocess.assert_not_called()


@patch("xulbux.system._platform.system")
@patch("xulbux.system._subprocess.check_output")
@patch("xulbux.system._os.system")
def test_restart_windows_simple(mock_os_system, mock_subprocess, mock_platform):
    """Test simple restart on Windows"""
    mock_platform.return_value = "Windows"
    mock_subprocess.return_value = b"minimal\nprocess\nlist\n"
    System.restart()
    mock_os_system.assert_called_once_with("shutdown /r /t 0")


@patch("xulbux.system._platform.system")
@patch("xulbux.system._subprocess.check_output")
def test_restart_too_many_processes(mock_subprocess, mock_platform):
    """Test restart fails when too many processes running"""
    mock_platform.return_value = "Windows"
    mock_subprocess.return_value = b"many\nprocess\nlines\nhere\nmore\nprocesses\neven\nmore\n"
    with pytest.raises(RuntimeError, match="Processes are still running"):
        System.restart()


@patch("xulbux.system._platform.system")
@patch("xulbux.system._subprocess.check_output")
def test_restart_unsupported_system(mock_subprocess, mock_platform):
    """Test restart on unsupported system"""
    mock_platform.return_value = "Unknown"
    mock_subprocess.return_value = b"some output"
    with pytest.raises(NotImplementedError, match="Restart not implemented for 'unknown' systems."):
        System.restart()


@pytest.mark.skipif(os.name != "nt", reason="Windows-specific test")
@patch("xulbux.system._ctypes")
def test_elevate_windows_already_elevated(mock_ctypes):
    """Test elevate on WINDOWS when already elevated"""
    # SETUP THE MOCK TO RETURN 1 (True) FOR IsUserAnAdmin
    mock_ctypes.windll.shell32.IsUserAnAdmin.return_value = 1

    result = System.elevate()
    assert result is True


@pytest.mark.skipif(os.name == "nt", reason="POSIX-specific test")
@patch("xulbux.system._os.geteuid")
def test_elevate_posix_already_elevated(mock_geteuid):
    """Test elevate on POSIX when already elevated"""
    mock_geteuid.return_value = 0
    result = System.elevate()
    assert result is True
