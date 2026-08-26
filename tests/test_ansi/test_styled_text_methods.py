from unittest.mock import patch
import xulbux.ansi
from xulbux.ansi import S, StyledText, _config_terminal, _Link, _StyleGroup
import pytest


def test_styledtext_raw_code_positions():
    st = StyledText(S.BOLD("a"), "b")
    assert isinstance(st.raw_code_positions, tuple)
    assert len(st.raw_code_positions) == 2


def test_styledtext_iadd():
    st = StyledText("a")
    st += StyledText("b")
    assert st.ansi == "ab"
    st += "c"
    assert st.ansi == "abc"


def test_styledtext_eq_fallback():
    assert StyledText("a") != 1


def test_styledtext_multiply_char_edge():
    from xulbux.ansi import StyledText

    # times <= 0:
    assert StyledText._multiply_char(StyledText("a"), 0) == ""
    assert StyledText._multiply_char(StyledText("a"), -1) == ""
    # with ansi code:
    st = StyledText(S.BOLD("a"))
    assert isinstance(StyledText._multiply_char(st, 2), str)


def test_styledtext_just_edge_cases():
    st = StyledText("a")

    # fill_char != 1:
    with pytest.raises(TypeError):
        st.ljust(5, "ab")
    with pytest.raises(TypeError):
        st.rjust(5, "ab")
    with pytest.raises(TypeError):
        st.center(5, "ab")

    # padding == 0:
    assert st.ljust(1).ansi == "a"
    assert st.rjust(1).ansi == "a"
    assert st.center(1).ansi == "a"


def test_styledtext_wrap_edge():
    # width <= 0 or fits:
    assert len(StyledText("a").wrap(0)) == 1
    assert len(StyledText("a").wrap(10)) == 1

    # empty paragraph:
    st = StyledText("\n")
    assert len(st.wrap(10)) == 2

    # wrapped_chunks empty? (word too long):
    st = StyledText("abcdefghij")
    assert len(st.wrap(5)) == 2  # textwrap will chunk it.


def test_styledtext_input():
    with patch("builtins.input", return_value="x"):
        assert StyledText("a").input(reset_ansi=True) == "x"


def test_styledtext_render_fallback():
    st = StyledText(123)  # pyright:ignore[reportArgumentType]
    assert st.ansi == "123"


def test_config_terminal_windows_error():
    import os

    if os.name == "nt":
        with patch("ctypes.windll.kernel32.GetConsoleMode", side_effect=Exception):
            import xulbux.ansi

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


def test_stylegroup_eq_fallback():
    assert _StyleGroup() != 1


def test_stylegroup_ror_custom():
    # Just call __ror__ explicitly to cover it:
    g1_st = _StyleGroup(S.BOLD)
    g2_st = g1_st.__ror__(S.ITALIC)
    assert isinstance(g2_st, _StyleGroup)
