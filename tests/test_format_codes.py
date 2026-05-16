from xulbux.format_codes import FormatCodes, FC, Format, F, Term, _FmtGroup, _build_open_close
from xulbux.base.consts import ANSI

import pytest
import sys
import io


ESC = ANSI.CHAR

#
################################################## FormatCodes TESTS ##################################################


def test_bare_fmt_emits_only_open_sequence():
    result = FC(F.RED)
    assert result.ansi == f"{ESC}[31m"
    assert result.raw == ""


def test_bare_reset_fmt():
    result = FC(F.RESET)
    assert result.ansi == f"{ESC}[0m"
    assert result.raw == ""


def test_bare_fmt_sequence_with_explicit_reset():
    result = FC(F.RED, "hello", F.RESET)
    assert result.ansi == f"{ESC}[31m\nhello\n{ESC}[0m"
    assert result.raw == "\nhello\n"


def test_bare_fmt_inside_tuple():
    result = FC((F.RED, "hello", F.RESET))
    assert result.ansi == f"{ESC}[31mhello{ESC}[0m"
    assert result.raw == "hello"


def test_bare_colorfmt_emits_open_sequence():
    result = FC(F.hex("#ff6070"))
    assert result.ansi == f"{ESC}[38;2;255;96;112m"
    assert result.raw == ""


def test_bare_linkfmt_emits_open_sequence():
    result = FC(F.link("https://example.com"))
    assert result.ansi == f"{ESC}]8;;https://example.com{ESC}\\"
    assert result.raw == ""


def test_bare_fmtgroup_emits_open_sequence():
    result = FC(F.BOLD | F.RED)
    assert result.ansi == f"{ESC}[1;31m"
    assert result.raw == ""


def test_bare_fmt_inside_nested_styled_call():
    result = FC(F.DIM("a", F.RED, "b", F.RESET_FG, "c"))
    expected = f"{ESC}[2ma{ESC}[31mb{ESC}[39mc{ESC}[22m"
    assert result.ansi == expected
    assert result.raw == "abc"


def test_plain_string_passes_through():
    result = FC("hello world")
    assert result.ansi == "hello world"
    assert result.raw == "hello world"
    assert result.code_positions == ()


def test_single_style_wraps_text_with_open_and_reset():
    result = FC(F.BOLD("hi"))
    assert result.ansi == f"{ESC}[1mhi{ESC}[22m"
    assert result.raw == "hi"


def test_combined_group_emits_single_sgr():
    result = FC((F.BOLD | F.RED)("hi"))
    assert result.ansi == f"{ESC}[1;31mhi{ESC}[22;39m"
    assert result.raw == "hi"


def test_default_separator_is_newline():
    result = FC("a", "b", "c")
    assert result.ansi == "a\nb\nc"
    assert result.raw == "a\nb\nc"


def test_custom_separator():
    result = FC("a", "b", sep=" | ")
    assert result.ansi == "a | b"


def test_nested_styled_keeps_outer_style_after_inner_reset():
    result = FC(F.CYAN("outer ", F.DIM("inner"), " outer"))
    expected = f"{ESC}[36mouter {ESC}[2minner{ESC}[22m outer{ESC}[39m"
    assert result.ansi == expected
    assert result.raw == "outer inner outer"


def test_tuple_as_multi_segment_group():
    result = FC(("a", F.BOLD("b"), "c"))
    assert result.ansi == f"a{ESC}[1mb{ESC}[22mc"
    assert result.raw == "abc"


def test_multi_text_args_in_call():
    result = FC(F.BOLD("a", F.RED("b"), "c"))
    expected = f"{ESC}[1ma{ESC}[31mb{ESC}[39mc{ESC}[22m"
    assert result.ansi == expected
    assert result.raw == "abc"


def test_bright_fg_color():
    result = FC(F.BR.BLUE("x"))
    assert result.ansi == f"{ESC}[94mx{ESC}[39m"


def test_bg_color():
    result = FC(F.BG.RED("x"))
    assert result.ansi == f"{ESC}[41mx{ESC}[49m"


def test_bright_bg_color():
    result = FC(F.BG.BR.GREEN("x"))
    assert result.ansi == f"{ESC}[102mx{ESC}[49m"


def test_rgb_fg():
    result = FC(F.rgb(10, 20, 30)("x"))
    assert result.ansi == f"{ESC}[38;2;10;20;30mx{ESC}[39m"


def test_rgb_bg():
    result = FC(F.BG.rgb(10, 20, 30)("x"))
    assert result.ansi == f"{ESC}[48;2;10;20;30mx{ESC}[49m"


def test_hex_fg_short_and_long():
    short_form = FC(F.hex("#abc")("x")).ansi
    long_form = FC(F.hex("aabbcc")("x")).ansi
    assert short_form == long_form == f"{ESC}[38;2;170;187;204mx{ESC}[39m"


def test_hex_bg():
    result = FC(F.BG.hex("#102030")("x"))
    assert result.ansi == f"{ESC}[48;2;16;32;48mx{ESC}[49m"


def test_link_alone_wraps_text():
    result = FC(F.link("https://example.com")("click"))
    assert result.ansi == f"{ESC}]8;;https://example.com{ESC}\\click{ESC}]8;;{ESC}\\"
    assert result.raw == "click"


def test_link_combined_with_style():
    result = FC((F.link("https://x") | F.BOLD)("click"))
    expected = (f"{ESC}]8;;https://x{ESC}\\"
                f"{ESC}[1m"
                f"click"
                f"{ESC}[22m"
                f"{ESC}]8;;{ESC}\\")
    assert result.ansi == expected


def test_code_positions_match_offsets_in_ansi():
    result = FC(F.BOLD("hi"))
    # ESC[1m  THEN  "hi"  THEN  ESC[22m
    assert result.code_positions == ((0, f"{ESC}[1m"), (len(f"{ESC}[1m") + 2, f"{ESC}[22m"))
    # OFFSETS MUST BE VALID SLICE POINTS INTO THE ANSI STRING
    for position, sequence in result.code_positions:
        assert result.ansi[position:position + len(sequence)] == sequence


def test_raw_equals_ansi_minus_sequences():
    result = FC(F.CYAN("a"), (F.BOLD | F.RED)("b"), "plain")
    stripped = result.ansi
    for _, sequence in result.code_positions:
        stripped = stripped.replace(sequence, "", 1)
    assert stripped == result.raw


def test_remove_ansi_strips_csi_and_osc():
    mixed = f"{ESC}[1mhi{ESC}[0m and {ESC}]8;;u{ESC}\\link{ESC}]8;;{ESC}\\"
    assert FC.remove_ansi(mixed) == "hi and link"


def test_print_writes_ansi_plus_end_to_stdout(monkeypatch: pytest.MonkeyPatch):
    buffer = io.StringIO()
    monkeypatch.setattr(sys, "stdout", buffer)
    FC(F.BOLD("hi")).print(end="!")
    assert buffer.getvalue() == f"{ESC}[1mhi{ESC}[22m!"


def test_input_uses_ansi_as_prompt(monkeypatch: pytest.MonkeyPatch):
    captured: dict[str, str] = {}

    def fake_input(prompt: str = "") -> str:
        captured["prompt"] = prompt
        return "answer"

    monkeypatch.setattr("builtins.input", fake_input)
    result = FC(F.BOLD("Name: ")).input()
    assert result == "answer"
    assert captured["prompt"] == f"{ESC}[1mName: {ESC}[22m"


def test_or_chains_produce_fmtgroup():
    group = F.BOLD | F.RED | F.UNDERLINE
    assert isinstance(group, _FmtGroup)
    # `_Fmt` IS AN `int` SUBCLASS, SO DIRECT INT COMPARISON WORKS
    assert list(group) == [1, 31, 4]


def test_pipe_with_fmtgroup_left_and_right():
    left_assoc = (F.BOLD | F.RED) | F.UNDERLINE
    right_assoc = F.BOLD | (F.RED | F.UNDERLINE)
    assert list(left_assoc) == list(right_assoc) == [1, 31, 4]


def test_build_open_close_dedupes_close_codes():
    # BOLD + DIM BOTH RESET TO 22 -> ONLY ONE 22 IN CLOSE
    opens, closes = _build_open_close(F.BOLD | F.DIM)
    assert opens == (f"{ESC}[1;2m", )
    assert closes == (f"{ESC}[22m", )


def test_term_constants():
    assert Term.CLEAR_LINE == f"{ESC}[2K"
    assert Term.CLEAR_SCREEN == f"{ESC}[2J"
    assert Term.HIDE_CURSOR == f"{ESC}[?25l"
    assert Term.SHOW_CURSOR == f"{ESC}[?25h"
    assert Term.ALT_SCREEN == f"{ESC}[?1049h"
    assert Term.MAIN_SCREEN == f"{ESC}[?1049l"


def test_term_cursor_movement():
    assert Term.up(3) == f"{ESC}[3A"
    assert Term.down() == f"{ESC}[1B"
    assert Term.right(5) == f"{ESC}[5C"
    assert Term.left(2) == f"{ESC}[2D"
    assert Term.move(4, 7) == f"{ESC}[4;7H"


def test_term_save_restore_and_title():
    assert Term.save() == f"{ESC}[s"
    assert Term.restore() == f"{ESC}[u"
    assert Term.title("hi") == f"{ESC}]2;hi\x07"


def test_FormatCodes_and_FC_are_same_object():
    assert FC is FormatCodes


def test_Format_and_F_are_same_object():
    assert F is Format
