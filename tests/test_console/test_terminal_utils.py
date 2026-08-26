import os
import sys
from typing import Any
from unittest.mock import MagicMock
from xulbux.console import cls, debug, done, fail, get_encoding, get_height, get_size, info, log, warn
import pytest


def test_get_height(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(os, "get_terminal_size", lambda: os.terminal_size((80, 50)))
    assert get_height() == 50

    def raise_oserror():
        raise OSError()

    monkeypatch.setattr(os, "get_terminal_size", raise_oserror)
    assert get_height() == 24


def test_get_size(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(os, "get_terminal_size", lambda: os.terminal_size((100, 40)))
    assert get_size() == (100, 40)

    def raise_oserror():
        raise OSError()

    monkeypatch.setattr(os, "get_terminal_size", raise_oserror)
    assert get_size() == (80, 24)


def test_get_encoding(monkeypatch: pytest.MonkeyPatch):
    class FakeStdout:
        @property
        def encoding(self):
            raise AttributeError()

    monkeypatch.setattr(sys, "stdout", FakeStdout())
    assert get_encoding() == "utf-8"

    class FakeStdout2:
        encoding = None

    monkeypatch.setattr(sys, "stdout", FakeStdout2())
    assert get_encoding() == "utf-8"


def test_cls_clear(monkeypatch: pytest.MonkeyPatch, mock_subprocess_run: MagicMock):
    def fake_which(cmd: Any):
        return cmd == "clear"  # pyright:ignore[reportUnknownVariableType]

    monkeypatch.setattr("xulbux.console._shutil.which", fake_which)  # pyright:ignore[reportUnknownArgumentType]
    cls()
    mock_subprocess_run.assert_called_with(["clear"])


def test_log_value_errors():
    with pytest.raises(ValueError, match="tab_size"):
        log("T", "msg", tab_size=-1)
    with pytest.raises(ValueError, match="title_px"):
        log("T", "msg", title_px=-1)
    with pytest.raises(ValueError, match="title_mx"):
        log("T", "msg", title_mx=-1)


def test_log_presets():
    # Call them to increase coverage, they mostly output to stdout:
    debug("msg", active=False)
    debug("msg", active=True, pause=False, exit=False)
    info("msg", pause=False, exit=False)
    warn("msg", pause=False, exit=False)
    done("msg", pause=False, exit=False)
    # Fail defaults to exit=True, so test with exit=False:
    fail("msg", pause=False, exit=False)
    # Or catch exit:
    with pytest.raises(SystemExit):
        fail("msg", exit=True)
