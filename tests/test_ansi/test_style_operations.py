import io
from collections.abc import Callable
from unittest.mock import MagicMock
import xulbux.ansi
from xulbux.ansi import S, StyledText, _Link, _StyleGroup
import pytest


def test_explicit_ror():
    assert isinstance(S.BOLD.__ror__(_Link("url")), _StyleGroup)
    assert isinstance(S.hex("#F00").__ror__(S.BOLD), _StyleGroup)
    assert isinstance(_Link("url").__ror__(S.BOLD), _StyleGroup)


def test_ColorStyle_or_group():
    g_st = S.BOLD | S.RED
    c_st = S.hex("#F00")
    assert isinstance(c_st | g_st, _StyleGroup)


def test_ColorStyle_call_multiple():
    c_st = S.hex("#F00")
    assert c_st("a", "b").text == ("a", "b")


def test_link_matmul_multiple():
    # `_Link.__matmul__`:
    link_st = _Link("url")
    assert (link_st @ "a").text == "a"
    assert (link_st @ ("a", "b")).text == ("a", "b")


def test_S_properties():
    # Just touch them:
    _ = S.RESET
    _ = S.RESET_FG
    _ = S.RESET_BG
    _ = S.hex
    _ = S.rgb
    _ = S.BG.hex
    _ = S.BG.rgb
    _ = S.link


def test_StyledText_methods_missing():
    # `StyledText` stuff:
    st = StyledText("a")
    assert issubclass(type(st), object)
    assert st.raw == "a"
    assert StyledText(S.BOLD("a")).raw == "a"


def test_StyledText_getitem_error():
    st = StyledText("a")
    with pytest.raises(ValueError):
        _ = st[::2]


def test_StyledText_wrap_edges():
    st1 = StyledText("abc\\ndef\\n\\nghi")
    wrapped_st1 = st1.wrap(2)
    assert isinstance(wrapped_st1, list)

    # Word longer than width:
    st2 = StyledText("abcdef")
    wrapped_st2 = st2.wrap(2)
    assert isinstance(wrapped_st2, list)


def test_print_exit():
    file = io.StringIO()
    StyledText("a").print(file=file, flush=False)
    assert file.getvalue() == "a\n"


def test_config_terminal_posix(mock_os_linux: None):

    xulbux.ansi._terminal_ansi_configured = False
    xulbux.ansi._config_terminal()


def test_config_terminal_windows_success(mock_os_windows: None, mock_ctypes_windll: Callable[..., MagicMock]):

    mock_ctypes_windll()
    xulbux.ansi._terminal_ansi_configured = False
    xulbux.ansi._config_terminal()


def test_build_open_close_edges():
    # Single cached style code:
    g1_st = _StyleGroup(S.BOLD)
    opens, _closes = xulbux.ansi._build_open_close(g1_st)
    assert opens

    # FG `color` style:
    g2_st = _StyleGroup(S.hex("#F00"))
    _opens2, _closes2 = xulbux.ansi._build_open_close(g2_st)

    # Multiple styles that share the same reset:
    g3_st = S.BOLD | S.DIM | S.RESET
    _opens3, _closes3 = xulbux.ansi._build_open_close(g3_st)


def test_render_tuple_StyledText():
    # Tuple inside `StyledText`:
    st1 = StyledText(("a", "b"))
    assert st1.ansi == "ab"
    st2 = StyledText((S.BOLD("a"), "b"))
    assert "b" in st2.ansi
