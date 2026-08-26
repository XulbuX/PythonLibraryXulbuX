import io
import sys
from pathlib import Path
from xulbux.ansi import S, StyledText, _build_open_close, _StyleGroup
from xulbux.base.consts import ANSI
import pytest

ESC = ANSI.CHAR


def test_plain_string_passes_through():
    st = StyledText("Hello, world!")
    assert st.ansi == "Hello, world!"
    assert st.raw == "Hello, world!"
    assert st.code_positions == ()


def test_single_style_wraps_text_with_open_and_reset():
    st = StyledText(S.BOLD("Hi"))
    assert st.ansi == f"{ESC}[1mHi{ESC}[22m"
    assert st.raw == "Hi"


def test_combined_group_emits_single_sgr():
    st = StyledText((S.BOLD | S.RED)("Hi"))
    assert st.ansi == f"{ESC}[1;31mHi{ESC}[22;39m"
    assert st.raw == "Hi"


def test_default_separator_is_empty_string():
    st = StyledText("a", "b", "c")
    assert st.ansi == "abc"
    assert st.raw == "abc"


def test_custom_separator():
    st = StyledText("a", "b", sep=" | ")
    assert st.ansi == "a | b"


def test_nested_styled_keeps_outer_style_after_inner_reset():
    st = StyledText(S.CYAN("Outer ", S.DIM("Inner"), " Outer"))
    assert st.ansi == f"{ESC}[36mOuter {ESC}[2mInner{ESC}[22m Outer{ESC}[39m"
    assert st.raw == "Outer Inner Outer"


def test_tuple_as_multi_segment_group():
    st = StyledText(("a", S.BOLD("b"), "c"))
    assert st.ansi == f"a{ESC}[1mb{ESC}[22mc"
    assert st.raw == "abc"


def test_multi_text_args_in_call():
    st = StyledText(S.BOLD("a", S.RED("b"), "c"))
    assert st.ansi == f"{ESC}[1ma{ESC}[31mb{ESC}[39mc{ESC}[22m"
    assert st.raw == "abc"


def test_bright_fg_color():
    st = StyledText(S.BR.BLUE("x"))
    assert st.ansi == f"{ESC}[94mx{ESC}[39m"


def test_bg_color():
    st = StyledText(S.BG.RED("x"))
    assert st.ansi == f"{ESC}[41mx{ESC}[49m"


def test_bright_bg_color():
    st = StyledText(S.BG.BR.GREEN("x"))
    assert st.ansi == f"{ESC}[102mx{ESC}[49m"


def test_rgb_fg():
    st = StyledText(S.rgb(10, 20, 30)("x"))
    assert st.ansi == f"{ESC}[38;2;10;20;30mx{ESC}[39m"


def test_rgb_bg():
    st = StyledText(S.BG.rgb(10, 20, 30)("x"))
    assert st.ansi == f"{ESC}[48;2;10;20;30mx{ESC}[49m"


def test_hex_fg_short_and_long():
    short_hex_st = StyledText(S.hex("#abc")("x")).ansi
    long_hex_st = StyledText(S.hex("aabbcc")("x")).ansi
    assert short_hex_st == long_hex_st == f"{ESC}[38;2;170;187;204mx{ESC}[39m"


def test_hex_bg():
    st = StyledText(S.BG.hex("#102030")("x"))
    assert st.ansi == f"{ESC}[48;2;16;32;48mx{ESC}[49m"


def test_link_alone_wraps_text():
    st = StyledText(S.link("https://example.com")("click"))
    assert st.ansi == f"{ESC}]8;;https://example.com{ESC}\\click{ESC}]8;;{ESC}\\"
    assert st.raw == "click"


def test_link_combined_with_style():
    st = StyledText((S.link("https://x") | S.BOLD)("click"))
    assert st.ansi == f"{ESC}]8;;https://x{ESC}\\{ESC}[1mclick{ESC}[22m{ESC}]8;;{ESC}\\"


def test_link_with_path():
    path = Path("docs/readme.md")
    st = StyledText(S.link(path)("click"))
    assert st.ansi == f"{ESC}]8;;{path.resolve().as_uri()}{ESC}\\click{ESC}]8;;{ESC}\\"


def test_code_positions_match_offsets_in_ansi():
    st = StyledText(S.BOLD("hi"))
    # `{ESC}[1m` then `hi` then `{ESC}[22m`:
    assert st.code_positions == ((0, f"{ESC}[1m"), (len(f"{ESC}[1m") + 2, f"{ESC}[22m"))
    # Offsets must be valid slice points into the ANSI string:
    for position, seq in st.code_positions:
        assert st.ansi[position : position + len(seq)] == seq


def test_raw_equals_ansi_minus_sequences():
    st = StyledText(S.CYAN("a"), (S.BOLD | S.RED)("b"), "plain")
    stripped = st.ansi
    for _, sequence in st.code_positions:
        stripped = stripped.replace(sequence, "", 1)
    assert stripped == st.raw


def test_remove_ansi_strips_csi_and_osc():
    mixed = f"{ESC}[1mhi{ESC}[0m and {ESC}]8;;u{ESC}\\link{ESC}]8;;{ESC}\\"
    assert StyledText.remove_ansi(mixed) == "hi and link"


def test_print_writes_ansi_plus_end_to_stdout(monkeypatch: pytest.MonkeyPatch):
    buffer = io.StringIO()
    monkeypatch.setattr(sys, "stdout", buffer)
    StyledText(S.BOLD("hi")).print(end="!")
    assert buffer.getvalue() == f"{ESC}[1mhi{ESC}[22m!"


def test_input_uses_ansi_as_prompt(monkeypatch: pytest.MonkeyPatch):
    captured: dict[str, str] = {}

    def fake_input(prompt: str = "") -> str:
        captured["prompt"] = prompt
        return "answer"

    monkeypatch.setattr("builtins.input", fake_input)
    st = StyledText(S.BOLD("Name: ")).input()
    assert st == "answer"
    assert captured["prompt"] == f"{ESC}[1mName: {ESC}[22m"


def test_or_chains_produce_FmtGroup():
    group = S.BOLD | S.RED | S.UNDERLINE
    assert isinstance(group, _StyleGroup)
    # `_Style` is an `int` subclass, so direct `int` comparison works:
    assert list(group) == [1, 31, 4]


def test_pipe_with_FmtGroup_left_and_right():
    left_assoc = (S.BOLD | S.RED) | S.UNDERLINE
    right_assoc = S.BOLD | (S.RED | S.UNDERLINE)
    assert list(left_assoc) == list(right_assoc) == [1, 31, 4]


def test_build_open_close_dedupes_close_codes():
    # Bold + dim both reset to 22 → only one 22 in close:
    opens, closes = _build_open_close(S.BOLD | S.DIM)
    assert opens == (f"{ESC}[1;2m",)
    assert closes == (f"{ESC}[22m",)
