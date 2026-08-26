import io
import threading
import time
from unittest.mock import MagicMock, patch
from xulbux.console import FRAMES_STANDARD, FRAMES_WINDMILL, ProgressBar, Throbber, _InterceptedOutput, _StdoutInterceptorMixin
import pytest


def test_progress_bar_initialization_and_configuration() -> None:
    bar = ProgressBar(min_width=15, max_width=30, sep=" | ")
    assert bar.min_width == 15
    assert bar.max_width == 30
    assert bar.sep == " | "

    # Width updates and validation:
    bar.set_width(min_width=20, max_width=10)
    assert bar.min_width == 20
    assert bar.max_width == 20

    bar.set_width(min_width=None, max_width=50)
    assert bar.max_width == 50

    bar.set_width(min_width=10, max_width=None)
    assert bar.min_width == 10

    with pytest.raises(ValueError, match="min_width"):
        bar.set_width(min_width=0)
    with pytest.raises(ValueError, match="max_width"):
        bar.set_width(max_width=0)

    # Chars validation:
    bar.set_chars(("=", "-"))
    assert bar.chars == ("=", "-")

    with pytest.raises(ValueError, match="at least two characters"):
        bar.set_chars(["="])  # pyright:ignore[reportArgumentType]
    with pytest.raises(ValueError, match="single-character"):
        bar.set_chars(["==", "--"])  # pyright:ignore[reportArgumentType]

    # Format validation:
    with pytest.raises(ValueError, match=r"must contain the '\{bar\}'"):
        bar.set_format(format=["{l}", "{c}"])
    with pytest.raises(ValueError, match=r"must contain the '\{bar\}'"):
        bar.set_format(limited_format=["{l}"])

    # None format handling:
    bar.set_format(format=None, limited_format=None, sep=" - ")
    assert bar.sep == " - "
    bar.set_format(format=None, limited_format=None, sep=None)


def test_progress_bar_display_and_context() -> None:
    mock_stdout = io.StringIO()
    bar = ProgressBar(
        min_width=5,
        max_width=20,
        format=["{l}", "{b}", "{c:,}/{t:,}", "({p:.2f}%)"],
        limited_format=["{b}"],
    )
    bar._min_update_interval = 0.0

    with patch("sys.stdout", mock_stdout), bar.progress_context(10000, label="Processing") as update_progress:
        # 1 argument: current
        update_progress(1000)
        # 2 arguments: current, label
        bar._last_update_time = 0.0
        update_progress(5000, "Halfway")
        bar._last_update_time = 0.0
        # 1 arg with label kwarg:
        update_progress(6000, label="Updated label")
        bar._last_update_time = 0.0
        # Positional with current kwarg:
        update_progress(8000, current=8500)  # type:ignore[call-overload]
        bar._last_update_time = 0.0
        # None current with label:
        update_progress(None, "Only label")  # type:ignore[call-overload]
        bar._last_update_time = 0.0
        update_progress(10000, "Completed")
        # Over 100% hides progress:
        bar.show_progress(11000, 10000)

    output = mock_stdout.getvalue()
    assert "Processing" in output
    assert "Halfway" in output
    assert "Updated label" in output
    assert "Only label" in output
    assert "Completed" in output
    assert "1,000" in output
    assert "10,000" in output

    # Progress helper validation errors:
    with bar.progress_context(100) as update_fn:
        with pytest.raises(TypeError, match="1 or 2 positional arguments"):
            update_fn(1, 2, 3)  # type:ignore[call-overload]
        with pytest.raises(TypeError, match="1 or 2 positional arguments"):
            update_fn()  # type:ignore[call-overload]
        with pytest.raises(TypeError, match="must be provided"):
            update_fn(None)  # type:ignore[call-overload]

    # Validation errors on show_progress:
    with pytest.raises(ValueError, match="current"):
        bar.show_progress(-1, 100)
    with pytest.raises(ValueError, match="total"):
        bar.show_progress(10, 0)
    with pytest.raises(ValueError, match="total"), bar.progress_context(0):
        pass


def test_progress_bar_terminal_interception_and_limited_width() -> None:
    mock_stdout = io.StringIO()
    bar = ProgressBar(min_width=50, max_width=80, limited_format=["{b}"])
    bar._min_update_interval = 0.0

    with patch("sys.stdout", mock_stdout), patch("xulbux.console.get_width", return_value=30):
        bar.show_progress(25, 100, label="Step 1")
        # Direct print intercepted and buffered/flushed:
        print("Logged message while progress active")
        # Redraw display with string and with empty string:
        bar._current_progress_str = "something"
        bar._redraw_display()
        bar._current_progress_str = ""
        bar._redraw_display()
        # Throttled update branch:
        bar._min_update_interval = 100.0
        bar.show_progress(26, 100)
        bar.hide_progress()

    assert "Logged message while progress active" in mock_stdout.getvalue()


def test_progress_bar_draw_edge_cases() -> None:
    bar = ProgressBar()
    # No stdout set:
    bar._original_stdout = None
    bar._draw_progress_bar(10, 100)
    # Total <= 0:
    bar._draw_progress_bar(10, 0)

    # Emergency cleanup on draw failure:
    with patch.object(bar, "_draw_progress_bar", side_effect=RuntimeError("Draw fail")), pytest.raises(RuntimeError):
        bar.show_progress(10, 100)


def test_intercepted_output_and_mixin() -> None:
    mixin = _StdoutInterceptorMixin()
    mock_stdout = MagicMock()
    mock_stdout.isatty.return_value = True
    mixin._buffer = []
    mixin._original_stdout = mock_stdout
    mixin.active = True
    mixin._last_line_len = 10

    interceptor = _InterceptedOutput(mixin, mock_stdout)
    assert interceptor.write("") == 0
    assert interceptor.write("\r") == 1
    assert interceptor.write("test output\n") == 12
    interceptor.flush()
    assert interceptor.isatty() is True

    # Inactive flush:
    mixin.active = False
    interceptor.flush()

    # Clear intercept line when len is 0:
    mixin._last_line_len = 0
    mixin._clear_intercept_line()

    # Base mixin stubs:
    mixin._redraw_display()
    mixin._reset_state()

    # Error handling on write:
    mock_failing_mixin = MagicMock(spec=_StdoutInterceptorMixin)
    mock_failing_mixin._buffer = MagicMock()
    mock_failing_mixin._buffer.append.side_effect = Exception("Write fail")
    failing_interceptor = _InterceptedOutput(mock_failing_mixin, mock_stdout)
    with pytest.raises(Exception, match="Write fail"):
        failing_interceptor.write("crash")

    # Error handling on flush:
    mock_failing_flush = MagicMock(spec=_StdoutInterceptorMixin)
    mock_failing_flush.active = True
    mock_failing_flush._buffer = ["content"]
    mock_failing_flush._flush_buffer.side_effect = Exception("Flush fail")
    failing_flush_interceptor = _InterceptedOutput(mock_failing_flush, mock_stdout)
    with pytest.raises(Exception, match="Flush fail"):
        failing_flush_interceptor.flush()


def test_progress_bar_context_exception_handling() -> None:
    bar = ProgressBar()
    with pytest.raises(RuntimeError), bar.progress_context(100):
        raise RuntimeError("Context crash")
    assert bar.active is False


def test_throbber_initialization_and_configuration() -> None:
    throbber = Throbber(label="Loading", interval=0.05, frames=FRAMES_WINDMILL)
    assert abs(throbber.interval - 0.05) < 1e-9
    assert throbber.frames == FRAMES_WINDMILL

    # Setters and validation:
    throbber.set_interval(0.1)
    assert abs(throbber.interval - 0.1) < 1e-9

    with pytest.raises(ValueError, match="interval"):
        throbber.set_interval(0)

    throbber.set_frames(FRAMES_STANDARD)
    assert throbber.frames == FRAMES_STANDARD

    with pytest.raises(ValueError, match="at least two frames"):
        throbber.set_frames(["."])  # pyright:ignore[reportArgumentType]

    with pytest.raises(ValueError, match=r"must contain the '\{animation\}'"):
        throbber.set_format("{l}")


def test_throbber_context_and_animation() -> None:
    mock_stdout = io.StringIO()
    throbber = Throbber(label="Working", interval=0.01)

    with patch("sys.stdout", mock_stdout), throbber.context("Initial step") as update_label:
        time.sleep(0.03)
        update_label("Next step")
        time.sleep(0.03)
        # Redraw display:
        throbber._redraw_display()

    assert "Initial step" in mock_stdout.getvalue()
    assert "Next step" in mock_stdout.getvalue()
    assert throbber.active is False

    # Redraw when inactive:
    throbber._redraw_display()


def test_throbber_start_stop_manual() -> None:
    mock_stdout = io.StringIO()
    throbber = Throbber(interval=0.01)

    with patch("sys.stdout", mock_stdout):
        throbber.start("Manual start")
        assert throbber.active is True
        # Direct animation loop call when active vs inactive:
        throbber.active = False
        throbber._animation_loop()
        throbber.active = True
        # Repeated start is no-op:
        throbber.start("Repeated")
        time.sleep(0.03)
        throbber.stop()
        assert throbber.active is False
        # Repeated stop is no-op:
        throbber.stop()

        # Stop when active but stop_event is None and animation_thread is None:
        throbber.active = True
        throbber._stop_event = None
        throbber._animation_thread = None
        throbber.stop()


def test_throbber_animation_loop_error() -> None:
    throbber = Throbber(interval=0.01)
    mock_stdout = io.StringIO()
    with patch("sys.stdout", mock_stdout):
        throbber._buffer = []
        throbber._start_intercepting()
        throbber._stop_event = threading.Event()
        with patch.object(throbber, "_redraw_display", side_effect=Exception("Redraw boom")):
            throbber._animation_loop()
        assert throbber.active is False


def test_throbber_animation_loop_stop_event_cleared() -> None:
    throbber = Throbber(interval=0.01)
    mock_stdout = io.StringIO()
    with patch("sys.stdout", mock_stdout):
        throbber._buffer = []
        throbber._start_intercepting()
        throbber._stop_event = threading.Event()

        def clear_event() -> None:
            throbber._stop_event = None

        with patch.object(throbber, "_redraw_display", side_effect=clear_event):
            throbber._animation_loop()
        throbber.stop()


def test_throbber_context_exception_handling() -> None:
    throbber = Throbber(interval=0.01)
    with pytest.raises(RuntimeError), throbber.context("Crash"):
        raise RuntimeError("Throbber error")
    assert throbber.active is False
