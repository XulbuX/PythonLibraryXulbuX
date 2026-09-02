import json
from unittest.mock import MagicMock, patch
from xulbux import __version__
from xulbux.cli.help import get_latest_version, is_latest_version, show_help
import pytest


def test_get_latest_version_successful_response() -> None:
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.__enter__.return_value = mock_response

    with (
        patch("urllib.request.urlopen", return_value=mock_response),
        patch("json.load", return_value={"info": {"version": "v2.0.0"}}),
    ):
        assert get_latest_version() == "2.0.0"


def test_get_latest_version_invalid_json() -> None:
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.__enter__.return_value = mock_response

    with (
        patch("urllib.request.urlopen", return_value=mock_response),
        patch("json.load", side_effect=json.JSONDecodeError("msg", "doc", 0)),
    ):
        assert get_latest_version() is None


def test_is_latest_version_evaluations() -> None:
    with patch("xulbux.cli.help.__version__", "1.0.0"):
        with patch("xulbux.cli.help.get_latest_version", return_value=None):
            assert is_latest_version() is None

        with patch("xulbux.cli.help.get_latest_version", return_value=""):
            assert is_latest_version() is None

        with patch("xulbux.cli.help.get_latest_version", return_value="v1.0.0"):
            assert is_latest_version() is True

        with patch("xulbux.cli.help.get_latest_version", return_value="v99.0.0"):
            assert is_latest_version() is False

        with patch("xulbux.cli.help.get_latest_version", return_value="invalid_semver"):
            assert is_latest_version() is None


def test_is_latest_version_with_provided_version() -> None:
    with patch("xulbux.cli.help.__version__", "1.0.0"):
        assert is_latest_version("1.0.0") is True
        assert is_latest_version("2.0.0") is False
        assert is_latest_version("0.9.0") is True


def test_show_help_prints_and_pauses(capsys: pytest.CaptureFixture[str]) -> None:
    mock_pause = MagicMock()
    with patch("xulbux.console.pause_exit", mock_pause):
        show_help()

    captured = capsys.readouterr()
    assert __version__ in captured.out
    assert "Commands:" in captured.out
    assert "Modules:" in captured.out
    assert "Resources:" in captured.out
    mock_pause.assert_called_once()


def test_show_help_with_update_notice(capsys: pytest.CaptureFixture[str]) -> None:
    mock_pause = MagicMock()
    with (
        patch("xulbux.cli.help.get_latest_version", return_value="99.0.0"),
        patch("xulbux.console.pause_exit", mock_pause),
    ):
        show_help()

    captured = capsys.readouterr()
    assert "99.0.0" in captured.out
    assert "available" in captured.out
    mock_pause.assert_called_once()


def test_show_help_when_not_latest_but_get_version_none(capsys: pytest.CaptureFixture[str]) -> None:
    mock_pause = MagicMock()
    with (
        patch("xulbux.cli.help.get_latest_version", return_value=None),
        patch("xulbux.console.pause_exit", mock_pause),
    ):
        show_help()

    captured = capsys.readouterr()
    assert __version__ in captured.out
    assert "available" not in captured.out
    mock_pause.assert_called_once()
