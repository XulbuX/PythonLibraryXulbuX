import io
import sys
from pathlib import Path
from xulbux.ansi import S, StyledText, _build_open_close, _StyleGroup
from xulbux.base.consts import ANSI
import pytest

ESC = ANSI.CHAR


def test_plain_string_passes_through():
    result = StyledText("Hello, world!")
    assert result.ansi == "Hello, world!"
    assert result.raw == "Hello, world!"
    assert result.code_positions == ()


def test_single_style_wraps_text_with_open_and_reset():
    result = StyledText(S.BOLD("Hi"))
    assert result.ansi == f"{ESC}[1mHi{ESC}[22m"
    assert result.raw == "Hi"


def test_combined_group_emits_single_sgr():
    result = StyledText((S.BOLD | S.RED)("Hi"))
    assert result.ansi == f"{ESC}[1;31mHi{ESC}[22;39m"
    assert result.raw == "Hi"


def test_default_separator_is_empty_string():
    result = StyledText("a", "b", "c")
    assert result.ansi == "abc"
    assert result.raw == "abc"


def test_custom_separator():
    result = StyledText("a", "b", sep=" | ")
    assert result.ansi == "a | b"


def test_nested_styled_keeps_outer_style_after_inner_reset():
    result = StyledText(S.CYAN("Outer ", S.DIM("Inner"), " Outer"))
    expected = f"{ESC}[36mOuter {ESC}[2mInner{ESC}[22m Outer{ESC}[39m"
    assert result.ansi == expected
    assert result.raw == "Outer Inner Outer"


def test_tuple_as_multi_segment_group():
    result = StyledText(("a", S.BOLD("b"), "c"))
    assert result.ansi == f"a{ESC}[1mb{ESC}[22mc"
    assert result.raw == "abc"


def test_multi_text_args_in_call():
    result = StyledText(S.BOLD("a", S.RED("b"), "c"))
    expected = f"{ESC}[1ma{ESC}[31mb{ESC}[39mc{ESC}[22m"
    assert result.ansi == expected
    assert result.raw == "abc"


def test_bright_fg_color():
    result = StyledText(S.BR.BLUE("x"))
    assert result.ansi == f"{ESC}[94mx{ESC}[39m"


def test_bg_color():
    result = StyledText(S.BG.RED("x"))
    assert result.ansi == f"{ESC}[41mx{ESC}[49m"


def test_bright_bg_color():
    result = StyledText(S.BG.BR.GREEN("x"))
    assert result.ansi == f"{ESC}[102mx{ESC}[49m"


def test_rgb_fg():
    result = StyledText(S.rgb(10, 20, 30)("x"))
    assert result.ansi == f"{ESC}[38;2;10;20;30mx{ESC}[39m"


def test_rgb_bg():
    result = StyledText(S.BG.rgb(10, 20, 30)("x"))
    assert result.ansi == f"{ESC}[48;2;10;20;30mx{ESC}[49m"


def test_hex_fg_short_and_long():
    short_form = StyledText(S.hex("#abc")("x")).ansi
    long_form = StyledText(S.hex("aabbcc")("x")).ansi
    assert short_form == long_form == f"{ESC}[38;2;170;187;204mx{ESC}[39m"


def test_hex_bg():
    result = StyledText(S.BG.hex("#102030")("x"))
    assert result.ansi == f"{ESC}[48;2;16;32;48mx{ESC}[49m"


def test_link_alone_wraps_text():
    result = StyledText(S.link("https://example.com")("click"))
    assert result.ansi == f"{ESC}]8;;https://example.com{ESC}\\click{ESC}]8;;{ESC}\\"
    assert result.raw == "click"


def test_link_combined_with_style():
    result = StyledText((S.link("https://x") | S.BOLD)("click"))
    expected = f"{ESC}]8;;https://x{ESC}\\{ESC}[1mclick{ESC}[22m{ESC}]8;;{ESC}\\"
    assert result.ansi == expected


def test_link_with_path():
    p = Path("docs/readme.md")
    result = StyledText(S.link(p)("click"))
    url = p.resolve().as_uri()
    assert result.ansi == f"{ESC}]8;;{url}{ESC}\\click{ESC}]8;;{ESC}\\"


def test_code_positions_match_offsets_in_ansi():
    result = StyledText(S.BOLD("hi"))
    # `{ESC}[1m` then `hi` then `{ESC}[22m`:
    assert result.code_positions == ((0, f"{ESC}[1m"), (len(f"{ESC}[1m") + 2, f"{ESC}[22m"))
    # Offsets must be valid slice points into the ANSI string:
    for position, sequence in result.code_positions:
        assert result.ansi[position : position + len(sequence)] == sequence


def test_raw_equals_ansi_minus_sequences():
    result = StyledText(S.CYAN("a"), (S.BOLD | S.RED)("b"), "plain")
    stripped = result.ansi
    for _, sequence in result.code_positions:
        stripped = stripped.replace(sequence, "", 1)
    assert stripped == result.raw


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
    result = StyledText(S.BOLD("Name: ")).input()
    assert result == "answer"
    assert captured["prompt"] == f"{ESC}[1mName: {ESC}[22m"


def test_or_chains_produce_FmtGroup():
    group = S.BOLD | S.RED | S.UNDERLINE
    assert isinstance(group, _StyleGroup)
    # `_Style` is an `int` subclass, so direct int comparison works:
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
