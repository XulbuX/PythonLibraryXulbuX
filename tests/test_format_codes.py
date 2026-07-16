from xulbux.format_codes import _FmtGroup, Term, FC, F, _build_open_close
from xulbux.base.consts import ANSI

from pathlib import Path
import pytest
import sys
import io


ESC = ANSI.CHAR

#
###################################################### BARE FC TESTS #####################################################


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
    result = FC((F.RED, "Hello", F.RESET))
    assert result.ansi == f"{ESC}[31mHello{ESC}[0m"
    assert result.raw == "Hello"


def test_bare_ColorFmt_emits_open_sequence():
    result = FC(F.hex("#ff6070"))
    assert result.ansi == f"{ESC}[38;2;255;96;112m"
    assert result.raw == ""


def test_bare_LinkFmt_emits_open_sequence():
    result = FC(F.link("https://example.com"))
    assert result.ansi == f"{ESC}]8;;https://example.com{ESC}\\"
    assert result.raw == ""


def test_bare_FmtGroup_emits_open_sequence():
    result = FC(F.BOLD | F.RED)
    assert result.ansi == f"{ESC}[1;31m"
    assert result.raw == ""


def test_bare_fmt_inside_nested_styled_call():
    result = FC(F.DIM("a", F.RED, "b", F.RESET_FG, "c"))
    expected = f"{ESC}[2ma{ESC}[31mb{ESC}[39mc{ESC}[22m"
    assert result.ansi == expected
    assert result.raw == "abc"


#
###################################################### FC CALL TESTS #####################################################


def test_plain_string_passes_through():
    result = FC("Hello, world!")
    assert result.ansi == "Hello, world!"
    assert result.raw == "Hello, world!"
    assert result.code_positions == ()


def test_single_style_wraps_text_with_open_and_reset():
    result = FC(F.BOLD("Hi"))
    assert result.ansi == f"{ESC}[1mHi{ESC}[22m"
    assert result.raw == "Hi"


def test_combined_group_emits_single_sgr():
    result = FC((F.BOLD | F.RED)("Hi"))
    assert result.ansi == f"{ESC}[1;31mHi{ESC}[22;39m"
    assert result.raw == "Hi"


def test_default_separator_is_newline():
    result = FC("a", "b", "c")
    assert result.ansi == "a\nb\nc"
    assert result.raw == "a\nb\nc"


def test_custom_separator():
    result = FC("a", "b", sep=" | ")
    assert result.ansi == "a | b"


def test_nested_styled_keeps_outer_style_after_inner_reset():
    result = FC(F.CYAN("Outer ", F.DIM("Inner"), " Outer"))
    expected = f"{ESC}[36mOuter {ESC}[2mInner{ESC}[22m Outer{ESC}[39m"
    assert result.ansi == expected
    assert result.raw == "Outer Inner Outer"


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


def test_link_with_path():
    p = Path("docs/readme.md")
    result = FC(F.link(p)("click"))
    url = p.resolve().as_uri()
    assert result.ansi == f"{ESC}]8;;{url}{ESC}\\click{ESC}]8;;{ESC}\\"


def test_code_positions_match_offsets_in_ansi():
    result = FC(F.BOLD("hi"))
    # `{ESC}[1m` then `hi` then `{ESC}[22m`:
    assert result.code_positions == ((0, f"{ESC}[1m"), (len(f"{ESC}[1m") + 2, f"{ESC}[22m"))
    # Offsets must be valid slice points into the ANSI string:
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


def test_or_chains_produce_FmtGroup():
    group = F.BOLD | F.RED | F.UNDERLINE
    assert isinstance(group, _FmtGroup)
    # `_Fmt` is an `int` subclass, so direct int comparison works:
    assert list(group) == [1, 31, 4]


def test_pipe_with_FmtGroup_left_and_right():
    left_assoc = (F.BOLD | F.RED) | F.UNDERLINE
    right_assoc = F.BOLD | (F.RED | F.UNDERLINE)
    assert list(left_assoc) == list(right_assoc) == [1, 31, 4]


def test_build_open_close_dedupes_close_codes():
    # Bold + dim both reset to 22 → only one 22 in close:
    opens, closes = _build_open_close(F.BOLD | F.DIM)
    assert opens == (f"{ESC}[1;2m", )
    assert closes == (f"{ESC}[22m", )


#
################################################### Term OPERATOR TESTS ##################################################


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


#
#################################################### FC OPERATOR TESTS ###################################################


def test_add_with_string():
    result = FC(F.BOLD("hi")) + " there"
    assert result.ansi == f"{ESC}[1mhi{ESC}[22m there"
    assert result.raw == "hi there"
    assert isinstance(result, FC)


def test_radd_with_string():
    result = "hello " + FC(F.RED("world"))
    assert result.ansi == f"hello {ESC}[31mworld{ESC}[39m"
    assert result.raw == "hello world"
    assert isinstance(result, FC)


def test_iadd_with_string():
    x = FC(F.CYAN("a"))
    x += " b"
    assert x.ansi == f"{ESC}[36ma{ESC}[39m b"
    assert x.raw == "a b"


def test_add_concatenates_ansi_strings():
    x = FC("Hello, ")
    y = FC("world!")
    result = x + y
    assert result.ansi == "Hello, world!"
    assert isinstance(result, FC)


def test_add_preserves_ansi_sequences():
    x = FC(F.BOLD("Hello"))
    y = FC(F.RED(" world"))
    result = x + y
    assert result.ansi == f"{ESC}[1mHello{ESC}[22m{ESC}[31m world{ESC}[39m"
    assert result.raw == "Hello world"


def test_add_does_not_mutate_operands():
    x = FC("a")
    y = FC("b")
    _ = x + y
    assert x.ansi == "a"
    assert y.ansi == "b"


def test_iadd_mutates_in_place():
    x = FC("Hello")
    original_id = id(x)
    x += FC(", world!")
    assert x.ansi == "Hello, world!"
    assert id(x) == original_id


def test_iadd_preserves_ansi_sequences():
    x = FC(F.CYAN("a"))
    x += FC(F.DIM("b"))
    assert x.ansi == f"{ESC}[36ma{ESC}[39m{ESC}[2mb{ESC}[22m"


def test_mul_repeats_output():
    x = FC("-")
    result = x * 3
    assert result.ansi == "---"
    assert isinstance(result, FC)


def test_mul_preserves_ansi_sequences():
    x = FC(F.BOLD("!"))
    result = x * 3
    unit = f"{ESC}[1m!{ESC}[22m"
    assert result.ansi == unit * 3


def test_mul_does_not_mutate_operand():
    x = FC("x")
    _ = x * 4
    assert x.ansi == "x"


def test_rmul_equals_mul():
    x = FC(F.RED("-"))
    assert (x * 5).ansi == (5 * x).ansi


def test_mul_by_zero_gives_empty():
    result = FC(F.BOLD("hi")) * 0
    assert result.ansi == ""
    assert result.raw == ""


def test_len_returns_visible_character_count():
    result = FC(F.BOLD("hello"))
    assert len(result) == 5


def test_len_ignores_ansi_sequences():
    styled = FC((F.BOLD | F.RED)("abc"))
    plain = FC("abc")
    assert len(styled) == len(plain) == 3


def test_len_of_empty():
    assert len(FC()) == 0


def test_join():
    sep = FC(F.BR.CYAN(" | "))
    result = sep.join(["a", F.BOLD("b"), "c"])
    expected = f"a{ESC}[96m | {ESC}[39m{ESC}[1mb{ESC}[22m{ESC}[96m | {ESC}[39mc"
    assert result.ansi == expected


def test_ljust():
    result = FC(F.RED("hi")).ljust(5)
    assert result.ansi == f"{ESC}[31mhi{ESC}[39m   "
    assert len(result) == 5


def test_rjust():
    result = FC(F.RED("hi")).rjust(5)
    assert result.ansi == f"   {ESC}[31mhi{ESC}[39m"
    assert len(result) == 5


def test_center():
    result = FC(F.RED("hi")).center(6)
    assert result.ansi == f"  {ESC}[31mhi{ESC}[39m  "
    assert len(result) == 6


def test_print_with_file():
    buf = io.StringIO()
    FC(F.RED("hi")).print(file=buf, end="")
    assert buf.getvalue() == f"{ESC}[31mhi{ESC}[39m"
