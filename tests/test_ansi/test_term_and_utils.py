import io
from pathlib import Path
from unittest.mock import patch
import xulbux.ansi as _ansi_module
from xulbux.ansi import S, StyledText, Term, _build_open_close, _config_terminal, _StyleGroup
from xulbux.base.consts import ANSI
from xulbux.color import hexa, rgba


def test_term_control_constants() -> None:
    assert f"{ANSI.CHAR}[2K" == Term.CLEAR_LINE
    assert f"{ANSI.CHAR}[2J" == Term.CLEAR_SCREEN
    assert f"{ANSI.CHAR}[?25l" == Term.HIDE_CURSOR
    assert f"{ANSI.CHAR}[?25h" == Term.SHOW_CURSOR
    assert f"{ANSI.CHAR}[?1049h" == Term.ALT_SCREEN
    assert f"{ANSI.CHAR}[?1049l" == Term.MAIN_SCREEN


def test_term_cursor_methods() -> None:
    assert Term.up(3) == f"{ANSI.CHAR}[3A"
    assert Term.down(2) == f"{ANSI.CHAR}[2B"
    assert Term.left(4) == f"{ANSI.CHAR}[4D"
    assert Term.right(5) == f"{ANSI.CHAR}[5C"
    assert Term.prev_line(1) == f"{ANSI.CHAR}[1F"
    assert Term.next_line(2) == f"{ANSI.CHAR}[2E"
    assert Term.move(10, 20) == f"{ANSI.CHAR}[10;20H"
    assert Term.title("Terminal Title") == f"{ANSI.CHAR}]2;Terminal Title\x07"
    assert Term.save() == f"{ANSI.CHAR}[s"
    assert Term.restore() == f"{ANSI.CHAR}[u"


def test_rgb_and_hex_overloads() -> None:
    rgb_from_rgba = S.rgb(rgba(255, 0, 0))
    assert StyledText(rgb_from_rgba("text")).ansi == "\x1b[38;2;255;0;0mtext\x1b[39m"

    hex_from_hexa = S.hex(hexa("#00FF00"))
    assert StyledText(hex_from_hexa("text")).ansi == "\x1b[38;2;0;255;0mtext\x1b[39m"

    link_from_path = S.link(Path("tests/test_ansi"))
    assert "tests/test_ansi" in StyledText(link_from_path("Link")).ansi


def test_terminal_configuration_windows_and_posix() -> None:
    # Test configuring terminal on Windows:
    _ansi_module._terminal_ansi_configured = False
    with (
        patch("os.name", "nt"),
        patch("ctypes.windll.kernel32.GetStdHandle", return_value=1),
        patch("ctypes.windll.kernel32.GetConsoleMode", return_value=1),
        patch("ctypes.windll.kernel32.SetConsoleMode", return_value=1),
    ):
        _config_terminal()
        assert _ansi_module._terminal_ansi_configured is True

    # Test configuring terminal on POSIX:
    _ansi_module._terminal_ansi_configured = False
    with patch("os.name", "posix"):
        _config_terminal()
        assert _ansi_module._terminal_ansi_configured is True

    # Repeated calls should be no-ops:
    _config_terminal()


def test_styled_text_print_stream_options() -> None:
    stream = io.StringIO()
    text = StyledText("No flush")
    text.print(file=stream, flush=False)
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
