from xulbux.system import System

from unittest.mock import patch
import pytest
import os


def test_system_class_exists():
    """Test that System class exists and has expected methods"""
    assert hasattr(System, 'is_elevated')
    assert hasattr(System, 'restart')
    assert hasattr(System, 'check_libs')
    assert hasattr(System, 'elevate')


def test_system_is_elevated_property():
    """Test is_elevated property returns a boolean"""
    result = System.is_elevated
    assert isinstance(result, bool)


def test_check_libs_existing_modules():
    """Test check_libs with existing modules"""
    result = System.check_libs(["os", "sys", "json"])
    assert result is None


def test_check_libs_nonexistent_module():
    """Test check_libs with nonexistent module returns list"""
    result = System.check_libs(["nonexistent_module_12345"], install_missing=False)
    assert isinstance(result, list)
    assert "nonexistent_module_12345" in result


@patch('xulbux.system._subprocess.check_call')
@patch('builtins.input', return_value='n')  # Decline installation
def test_check_libs_decline_install(mock_input, mock_subprocess):
    """Test check_libs when user declines installation"""
    with pytest.raises(ImportError, match="Missing required libraries"):
        System.check_libs(["nonexistent_module_12345"], install_missing=True, confirm_install=True)


@pytest.mark.skipif(os.name != 'nt', reason="Windows-specific test")
def test_elevate_windows_already_elevated():
    """Test elevate on Windows when already elevated"""
    with patch.object(System, 'is_elevated', True):
        result = System.elevate()
        assert result is True


@pytest.mark.skipif(os.name == 'nt', reason="POSIX-specific test")
def test_elevate_posix_already_elevated():
    """Test elevate on POSIX when already elevated"""
    with patch.object(System, 'is_elevated', True):
        result = System.elevate()
        assert result is True


@patch('xulbux.system._platform.system')
@patch('xulbux.system._subprocess.check_output')
@patch('xulbux.system._os.system')
def test_restart_windows_simple(mock_os_system, mock_subprocess, mock_platform):
    """Test simple restart on Windows"""
    mock_platform.return_value.lower.return_value = "windows"
    mock_subprocess.return_value = b"minimal\nprocess\nlist\n"
    System.restart()
    mock_os_system.assert_called_once_with("shutdown /r /t 0")


@patch('xulbux.system._platform.system')
@patch('xulbux.system._subprocess.check_output')
def test_restart_too_many_processes(mock_subprocess, mock_platform):
    """Test restart fails when too many processes running"""
    mock_platform.return_value.lower.return_value = "windows"
    mock_subprocess.return_value = b"many\nprocess\nlines\nhere\nmore\nprocesses\neven\nmore\n"
    with pytest.raises(RuntimeError, match="Processes are still running"):
        System.restart()


@patch('xulbux.system._platform.system')
@patch('xulbux.system._subprocess.check_output')
def test_restart_unsupported_system(mock_subprocess, mock_platform):
    """Test restart on unsupported system"""
    mock_platform.return_value.lower.return_value = "unknown"
    mock_subprocess.return_value = b"some output"
    with pytest.raises(NotImplementedError, match="Restart not implemented for `unknown`"):
        System.restart()
