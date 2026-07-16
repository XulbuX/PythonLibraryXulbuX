from xulbux.cli.help import show_help

from unittest.mock import MagicMock
from pathlib import Path
import pytest
import toml


ROOT_DIR = Path(__file__).parent.parent
PYPROJECT_PATH = ROOT_DIR / "pyproject.toml"

############################################## ENTRYPOINT REGISTRATION TESTS #############################################


def test_xulbux_lib_entrypoint_registered():
    """Verifies that the `xulbux-lib` script is registered in pyproject.toml pointing to the CLI main()."""
    with open(PYPROJECT_PATH, "r", encoding="utf-8") as file:
        pyproject_data = toml.load(file)
    scripts = pyproject_data.get("project", {}).get("scripts", {})
    assert "xulbux-lib" in scripts, "`xulbux-lib` not found in [project.scripts] in pyproject.toml"
    assert scripts["xulbux-lib"] == "xulbux.cli:main"


#################################################### xulbux-lib TESTS ####################################################


def test_show_help_prints_output(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]):
    """show_help() must print the ANSI help banner to stdout."""
    monkeypatch.setattr("xulbux.console.Console._read_single_key", MagicMock())

    show_help()

    captured = capsys.readouterr()
    assert len(captured.out) > 0, "show_help() produced no output"


def test_show_help_contains_version(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]):
    """The help banner must contain the installed package version."""
    from xulbux import __version__

    monkeypatch.setattr("xulbux.console.Console._read_single_key", MagicMock())

    show_help()

    captured = capsys.readouterr()
    assert __version__ in captured.out


def test_show_help_calls_pause_exit(monkeypatch: pytest.MonkeyPatch):
    """show_help() must call Console.pause_exit to wait for a key press before exiting."""
    mock_pause_exit = MagicMock()
    monkeypatch.setattr("xulbux.cli.help.Console.pause_exit", mock_pause_exit)

    show_help()

    mock_pause_exit.assert_called_once()
    call_kwargs = mock_pause_exit.call_args
    # `pause=True` must be passed so the user sees the prompt:
    assert call_kwargs.kwargs.get("pause", True) is True


def test_show_help_does_not_raise(monkeypatch: pytest.MonkeyPatch):
    """show_help() must complete without errors."""
    monkeypatch.setattr("xulbux.console.Console._read_single_key", MagicMock())

    show_help()  # Must not raise.
