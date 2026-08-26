import json
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError
from xulbux.cli.help import get_latest_version, is_latest_version
import pytest


def test_get_latest_version_http_error():
    # Test HTTP error status != 200
    mock_response = MagicMock()
    mock_response.status = 404
    mock_response.headers = {}
    mock_response.__enter__.return_value = mock_response

    with patch("urllib.request.urlopen", return_value=mock_response), pytest.raises(HTTPError):
        get_latest_version()


def test_get_latest_version_json_error():
    # Test JSON parse error or missing fields
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.__enter__.return_value = mock_response

    with (
        patch("urllib.request.urlopen", return_value=mock_response),
        patch("json.load", side_effect=json.JSONDecodeError("msg", "doc", 0)),
    ):
        assert get_latest_version() is None


def test_is_latest_version_none():
    # Test when latest is None
    with patch("xulbux.cli.help.get_latest_version", return_value=None):
        assert is_latest_version() is None

    with patch("xulbux.cli.help.get_latest_version", return_value=""):
        assert is_latest_version() is None


def test_is_latest_version_exception():
    # Test when version parsing fails
    with patch("xulbux.cli.help.get_latest_version", return_value="vNotAVersion"):
        assert is_latest_version() is None
