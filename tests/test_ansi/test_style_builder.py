import io
from pathlib import Path
from unittest.mock import patch
from xulbux.ansi import (
    S,
    _Color256Style,
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
import pytest


def test_standard_text_styles() -> None:
    bold = S.BOLD("bold text")
    assert isinstance(bold, S)
    assert bold.raw == "bold text"
    assert bold.ansi == "\x1b[1mbold text\x1b[22m"
    assert len(bold) == 9
    assert S.DIM("dim text").ansi == "\x1b[2mdim text\x1b[22m"
    assert S.ITALIC("italic text").ansi == "\x1b[3mitalic text\x1b[23m"
    assert S.UNDERLINE("underline text").ansi == "\x1b[4munderline text\x1b[24m"
    assert S.DOUBLE_UNDERLINE("double").ansi == "\x1b[21mdouble\x1b[24m"
    assert S.BLINK("blink text").ansi == "\x1b[5mblink text\x1b[25m"
    assert S.INVERSE("inverse text").ansi == "\x1b[7minverse text\x1b[27m"
    assert S.HIDDEN("hidden text").ansi == "\x1b[8mhidden text\x1b[28m"
    assert S.STRIKETHROUGH("strike text").ansi == "\x1b[9mstrike text\x1b[29m"


def test_foreground_colors() -> None:
    red = S.RED("red")
    assert isinstance(red, S)
    assert red.raw == "red"
    assert red.ansi == "\x1b[31mred\x1b[39m"
    assert len(red) == 3
    assert S.BLACK("black").ansi == "\x1b[30mblack\x1b[39m"
    assert S.GREEN("green").ansi == "\x1b[32mgreen\x1b[39m"
    assert S.YELLOW("yellow").ansi == "\x1b[33myellow\x1b[39m"
    assert S.BLUE("blue").ansi == "\x1b[34mblue\x1b[39m"
    assert S.MAGENTA("magenta").ansi == "\x1b[35mmagenta\x1b[39m"
    assert S.CYAN("cyan").ansi == "\x1b[36mcyan\x1b[39m"
    assert S.WHITE("white").ansi == "\x1b[37mwhite\x1b[39m"

    # Bright foreground:
    assert S.BR.BLACK("bright black").ansi == "\x1b[90mbright black\x1b[39m"
    assert S.BR.RED("bright red").ansi == "\x1b[91mbright red\x1b[39m"
    assert S.BR.GREEN("bright green").ansi == "\x1b[92mbright green\x1b[39m"
    assert S.BR.YELLOW("bright yellow").ansi == "\x1b[93mbright yellow\x1b[39m"
    assert S.BR.BLUE("bright blue").ansi == "\x1b[94mbright blue\x1b[39m"
    assert S.BR.MAGENTA("bright magenta").ansi == "\x1b[95mbright magenta\x1b[39m"
    assert S.BR.CYAN("bright cyan").ansi == "\x1b[96mbright cyan\x1b[39m"
    assert S.BR.WHITE("bright white").ansi == "\x1b[97mbright white\x1b[39m"


def test_background_colors() -> None:
    bg_red = S.BG.RED("bg red")
    assert isinstance(bg_red, S)
    assert bg_red.raw == "bg red"
    assert bg_red.ansi == "\x1b[41mbg red\x1b[49m"
    assert S.BG.BLACK("bg black").ansi == "\x1b[40mbg black\x1b[49m"
    assert S.BG.GREEN("bg green").ansi == "\x1b[42mbg green\x1b[49m"
    assert S.BG.YELLOW("bg yellow").ansi == "\x1b[43mbg yellow\x1b[49m"
    assert S.BG.BLUE("bg blue").ansi == "\x1b[44mbg blue\x1b[49m"
    assert S.BG.MAGENTA("bg magenta").ansi == "\x1b[45mbg magenta\x1b[49m"
    assert S.BG.CYAN("bg cyan").ansi == "\x1b[46mbg cyan\x1b[49m"
    assert S.BG.WHITE("bg white").ansi == "\x1b[47mbg white\x1b[49m"

    # Bright background:
    assert S.BG.BR.BLACK("bg bright black").ansi == "\x1b[100mbg bright black\x1b[49m"
    assert S.BG.BR.RED("bg bright red").ansi == "\x1b[101mbg bright red\x1b[49m"
    assert S.BG.BR.GREEN("bg bright green").ansi == "\x1b[102mbg bright green\x1b[49m"
    assert S.BG.BR.YELLOW("bg bright yellow").ansi == "\x1b[103mbg bright yellow\x1b[49m"
    assert S.BG.BR.BLUE("bg bright blue").ansi == "\x1b[104mbg bright blue\x1b[49m"
    assert S.BG.BR.MAGENTA("bg bright magenta").ansi == "\x1b[105mbg bright magenta\x1b[49m"
    assert S.BG.BR.CYAN("bg bright cyan").ansi == "\x1b[106mbg bright cyan\x1b[49m"
    assert S.BG.BR.WHITE("bg bright white").ansi == "\x1b[107mbg bright white\x1b[49m"


def test_custom_color_builders() -> None:
    rgb_st = S.rgb(255, 0, 128)("custom rgb")
    assert isinstance(rgb_st, S)
    assert rgb_st.ansi == "\x1b[38;2;255;0;128mcustom rgb\x1b[39m"
    assert S.hex("#FF0080")("custom hex").ansi == "\x1b[38;2;255;0;128mcustom hex\x1b[39m"
    assert S.hex("0xFF0080")("0x hex").ansi == "\x1b[38;2;255;0;128m0x hex\x1b[39m"
    assert S.hex(0xFF0080)("int hex").ansi == "\x1b[38;2;255;0;128mint hex\x1b[39m"
    assert S.hex(0x00FF00)("int hex green").ansi == "\x1b[38;2;0;255;0mint hex green\x1b[39m"
    assert S.hex("F08")("short hex").ansi == "\x1b[38;2;255;0;136mshort hex\x1b[39m"
    assert S.rgb(rgba(255, 0, 128))("from rgba").ansi == "\x1b[38;2;255;0;128mfrom rgba\x1b[39m"
    assert S.hex(hexa("#FF0080"))("from hexa").ansi == "\x1b[38;2;255;0;128mfrom hexa\x1b[39m"

    # `ColorStyle.from_hex` with explicit bg:
    assert _ColorStyle.from_hex("#FF0000", bg=True)._bg is True
    assert _ColorStyle.from_hex("#FF0000", bg=False)._bg is False
    assert _ColorStyle.from_hex(0xFF0000, bg=True)._bg is True
    assert _ColorStyle.from_hex(0xFF0000, bg=False)._bg is False

    # Out-of-range integer validation:
    with pytest.raises(ValueError, match="24-bit HEX integer"):
        _ColorStyle.from_hex(-1)
    with pytest.raises(ValueError, match="24-bit HEX integer"):
        _ColorStyle.from_hex(0x1000000)

    # Background custom colors:
    assert S.BG.rgb(0, 128, 255)("bg rgb").ansi == "\x1b[48;2;0;128;255mbg rgb\x1b[49m"
    assert S.BG.hex("#0080FF")("bg hex").ansi == "\x1b[48;2;0;128;255mbg hex\x1b[49m"
    assert S.BG.hex(0x0080FF)("bg int hex").ansi == "\x1b[48;2;0;128;255mbg int hex\x1b[49m"
    assert S.BG.hex("08F")("bg short hex").ansi == "\x1b[48;2;0;136;255mbg short hex\x1b[49m"
    assert S.BG.rgb(rgba(0, 128, 255))("bg from rgba").ansi == "\x1b[48;2;0;128;255mbg from rgba\x1b[49m"
    assert S.BG.hex(hexa("#0080FF"))("bg from hexa").ansi == "\x1b[48;2;0;128;255mbg from hexa\x1b[49m"


def test_hyperlink_builder() -> None:
    link_styled = S.link("https://github.com")("GitHub Link")
    assert isinstance(link_styled, S)
    assert link_styled.raw == "GitHub Link"
    assert "\x1b]8;;https://github.com\x1b\\GitHub Link\x1b]8;;\x1b\\" in link_styled.ansi

    path_link = S.link(Path("tests/test_ansi"))
    assert repr(path_link) != ""
    assert path_link == S.link(Path("tests/test_ansi"))
    assert (path_link == "not_a_link") is False
    assert path_link("text").raw == "text"
    assert (path_link @ "text").raw == "text"
    assert _Link.__ror__(path_link, S.BOLD) == (S.BOLD | path_link)


def test_style_group_composition_and_conversions() -> None:
    bold_red = S.BOLD | S.RED
    assert bold_red("alert").ansi == "\x1b[1;31malert\x1b[22;39m"

    # Combining groups with groups and styles:
    group1 = S.BOLD | S.RED
    group2 = S.ITALIC | S.BLUE
    combined_group = group1 | group2
    assert len(list(combined_group)) == 4

    right_styled_group = S.UNDERLINE | group1
    assert len(list(right_styled_group)) == 3

    left_styled_group = group1 | S.UNDERLINE
    assert len(list(left_styled_group)) == 3

    # Explicit `__ror__` calls:
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
    result = complex_group("complex text")
    assert isinstance(result, S)
    assert result.raw == "complex text"
    assert "\x1b[1;4;94;47mcomplex text\x1b[22;24;39;49m" in result.ansi

    # Group `as_bg` and `as_fg` conversions:
    fg_group = S.RED | S.BOLD | S.hex("#FF0000")
    bg_group = fg_group.as_bg()
    assert any(code == S.BG.RED for code in bg_group)
    assert any(code == S.RED for code in bg_group.as_fg())

    # Individual style conversions:
    assert S.RED.as_bg() == S.BG.RED
    assert S.RED.as_fg() == S.RED
    assert S.BG.RED.as_fg() == S.RED
    assert S.BG.RED.as_bg() == S.BG.RED
    assert S.hex("#FF0000").as_bg() == S.BG.hex("#FF0000")
    assert S.hex("#FF0000").as_fg() == S.hex("#FF0000")
    assert S.BG.hex("#FF0000").as_fg() == S.hex("#FF0000")
    assert S.BG.hex("#FF0000").as_bg() == S.BG.hex("#FF0000")
    assert S.color256(196).as_fg() == S.color256(196)
    assert S.color256(196).as_bg() == S.BG.color256(196)
    assert S.BG.color256(196).as_fg() == S.color256(196)
    assert S.BG.color256(196).as_bg() == S.BG.color256(196)
    assert S.BOLD.as_fg() == S.BOLD
    assert S.BOLD.as_bg() == S.BOLD
    assert S.link("https://example.com").as_fg() == S.link("https://example.com")
    assert S.link("https://example.com").as_bg() == S.link("https://example.com")
    assert _ColorStyle(255, 0, 0, bg=False).as_bg() == S.BG.hex("#FF0000")
    assert _ColorStyle(255, 0, 0, bg=True).as_fg() == S.hex("#FF0000")
    assert _Color256Style(196, bg=False).as_bg() == S.BG.color256(196)
    assert _Color256Style(196, bg=True).as_fg() == S.color256(196)


def test_reset_tokens() -> None:
    assert S.RESET.ansi == "\x1b[0m"
    assert S.RESET_BOLD.ansi == "\x1b[22m"
    assert S.RESET_DIM.ansi == "\x1b[22m"
    assert S.RESET_ITALIC.ansi == "\x1b[23m"
    assert S.RESET_UNDERLINE.ansi == "\x1b[24m"
    assert S.RESET_INVERSE.ansi == "\x1b[27m"
    assert S.RESET_HIDDEN.ansi == "\x1b[28m"
    assert S.RESET_STRIKETHROUGH.ansi == "\x1b[29m"
    assert S.RESET_FG.ansi == "\x1b[39m"
    assert S.RESET_BG.ansi == "\x1b[49m"


def test_bare_styles_in_styled_text() -> None:
    output = S(S.RED, "Error Text", S.RESET_FG, " Normal Text")
    assert output.raw == "Error Text Normal Text"
    assert output.ansi == "\x1b[31mError Text\x1b[39m Normal Text"


def test_style_equality_and_representations() -> None:
    assert S.BOLD == S.BOLD
    assert S.BOLD != S.DIM
    assert S.BOLD == 1
    assert (S.BOLD == "not_an_int") is False
    assert (object() == S.BOLD) is False
    assert hash(S.BOLD) == hash(1)
    assert int(S.BOLD) == 1
    assert str(S.BOLD) == "1"

    assert (S.BOLD | S.RED) == (S.BOLD | S.RED)
    assert (S.BOLD | S.RED) != (S.BOLD | S.BLUE)
    assert (S.BOLD | S.RED) != "not_a_style"
    assert (object() == (S.BOLD | S.RED)) is False
    assert (S.hex("#FF0000") == object()) is False
    assert (S.link("https://example.com") == object()) is False
    assert (123 in S("text")) is False
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
    assert S.RED.raw == ""
    assert S.RED.ansi == "\x1b[31m"
    assert len(S.RED) == 0
    assert bool(S.RED) is False
    assert (S.RED + "text").raw == "text"
    assert ("text" + S.RED).raw == "text"
    assert (S.RED * 2).ansi == "\x1b[31m\x1b[31m"
    assert (2 * S.RED).ansi == "\x1b[31m\x1b[31m"
    assert S.RED[0:2].raw == ""
    assert len(S.RED.code_positions) == 1
    assert len(S.RED.raw_code_positions) == 1

    stream_red = io.StringIO()
    S.RED.print(file=stream_red)
    assert stream_red.getvalue() == "\x1b[31m\n"

    with patch("builtins.input", return_value="user_style_input") as mock_input_style:
        assert S.RED.input() == "user_style_input"
        mock_input_style.assert_called_once_with("\x1b[31m")

    # Bare `_StyleGroup` helpers:
    group = S.BOLD | S.RED
    assert group.raw == ""
    assert group.ansi == "\x1b[1;31m"
    assert len(group) == 0
    assert bool(group) is False
    assert (group + "text").raw == "text"
    assert ("text" + group).raw == "text"
    assert (group * 2).ansi == "\x1b[1;31m\x1b[1;31m"
    assert (2 * group).ansi == "\x1b[1;31m\x1b[1;31m"
    assert group[0:2].raw == ""
    assert len(group.code_positions) == 1
    assert len(group.raw_code_positions) == 1

    stream_grp = io.StringIO()
    group.print(file=stream_grp)
    assert stream_grp.getvalue() == "\x1b[1;31m\n"

    with patch("builtins.input", return_value="user_group_input") as mock_input_grp:
        assert group.input() == "user_group_input"
        mock_input_grp.assert_called_once_with("\x1b[1;31m")

    color_style = S.hex("#FF0000")
    assert color_style.ljust(5, "-").raw == "-----"
    assert color_style.rjust(5, "-").raw == "-----"
    assert color_style.center(5, "-").raw == "-----"
    assert color_style.wrap(10)[0].raw == ""
    assert color_style.join(["A", "B"]).raw == "AB"
    assert color_style.raw == ""
    assert color_style.ansi == "\x1b[38;2;255;0;0m"
    assert len(color_style) == 0
    assert bool(color_style) is False
    assert (color_style + "text").raw == "text"
    assert ("text" + color_style).raw == "text"
    assert (color_style * 2).ansi == "\x1b[38;2;255;0;0m\x1b[38;2;255;0;0m"
    assert (2 * color_style).ansi == "\x1b[38;2;255;0;0m\x1b[38;2;255;0;0m"
    assert color_style[0:2].raw == ""
    assert len(color_style.code_positions) == 1
    assert len(color_style.raw_code_positions) == 1
    assert color_style == S.hex("#FF0000")
    assert color_style != S.hex("#0000FF")
    assert color_style != "not_a_color_style"
    assert (color_style @ "text").raw == "text"

    stream_col = io.StringIO()
    color_style.print(file=stream_col)
    assert stream_col.getvalue() == "\x1b[38;2;255;0;0m\n"

    with patch("builtins.input", return_value="user_col_input") as mock_input_col:
        assert color_style.input() == "user_col_input"
        mock_input_col.assert_called_once_with("\x1b[38;2;255;0;0m")

    link_obj = S.link("https://example.com")
    assert link_obj.ljust(5, "-").raw == "-----"
    assert link_obj.rjust(5, "-").raw == "-----"
    assert link_obj.center(5, "-").raw == "-----"
    assert link_obj.wrap(10)[0].raw == ""
    assert link_obj.join(["A", "B"]).raw == "AB"
    assert link_obj.raw == ""
    assert "\x1b]8;;https://example.com\x1b\\" in link_obj.ansi
    assert len(link_obj) == 0
    assert bool(link_obj) is False
    assert (link_obj + "text").raw == "text"
    assert ("text" + link_obj).raw == "text"
    assert len(link_obj * 2) == 0
    assert len(2 * link_obj) == 0
    assert link_obj[0:2].raw == ""
    assert len(link_obj.code_positions) == 1
    assert len(link_obj.raw_code_positions) == 1

    stream_lnk = io.StringIO()
    link_obj.print(file=stream_lnk)
    assert "\x1b]8;;https://example.com\x1b\\\n" in stream_lnk.getvalue()

    with patch("builtins.input", return_value="user_lnk_input") as mock_input_lnk:
        assert link_obj.input() == "user_lnk_input"
        mock_input_lnk.assert_called_once_with(link_obj.ansi)

    link_group = link_obj | S.BOLD
    assert len(list(link_group)) == 2
    right_link_group = S.BOLD | link_obj
    assert len(list(right_link_group)) == 2

    # Direct `S` returned by style calls:
    seq = S.RED("Text")
    assert isinstance(seq, S)
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
        mock_input.assert_called_once_with(seq.ansi)

    # Style call with multiple arguments:
    multi_arg = S.BOLD("a", "b", "c")
    assert multi_arg.raw == "abc"
    multi_color_arg = S.hex("#FF0000")("a", "b", "c")
    assert multi_color_arg.raw == "abc"
    multi_link_arg = S.link("https://example.com")("a", "b", "c")
    assert multi_link_arg.raw == "abc"

    # Custom `_Style` outside standard precomputed sequences:
    custom_style_matmul = _Style(999)
    assert (custom_style_matmul @ "custom").raw == "custom"
    custom_style_call = _Style(998)
    assert custom_style_call("custom").raw == "custom"


def test_type_guards() -> None:
    assert is_fg_color_style(S.RED) is True
    assert is_fg_color_style(S.hex("#FF0000")) is True
    assert is_fg_color_style(_Style(35)) is True
    assert is_fg_color_style(_Style(95)) is True
    assert is_fg_color_style(_Style(1)) is False
    assert is_fg_color_style(_ColorStyle(255, 0, 0, bg=False)) is True
    assert is_fg_color_style(_ColorStyle(255, 0, 0, bg=True)) is False
    assert is_fg_color_style(S.BG.RED) is False
    assert is_fg_color_style(S.color256(196)) is True
    assert is_fg_color_style(S.BG.color256(196)) is False
    assert is_fg_color_style(_Color256Style(196, bg=False)) is True
    assert is_fg_color_style(_Color256Style(196, bg=True)) is False
    assert is_fg_color_style(S.BOLD) is False
    assert is_fg_color_style(123) is False

    assert is_bg_color_style(S.BG.RED) is True
    assert is_bg_color_style(S.BG.hex("#FF0000")) is True
    assert is_bg_color_style(S.BG.color256(21)) is True
    assert is_bg_color_style(S.color256(21)) is False
    assert is_bg_color_style(_Color256Style(21, bg=True)) is True
    assert is_bg_color_style(_Color256Style(21, bg=False)) is False
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
    assert is_color_style(S.color256(196)) is True
    assert is_color_style(S.BG.color256(196)) is True
    assert is_color_style(S.BOLD) is False

    assert is_base_style(S.BOLD) is True
    assert is_base_style(S.hex("#FF0000")) is True
    assert is_base_style(S.color256(196)) is True
    assert is_base_style(S.link("url")) is True
    assert is_base_style(S.BOLD | S.RED) is False

    assert is_any_style(S.BOLD) is True
    assert is_any_style(S.color256(196)) is True
    assert is_any_style(S.BOLD | S.color256(196)) is True
    assert is_any_style(S.BOLD | S.RED) is True
    assert is_any_style("not_a_style") is False

    assert is_text_segment("text") is True
    assert is_text_segment(S.RED("text")) is True
    assert is_text_segment(S("text")) is True
    assert is_text_segment(S.RED) is False

    assert is_render_segment("text") is True
    assert is_render_segment(S.RED) is True
    assert is_render_segment(S.color256(196)) is True
    assert is_render_segment(123) is False

    assert is_text_renderable("text") is True
    assert is_text_renderable(("text", S.RED("subtext"))) is True
    assert is_text_renderable(("text", S.RED)) is False
    assert is_text_renderable(123) is False

    assert is_renderable("text") is True
    assert is_renderable(("text", S.RED)) is True
    assert is_renderable(("text", S.color256(196))) is True
    assert is_renderable(123) is False
    assert is_renderable(("text", 123)) is False


def test_256_color_styles() -> None:
    fg_256 = S.color256(196)("text")
    assert isinstance(fg_256, S)
    assert fg_256.raw == "text"
    assert fg_256.ansi == "\x1b[38;5;196mtext\x1b[39m"

    bg_256 = S.BG.color256(21)("bg text")
    assert isinstance(bg_256, S)
    assert bg_256.raw == "bg text"
    assert bg_256.ansi == "\x1b[48;5;21mbg text\x1b[49m"

    # Conversion methods:
    fg_style = S.color256(196)
    bg_converted = fg_style.as_bg()
    assert bg_converted("text").ansi == "\x1b[48;5;196mtext\x1b[49m"

    bg_style = S.BG.color256(21)
    fg_converted = bg_style.as_fg()
    assert fg_converted("text").ansi == "\x1b[38;5;21mtext\x1b[39m"

    # Combining:
    combined = (S.BOLD | S.color256(196) | S.BG.color256(21))("styled")
    assert combined.ansi == "\x1b[1;38;5;196;48;5;21mstyled\x1b[22;39;49m"
    comb_simple = S.color256(196) | S.BOLD
    assert isinstance(comb_simple, _StyleGroup)
    comb_ror_direct = S.color256(196).__ror__(S.BOLD)
    assert isinstance(comb_ror_direct, _StyleGroup)

    # StyleGroup `as_bg` and `as_fg` conversions:
    group = S.BOLD | S.color256(196)
    group_bg = group.as_bg()
    assert group_bg("text").ansi == "\x1b[1;48;5;196mtext\x1b[22;49m"

    group_fg = group_bg.as_fg()
    assert group_fg("text").ansi == "\x1b[1;38;5;196mtext\x1b[22;39m"

    # Single item application:
    assert (S.color256(10) @ "item").ansi == "\x1b[38;5;10mitem\x1b[39m"

    # Reverse combining:
    r_comb = S.BOLD.__ror__(S.color256(5))
    assert isinstance(r_comb, _StyleGroup)

    # Combining with StyleGroup and ror:
    comb_with_group = S.color256(196) | (S.BOLD | S.UNDERLINE)
    assert isinstance(comb_with_group, _StyleGroup)
    comb_ror = S.link("https://example.com") | S.color256(196)
    assert isinstance(comb_ror, _StyleGroup)

    # Repr and equality:
    c256 = _Color256Style(196, bg=False)
    assert repr(c256) == "_Color256Style(fg 196)"
    assert repr(_Color256Style(21, bg=True)) == "_Color256Style(bg 21)"
    assert c256 == _Color256Style(196, bg=False)
    assert c256 != _Color256Style(196, bg=True)
    assert c256 != _Color256Style(100, bg=False)
    assert c256 == c256.ansi
    assert c256 == S(c256.ansi)
    assert c256 != "other_string"
    assert (c256 == object()) is False

    # Validation errors:
    with pytest.raises(ValueError, match="256-color index"):
        S.color256(-1)
    with pytest.raises(ValueError, match="256-color index"):
        S.color256(256)
    with pytest.raises(ValueError, match="256-color index"):
        S.BG.color256(-1)
    with pytest.raises(ValueError, match="256-color index"):
        S.BG.color256(256)

    # Hashing tests:
    assert isinstance(hash(S.RED), int)
    assert isinstance(hash(S.rgb(255, 0, 0)), int)
    assert isinstance(hash(S.color256(196)), int)
    assert isinstance(hash(S.link("https://example.com")), int)
    assert isinstance(hash(S.BOLD | S.RED), int)


def test_as_text_methods() -> None:
    # Standard ANSI background colors -> `as_text_fg`:
    assert S.BG.BLACK.as_text_fg() == S.rgb(255, 255, 255)
    assert S.BG.BR.BLACK.as_text_fg() == S.rgb(255, 255, 255)
    assert S.BG.RED.as_text_fg() == S.rgb(0, 0, 0)
    assert S.BG.GREEN.as_text_fg() == S.rgb(0, 0, 0)
    assert S.BG.YELLOW.as_text_fg() == S.rgb(0, 0, 0)
    assert S.BG.BLUE.as_text_fg() == S.rgb(0, 0, 0)
    assert S.BG.MAGENTA.as_text_fg() == S.rgb(0, 0, 0)
    assert S.BG.CYAN.as_text_fg() == S.rgb(0, 0, 0)
    assert S.BG.WHITE.as_text_fg() == S.rgb(0, 0, 0)
    assert S.BG.BR.RED.as_text_fg() == S.rgb(0, 0, 0)
    assert S.BG.BR.WHITE.as_text_fg() == S.rgb(0, 0, 0)

    # Standard ANSI background colors -> `as_text_bg`:
    assert S.BG.BLACK.as_text_bg() == S.BG.rgb(255, 255, 255)
    assert S.BG.BR.BLACK.as_text_bg() == S.BG.rgb(255, 255, 255)
    assert S.BG.RED.as_text_bg() == S.BG.rgb(0, 0, 0)
    assert S.BG.WHITE.as_text_bg() == S.BG.rgb(0, 0, 0)

    # Standard ANSI foreground colors -> `as_text_bg`:
    assert S.BLACK.as_text_bg() == S.BG.rgb(255, 255, 255)
    assert S.BR.BLACK.as_text_bg() == S.BG.rgb(255, 255, 255)
    assert S.RED.as_text_bg() == S.BG.rgb(0, 0, 0)
    assert S.GREEN.as_text_bg() == S.BG.rgb(0, 0, 0)
    assert S.WHITE.as_text_bg() == S.BG.rgb(0, 0, 0)
    assert S.BR.WHITE.as_text_bg() == S.BG.rgb(0, 0, 0)

    # Standard ANSI foreground colors -> `as_text_fg`:
    assert S.BLACK.as_text_fg() == S.rgb(255, 255, 255)
    assert S.BR.BLACK.as_text_fg() == S.rgb(255, 255, 255)
    assert S.RED.as_text_fg() == S.rgb(0, 0, 0)
    assert S.WHITE.as_text_fg() == S.rgb(0, 0, 0)

    # True color styles -> `as_text_fg` & `as_text_bg`:
    assert S.BG.rgb(0, 0, 0).as_text_fg() == S.rgb(255, 255, 255)
    assert S.BG.rgb(255, 255, 255).as_text_fg() == S.rgb(0, 0, 0)
    assert S.BG.rgb(0, 0, 0).as_text_bg() == S.BG.rgb(255, 255, 255)
    assert S.BG.rgb(255, 255, 255).as_text_bg() == S.BG.rgb(0, 0, 0)
    assert S.BG.hex("#111111").as_text_fg() == S.rgb(255, 255, 255)
    assert S.BG.hex("#EEEEEE").as_text_fg() == S.rgb(0, 0, 0)

    assert S.rgb(0, 0, 0).as_text_bg() == S.BG.rgb(255, 255, 255)
    assert S.rgb(255, 255, 255).as_text_bg() == S.BG.rgb(0, 0, 0)
    assert S.rgb(0, 0, 0).as_text_fg() == S.rgb(255, 255, 255)
    assert S.rgb(255, 255, 255).as_text_fg() == S.rgb(0, 0, 0)
    assert S.hex("#111111").as_text_bg() == S.BG.rgb(255, 255, 255)
    assert S.hex("#EEEEEE").as_text_bg() == S.BG.rgb(0, 0, 0)

    # 256-color palette styles -> `as_text_fg` & `as_text_bg`:
    assert S.BG.color256(0).as_text_fg() == S.rgb(255, 255, 255)
    assert S.BG.color256(1).as_text_fg() == S.rgb(0, 0, 0)
    assert S.BG.color256(8).as_text_fg() == S.rgb(255, 255, 255)
    assert S.BG.color256(9).as_text_fg() == S.rgb(0, 0, 0)
    assert S.BG.color256(15).as_text_fg() == S.rgb(0, 0, 0)
    assert S.BG.color256(16).as_text_fg() == S.rgb(255, 255, 255)
    assert S.BG.color256(231).as_text_fg() == S.rgb(0, 0, 0)
    assert S.BG.color256(232).as_text_fg() == S.rgb(255, 255, 255)
    assert S.BG.color256(255).as_text_fg() == S.rgb(0, 0, 0)

    assert S.BG.color256(0).as_text_bg() == S.BG.rgb(255, 255, 255)
    assert S.BG.color256(1).as_text_bg() == S.BG.rgb(0, 0, 0)
    assert S.BG.color256(8).as_text_bg() == S.BG.rgb(255, 255, 255)
    assert S.BG.color256(9).as_text_bg() == S.BG.rgb(0, 0, 0)
    assert S.BG.color256(15).as_text_bg() == S.BG.rgb(0, 0, 0)
    assert S.BG.color256(16).as_text_bg() == S.BG.rgb(255, 255, 255)
    assert S.BG.color256(231).as_text_bg() == S.BG.rgb(0, 0, 0)
    assert S.BG.color256(232).as_text_bg() == S.BG.rgb(255, 255, 255)
    assert S.BG.color256(255).as_text_bg() == S.BG.rgb(0, 0, 0)

    assert S.color256(0).as_text_bg() == S.BG.rgb(255, 255, 255)
    assert S.color256(1).as_text_bg() == S.BG.rgb(0, 0, 0)
    assert S.color256(8).as_text_bg() == S.BG.rgb(255, 255, 255)
    assert S.color256(9).as_text_bg() == S.BG.rgb(0, 0, 0)
    assert S.color256(15).as_text_bg() == S.BG.rgb(0, 0, 0)
    assert S.color256(16).as_text_bg() == S.BG.rgb(255, 255, 255)
    assert S.color256(231).as_text_bg() == S.BG.rgb(0, 0, 0)
    assert S.color256(232).as_text_bg() == S.BG.rgb(255, 255, 255)
    assert S.color256(255).as_text_bg() == S.BG.rgb(0, 0, 0)

    assert S.color256(0).as_text_fg() == S.rgb(255, 255, 255)
    assert S.color256(1).as_text_fg() == S.rgb(0, 0, 0)
    assert S.color256(8).as_text_fg() == S.rgb(255, 255, 255)
    assert S.color256(9).as_text_fg() == S.rgb(0, 0, 0)
    assert S.color256(15).as_text_fg() == S.rgb(0, 0, 0)
    assert S.color256(16).as_text_fg() == S.rgb(255, 255, 255)
    assert S.color256(231).as_text_fg() == S.rgb(0, 0, 0)
    assert S.color256(232).as_text_fg() == S.rgb(255, 255, 255)
    assert S.color256(255).as_text_fg() == S.rgb(0, 0, 0)

    # Style group -> `as_text_fg` & `as_text_bg`:
    assert (S.BOLD | S.BG.BLACK).as_text_fg() == S.rgb(255, 255, 255)
    assert (S.BOLD | S.BG.WHITE).as_text_fg() == S.rgb(0, 0, 0)
    assert (S.BOLD | S.BG.hex("#000")).as_text_fg() == S.rgb(255, 255, 255)
    assert (S.BOLD | S.BG.color256(0)).as_text_fg() == S.rgb(255, 255, 255)
    assert (S.BOLD | S.BG.color256(231)).as_text_fg() == S.rgb(0, 0, 0)
    assert (S.BOLD | S.DIM).as_text_fg() == S.rgb(255, 255, 255)

    assert (S.BOLD | S.BLACK).as_text_bg() == S.BG.rgb(255, 255, 255)
    assert (S.BOLD | S.WHITE).as_text_bg() == S.BG.rgb(0, 0, 0)
    assert (S.BOLD | S.hex("#000")).as_text_bg() == S.BG.rgb(255, 255, 255)
    assert (S.BOLD | S.color256(0)).as_text_bg() == S.BG.rgb(255, 255, 255)
    assert (S.BOLD | S.color256(231)).as_text_bg() == S.BG.rgb(0, 0, 0)
    assert (S.BOLD | S.DIM).as_text_bg() == S.BG.rgb(0, 0, 0)


def test_with_text_methods() -> None:
    # Standard ANSI styles:
    assert S.BG.BLACK.with_text_fg() == (S.BG.BLACK | S.rgb(255, 255, 255))
    assert S.BG.WHITE.with_text_fg() == (S.BG.WHITE | S.rgb(0, 0, 0))
    assert S.BLACK.with_text_bg() == (S.BLACK | S.BG.rgb(255, 255, 255))
    assert S.WHITE.with_text_bg() == (S.WHITE | S.BG.rgb(0, 0, 0))

    # True color styles:
    assert S.BG.hex("#000000").with_text_fg() == (S.BG.hex("#000000") | S.rgb(255, 255, 255))
    assert S.BG.hex("#FFFFFF").with_text_fg() == (S.BG.hex("#FFFFFF") | S.rgb(0, 0, 0))
    assert S.hex("#000000").with_text_bg() == (S.hex("#000000") | S.BG.rgb(255, 255, 255))
    assert S.hex("#FFFFFF").with_text_bg() == (S.hex("#FFFFFF") | S.BG.rgb(0, 0, 0))

    # 256-color palette styles:
    assert S.BG.color256(0).with_text_fg() == (S.BG.color256(0) | S.rgb(255, 255, 255))
    assert S.BG.color256(231).with_text_fg() == (S.BG.color256(231) | S.rgb(0, 0, 0))
    assert S.color256(0).with_text_bg() == (S.color256(0) | S.BG.rgb(255, 255, 255))
    assert S.color256(231).with_text_bg() == (S.color256(231) | S.BG.rgb(0, 0, 0))

    # StyleGroup:
    assert (S.BOLD | S.BG.BLACK).with_text_fg() == (S.BOLD | S.BG.BLACK | S.rgb(255, 255, 255))
    assert (S.BOLD | S.BLACK).with_text_bg() == (S.BOLD | S.BLACK | S.BG.rgb(255, 255, 255))
