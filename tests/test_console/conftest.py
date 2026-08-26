import builtins
import os
from unittest.mock import MagicMock
import pytest


@pytest.fixture
def mock_terminal_size(monkeypatch: pytest.MonkeyPatch):

    def mock_get_terminal_size(fd: int | None = None) -> os.terminal_size:
        return os.terminal_size((80, 24))

    monkeypatch.setattr("xulbux.console._os.get_terminal_size", mock_get_terminal_size)


@pytest.fixture
def mock_formatcodes_print(monkeypatch: pytest.MonkeyPatch):
    mock = MagicMock()
    # Patch in the original module where it is defined:
    import xulbux.format_codes

    monkeypatch.setattr(xulbux.format_codes.FormatCodes, "print", mock)
    return mock


@pytest.fixture
def mock_builtin_input(monkeypatch: pytest.MonkeyPatch):
    mock = MagicMock()
    monkeypatch.setattr(builtins, "input", mock)
    return mock


@pytest.fixture
def mock_prompt_toolkit(monkeypatch: pytest.MonkeyPatch):
    mock = MagicMock(return_value="mocked multiline input")
    monkeypatch.setattr("xulbux.console._pt.prompt", mock)
    return mock


@pytest.fixture
def mock_prompt_session(monkeypatch: pytest.MonkeyPatch):
    mock_session = MagicMock()
    mock_session_class = MagicMock(return_value=mock_session)
    mock_session.prompt.return_value = None
    monkeypatch.setattr("xulbux.console._pt.PromptSession", mock_session_class)
    return mock_session_class, mock_session
