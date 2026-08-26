import ctypes
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest


@pytest.fixture
def tmp_path():
    """Provides access to a temporary directory for testing purposes."""

    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


# ********************************************************* OS MOCKS **********************************************************


@pytest.fixture
def mock_os_windows(monkeypatch: pytest.MonkeyPatch):
    """Mocks the OS to be detected as Windows for testing purposes."""

    monkeypatch.setattr("os.name", "nt")
    monkeypatch.setattr("platform.system", lambda: "Windows")
    monkeypatch.setattr("sys.platform", "win32")


@pytest.fixture
def mock_os_linux(monkeypatch: pytest.MonkeyPatch):
    """Mocks the OS to be detected as Linux for testing purposes."""

    monkeypatch.setattr("os.name", "posix")
    monkeypatch.setattr("platform.system", lambda: "Linux")
    monkeypatch.setattr("sys.platform", "linux")


@pytest.fixture
def mock_os_darwin(monkeypatch: pytest.MonkeyPatch):
    """Mocks the OS to be detected as macOS for testing purposes."""

    monkeypatch.setattr("os.name", "posix")
    monkeypatch.setattr("platform.system", lambda: "Darwin")
    monkeypatch.setattr("sys.platform", "darwin")


# ***************************************************** SUBPROCESS MOCKS ******************************************************


@pytest.fixture
def mock_subprocess_run():
    """Mocks `subprocess.run` for testing purposes."""

    with patch("subprocess.run") as mock:
        yield mock


@pytest.fixture
def mock_subprocess_popen():
    """Mocks `subprocess.Popen` for testing purposes."""

    with patch("subprocess.Popen") as mock:
        yield mock


@pytest.fixture
def mock_subprocess_check_output():
    """Mocks `subprocess.check_output` for testing purposes."""

    with patch("subprocess.check_output") as mock:
        yield mock


# ****************************************************** WIN CTYPES MOCK ******************************************************


@pytest.fixture
def mock_ctypes_windll(monkeypatch: pytest.MonkeyPatch):
    """Safely mocks `ctypes.windll` so it can be tested on Unix without crashing.<br>
    Returns a factory function that optionally takes `shell_execute_return`."""

    def _factory(shell_execute_return: int = 42) -> MagicMock:

        mock_windll = MagicMock()
        mock_windll.shell32.ShellExecuteW.return_value = shell_execute_return
        monkeypatch.setattr(ctypes, "windll", mock_windll, raising=False)

        return mock_windll

    return _factory
