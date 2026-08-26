import io
from xulbux.ansi import (
    S,
    StyledText,
    _BgColorStyle,
    _BgStyle,
    _ColorStyle,
    _FgColorStyle,
    _FgStyle,
    _Style,
    is_bg_color_style,
    is_color_style,
    is_fg_color_style,
    is_renderable,
    is_text_renderable,
)
from xulbux.base.consts import ANSI

ESC = ANSI.CHAR


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
    st1 = StyledText(S.CYAN("a"))
    st1 += " b"
    assert st1.ansi == f"{ESC}[36ma{ESC}[39m b"
    assert st1.raw == "a b"


def test_add_concatenates_ansi_strings():
    st1 = StyledText("Hello, ")
    st2 = StyledText("world!")
    result = st1 + st2
    assert result.ansi == "Hello, world!"
    assert isinstance(result, StyledText)


def test_add_preserves_ansi_sequences():
    st1 = StyledText(S.BOLD("Hello"))
    st2 = StyledText(S.RED(" world"))
    result = st1 + st2
    assert result.ansi == f"{ESC}[1mHello{ESC}[22m{ESC}[31m world{ESC}[39m"
    assert result.raw == "Hello world"


def test_add_does_not_mutate_operands():
    st1 = StyledText("a")
    st2 = StyledText("b")
    _ = st1 + st2
    assert st1.ansi == "a"
    assert st2.ansi == "b"


def test_iadd_mutates_in_place():
    st1 = StyledText("Hello")
    original_id = id(st1)
    st1 += ", world!"
    assert st1.ansi == "Hello, world!"
    assert id(st1) == original_id


def test_iadd_preserves_ansi_sequences():
    st1 = StyledText(S.CYAN("a"))
    st1 += S.DIM("b")
    assert st1.ansi == f"{ESC}[36ma{ESC}[39m{ESC}[2mb{ESC}[22m"


def test_mul_repeats_output():
    st1 = StyledText("-")
    result = st1 * 3
    assert result.ansi == "---"
    assert isinstance(result, StyledText)


def test_mul_preserves_ansi_sequences():
    st1 = StyledText(S.BOLD("!"))
    result = st1 * 3
    unit = f"{ESC}[1m!{ESC}[22m"
    assert result.ansi == unit * 3


def test_mul_does_not_mutate_operand():
    st1 = StyledText("x")
    _ = st1 * 4
    assert st1.ansi == "x"


def test_rmul_equals_mul():
    st1 = StyledText(S.RED("-"))
    assert (st1 * 5).ansi == (5 * st1).ansi


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
    hex_fg_st = S.hex("#FF6070")
    assert isinstance(hex_fg_st, _FgColorStyle)
    assert isinstance(hex_fg_st, _ColorStyle)
    assert not isinstance(hex_fg_st, _BgColorStyle)
    assert is_fg_color_style(hex_fg_st) is True
    assert is_bg_color_style(hex_fg_st) is False
    assert is_color_style(hex_fg_st) is True

    rgb_fg_st = S.rgb(255, 96, 112)
    assert isinstance(rgb_fg_st, _FgColorStyle)
    assert is_fg_color_style(rgb_fg_st) is True
    assert is_bg_color_style(rgb_fg_st) is False
    assert is_color_style(rgb_fg_st) is True

    # 24-bit True-Color BG:
    hex_bg_st = S.BG.hex("#FF6070")
    assert isinstance(hex_bg_st, _BgColorStyle)
    assert isinstance(hex_bg_st, _ColorStyle)
    assert not isinstance(hex_bg_st, _FgColorStyle)
    assert is_fg_color_style(hex_bg_st) is False
    assert is_bg_color_style(hex_bg_st) is True
    assert is_color_style(hex_bg_st) is True

    rgb_bg_st = S.BG.rgb(0, 0, 0)
    assert isinstance(rgb_bg_st, _BgColorStyle)
    assert is_fg_color_style(rgb_bg_st) is False
    assert is_bg_color_style(rgb_bg_st) is True
    assert is_color_style(rgb_bg_st) is True

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
    seq_st = S.RED("hello world foo bar")
    wrapped = seq_st.wrap(11)
    assert [line.raw for line in wrapped] == ["hello world", "foo bar"]
    assert f"{ESC}[31mhello world{ESC}[39m" == wrapped[0].ansi
    assert f"{ESC}[31mfoo bar{ESC}[39m" == wrapped[1].ansi


def test_style_group_wrap_preserves_combined_styles():
    g_st = (S.BOLD | S.GREEN)("first long line second long line")
    wrapped = g_st.wrap(15)
    assert [line.raw for line in wrapped] == ["first long line", "second long", "line"]
    for line in wrapped:
        assert f"{ESC}[1;32m" in line.ansi
        assert f"{ESC}[22;39m" in line.ansi


def test_wrap_nested_styles():
    st = StyledText("Start ", S.DIM("(dimmed notes here)"), " end")
    wrapped = st.wrap(12)
    assert [line.raw for line in wrapped] == ["Start", "(dimmed", "notes here)", "end"]
    # Check that dim style is present in the lines containing dimmed text:
    dim_seq_st = StyledText(S.DIM).ansi
    assert dim_seq_st in wrapped[1].ansi
    assert dim_seq_st in wrapped[2].ansi


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


def test_wrap_splits_newlines_when_shorter_than_width():
    st = StyledText("hello\nworld")
    wrapped = st.wrap(80)
    assert [line.raw for line in wrapped] == ["hello", "world"]
    assert wrapped[0].ansi == "hello"
    assert wrapped[1].ansi == "world"
