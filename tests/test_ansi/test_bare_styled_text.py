from xulbux.ansi import S, StyledText
from xulbux.base.consts import ANSI

ESC = ANSI.CHAR


def test_bare_fmt_emits_only_open_sequence():
    st = StyledText(S.RED)
    assert st.ansi == f"{ESC}[31m"
    assert st.raw == ""


def test_bare_reset_fmt():
    st = StyledText(S.RESET)
    assert st.ansi == f"{ESC}[0m"
    assert st.raw == ""


def test_bare_fmt_sequence_with_explicit_reset():
    st = StyledText(S.RED, "hello", S.RESET)
    assert st.ansi == f"{ESC}[31mhello{ESC}[0m"
    assert st.raw == "hello"


def test_bare_fmt_inside_tuple():
    st = StyledText((S.RED, "Hello", S.RESET))
    assert st.ansi == f"{ESC}[31mHello{ESC}[0m"
    assert st.raw == "Hello"


def test_bare_ColorFmt_emits_open_sequence():
    st = StyledText(S.hex("#ff6070"))
    assert st.ansi == f"{ESC}[38;2;255;96;112m"
    assert st.raw == ""


def test_bare_LinkFmt_emits_open_sequence():
    st = StyledText(S.link("https://example.com"))
    assert st.ansi == f"{ESC}]8;;https://example.com{ESC}\\"
    assert st.raw == ""


def test_bare_FmtGroup_emits_open_sequence():
    st = StyledText(S.BOLD | S.RED)
    assert st.ansi == f"{ESC}[1;31m"
    assert st.raw == ""


def test_bare_fmt_inside_nested_styled_call():
    st = StyledText(S.DIM("a", S.RED, "b", S.RESET_FG, "c"))
    assert st.ansi == f"{ESC}[2ma{ESC}[31mb{ESC}[39mc{ESC}[22m"
    assert st.raw == "abc"
