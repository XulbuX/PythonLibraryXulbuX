import subprocess
from typing import TYPE_CHECKING
from unittest.mock import patch
import xulbux.system as _system_module

if TYPE_CHECKING:
    from xulbux.base.types import MissingLibsMsgs


def test_check_libs_all_installed_modules() -> None:
    assert _system_module.check_libs(["os", "sys", "json"]) is None


def test_check_libs_missing_module_without_install() -> None:
    result = _system_module.check_libs(["nonexistent_module_12345"], install_missing=False)
    assert result == ["nonexistent_module_12345"]


def test_check_libs_find_spec_exception_handling() -> None:
    with patch("importlib.util.find_spec", side_effect=ValueError("Invalid spec")):
        result = _system_module.check_libs(["problematic_lib"], install_missing=False)
        assert result == ["problematic_lib"]


def test_check_libs_user_declines_installation() -> None:
    with patch("xulbux.console.confirm", return_value=False) as mock_confirm:
        result = _system_module.check_libs(["nonexistent_lib"], install_missing=True)
        assert result == ["nonexistent_lib"]
        mock_confirm.assert_called_once()


def test_check_libs_with_custom_messages() -> None:
    custom_msgs: MissingLibsMsgs = {
        "found_missing": "Missing packages detected:",
        "should_install": "Proceed with pip install?",
    }
    with patch("xulbux.console.confirm", return_value=False) as mock_confirm:
        result = _system_module.check_libs(["nonexistent_lib"], install_missing=True, missing_libs_msgs=custom_msgs)
        assert result == ["nonexistent_lib"]
        mock_confirm.assert_called_once_with("Proceed with pip install?", end="\n")


def test_check_libs_successful_installation() -> None:
    with patch("xulbux.console.confirm", return_value=True), patch("xulbux.system._subprocess.check_call") as mock_check_call:
        result = _system_module.check_libs(["nonexistent_lib"], install_missing=True)
        assert result is None
        mock_check_call.assert_called_once()


def test_check_libs_failed_pip_installation() -> None:
    with (
        patch("xulbux.console.confirm", return_value=True),
        patch("xulbux.system._subprocess.check_call", side_effect=subprocess.CalledProcessError(1, "pip")),
    ):
        result = _system_module.check_libs(["failing_lib"], install_missing=True)
        assert result == ["failing_lib"]


def test_check_libs_without_confirmation_prompt() -> None:
    with patch("xulbux.system._subprocess.check_call") as mock_check_call:
        result = _system_module.check_libs(["nonexistent_lib"], install_missing=True, confirm_install=False)
        assert result is None
        mock_check_call.assert_called_once()
