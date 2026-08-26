import json
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError
from xulbux import __version__
from xulbux.cli.help import H, get_latest_version, is_latest_version, show_help
import pytest


def test_get_latest_version_successful_response():
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.__enter__.return_value = mock_response

    with (
        patch("urllib.request.urlopen", return_value=mock_response),
        patch("json.load", return_value={"info": {"version": "2.0.0"}}),
    ):
        assert get_latest_version() == "2.0.0"


def test_get_latest_version_http_error():
    mock_response = MagicMock()
    mock_response.status = 404
    mock_response.headers = {}
    mock_response.__enter__.return_value = mock_response

    with patch("urllib.request.urlopen", return_value=mock_response), pytest.raises(HTTPError):
        get_latest_version()


def test_get_latest_version_invalid_json():
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.__enter__.return_value = mock_response

    with (
        patch("urllib.request.urlopen", return_value=mock_response),
        patch("json.load", side_effect=json.JSONDecodeError("msg", "doc", 0)),
    ):
        assert get_latest_version() is None


def test_is_latest_version_evaluations():
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


def test_show_help_prints_and_pauses(capsys: pytest.CaptureFixture[str]):
    mock_pause = MagicMock()
    with patch("xulbux.console.pause_exit", mock_pause):
        show_help()

    captured = capsys.readouterr()
    assert __version__ in captured.out
    assert "Commands:" in captured.out
    assert "Usage:" in captured.out
    assert "Documentation:" in captured.out
    mock_pause.assert_called_once()


def test_h_styling_constants():
    assert H.CMD is not None
    assert H.HEADING is not None
    assert H.BORDER is not None
