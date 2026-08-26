import subprocess
from unittest.mock import patch
import xulbux.system as _system_module


def test_check_libs_existing_modules():
    result = _system_module.check_libs(["os", "sys", "json"])
    assert result is None


def test_check_libs_nonexistent_module():
    result = _system_module.check_libs(["nonexistent_module_12345"], install_missing=False)
    assert result == ["nonexistent_module_12345"]


def test_check_libs_import_error_value_error_attr_error():
    with patch("importlib.util.find_spec", side_effect=ValueError("test")):
        result = _system_module.check_libs(["some_lib"], install_missing=False)
        assert result == ["some_lib"]


def test_check_libs_decline_install():
    with patch("xulbux.console.confirm", return_value=False) as mock_confirm:
        result = _system_module.check_libs(["nonexistent_module_12345"], install_missing=True)
        assert result == ["nonexistent_module_12345"]
        mock_confirm.assert_called_once()


def test_check_libs_custom_missing_msgs():
    msgs = {"found_missing": "Missing:", "should_install": "Install?"}
    with patch("xulbux.console.confirm", return_value=False) as mock_confirm:
        result = _system_module.check_libs(["nonexistent_module_12345"], install_missing=True, missing_libs_msgs=msgs)  # pyright:ignore[reportArgumentType]
        assert result == ["nonexistent_module_12345"]
        mock_confirm.assert_called_once_with("Install?", end="\n")


def test_check_libs_install_success():
    with patch("xulbux.console.confirm", return_value=True), patch("xulbux.system._subprocess.check_call") as mock_check_call:
        result = _system_module.check_libs(["nonexistent_module_12345"], install_missing=True)
        assert result is None
        mock_check_call.assert_called_once()


def test_check_libs_install_failure():
    with (
        patch("xulbux.console.confirm", return_value=True),
        patch("xulbux.system._subprocess.check_call", side_effect=subprocess.CalledProcessError(1, "pip")),
    ):
        result = _system_module.check_libs(["nonexistent_module_12345"], install_missing=True)
        assert result == ["nonexistent_module_12345"]


def test_check_libs_no_confirm_install():
    with patch("xulbux.system._subprocess.check_call") as mock_check_call:
        result = _system_module.check_libs(["nonexistent_module_12345"], install_missing=True, confirm_install=False)
        assert result is None
        mock_check_call.assert_called_once()
