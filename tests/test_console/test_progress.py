import sys
from io import StringIO
from unittest.mock import MagicMock, patch
import xulbux.console as _console_module
from xulbux.ansi import S, StyledText
from xulbux.base.consts import ANSI
from xulbux.console import ProgressBar
import pytest

# ***************************************************** ProgressBar TESTS *****************************************************


def test_progressbar_clear_intercept_line():
    pb = ProgressBar()
    mock_stdout = MagicMock()
    mock_stdout.write.return_value = 0
    mock_stdout.flush.return_value = None
    pb._original_stdout = mock_stdout
    pb._last_line_len = 20
    pb._clear_intercept_line()
    mock_stdout.write.assert_called_once()
    mock_stdout.flush.assert_called_once()


def test_progressbar_create_bar():
    pb = ProgressBar()

    bar = pb._create_bar(50, 100, 10)
    assert len(bar) == 10
    assert bar[0] == pb.chars[0]
    assert bar[-1] == pb.chars[-1]

    bar = pb._create_bar(100, 100, 10)
    assert len(bar) == 10
    assert all(char == pb.chars[0] for char in bar)

    bar = pb._create_bar(0, 100, 10)
    assert len(bar) == 10
    assert all(char == pb.chars[-1] for char in bar)


def test_progressbar_emergency_cleanup():
    pb = ProgressBar()
    pb.active = True
    original_stdout = MagicMock()
    pb._original_stdout = original_stdout
    pb._emergency_cleanup()
    assert pb.active is False


def test_progressbar_get_formatted_info_and_bar_width(mock_terminal_size: MagicMock):
    pb = ProgressBar()
    formatted, bar_width = pb._get_formatted_info_and_bar_width(
        ["{l}", "|{b}|", "{c}/{t}", "({p}%)"], 50, 100, 50.0, "Loading"
    )
    assert "Loading" in formatted
    assert "50" in formatted
    assert "100" in formatted
    assert "50.0" in formatted
    assert isinstance(bar_width, int)
    assert bar_width > 0


def test_progressbar_hide_progress():
    pb = ProgressBar()
    pb.active = True
    pb._original_stdout = MagicMock()
    pb.hide_progress()
    assert pb.active is False
    assert pb._original_stdout is None


def test_progressbar_init():
    pb = ProgressBar(min_width=5, max_width=30)
    assert pb.min_width == 5
    assert pb.max_width == 30
    assert pb.active is False
    assert len(pb.chars) == 9


def test_progressbar_intercepted_output():
    pb = ProgressBar()
    intercepted = _console_module._InterceptedOutput(pb, sys.stdout)
    result = intercepted.write("test content")
    assert result == len("test content")
    assert "test content" in pb._buffer
    intercepted.flush()


def test_progressbar_progress_context(capsys: pytest.CaptureFixture[str]):
    pb = ProgressBar()

    # Test context manager behavior by checking actual effects:
    with pb.progress_context(100, "Testing") as update_progress:
        update_progress(25)
        assert pb.active is True  # Active after first update.
        update_progress(50)

    # After context exits, progress bar should be hidden:
    assert pb.active is False
    captured = capsys.readouterr()
    assert captured.out != ""  # Some output should have been produced.


def test_progressbar_progress_context_exception():
    pb = ProgressBar()

    # Test that cleanup happens even with exceptions:
    with pytest.raises(ValueError), pb.progress_context(100, "Testing") as update_progress:
        update_progress(25)
        raise ValueError("Test exception")

    # After exception, progress bar should still be cleaned up:
    assert pb.active is False


def test_progressbar_redraw_progress_bar():
    pb = ProgressBar()
    mock_stdout = MagicMock()
    mock_stdout.write.return_value = 0
    mock_stdout.flush.return_value = None
    pb._original_stdout = mock_stdout
    pb._current_progress_str = "\x1b[2K\rLoading... ▕██████████          ▏ 50/100 (50.0%)"
    pb._redraw_display()
    mock_stdout.flush.assert_called_once()


def test_progressbar_set_bar_format():
    pb = ProgressBar()
    pb.set_format(format=["{l}", "[{b}]", "{p}%"], limited_format=["[{b}]"])
    assert pb.format == ["{l}", "[{b}]", "{p}%"]
    assert pb.limited_format == ["[{b}]"]


def test_progressbar_set_bar_format_invalid():
    pb = ProgressBar()
    with pytest.raises(ValueError, match=r"must contain the '{bar}' or '{b}' placeholder"):
        pb.set_format(format=["Progress: {p}%"])
    with pytest.raises(ValueError, match=r"must contain the '{bar}' or '{b}' placeholder"):
        pb.set_format(limited_format=["Progress: {p}%"])


def test_progressbar_set_chars():
    pb = ProgressBar()
    custom_chars = ("█", "▓", "▒", "░", " ")
    pb.set_chars(custom_chars)
    assert pb.chars == custom_chars

    pb.set_chars(["█", " "])
    assert pb.chars == ("█", " ")


def test_progressbar_set_chars_invalid():
    pb = ProgressBar()
    with pytest.raises(ValueError, match=r"must contain at least two characters"):
        pb.set_chars(("█",))
    with pytest.raises(ValueError, match=r"must be single-character strings"):
        pb.set_chars(("█", "▓▓", " "))


def test_progressbar_set_width():
    pb = ProgressBar()
    pb.set_width(min_width=15, max_width=60)
    assert pb.min_width == 15
    assert pb.max_width == 60


def test_progressbar_set_width_invalid():
    pb = ProgressBar()
    with pytest.raises(TypeError):
        pb.set_width(min_width="not_int")
    with pytest.raises(ValueError):
        pb.set_width(min_width=0)
    with pytest.raises(TypeError):
        pb.set_width(max_width="not_int")
    with pytest.raises(ValueError):
        pb.set_width(max_width=0)


@patch("sys.stdout", new_callable=StringIO)
def test_progressbar_show_progress(mock_stdout: MagicMock):
    pb = ProgressBar()
    # Manually set and restore `_original_stdout` to avoid patching issues with compiled classes:
    original = pb._original_stdout
    pb._original_stdout = mock_stdout
    try:
        pb.active = True
        pb._draw_progress_bar(50, 100, "Loading")
    finally:
        pb._original_stdout = original

    output = mock_stdout.getvalue()
    assert len(output) > 0


def test_progressbar_show_progress_invalid_total():
    pb = ProgressBar()
    with pytest.raises(ValueError, match=r"The 'total' parameter must be a positive integer, got 0"):
        pb.show_progress(10, 0)
    with pytest.raises(ValueError, match=r"The 'total' parameter must be a positive integer, got -5"):
        pb.show_progress(10, -5)


def test_progressbar_start_stop_intercepting():
    pb = ProgressBar()
    original_stdout = sys.stdout

    pb._start_intercepting()
    assert pb.active is True
    assert pb._original_stdout == original_stdout
    assert isinstance(sys.stdout, _console_module._InterceptedOutput)

    pb._stop_intercepting()
    assert pb.active is False
    assert pb._original_stdout is None
    assert sys.stdout == original_stdout


@patch("sys.stdout", new_callable=StringIO)
def test_progressbar_styled_text_label(mock_stdout: MagicMock):

    pb = ProgressBar()
    original = pb._original_stdout
    pb._original_stdout = mock_stdout
    try:
        pb.active = True
        pb._draw_progress_bar(50, 100, StyledText("Label ", S.BOLD("styled")))
    finally:
        pb._original_stdout = original

    output = mock_stdout.getvalue()
    assert len(output) > 0
    assert "Label " in output
    assert f"{ANSI.CHAR}[1mstyled{ANSI.CHAR}[22m" in output
