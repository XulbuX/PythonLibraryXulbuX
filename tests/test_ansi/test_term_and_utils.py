import io
from collections.abc import Callable
from pathlib import Path
from unittest.mock import MagicMock
import xulbux.ansi as _ansi_module
from xulbux.ansi import S, Term, _build_open_close, _config_terminal, _StyleGroup
from xulbux.base.consts import ANSI
from xulbux.color import hexa, rgba
import pytest


def test_term_control_constants() -> None:
    assert f"{ANSI.CHAR}[2K" == Term.CLEAR_LINE
    assert f"{ANSI.CHAR}[0K" == Term.CLEAR_LINE_TO_END
    assert f"{ANSI.CHAR}[1K" == Term.CLEAR_LINE_TO_START
    assert f"{ANSI.CHAR}[2J" == Term.CLEAR_SCREEN
    assert f"{ANSI.CHAR}[0J" == Term.CLEAR_SCREEN_TO_END
    assert f"{ANSI.CHAR}[1J" == Term.CLEAR_SCREEN_TO_START
    assert f"{ANSI.CHAR}[3J" == Term.CLEAR_SCROLLBACK
    assert f"{ANSI.CHAR}[?25l" == Term.HIDE_CURSOR
    assert f"{ANSI.CHAR}[?25h" == Term.SHOW_CURSOR
    assert f"{ANSI.CHAR}[?1049h" == Term.ALT_SCREEN
    assert f"{ANSI.CHAR}[?1049l" == Term.MAIN_SCREEN
    assert Term.BELL == "\x07"
    assert f"{ANSI.CHAR}[?2004h" == Term.BRACKETED_PASTE_ENABLE
    assert f"{ANSI.CHAR}[?2004l" == Term.BRACKETED_PASTE_DISABLE
    assert f"{ANSI.CHAR}[?7h" == Term.LINE_WRAP_ENABLE
    assert f"{ANSI.CHAR}[?7l" == Term.LINE_WRAP_DISABLE
    assert f"{ANSI.CHAR}c" == Term.RESET
    assert f"{ANSI.CHAR}[!p" == Term.SOFT_RESET


def test_term_cursor_methods() -> None:
    assert Term.up(3) == f"{ANSI.CHAR}[3A"
    assert Term.down(2) == f"{ANSI.CHAR}[2B"
    assert Term.left(4) == f"{ANSI.CHAR}[4D"
    assert Term.right(5) == f"{ANSI.CHAR}[5C"
    assert Term.prev_line(1) == f"{ANSI.CHAR}[1F"
    assert Term.next_line(2) == f"{ANSI.CHAR}[2E"
    assert Term.column(10) == f"{ANSI.CHAR}[10G"
    assert Term.move(10, 20) == f"{ANSI.CHAR}[10;20H"
    assert Term.home() == f"{ANSI.CHAR}[H"
    assert Term.insert_lines(2) == f"{ANSI.CHAR}[2L"
    assert Term.delete_lines(3) == f"{ANSI.CHAR}[3M"
    assert Term.insert_chars(4) == f"{ANSI.CHAR}[4@"
    assert Term.delete_chars(5) == f"{ANSI.CHAR}[5P"
    assert Term.scroll_up(2) == f"{ANSI.CHAR}[2S"
    assert Term.scroll_down(3) == f"{ANSI.CHAR}[3T"
    assert Term.title("Terminal Title") == f"{ANSI.CHAR}]2;Terminal Title\x07"
    assert Term.save() == f"{ANSI.CHAR}[s"
    assert Term.restore() == f"{ANSI.CHAR}[u"
    assert Term.save_dec() == f"{ANSI.CHAR}7"
    assert Term.restore_dec() == f"{ANSI.CHAR}8"


def test_term_cursor_shape() -> None:
    assert Term.cursor_shape("blinking_block") == f"{ANSI.CHAR}[1 q"
    assert Term.cursor_shape("steady_block") == f"{ANSI.CHAR}[2 q"
    assert Term.cursor_shape("blinking_underline") == f"{ANSI.CHAR}[3 q"
    assert Term.cursor_shape("steady_underline") == f"{ANSI.CHAR}[4 q"
    assert Term.cursor_shape("blinking_bar") == f"{ANSI.CHAR}[5 q"
    assert Term.cursor_shape("steady_bar") == f"{ANSI.CHAR}[6 q"
    assert Term.cursor_shape(1) == f"{ANSI.CHAR}[1 q"
    assert Term.cursor_shape(6) == f"{ANSI.CHAR}[6 q"

    with pytest.raises(ValueError, match="cursor shape"):
        Term.cursor_shape(0)  # type:ignore[arg-type]
    with pytest.raises(ValueError, match="cursor shape"):
        Term.cursor_shape(7)  # type:ignore[arg-type]
    with pytest.raises(ValueError, match="cursor shape"):
        Term.cursor_shape("invalid_shape")  # type:ignore[arg-type]


def test_term_clipboard_and_cwd() -> None:
    assert Term.clipboard_copy("hello world") == f"{ANSI.CHAR}]52;c;aGVsbG8gd29ybGQ={ANSI.CHAR}\\"
    assert Term.cwd("/custom/path") == f"{ANSI.CHAR}]7;/custom/path{ANSI.CHAR}\\"
    cwd_path_res = Term.cwd(Path("tests/test_ansi"))
    assert "file://" in cwd_path_res
    assert cwd_path_res.startswith(f"{ANSI.CHAR}]7;")
    assert cwd_path_res.endswith(f"{ANSI.CHAR}\\")

    # Verify SEQ_PATTERN strips new sequences properly in S.raw:
    styled_with_dec = S(Term.save_dec(), "hello", Term.restore_dec())
    assert styled_with_dec.raw == "hello"


def test_rgb_and_hex_overloads() -> None:
    rgb_from_rgba = S.rgb(rgba(255, 0, 0))
    assert rgb_from_rgba("text").ansi == "\x1b[38;2;255;0;0mtext\x1b[39m"

    hex_from_hexa = S.hex(hexa("#00FF00"))
    assert hex_from_hexa("text").ansi == "\x1b[38;2;0;255;0mtext\x1b[39m"

    link_from_path = S.link(Path("tests/test_ansi"))
    assert "tests/test_ansi" in link_from_path("Link").ansi


def test_terminal_configuration_windows(mock_os_windows: None, mock_ctypes_windll: Callable[..., MagicMock]) -> None:
    _ansi_module._terminal_configured = False
    mock_ctypes = mock_ctypes_windll()
    mock_ctypes.kernel32.GetStdHandle.return_value = 1
    mock_ctypes.kernel32.GetConsoleMode.return_value = 1
    mock_ctypes.kernel32.SetConsoleMode.return_value = 1
    _config_terminal()
    assert _ansi_module._terminal_configured is True


def test_terminal_configuration_posix(mock_os_linux: None) -> None:
    _ansi_module._terminal_configured = False
    _config_terminal()
    assert _ansi_module._terminal_configured is True


def test_terminal_configuration_repeated_calls_are_no_ops() -> None:
    _ansi_module._terminal_configured = True
    _config_terminal()
    assert _ansi_module._terminal_configured is True


def test_styled_text_print_stream_options() -> None:
    stream = io.StringIO()
    S("No flush").print(file=stream, flush=False)
    assert stream.getvalue() == "No flush\n"


def test_build_open_close_complex_groups() -> None:
    # Fast path for single standard code:
    single_opens, single_closes = _build_open_close(_StyleGroup(S.BOLD))
    assert single_opens == ("\x1b[1m",)
    assert single_closes == ("\x1b[22m",)

    # Duplicate resets deduplication check:
    dedup_opens, dedup_closes = _build_open_close(S.BOLD | S.DIM | S.RED | S.GREEN)
    assert dedup_opens == ("\x1b[1;2;31;32m",)
    assert dedup_closes == ("\x1b[22;39m",)

    # Link only group (no SGR opens):
    link_only_opens, link_only_closes = _build_open_close(_StyleGroup(S.link("https://example.com")))
    assert any("https://example.com" in piece for piece in link_only_opens)
    assert link_only_closes == ("\x1b]8;;\x1b\\",)

    # StyleGroup with multiple colors & resets:
    complex_group = S.BOLD | S.rgb(255, 0, 0) | S.BG.rgb(0, 0, 255) | S.link("https://example.com")
    opens, closes = _build_open_close(complex_group)

    assert any("https://example.com" in piece for piece in opens)
    assert any("38;2;255;0;0" in piece for piece in opens)
    assert any("48;2;0;0;255" in piece for piece in opens)
    assert any("\x1b]8;;\x1b\\" in piece for piece in closes)
