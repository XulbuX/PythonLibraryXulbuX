import sys
import tomllib
from pathlib import Path
from unittest.mock import patch
from xulbux.cli._main import main
import pytest

ROOT_DIR = Path(__file__).parent.parent.parent
PYPROJECT_PATH = ROOT_DIR / "pyproject.toml"


def test_cli_entrypoint_registered_in_pyproject() -> None:
    with open(PYPROJECT_PATH, "rb") as file:
        pyproject_data = tomllib.load(file)

    scripts = pyproject_data.get("project", {}).get("scripts", {})
    assert "xulbux-lib" in scripts
    assert scripts["xulbux-lib"] == "xulbux.cli:main"


def test_cli_main_ansi_subcommand(capsys: pytest.CaptureFixture[str]) -> None:
    with patch.object(sys, "argv", ["xulbux-lib", "ansi"]):
        main()
        captured = capsys.readouterr()
        assert "Text Styles" in captured.out
        assert "Foreground Colors" in captured.out


def test_cli_main_color256_subcommand(capsys: pytest.CaptureFixture[str]) -> None:
    with patch.object(sys, "argv", ["xulbux-lib", "color256"]):
        main()
        captured = capsys.readouterr()
        assert "000" in captured.out
        assert "255" in captured.out


def test_cli_main_c256_alias_subcommand(capsys: pytest.CaptureFixture[str]) -> None:
    with patch.object(sys, "argv", ["xulbux-lib", "c256"]):
        main()
        captured = capsys.readouterr()
        assert "000" in captured.out
        assert "255" in captured.out


def test_cli_main_true_color_subcommand(capsys: pytest.CaptureFixture[str]) -> None:
    with patch.object(sys, "argv", ["xulbux-lib", "truecolor"]):
        main()
        captured = capsys.readouterr()
        assert "▄" in captured.out


def test_cli_main_tc_alias_with_color(capsys: pytest.CaptureFixture[str]) -> None:
    with patch.object(sys, "argv", ["xulbux-lib", "tc", "#FF0000"]):
        main()
        captured = capsys.readouterr()
        assert "▄" in captured.out


def test_cli_main_default_help_subcommand(capsys: pytest.CaptureFixture[str]) -> None:
    with patch.object(sys, "argv", ["xulbux-lib"]), patch("xulbux.console.pause_exit"):
        main()
        captured = capsys.readouterr()
        assert "Commands:" in captured.out
        assert "xulbux-lib" in captured.out


def test_cli_main_unknown_subcommand(capsys: pytest.CaptureFixture[str]) -> None:
    with patch.object(sys, "argv", ["xulbux-lib", "unknown_cmd"]), patch("xulbux.console.pause_exit"):
        main()
        captured = capsys.readouterr()
        assert "Commands:" in captured.out
