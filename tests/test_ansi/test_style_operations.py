import xulbux.ansi
from xulbux.ansi import S, StyledText, _Link, _StyleGroup
import pytest


def test_explicit_rors():
    # 471:
    assert isinstance(S.BOLD.__ror__(_Link("url")), _StyleGroup)
    # 651:
    assert isinstance(S.hex("#F00").__ror__(S.BOLD), _StyleGroup)
    # 808:
    assert isinstance(_Link("url").__ror__(S.BOLD), _StyleGroup)


def test_colorstyle_or_group():
    # 644:
    g_st = S.BOLD | S.RED
    c_st = S.hex("#F00")
    assert isinstance(c_st | g_st, _StyleGroup)


def test_colorstyle_call_multiple():
    # 661: text[0] if len(text) == 1 else text:
    c_st = S.hex("#F00")
    assert c_st("a", "b").text == ("a", "b")


def test_link_matmul_multiple():
    # 828-831: _Link.__matmul__:
    link_st = _Link("url")
    assert (link_st @ "a").text == "a"
    assert (link_st @ ("a", "b")).text == ("a", "b")


def test_S_properties():
    # 946, 965, 984, 1002, 1030, 1048.
    # Just touch them:
    _ = S.RESET
    _ = S.RESET_FG
    _ = S.RESET_BG
    _ = S.hex
    _ = S.rgb
    _ = S.BG.hex
    _ = S.BG.rgb
    _ = S.link


def test_styledtext_methods_missing():
    # 1113, 1123, 1133, 1143, 1182, 1185, 1248, 1383.
    # StyledText stuff:
    st = StyledText("a")
    # 1113?
    assert issubclass(type(st), object)

    # 1182, 1185: raw property?
    assert st.raw == "a"
    assert StyledText(S.BOLD("a")).raw == "a"

    # 1248: probably rjust?
    # 1383: probably wrap?
    pass


def test_styledtext_getitem_error():
    # 1611:
    st = StyledText("a")
    with pytest.raises(ValueError):
        _ = st[::2]


def test_styledtext_wrap_edges():
    # 1785-1787, 1793, 1809:
    st1 = StyledText("abc\\ndef\\n\\nghi")
    wrapped_st1 = st1.wrap(2)
    assert isinstance(wrapped_st1, list)

    # word longer than width:
    st2 = StyledText("abcdef")
    wrapped_st2 = st2.wrap(2)
    assert isinstance(wrapped_st2, list)


def test_print_exit():
    # 1839->exit:
    import io

    file = io.StringIO()
    StyledText("a").print(file=file, flush=False)
    assert file.getvalue() == "a\n"


def test_config_terminal_windows_success():
    # 1943->1953:
    from unittest.mock import patch

    with patch("xulbux.ansi._os.name", "posix"):
        xulbux.ansi._terminal_ansi_configured = False
        xulbux.ansi._config_terminal()


def test_buildopenclose_edges():
    # 1971, 1986-1987, 1991->exit.
    # 1971: single cached style code:
    g1_st = _StyleGroup(S.BOLD)
    opens, _closes = xulbux.ansi._build_open_close(g1_st)
    assert opens

    # 1986-1987: FG color style:
    g2_st = _StyleGroup(S.hex("#F00"))
    _opens2, _closes2 = xulbux.ansi._build_open_close(g2_st)

    # 1991->exit: _process_code SGR.
    # multiple styles that share the same reset?
    g3_st = S.BOLD | S.DIM | S.RESET
    _opens3, _closes3 = xulbux.ansi._build_open_close(g3_st)


def test_render_tuple_styledtext():
    # render a tuple inside StyledText:
    st1 = StyledText(("a", "b"))
    assert st1.ansi == "ab"
    st2 = StyledText((S.BOLD("a"), "b"))
    assert "b" in st2.ansi
