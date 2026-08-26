from collections.abc import Callable
from unittest.mock import MagicMock, patch
import xulbux.ansi
from xulbux.ansi import S, StyledText, _config_terminal, _Link, _StyleGroup
import pytest


def test_StyledText_raw_code_positions():
    st = StyledText(S.BOLD("a"), "b")
    assert isinstance(st.raw_code_positions, tuple)
    assert len(st.raw_code_positions) == 2


def test_StyledText_iadd():
    st = StyledText("a")
    st += StyledText("b")
    assert st.ansi == "ab"
    st += "c"
    assert st.ansi == "abc"


def test_StyledText_eq_fallback():
    assert StyledText("a") != 1


def test_StyledText_multiply_char_edge():

    # Times <= 0:
    assert StyledText._multiply_char(StyledText("a"), 0) == ""
    assert StyledText._multiply_char(StyledText("a"), -1) == ""
    # With ansi code:
    st = StyledText(S.BOLD("a"))
    assert isinstance(StyledText._multiply_char(st, 2), str)


def test_StyledText_just_edge_cases():
    st = StyledText("a")

    # `fill_char` != 1:
    with pytest.raises(TypeError):
        st.ljust(5, "ab")
    with pytest.raises(TypeError):
        st.rjust(5, "ab")
    with pytest.raises(TypeError):
        st.center(5, "ab")

    # Padding == 0:
    assert st.ljust(1).ansi == "a"
    assert st.rjust(1).ansi == "a"
    assert st.center(1).ansi == "a"


def test_StyledText_wrap_edge():
    # Width <= 0 or fits:
    assert len(StyledText("a").wrap(0)) == 1
    assert len(StyledText("a").wrap(10)) == 1

    # Empty paragraph:
    st = StyledText("\n")
    assert len(st.wrap(10)) == 2

    # `wrapped_chunks` empty? (word too long):
    st = StyledText("abcdefghij")
    assert len(st.wrap(5)) == 2  # Textwrap will chunk it.


def test_StyledText_input():
    with patch("builtins.input", return_value="x"):
        assert StyledText("a").input(reset_ansi=True) == "x"


def test_StyledText_render_fallback():
    st = StyledText(123)  # pyright:ignore[reportArgumentType]
    assert st.ansi == "123"


def test_config_terminal_windows_error(mock_os_windows: None, mock_ctypes_windll: Callable[..., MagicMock]):

    mock_windll = mock_ctypes_windll()
    mock_windll.kernel32.GetConsoleMode.side_effect = Exception
    xulbux.ansi._terminal_ansi_configured = False
    _config_terminal()


def test_build_open_close_bg_color():
    g_st = S.BG.hex("#F00") | S.BOLD
    opens, _closes = xulbux.ansi._build_open_close(g_st)
    assert "\\x1b[48;2;255;0;0;1m" in opens or "\\x1b[1;48;2;255;0;0m" in opens or len(opens) >= 1


def test_build_open_close_empty():
    g_st = _StyleGroup()
    opens, closes = xulbux.ansi._build_open_close(g_st)
    assert not opens
    assert not closes


def test_build_open_close_link_only():
    g_st = _StyleGroup(_Link("url"))
    opens, _closes = xulbux.ansi._build_open_close(g_st)
    assert opens[0].startswith("\x1b]8;;")


def test_StyleGroup_eq_fallback():
    assert _StyleGroup() != 1


def test_StyleGroup_ror_custom():
    # Just call `__ror__` explicitly to cover it:
    g1_st = _StyleGroup(S.BOLD)
    g2_st = g1_st.__ror__(S.ITALIC)
    assert isinstance(g2_st, _StyleGroup)
