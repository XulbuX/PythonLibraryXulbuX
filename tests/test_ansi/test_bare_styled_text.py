from xulbux.ansi import S, StyledText
from xulbux.base.consts import ANSI

ESC = ANSI.CHAR


def test_bare_fmt_emits_only_open_sequence():
    result = StyledText(S.RED)
    assert result.ansi == f"{ESC}[31m"
    assert result.raw == ""


def test_bare_reset_fmt():
    result = StyledText(S.RESET)
    assert result.ansi == f"{ESC}[0m"
    assert result.raw == ""


def test_bare_fmt_sequence_with_explicit_reset():
    result = StyledText(S.RED, "hello", S.RESET)
    assert result.ansi == f"{ESC}[31mhello{ESC}[0m"
    assert result.raw == "hello"


def test_bare_fmt_inside_tuple():
    result = StyledText((S.RED, "Hello", S.RESET))
    assert result.ansi == f"{ESC}[31mHello{ESC}[0m"
    assert result.raw == "Hello"


def test_bare_ColorFmt_emits_open_sequence():
    result = StyledText(S.hex("#ff6070"))
    assert result.ansi == f"{ESC}[38;2;255;96;112m"
    assert result.raw == ""


def test_bare_LinkFmt_emits_open_sequence():
    result = StyledText(S.link("https://example.com"))
    assert result.ansi == f"{ESC}]8;;https://example.com{ESC}\\"
    assert result.raw == ""


def test_bare_FmtGroup_emits_open_sequence():
    result = StyledText(S.BOLD | S.RED)
    assert result.ansi == f"{ESC}[1;31m"
    assert result.raw == ""


def test_bare_fmt_inside_nested_styled_call():
    result = StyledText(S.DIM("a", S.RED, "b", S.RESET_FG, "c"))
    expected = f"{ESC}[2ma{ESC}[31mb{ESC}[39mc{ESC}[22m"
    assert result.ansi == expected
    assert result.raw == "abc"
