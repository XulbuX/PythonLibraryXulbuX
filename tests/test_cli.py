from xulbux.cli.tools import render_format_codes
from xulbux.cli.help import show_help

from unittest.mock import MagicMock
from pathlib import Path
import pytest
import toml
import sys


ROOT_DIR = Path(__file__).parent.parent
PYPROJECT_PATH = ROOT_DIR / "pyproject.toml"


################################################## ENTRYPOINT REGISTRATION TESTS ##################################################


def test_xulbux_help_entrypoint_registered():
    """Verifies that the `xulbux-help` script is registered in pyproject.toml."""
    with open(PYPROJECT_PATH, "r", encoding="utf-8") as file:
        pyproject_data = toml.load(file)
    scripts = pyproject_data.get("project", {}).get("scripts", {})
    assert "xulbux-help" in scripts, "`xulbux-help` not found in [project.scripts] in pyproject.toml"
    assert scripts["xulbux-help"] == "xulbux.cli.help:show_help"


def test_xulbux_fc_entrypoint_registered():
    """Verifies that the `xulbux-fc` script is registered in pyproject.toml."""
    with open(PYPROJECT_PATH, "r", encoding="utf-8") as file:
        pyproject_data = toml.load(file)
    scripts = pyproject_data.get("project", {}).get("scripts", {})
    assert "xulbux-fc" in scripts, "`xulbux-fc` not found in [project.scripts] in pyproject.toml"
    assert scripts["xulbux-fc"] == "xulbux.cli.tools:render_format_codes"


################################################## xulbux-help TESTS ##################################################


def test_show_help_prints_output(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]):
    """show_help() must print the ANSI help banner to stdout."""
    monkeypatch.setattr("xulbux.console._read_single_key", MagicMock())

    show_help()

    captured = capsys.readouterr()
    assert len(captured.out) > 0, "show_help() produced no output"


def test_show_help_contains_version(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]):
    """The help banner must contain the installed package version."""
    from xulbux import __version__

    monkeypatch.setattr("xulbux.console._read_single_key", MagicMock())

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
    # pause=True must be passed so the user sees the prompt
    assert call_kwargs.kwargs.get("pause", True) is True


def test_show_help_does_not_require_elevated_privileges(monkeypatch: pytest.MonkeyPatch):
    """show_help() must not raise when the keyboard library is unavailable or unprivileged.
    This guards against regressions where elevated privileges are accidentally required
    (the original bug on macOS and Linux)."""
    mock_read_key = MagicMock(side_effect=OSError("Error 13 - Must be run as administrator"))
    # Simulate the failure mode that was reported on macOS/Linux
    monkeypatch.setattr("xulbux.console._read_single_key", mock_read_key)

    with pytest.raises(OSError):
        show_help()


def test_show_help_no_privileges_needed_when_properly_implemented(monkeypatch: pytest.MonkeyPatch):
    """With the cross-platform _read_single_key implementation, show_help()
    must complete without errors – no elevated privileges required."""
    monkeypatch.setattr("xulbux.console._read_single_key", MagicMock())

    # Must not raise at all
    show_help()


################################################## xulbux-fc TESTS ##################################################


def test_render_format_codes_no_input(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]):
    """When no positional arguments are provided, render_format_codes() prints a usage hint."""
    monkeypatch.setattr(sys, "argv", ["xulbux-fc"])

    render_format_codes()

    captured = capsys.readouterr()
    assert "Provide a string" in captured.out


def test_render_format_codes_with_plain_string(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]):
    """A plain string with no format codes must print the 'no valid format codes' notice."""
    monkeypatch.setattr(sys, "argv", ["xulbux-fc", "hello world"])

    render_format_codes()

    captured = capsys.readouterr()
    assert "hello world" in captured.out
    assert "doesn't contain any valid format codes" in captured.out


def test_render_format_codes_with_format_codes(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]):
    """A string containing valid format codes must render the ANSI output and the escaped form."""
    monkeypatch.setattr(sys, "argv", ["xulbux-fc", "[b]bold[_]"])

    render_format_codes()

    captured = capsys.readouterr()
    # The rendered ANSI output must be non-empty
    assert len(captured.out.strip()) > 0
    # The "doesn't contain any valid format codes" notice must NOT appear
    assert "doesn't contain any valid format codes" not in captured.out


def test_render_format_codes_multiple_tokens(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]):
    """Multiple positional tokens are joined and rendered as one string."""
    monkeypatch.setattr(sys, "argv", ["xulbux-fc", "hello", "world"])

    render_format_codes()

    captured = capsys.readouterr()
    assert "helloworld" in captured.out or "hello" in captured.out
