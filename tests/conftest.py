import ctypes
import tempfile
from collections.abc import Callable, Generator
from pathlib import Path, PosixPath, WindowsPath
from unittest.mock import MagicMock, patch
import pytest


@pytest.fixture
def tmp_path() -> Generator[Path, None, None]:
    """Provides access to a temporary directory for testing purposes."""

    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir).resolve()


# ********************************************************* OS MOCKS **********************************************************


def _mock_path_new(cls: type[object], *args: object, **kwargs: object) -> object:
    return object.__new__(cls)


@pytest.fixture
def mock_os_windows(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mocks the OS to be detected as Windows for testing purposes."""

    monkeypatch.setattr("os.name", "nt")
    monkeypatch.setattr("platform.system", lambda: "Windows")
    monkeypatch.setattr("sys.platform", "win32")
    monkeypatch.setattr(WindowsPath, "__new__", _mock_path_new)


@pytest.fixture
def mock_os_linux(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mocks the OS to be detected as Linux for testing purposes."""

    monkeypatch.setattr("os.name", "posix")
    monkeypatch.setattr("platform.system", lambda: "Linux")
    monkeypatch.setattr("sys.platform", "linux")
    monkeypatch.setattr(PosixPath, "__new__", _mock_path_new)


@pytest.fixture
def mock_os_darwin(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mocks the OS to be detected as macOS for testing purposes."""

    monkeypatch.setattr("os.name", "posix")
    monkeypatch.setattr("platform.system", lambda: "Darwin")
    monkeypatch.setattr("sys.platform", "darwin")
    monkeypatch.setattr(PosixPath, "__new__", _mock_path_new)


# ***************************************************** SUBPROCESS MOCKS ******************************************************


@pytest.fixture
def mock_subprocess_run() -> Generator[MagicMock, None, None]:
    """Mocks `subprocess.run` for testing purposes."""

    with patch("subprocess.run") as mock:
        yield mock


@pytest.fixture
def mock_subprocess_popen() -> Generator[MagicMock, None, None]:
    """Mocks `subprocess.Popen` for testing purposes."""

    with patch("subprocess.Popen") as mock:
        yield mock


@pytest.fixture
def mock_subprocess_check_output() -> Generator[MagicMock, None, None]:
    """Mocks `subprocess.check_output` for testing purposes."""

    with patch("subprocess.check_output") as mock:
        yield mock


# ****************************************************** WIN CTYPES MOCK ******************************************************


@pytest.fixture
def mock_ctypes_windll(monkeypatch: pytest.MonkeyPatch) -> Callable[..., MagicMock]:
    """Safely mocks `ctypes.windll` so it can be tested on Unix without crashing.<br>
    Returns a factory function that optionally takes `shell_execute_return`."""

    def _factory(shell_exec_return: int = 42) -> MagicMock:
        mock_windll = MagicMock()
        mock_windll.shell32.ShellExecuteW.return_value = shell_exec_return
        monkeypatch.setattr(ctypes, "windll", mock_windll, raising=False)

        return mock_windll

    return _factory
