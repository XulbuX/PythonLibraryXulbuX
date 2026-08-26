import math
from unittest.mock import MagicMock, patch
from xulbux.ansi import S, StyledText
from xulbux.base.consts import ANSI
from xulbux.console import Throbber
import pytest


def test_throbber_context_manager():
    throbber = Throbber()

    # Test context manager behavior by checking actual effects:
    with throbber.context("Test") as update:
        assert throbber.active is True
        assert throbber.label == "Test"
        update("New Label")
        assert throbber.label == "New Label"

    # After context exits, throbber should be stopped:
    assert throbber.active is False


def test_throbber_context_manager_exception():
    throbber = Throbber()

    # Test that cleanup happens even with exceptions:
    with pytest.raises(ValueError), throbber.context("Test"):
        raise ValueError("Oops")

    # After exception, throbber should still be cleaned up:
    assert throbber.active is False


def test_throbber_init_custom():
    throbber = Throbber(label="Loading", interval=0.5, sep="-")
    assert throbber.label == "Loading"
    assert math.isclose(throbber.interval, 0.5)
    assert throbber.sep == "-"


def test_throbber_init_defaults():
    throbber = Throbber()
    assert throbber.label is None
    assert math.isclose(throbber.interval, 0.08)
    assert throbber.active is False
    assert throbber.sep == " "
    assert len(throbber.frames) > 0


def test_throbber_set_format_invalid():
    throbber = Throbber()
    with pytest.raises(ValueError):
        throbber.set_format(["{l}"])  # Missing `{a}`.


def test_throbber_set_format_valid():
    throbber = Throbber()
    throbber.set_format(["{l}", "{a}"])
    assert throbber.format == ["{l}", "{a}"]


def test_throbber_set_frames_invalid():
    throbber = Throbber()
    with pytest.raises(ValueError):
        throbber.set_frames(("a",))  # Less than 2 frames.


def test_throbber_set_frames_valid():
    throbber = Throbber()
    throbber.set_frames(("a", "b"))
    assert throbber.frames == ("a", "b")

    throbber.set_frames(["x", "y", "z"])
    assert throbber.frames == ("x", "y", "z")


def test_throbber_set_interval_invalid():
    throbber = Throbber()
    with pytest.raises(ValueError):
        throbber.set_interval(0)
    with pytest.raises(ValueError):
        throbber.set_interval(-1)


def test_throbber_set_interval_valid():
    throbber = Throbber()
    throbber.set_interval(1.0)
    assert math.isclose(throbber.interval, 1.0)


@patch("xulbux.console._threading.Thread")
@patch("xulbux.console._threading.Event")
@patch("sys.stdout", new_callable=MagicMock)
def test_throbber_start(mock_stdout: MagicMock, mock_event: MagicMock, mock_thread: MagicMock):
    mock_thread.return_value.start.return_value = None
    throbber = Throbber()
    throbber.start("Test")

    assert throbber.active is True
    assert throbber.label == "Test"
    mock_event.assert_called_once()
    mock_thread.assert_called_once()

    # Test, calling start again doesn't do anything:
    throbber.start("Test2")
    assert mock_event.call_count == 1


@patch("xulbux.console._threading.Thread")
@patch("xulbux.console._threading.Event")
def test_throbber_stop(mock_event: MagicMock, mock_thread: MagicMock):
    throbber = Throbber()
    # Manually set active to simulate running:
    throbber.active = True
    mock_stop_event = MagicMock()
    mock_stop_event.set.return_value = None
    throbber._stop_event = mock_stop_event
    mock_animation_thread = MagicMock()
    mock_animation_thread.join.return_value = None
    throbber._animation_thread = mock_animation_thread
    throbber.stop()
    assert throbber.active is False
    mock_stop_event.set.assert_called_once()
    mock_animation_thread.join.assert_called_once()


def test_throbber_update_label():
    throbber = Throbber()
    throbber.update_label("New Label")
    assert throbber.label == "New Label"


def test_throbber_update_label_styled_text():
    throbber = Throbber()
    lbl = StyledText("Loading ", S.BR.CYAN("stuff"))
    throbber.update_label(lbl)
    assert throbber.label is lbl
    # The formatted throbber string gets evaluated via ANSI representation:
    assert f"{ANSI.CHAR}[96mstuff{ANSI.CHAR}[39m" in lbl.ansi
