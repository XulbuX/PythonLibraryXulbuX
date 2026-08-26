import io
from pathlib import Path
from unittest.mock import patch
from xulbux.ansi import (
    S,
    StyledText,
    _ColorStyle,
    _Link,
    _Style,
    _StyleGroup,
    is_any_style,
    is_base_style,
    is_bg_color_style,
    is_color_style,
    is_fg_color_style,
    is_render_segment,
    is_renderable,
    is_text_renderable,
    is_text_segment,
)
from xulbux.color import hexa, rgba


def test_standard_text_styles() -> None:
    assert StyledText(S.BOLD("bold text")).raw == "bold text"
    assert StyledText(S.BOLD("bold text")).ansi == "\x1b[1mbold text\x1b[22m"
    assert StyledText(S.DIM("dim text")).ansi == "\x1b[2mdim text\x1b[22m"
    assert StyledText(S.ITALIC("italic text")).ansi == "\x1b[3mitalic text\x1b[23m"
    assert StyledText(S.UNDERLINE("underline text")).ansi == "\x1b[4munderline text\x1b[24m"
    assert StyledText(S.DOUBLE_UNDERLINE("double")).ansi == "\x1b[21mdouble\x1b[24m"
    assert StyledText(S.INVERSE("inverse text")).ansi == "\x1b[7minverse text\x1b[27m"
    assert StyledText(S.HIDDEN("hidden text")).ansi == "\x1b[8mhidden text\x1b[28m"
    assert StyledText(S.STRIKETHROUGH("strike text")).ansi == "\x1b[9mstrike text\x1b[29m"


def test_foreground_colors() -> None:
    assert StyledText(S.BLACK("black")).ansi == "\x1b[30mblack\x1b[39m"
    assert StyledText(S.RED("red")).ansi == "\x1b[31mred\x1b[39m"
    assert StyledText(S.GREEN("green")).ansi == "\x1b[32mgreen\x1b[39m"
    assert StyledText(S.YELLOW("yellow")).ansi == "\x1b[33myellow\x1b[39m"
    assert StyledText(S.BLUE("blue")).ansi == "\x1b[34mblue\x1b[39m"
    assert StyledText(S.MAGENTA("magenta")).ansi == "\x1b[35mmagenta\x1b[39m"
    assert StyledText(S.CYAN("cyan")).ansi == "\x1b[36mcyan\x1b[39m"
    assert StyledText(S.WHITE("white")).ansi == "\x1b[37mwhite\x1b[39m"

    # Bright foreground:
    assert StyledText(S.BR.BLACK("bright black")).ansi == "\x1b[90mbright black\x1b[39m"
    assert StyledText(S.BR.RED("bright red")).ansi == "\x1b[91mbright red\x1b[39m"
    assert StyledText(S.BR.GREEN("bright green")).ansi == "\x1b[92mbright green\x1b[39m"
    assert StyledText(S.BR.YELLOW("bright yellow")).ansi == "\x1b[93mbright yellow\x1b[39m"
    assert StyledText(S.BR.BLUE("bright blue")).ansi == "\x1b[94mbright blue\x1b[39m"
    assert StyledText(S.BR.MAGENTA("bright magenta")).ansi == "\x1b[95mbright magenta\x1b[39m"
    assert StyledText(S.BR.CYAN("bright cyan")).ansi == "\x1b[96mbright cyan\x1b[39m"
    assert StyledText(S.BR.WHITE("bright white")).ansi == "\x1b[97mbright white\x1b[39m"


def test_background_colors() -> None:
    assert StyledText(S.BG.BLACK("bg black")).ansi == "\x1b[40mbg black\x1b[49m"
    assert StyledText(S.BG.RED("bg red")).ansi == "\x1b[41mbg red\x1b[49m"
    assert StyledText(S.BG.GREEN("bg green")).ansi == "\x1b[42mbg green\x1b[49m"
    assert StyledText(S.BG.YELLOW("bg yellow")).ansi == "\x1b[43mbg yellow\x1b[49m"
    assert StyledText(S.BG.BLUE("bg blue")).ansi == "\x1b[44mbg blue\x1b[49m"
    assert StyledText(S.BG.MAGENTA("bg magenta")).ansi == "\x1b[45mbg magenta\x1b[49m"
    assert StyledText(S.BG.CYAN("bg cyan")).ansi == "\x1b[46mbg cyan\x1b[49m"
    assert StyledText(S.BG.WHITE("bg white")).ansi == "\x1b[47mbg white\x1b[49m"

    # Bright background:
    assert StyledText(S.BG.BR.BLACK("bg bright black")).ansi == "\x1b[100mbg bright black\x1b[49m"
    assert StyledText(S.BG.BR.RED("bg bright red")).ansi == "\x1b[101mbg bright red\x1b[49m"
    assert StyledText(S.BG.BR.GREEN("bg bright green")).ansi == "\x1b[102mbg bright green\x1b[49m"
    assert StyledText(S.BG.BR.YELLOW("bg bright yellow")).ansi == "\x1b[103mbg bright yellow\x1b[49m"
    assert StyledText(S.BG.BR.BLUE("bg bright blue")).ansi == "\x1b[104mbg bright blue\x1b[49m"
    assert StyledText(S.BG.BR.MAGENTA("bg bright magenta")).ansi == "\x1b[105mbg bright magenta\x1b[49m"
    assert StyledText(S.BG.BR.CYAN("bg bright cyan")).ansi == "\x1b[106mbg bright cyan\x1b[49m"
    assert StyledText(S.BG.BR.WHITE("bg bright white")).ansi == "\x1b[107mbg bright white\x1b[49m"


def test_custom_color_builders() -> None:
    assert StyledText(S.rgb(255, 0, 128)("custom rgb")).ansi == "\x1b[38;2;255;0;128mcustom rgb\x1b[39m"
    assert StyledText(S.hex("#FF0080")("custom hex")).ansi == "\x1b[38;2;255;0;128mcustom hex\x1b[39m"
    assert StyledText(S.hex("0xFF0080")("0x hex")).ansi == "\x1b[38;2;255;0;128m0x hex\x1b[39m"
    assert StyledText(S.hex("F08")("short hex")).ansi == "\x1b[38;2;255;0;136mshort hex\x1b[39m"
    assert StyledText(S.rgb(rgba(255, 0, 128))("from rgba")).ansi == "\x1b[38;2;255;0;128mfrom rgba\x1b[39m"
    assert StyledText(S.hex(hexa("#FF0080"))("from hexa")).ansi == "\x1b[38;2;255;0;128mfrom hexa\x1b[39m"

    # ColorStyle.from_hex with explicit bg:
    assert _ColorStyle.from_hex("#FF0000", bg=True)._bg is True
    assert _ColorStyle.from_hex("#FF0000", bg=False)._bg is False

    # Background custom colors:
    assert StyledText(S.BG.rgb(0, 128, 255)("bg rgb")).ansi == "\x1b[48;2;0;128;255mbg rgb\x1b[49m"
    assert StyledText(S.BG.hex("#0080FF")("bg hex")).ansi == "\x1b[48;2;0;128;255mbg hex\x1b[49m"
    assert StyledText(S.BG.hex("08F")("bg short hex")).ansi == "\x1b[48;2;0;136;255mbg short hex\x1b[49m"
    assert StyledText(S.BG.rgb(rgba(0, 128, 255))("bg from rgba")).ansi == "\x1b[48;2;0;128;255mbg from rgba\x1b[49m"
    assert StyledText(S.BG.hex(hexa("#0080FF"))("bg from hexa")).ansi == "\x1b[48;2;0;128;255mbg from hexa\x1b[49m"


def test_hyperlink_builder() -> None:
    link_styled = StyledText(S.link("https://github.com")("GitHub Link"))
    assert link_styled.raw == "GitHub Link"
    assert "\x1b]8;;https://github.com\x1b\\GitHub Link\x1b]8;;\x1b\\" in link_styled.ansi

    path_link = S.link(Path("tests/test_ansi"))
    assert repr(path_link) != ""
    assert path_link == S.link(Path("tests/test_ansi"))
    assert (path_link == "not_a_link") is False
    assert StyledText(path_link("text")).raw == "text"
    assert StyledText(path_link @ "text").raw == "text"
    assert _Link.__ror__(path_link, S.BOLD) == (S.BOLD | path_link)


def test_style_group_composition_and_conversions() -> None:
    bold_red = S.BOLD | S.RED
    assert StyledText(bold_red("alert")).ansi == "\x1b[1;31malert\x1b[22;39m"

    # Combining groups with groups and styles:
    group1 = S.BOLD | S.RED
    group2 = S.ITALIC | S.BLUE
    combined_group = group1 | group2
    assert len(list(combined_group)) == 4

    right_styled_group = S.UNDERLINE | group1
    assert len(list(right_styled_group)) == 3

    left_styled_group = group1 | S.UNDERLINE
    assert len(list(left_styled_group)) == 3

    # Explicit __ror__ calls:
    assert _StyleGroup.__ror__(group1, S.UNDERLINE) == (S.UNDERLINE | group1)
    assert _Style.__ror__(S.BOLD, S.RED) == (S.RED | S.BOLD)
    assert _ColorStyle.__ror__(S.hex("#FF0000"), S.BOLD) == (S.BOLD | S.hex("#FF0000"))

    # Combining with color styles and links:
    color_group = S.hex("#FF0000") | (S.BOLD | S.BLUE)
    assert len(list(color_group)) == 3

    color_single_or = S.hex("#FF0000") | S.BOLD
    assert len(list(color_single_or)) == 2

    link_group_combined = S.link("https://example.com") | (S.BOLD | S.BLUE)
    assert len(list(link_group_combined)) == 3

    complex_group = S.BOLD | S.UNDERLINE | S.BR.BLUE | S.BG.WHITE
    result = StyledText(complex_group("complex text"))
    assert result.raw == "complex text"
    assert "\x1b[1;4;94;47mcomplex text\x1b[22;24;39;49m" in result.ansi

    # Group to_bg and to_fg conversions:
    fg_group = S.RED | S.BOLD | S.hex("#FF0000")
    bg_group = fg_group.to_bg()
    assert any(code == S.BG.RED for code in bg_group)
    assert any(code == S.RED for code in bg_group.to_fg())

    # Individual style conversions:
    assert S.RED.to_bg() == S.BG.RED
    assert S.BG.RED.to_fg() == S.RED
    assert S.hex("#FF0000").to_bg() == S.BG.hex("#FF0000")
    assert S.BG.hex("#FF0000").to_fg() == S.hex("#FF0000")


def test_reset_tokens() -> None:
    assert StyledText(S.RESET).ansi == "\x1b[0m"
    assert StyledText(S.RESET_BOLD).ansi == "\x1b[22m"
    assert StyledText(S.RESET_DIM).ansi == "\x1b[22m"
    assert StyledText(S.RESET_ITALIC).ansi == "\x1b[23m"
    assert StyledText(S.RESET_UNDERLINE).ansi == "\x1b[24m"
    assert StyledText(S.RESET_INVERSE).ansi == "\x1b[27m"
    assert StyledText(S.RESET_HIDDEN).ansi == "\x1b[28m"
    assert StyledText(S.RESET_STRIKETHROUGH).ansi == "\x1b[29m"
    assert StyledText(S.RESET_FG).ansi == "\x1b[39m"
    assert StyledText(S.RESET_BG).ansi == "\x1b[49m"


def test_bare_styles_in_styled_text() -> None:
    output = StyledText(S.RED, "Error Text", S.RESET_FG, " Normal Text")
    assert output.raw == "Error Text Normal Text"
    assert output.ansi == "\x1b[31mError Text\x1b[39m Normal Text"


def test_style_equality_and_representations() -> None:
    assert S.BOLD == S.BOLD
    assert S.BOLD != S.DIM
    assert S.BOLD == 1
    assert (S.BOLD == "not_an_int") is False
    assert hash(S.BOLD) == hash(1)
    assert int(S.BOLD) == 1
    assert str(S.BOLD) == "1"

    assert (S.BOLD | S.RED) == (S.BOLD | S.RED)
    assert (S.BOLD | S.RED) != (S.BOLD | S.BLUE)
    assert (S.BOLD | S.RED) != "not_a_style"
    assert repr(S.BOLD) != ""
    assert repr(S.BOLD | S.RED) != ""
    assert repr(S.hex("#FF0000")) != ""
    assert repr(S.link("https://example.com")) != ""


def test_individual_style_string_helpers() -> None:
    assert S.RED.ljust(5, "-").raw == "-----"
    assert S.RED.rjust(5, "-").raw == "-----"
    assert S.RED.center(5, "-").raw == "-----"
    assert S.RED.wrap(10)[0].raw == ""
    assert S.RED.join(["A", "B"]).raw == "AB"

    color_style = S.hex("#FF0000")
    assert color_style.ljust(5, "-").raw == "-----"
    assert color_style.rjust(5, "-").raw == "-----"
    assert color_style.center(5, "-").raw == "-----"
    assert color_style.wrap(10)[0].raw == ""
    assert color_style.join(["A", "B"]).raw == "AB"
    assert color_style == S.hex("#FF0000")
    assert color_style != S.hex("#0000FF")
    assert color_style != "not_a_color_style"
    assert StyledText(color_style @ "text").raw == "text"

    link_obj = S.link("https://example.com")
    assert link_obj.ljust(5, "-").raw == "-----"
    assert link_obj.rjust(5, "-").raw == "-----"
    assert link_obj.center(5, "-").raw == "-----"
    assert link_obj.wrap(10)[0].raw == ""
    assert link_obj.join(["A", "B"]).raw == "AB"
    link_group = link_obj | S.BOLD
    assert len(list(link_group)) == 2
    right_link_group = S.BOLD | link_obj
    assert len(list(right_link_group)) == 2

    # StyledSequence helpers:
    seq = S.RED("Text")
    assert repr(seq) != ""
    assert seq.ljust(6, "-").raw == "Text--"
    assert seq.rjust(6, "-").raw == "--Text"
    assert seq.center(6, "-").raw == "-Text-"
    assert seq.wrap(10)[0].raw == "Text"
    assert seq.join(["A", "B"]).raw == "ATextB"

    stream = io.StringIO()
    seq.print(file=stream)
    assert stream.getvalue() == "\x1b[31mText\x1b[39m\n"

    with patch("builtins.input", return_value="user_input") as mock_input:
        assert seq.input() == "user_input"
        mock_input.assert_called_once_with(StyledText(seq).ansi)

    # Style call with multiple arguments:
    multi_arg = S.BOLD("a", "b", "c")
    assert StyledText(multi_arg).raw == "abc"
    multi_color_arg = S.hex("#FF0000")("a", "b", "c")
    assert StyledText(multi_color_arg).raw == "abc"
    multi_link_arg = S.link("https://example.com")("a", "b", "c")
    assert StyledText(multi_link_arg).raw == "abc"

    # Custom _Style outside standard precomputed sequences:
    custom_style_matmul = _Style(999)
    assert StyledText(custom_style_matmul @ "custom").raw == "custom"
    custom_style_call = _Style(998)
    assert StyledText(custom_style_call("custom")).raw == "custom"


def test_type_guards() -> None:
    assert is_fg_color_style(S.RED) is True
    assert is_fg_color_style(S.hex("#FF0000")) is True
    assert is_fg_color_style(_Style(35)) is True
    assert is_fg_color_style(_Style(95)) is True
    assert is_fg_color_style(_Style(1)) is False
    assert is_fg_color_style(_ColorStyle(255, 0, 0, bg=False)) is True
    assert is_fg_color_style(_ColorStyle(255, 0, 0, bg=True)) is False
    assert is_fg_color_style(S.BG.RED) is False
    assert is_fg_color_style(S.BOLD) is False
    assert is_fg_color_style(123) is False

    assert is_bg_color_style(S.BG.RED) is True
    assert is_bg_color_style(S.BG.hex("#FF0000")) is True
    assert is_bg_color_style(_Style(45)) is True
    assert is_bg_color_style(_Style(105)) is True
    assert is_bg_color_style(_Style(1)) is False
    assert is_bg_color_style(_ColorStyle(255, 0, 0, bg=True)) is True
    assert is_bg_color_style(_ColorStyle(255, 0, 0, bg=False)) is False
    assert is_bg_color_style(S.RED) is False
    assert is_bg_color_style(S.BOLD) is False
    assert is_bg_color_style(123) is False

    assert is_color_style(S.RED) is True
    assert is_color_style(S.BG.RED) is True
    assert is_color_style(S.BOLD) is False

    assert is_base_style(S.BOLD) is True
    assert is_base_style(S.hex("#FF0000")) is True
    assert is_base_style(S.link("url")) is True
    assert is_base_style(S.BOLD | S.RED) is False

    assert is_any_style(S.BOLD) is True
    assert is_any_style(S.BOLD | S.RED) is True
    assert is_any_style("not_a_style") is False

    assert is_text_segment("text") is True
    assert is_text_segment(S.RED("text")) is True
    assert is_text_segment(StyledText("text")) is True
    assert is_text_segment(S.RED) is False

    assert is_render_segment("text") is True
    assert is_render_segment(S.RED) is True
    assert is_render_segment(123) is False

    assert is_text_renderable("text") is True
    assert is_text_renderable(("text", S.RED("subtext"))) is True
    assert is_text_renderable(("text", S.RED)) is False
    assert is_text_renderable(123) is False

    assert is_renderable("text") is True
    assert is_renderable(("text", S.RED)) is True
    assert is_renderable(123) is False
    assert is_renderable(("text", 123)) is False
