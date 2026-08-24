import io
import sys
from pathlib import Path
from xulbux.ansi import (
    S,
    StyledText,
    Term,
    _BgColorStyle,
    _BgStyle,
    _build_open_close,
    _ColorStyle,
    _FgColorStyle,
    _FgStyle,
    _Style,
    _StyleGroup,
    is_bg_color_style,
    is_color_style,
    is_fg_color_style,
    is_renderable,
    is_text_renderable,
)
from xulbux.base.consts import ANSI
import pytest

ESC = ANSI.CHAR


# *************************************************** BARE StyledText TESTS ***************************************************


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


# *************************************************** StyledText CALL TESTS ***************************************************


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


# **************************************************** Term OPERATOR TESTS ****************************************************


def test_term_constants():
    assert f"{ESC}[2K" == Term.CLEAR_LINE
    assert f"{ESC}[2J" == Term.CLEAR_SCREEN
    assert f"{ESC}[?25l" == Term.HIDE_CURSOR
    assert f"{ESC}[?25h" == Term.SHOW_CURSOR
    assert f"{ESC}[?1049h" == Term.ALT_SCREEN
    assert f"{ESC}[?1049l" == Term.MAIN_SCREEN


def test_term_cursor_movement():
    assert Term.up(3) == f"{ESC}[3A"
    assert Term.down() == f"{ESC}[1B"
    assert Term.left(2) == f"{ESC}[2D"
    assert Term.right(5) == f"{ESC}[5C"
    assert Term.prev_line(2) == f"{ESC}[2F"
    assert Term.next_line() == f"{ESC}[1E"
    assert Term.move(4, 7) == f"{ESC}[4;7H"


def test_term_save_restore_and_title():
    assert Term.save() == f"{ESC}[s"
    assert Term.restore() == f"{ESC}[u"
    assert Term.title("hi") == f"{ESC}]2;hi\x07"


# ************************************************* StyledText OPERATOR TESTS *************************************************


def test_add_with_string():
    result = StyledText(S.BOLD("hi")) + " there"
    assert result.ansi == f"{ESC}[1mhi{ESC}[22m there"
    assert result.raw == "hi there"
    assert isinstance(result, StyledText)


def test_radd_with_string():
    result = "hello " + StyledText(S.RED("world"))
    assert result.ansi == f"hello {ESC}[31mworld{ESC}[39m"
    assert result.raw == "hello world"
    assert isinstance(result, StyledText)


def test_iadd_with_string():
    x = StyledText(S.CYAN("a"))
    x += " b"
    assert x.ansi == f"{ESC}[36ma{ESC}[39m b"
    assert x.raw == "a b"


def test_add_concatenates_ansi_strings():
    x = StyledText("Hello, ")
    y = StyledText("world!")
    result = x + y
    assert result.ansi == "Hello, world!"
    assert isinstance(result, StyledText)


def test_add_preserves_ansi_sequences():
    x = StyledText(S.BOLD("Hello"))
    y = StyledText(S.RED(" world"))
    result = x + y
    assert result.ansi == f"{ESC}[1mHello{ESC}[22m{ESC}[31m world{ESC}[39m"
    assert result.raw == "Hello world"


def test_add_does_not_mutate_operands():
    x = StyledText("a")
    y = StyledText("b")
    _ = x + y
    assert x.ansi == "a"
    assert y.ansi == "b"


def test_iadd_mutates_in_place():
    x = StyledText("Hello")
    original_id = id(x)
    x += ", world!"
    assert x.ansi == "Hello, world!"
    assert id(x) == original_id


def test_iadd_preserves_ansi_sequences():
    x = StyledText(S.CYAN("a"))
    x += S.DIM("b")
    assert x.ansi == f"{ESC}[36ma{ESC}[39m{ESC}[2mb{ESC}[22m"


def test_mul_repeats_output():
    x = StyledText("-")
    result = x * 3
    assert result.ansi == "---"
    assert isinstance(result, StyledText)


def test_mul_preserves_ansi_sequences():
    x = StyledText(S.BOLD("!"))
    result = x * 3
    unit = f"{ESC}[1m!{ESC}[22m"
    assert result.ansi == unit * 3


def test_mul_does_not_mutate_operand():
    x = StyledText("x")
    _ = x * 4
    assert x.ansi == "x"


def test_rmul_equals_mul():
    x = StyledText(S.RED("-"))
    assert (x * 5).ansi == (5 * x).ansi


def test_mul_by_zero_gives_empty():
    result = StyledText(S.BOLD("hi")) * 0
    assert result.ansi == ""
    assert result.raw == ""


def test_len_returns_visible_character_count():
    result = StyledText(S.BOLD("hello"))
    assert len(result) == 5


def test_len_ignores_ansi_sequences():
    styled = StyledText((S.BOLD | S.RED)("abc"))
    plain = StyledText("abc")
    assert len(styled) == len(plain) == 3


def test_len_of_empty():
    assert len(StyledText()) == 0


def test_join():
    sep = StyledText(S.BR.CYAN(" | "))
    result = sep.join(["a", S.BOLD("b"), "c"])
    expected = f"a{ESC}[96m | {ESC}[39m{ESC}[1mb{ESC}[22m{ESC}[96m | {ESC}[39mc"
    assert result.ansi == expected


def test_ljust():
    result = StyledText(S.RED("hi")).ljust(5)
    assert result.ansi == f"{ESC}[31mhi{ESC}[39m   "
    assert len(result) == 5


def test_rjust():
    result = StyledText(S.RED("hi")).rjust(5)
    assert result.ansi == f"   {ESC}[31mhi{ESC}[39m"
    assert len(result) == 5


def test_center():
    result = StyledText(S.RED("hi")).center(6)
    assert result.ansi == f"  {ESC}[31mhi{ESC}[39m  "
    assert len(result) == 6


def test_print_with_file():
    buf = io.StringIO()
    StyledText(S.RED("hi")).print(file=buf, end="")
    assert buf.getvalue() == f"{ESC}[31mhi{ESC}[39m"


def test_type_guards_and_nested_renderables():
    # Plain text and styled sequences:
    assert is_text_renderable("hello") is True
    assert is_text_renderable(S.RED("hello")) is True
    assert is_text_renderable(StyledText("hello")) is True
    assert is_text_renderable(S.RED) is False  # Bare style is not a `TextRenderable`.
    assert is_renderable(S.RED) is True  # Bare style is a `Renderable`.

    # Nested tuples:
    nested_text = ("a", (S.RED("b"), ("c", StyledText("d"))))
    assert is_text_renderable(nested_text) is True
    assert is_renderable(nested_text) is True

    # Bare style in nested tuple:
    nested_with_bare_style = ("a", (S.RED, "b"))
    assert is_text_renderable(nested_with_bare_style) is False
    assert is_renderable(nested_with_bare_style) is True

    # Rendering nested tuples with `StyledText`:
    rendered = StyledText(nested_text)
    assert rendered.raw == "abcd"
    assert rendered.ansi == f"a{ESC}[31mb{ESC}[39mcd"


def test_color_style_type_guards_and_subclasses():
    # FG standard and bright:
    assert isinstance(S.RED, _FgStyle)
    assert isinstance(S.RED, _Style)
    assert not isinstance(S.RED, _BgStyle)
    assert is_fg_color_style(S.RED) is True
    assert is_bg_color_style(S.RED) is False
    assert is_color_style(S.RED) is True

    assert isinstance(S.BR.BLUE, _FgStyle)
    assert is_fg_color_style(S.BR.BLUE) is True
    assert is_bg_color_style(S.BR.BLUE) is False
    assert is_color_style(S.BR.BLUE) is True

    # BG standard and bright:
    assert isinstance(S.BG.RED, _BgStyle)
    assert isinstance(S.BG.RED, _Style)
    assert not isinstance(S.BG.RED, _FgStyle)
    assert is_fg_color_style(S.BG.RED) is False
    assert is_bg_color_style(S.BG.RED) is True
    assert is_color_style(S.BG.RED) is True

    assert isinstance(S.BG.BR.BLUE, _BgStyle)
    assert is_fg_color_style(S.BG.BR.BLUE) is False
    assert is_bg_color_style(S.BG.BR.BLUE) is True
    assert is_color_style(S.BG.BR.BLUE) is True

    # 24-bit True-Color FG:
    fg_hex = S.hex("#FF6070")
    assert isinstance(fg_hex, _FgColorStyle)
    assert isinstance(fg_hex, _ColorStyle)
    assert not isinstance(fg_hex, _BgColorStyle)
    assert is_fg_color_style(fg_hex) is True
    assert is_bg_color_style(fg_hex) is False
    assert is_color_style(fg_hex) is True

    fg_rgb = S.rgb(255, 96, 112)
    assert isinstance(fg_rgb, _FgColorStyle)
    assert is_fg_color_style(fg_rgb) is True
    assert is_bg_color_style(fg_rgb) is False
    assert is_color_style(fg_rgb) is True

    # 24-bit True-Color BG:
    bg_hex = S.BG.hex("#FF6070")
    assert isinstance(bg_hex, _BgColorStyle)
    assert isinstance(bg_hex, _ColorStyle)
    assert not isinstance(bg_hex, _FgColorStyle)
    assert is_fg_color_style(bg_hex) is False
    assert is_bg_color_style(bg_hex) is True
    assert is_color_style(bg_hex) is True

    bg_rgb = S.BG.rgb(0, 0, 0)
    assert isinstance(bg_rgb, _BgColorStyle)
    assert is_fg_color_style(bg_rgb) is False
    assert is_bg_color_style(bg_rgb) is True
    assert is_color_style(bg_rgb) is True

    # Non-color styles:
    assert is_fg_color_style(S.BOLD) is False
    assert is_bg_color_style(S.BOLD) is False
    assert is_color_style(S.BOLD) is False

    assert is_fg_color_style(S.DIM) is False
    assert is_bg_color_style(S.DIM) is False
    assert is_color_style(S.DIM) is False

    assert is_fg_color_style(S.RESET) is False
    assert is_bg_color_style(S.RESET) is False
    assert is_color_style(S.RESET) is False

    # Non-style objects:
    assert is_fg_color_style("red") is False
    assert is_bg_color_style("red") is False
    assert is_color_style("red") is False
    assert is_fg_color_style(123) is False
    assert is_bg_color_style(123) is False
    assert is_color_style(123) is False


def test_styled_text_wrap_basic():
    st = StyledText("hello world foo bar")
    wrapped = st.wrap(11)
    assert [line.raw for line in wrapped] == ["hello world", "foo bar"]
    assert isinstance(wrapped[0], StyledText)
    assert isinstance(wrapped[1], StyledText)


def test_styled_sequence_wrap_preserves_styles():
    seq = S.RED("hello world foo bar")
    wrapped = seq.wrap(11)
    assert [line.raw for line in wrapped] == ["hello world", "foo bar"]
    assert f"{ESC}[31mhello world{ESC}[39m" == wrapped[0].ansi
    assert f"{ESC}[31mfoo bar{ESC}[39m" == wrapped[1].ansi


def test_style_group_wrap_preserves_combined_styles():
    grp = (S.BOLD | S.GREEN)("first long line second long line")
    wrapped = grp.wrap(15)
    assert [line.raw for line in wrapped] == ["first long line", "second long", "line"]
    for line in wrapped:
        assert f"{ESC}[1;32m" in line.ansi
        assert f"{ESC}[22;39m" in line.ansi


def test_wrap_nested_styles():
    st = StyledText("Start ", S.DIM("(dimmed notes here)"), " end")
    wrapped = st.wrap(12)
    assert [line.raw for line in wrapped] == ["Start", "(dimmed", "notes here)", "end"]
    # Check that dim style is present in the lines containing dimmed text:
    dim_seq = StyledText(S.DIM).ansi
    assert dim_seq in wrapped[1].ansi
    assert dim_seq in wrapped[2].ansi


def test_wrap_with_paragraphs_and_empty_lines():
    st = StyledText("Paragraph 1 word wrap\n\nParagraph 2 word wrap")
    wrapped = st.wrap(15)
    assert [line.raw for line in wrapped] == ["Paragraph 1", "word wrap", "", "Paragraph 2", "word wrap"]


def test_wrap_no_op_when_shorter_or_invalid_width():
    st = StyledText(S.CYAN("Short text"))
    assert len(st.wrap(20)) == 1
    assert st.wrap(20)[0].ansi == st.ansi

    assert len(st.wrap(0)) == 1
    assert st.wrap(0)[0].ansi == st.ansi

    assert len(st.wrap(-5)) == 1
    assert st.wrap(-5)[0].ansi == st.ansi
