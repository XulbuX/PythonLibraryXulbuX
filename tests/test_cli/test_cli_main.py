import sys
from unittest.mock import patch
from xulbux.cli._main import main
import pytest


def test_cli_main_ansi(capsys: pytest.CaptureFixture[str]):
    with patch.object(sys, "argv", ["xulbux-lib", "ansi"]):
        main()
        captured = capsys.readouterr()
        assert "Text Styles" in captured.out


def test_cli_main_help(capsys: pytest.CaptureFixture[str]):
    with patch.object(sys, "argv", ["xulbux-lib"]), patch("xulbux.console.pause_exit"):
        main()
        captured = capsys.readouterr()
        assert "Usage:" in captured.out or "help" in captured.out.lower() or "xulbux" in captured.out.lower()


def test_cli_main_unknown(capsys: pytest.CaptureFixture[str]):
    with patch.object(sys, "argv", ["xulbux-lib", "unknown"]), patch("xulbux.console.pause_exit"):
        main()
        captured = capsys.readouterr()
        assert "xulbux" in captured.out.lower()  # Prints help
