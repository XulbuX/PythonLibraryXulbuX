import io
import os
from collections.abc import Callable
from unittest.mock import MagicMock, patch
from xulbux.ansi import S
from xulbux.base.consts import CHARS
from xulbux.console import (
    _ConsoleInputHelper,
    _ConsoleInputValidator,
    _multiline_input_submit,
    _read_single_key,
    _to_styled_text,
    clear,
    confirm,
    get_encoding,
    get_height,
    get_size,
    get_width,
    has_color_support,
    input,
    is_tty,
    multiline_input,
    pause_exit,
)
import pytest
from prompt_toolkit.document import Document
from prompt_toolkit.key_binding import KeyPressEvent
from prompt_toolkit.validation import ValidationError


def test_terminal_dimensions_and_environment() -> None:
    with patch("os.get_terminal_size", return_value=os.terminal_size((120, 40))):
        assert get_width() == 120
        assert get_height() == 40
        assert get_size() == (120, 40)

    # Fallback on `OSError`:
    with patch("os.get_terminal_size", side_effect=OSError):
        assert get_width() == 80
        assert get_height() == 24
        assert get_size() == (80, 24)

    # `is_tty` check:
    with patch("sys.stdout.isatty", return_value=True):
        assert is_tty() is True
    with patch("sys.stdout.isatty", return_value=False):
        assert is_tty() is False

    # `get_encoding`:
    assert isinstance(get_encoding(), str)

    mock_stdout = MagicMock()
    mock_stdout.encoding = None
    with patch("sys.stdout", mock_stdout):
        assert get_encoding() == "utf-8"

    # Encoding exception:
    class FaultyStdout:
        @property
        def encoding(self) -> str:
            raise AttributeError("boom")

    with patch("sys.stdout", FaultyStdout()):
        assert get_encoding() == "utf-8"


def test_has_color_support_windows(mock_os_windows: None, mock_ctypes_windll: Callable[..., MagicMock]) -> None:
    # When not a TTY:
    with patch("xulbux.console.is_tty", return_value=False):
        assert has_color_support() is False

    mock_ctypes = mock_ctypes_windll()

    # Windows VT mode check:
    def mock_get_console_mode(handle: int, mode_ptr: MagicMock) -> int:
        mode_ptr._obj.value = 4
        return 1

    with (
        patch("xulbux.console.is_tty", return_value=True),
        patch.object(mock_ctypes.kernel32, "GetStdHandle", return_value=1),
        patch.object(mock_ctypes.kernel32, "GetConsoleMode", side_effect=mock_get_console_mode),
    ):
        assert has_color_support() is True

    # Windows VT mode disabled:
    def mock_get_console_mode_disabled(handle: int, mode_ptr: MagicMock) -> int:
        mode_ptr._obj.value = 0
        return 1

    with (
        patch("xulbux.console.is_tty", return_value=True),
        patch.object(mock_ctypes.kernel32, "GetStdHandle", return_value=1),
        patch.object(mock_ctypes.kernel32, "GetConsoleMode", side_effect=mock_get_console_mode_disabled),
    ):
        assert has_color_support() is False

    # Windows VT check returning False (0):
    with (
        patch("xulbux.console.is_tty", return_value=True),
        patch.object(mock_ctypes.kernel32, "GetStdHandle", return_value=1),
        patch.object(mock_ctypes.kernel32, "GetConsoleMode", return_value=0),
    ):
        assert has_color_support() is False

    # Windows VT check exception:
    with (
        patch("xulbux.console.is_tty", return_value=True),
        patch.object(mock_ctypes.kernel32, "GetStdHandle", side_effect=Exception),
    ):
        assert has_color_support() is False


def test_has_color_support_posix(mock_os_linux: None) -> None:
    with (
        patch("xulbux.console.is_tty", return_value=True),
        patch.dict("os.environ", {"TERM": "xterm-256color"}),
    ):
        assert has_color_support() is True


def test_clear_terminal() -> None:
    buffer = io.StringIO()
    with patch("sys.stdout", buffer):
        clear()
    assert buffer.getvalue() == "\033[2J\033[3J\033[H\033[0m"


def test_pause_and_pause_exit() -> None:
    # `pause_exit` without exiting:
    with patch("xulbux.console._read_single_key") as mock_read:
        pause_exit("Done", pause=True, exit=False)
        mock_read.assert_called_once()

    # `pause_exit` with exiting:
    with patch("xulbux.console._read_single_key"), pytest.raises(SystemExit) as exc_info:
        pause_exit("Exiting", pause=False, exit=True, exit_code=42)
    assert exc_info.value.code == 42


def test_read_single_key_non_tty() -> None:
    with patch("sys.stdin.isatty", return_value=False), patch("sys.stdin.readline", return_value=""):
        _read_single_key()


def test_read_single_key_windows(mock_os_windows: None) -> None:
    mock_msvcrt = MagicMock()
    mock_msvcrt.getch.return_value = b"a"
    with (
        patch("sys.stdin.isatty", return_value=True),
        patch.dict("sys.modules", {"msvcrt": mock_msvcrt}),
    ):
        _read_single_key()


def test_read_single_key_posix(mock_os_linux: None) -> None:
    mock_termios = MagicMock()
    mock_tty = MagicMock()
    with (
        patch("sys.stdin.isatty", return_value=True),
        patch("sys.stdin.fileno", return_value=0),
        patch("sys.stdin.read", return_value="a"),
        patch.dict("sys.modules", {"termios": mock_termios, "tty": mock_tty}),
    ):
        _read_single_key()


def test_confirm_prompts() -> None:
    with patch("xulbux.console.input", return_value="y"):
        assert confirm("Proceed?") is True

    with patch("xulbux.console.input", return_value="n"):
        assert confirm("Proceed?") is False

    with patch("xulbux.console.input", return_value=""):
        assert confirm("Proceed?", default_is_yes=True) is True
        assert confirm("Proceed?", default_is_yes=False) is False

    with patch("xulbux.console.input", return_value="yes"):
        assert confirm("Proceed?", start="Start: ", end="End\n", default_color=S.GREEN) is True


def test_multiline_input() -> None:
    with patch("prompt_toolkit.prompt", return_value="Line 1\nLine 2") as mock_prompt:
        result = multiline_input("Write code:", start="Start ", end="\n", show_keybindings=True)
        assert result == "Line 1\nLine 2"
        mock_prompt.assert_called_once()

    # Without keybindings:
    with patch("prompt_toolkit.prompt", return_value="Line"):
        assert multiline_input("Code:", show_keybindings=False) == "Line"

    # `_multiline_input_submit` event:
    mock_event = MagicMock()
    mock_event.app.current_buffer.document.text = "Submitted text"
    _multiline_input_submit(mock_event)
    mock_event.app.exit.assert_called_once_with(result="Submitted text")


def test_input_session_prompt_and_conversions() -> None:
    mock_session = MagicMock()
    mock_session.prompt.return_value = None

    with patch("prompt_toolkit.PromptSession", return_value=mock_session):
        with patch.object(_ConsoleInputHelper, "get_text", return_value="12345"):
            int_res = input("Enter number: ", default_color=S.CYAN, output_type=int)
            assert int_res == 12345

        # Empty string without `default_val`:
        with patch.object(_ConsoleInputHelper, "get_text", return_value=""):
            empty_str = input("Enter text: ")
            assert empty_str == ""

        # Default fallback when empty:
        with patch.object(_ConsoleInputHelper, "get_text", return_value=""):
            default_res = input("Enter text: ", default_val="DefaultText")
            assert default_res == "DefaultText"

        # Conversion error fallback:
        with patch.object(_ConsoleInputHelper, "get_text", return_value="not_an_int"):
            default_on_err = input("Enter number: ", default_val=999, output_type=int)
            assert default_on_err == 999

            with pytest.raises(ValueError):
                _ = input("Enter number: ", output_type=int)


def test_console_input_helper_and_validator() -> None:
    helper = _ConsoleInputHelper(
        mask_char="*",
        min_len=2,
        max_len=5,
        allowed_chars="abc123",
        allow_paste=False,
        validator=lambda text: "Too short" if len(text) < 3 else None,
    )

    # Key event handlers:
    mock_buffer = MagicMock()
    mock_buffer.document = Document("ab")
    mock_buffer.cursor_position = 1
    mock_buffer.selection_state = None
    mock_event = MagicMock(spec=KeyPressEvent)
    mock_event.app.current_buffer = mock_buffer
    mock_event.data = ""

    # Backspace & delete:
    helper.result_text = "ab"
    helper.handle_backspace(mock_event)
    assert helper.result_text == "b"

    mock_buffer.cursor_position = 0
    helper.result_text = "ab"
    helper.handle_delete(mock_event)
    assert helper.result_text == "b"

    # Edge cases: backspace at position 0, delete at position len:
    mock_buffer.cursor_position = 0
    helper.handle_backspace(mock_event)
    mock_buffer.cursor_position = len(helper.result_text)
    helper.handle_delete(mock_event)

    helper.handle_control_a(mock_event)

    # Direct `get_text`:
    assert helper.get_text() == helper.result_text

    # Selection delete:
    mock_buffer.selection_state = MagicMock()
    mock_buffer.document = MagicMock()
    mock_buffer.document.selection_range.return_value = (0, 2)
    helper.result_text = "abcd"
    helper.remove_text_event(mock_event)
    assert helper.result_text == "cd"

    # Pasting when allow_paste is False:
    mock_paste_event = MagicMock(spec=KeyPressEvent)
    mock_paste_event.data = "pasted_text"
    helper.handle_paste(mock_paste_event)
    assert helper.tried_pasting is True

    # Pasting when allow_paste is True:
    helper.allow_paste = True
    helper.handle_paste(mock_paste_event)

    # Any character insert unmasked vs masked:
    helper_unmasked_ins = _ConsoleInputHelper(
        mask_char=None,
        min_len=None,
        max_len=10,
        allowed_chars="abc",
        allow_paste=True,
        validator=None,
    )
    mock_event.data = "a"
    mock_buffer.cursor_position = 0
    helper_unmasked_ins.handle_any(mock_event)

    # Masked insert:
    helper.handle_any(mock_event)

    # Disallowed character:
    mock_event.data = "z"
    helper.handle_any(mock_event)

    # Empty data:
    mock_event.data = ""
    helper.insert_text_event(mock_event)

    # Insert text processing:
    helper.allowed_chars = "abc"
    helper.result_text = ""
    filtered, removed = helper.process_insert_text("a!b@c")
    assert filtered == "abc"
    assert removed == {"!", "@"}

    # Exceeding remaining space with `CHARS.ALL`:
    helper.allowed_chars = CHARS.ALL
    helper.max_len = 3
    helper.result_text = "a"
    trunc_txt, _ = helper.process_insert_text("bcde")
    assert trunc_txt == "bc"

    # Fully full space:
    helper.result_text = "abc"
    full_txt, _ = helper.process_insert_text("d")
    assert full_txt == ""

    # `max_len` is None:
    helper.max_len = None
    no_max_txt, _ = helper.process_insert_text("hello")
    assert no_max_txt == "hello"

    empty_proc, _ = helper.process_insert_text("")
    assert empty_proc == ""

    # Toolbar messages testing with masked mode:
    helper.mask_char = "*"
    helper.result_text = "abc"
    helper.min_len = 5
    helper.max_len = 5
    helper.filtered_chars = {"x"}
    helper.tried_pasting = True
    tb_masked = helper.bottom_toolbar()
    assert tb_masked is not None

    # Toolbar with multiple filtered chars:
    helper.filtered_chars = {"x", "y"}
    helper.result_text = "abcdef"  # Too long (> `max_len` 5)
    tb_long = helper.bottom_toolbar()
    assert tb_long is not None

    # Toolbar when `max_len` reached:
    helper.result_text = "abcde"  # == `max_len` 5
    tb_exact = helper.bottom_toolbar()
    assert tb_exact is not None

    # Toolbar with unmasked mode and validator error message:
    helper_unmasked_val = _ConsoleInputHelper(
        mask_char=None,
        min_len=2,
        max_len=10,
        allowed_chars=CHARS.ALL,
        allow_paste=True,
        validator=lambda text: "Validation failed" if text == "invalid" else None,
    )
    mock_app = MagicMock()
    mock_app.current_buffer.text = "invalid"
    with patch("prompt_toolkit.application.get_app", return_value=mock_app):
        tb_val = helper_unmasked_val.bottom_toolbar()
        assert tb_val is not None

    # Toolbar exception fallback:
    with patch("prompt_toolkit.application.get_app", side_effect=Exception):
        helper_unmask = _ConsoleInputHelper(None, None, None, "a", True, None)
        tb_err = helper_unmask.bottom_toolbar()
        assert tb_err is not None

    # Validation errors on `min_len` and custom validator:
    val_masked = _ConsoleInputValidator(lambda: "a", mask_char="*", min_len=5, validator=None)
    with pytest.raises(ValidationError):
        val_masked.validate(Document("a"))

    val_custom = _ConsoleInputValidator(lambda: "abc", mask_char=None, min_len=None, validator=lambda t: "Error")
    with pytest.raises(ValidationError):
        val_custom.validate(Document("abc"))

    # Validator returning None (valid):
    val_valid = _ConsoleInputValidator(lambda: "abc", mask_char=None, min_len=None, validator=lambda t: None)
    val_valid.validate(Document("abc"))


def test_to_styled_text_fallback() -> None:
    st = _to_styled_text(12345)
    assert isinstance(st, S)


def test_input_invalid_arguments() -> None:
    with pytest.raises(ValueError, match="mask_char"):
        _ = input(mask_char="**")
    with pytest.raises(ValueError, match="min_len"):
        _ = input(min_len=-1)
    with pytest.raises(ValueError, match="max_len"):
        _ = input(max_len=-1)
