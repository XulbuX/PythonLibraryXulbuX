from typing import TYPE_CHECKING
from unittest.mock import patch
from xulbux.ansi import S, StyledText
import pytest

if TYPE_CHECKING:
    from xulbux.base.types import Renderable


def test_styled_text_join() -> None:
    separator = StyledText(S.BR.BLACK(" | "))
    items: list[Renderable] = ["Item 1", S.RED("Item 2"), "Item 3"]
    joined = separator.join(items)

    assert joined.raw == "Item 1 | Item 2 | Item 3"
    assert "\x1b[90m | \x1b[39m" in joined.ansi
    assert "\x1b[31mItem 2\x1b[39m" in joined.ansi

    style_group_joined = (S.BOLD | S.BLUE).join(["A ", " B"])
    assert style_group_joined.raw == "A  B"


def test_styled_text_alignment_ljust_rjust_center() -> None:
    text = StyledText(S.RED("Alert"))
    assert len(text) == 5

    # Left justify:
    left_justified = text.ljust(10, ".")
    assert left_justified.raw == "Alert....."
    assert left_justified.ansi.startswith("\x1b[31mAlert\x1b[39m")

    # Right justify:
    right_justified = text.rjust(10, ".")
    assert right_justified.raw == ".....Alert"
    assert right_justified.ansi.endswith("\x1b[31mAlert\x1b[39m")

    # Center:
    centered = text.center(11, ".")
    assert centered.raw == "...Alert..."

    # Zero or negative extra padding (returns copy):
    assert text.ljust(5).raw == "Alert"
    assert text.rjust(3).raw == "Alert"
    assert text.center(5).raw == "Alert"

    # StyleGroup / Style wrappers:
    assert (S.BOLD | S.BLUE).ljust(4, "-").raw == "----"
    assert (S.BOLD | S.BLUE).rjust(4, "-").raw == "----"
    assert (S.BOLD | S.BLUE).center(4, "-").raw == "----"

    # Internal _multiply_char edge cases:
    assert StyledText._multiply_char(StyledText("x"), 0) == ""
    multi_char_st = StyledText(S.RED("a"), S.BLUE("b"))
    assert StyledText._multiply_char(multi_char_st, 2) != ""

    # Invalid fill characters (must be length 1):
    with pytest.raises(TypeError, match="exactly one visible character"):
        text.ljust(10, "..")
    with pytest.raises(TypeError, match="exactly one visible character"):
        text.rjust(10, "")
    with pytest.raises(TypeError, match="exactly one visible character"):
        text.center(10, "--")


def test_styled_text_wrap() -> None:
    long_styled = StyledText(S.RED("This is a long sentence that should be wrapped into multiple lines cleanly."))
    wrapped_lines = long_styled.wrap(20)

    assert len(wrapped_lines) > 1
    for line in wrapped_lines:
        assert len(line) <= 20
        assert line.ansi.startswith("\x1b[31m")

    # Edge cases for wrap:
    empty_lines = StyledText("Line 1\n\nLine 2").wrap(20)
    assert len(empty_lines) == 3

    short_line = StyledText("Short").wrap(20)
    assert len(short_line) == 1

    zero_width = StyledText("Text").wrap(0)
    assert len(zero_width) == 1

    # Whitespace only line where textwrap returns empty in multi-line text:
    spaces_line = StyledText("   \nvalid text").wrap(5)
    assert len(spaces_line) >= 2

    # Chunk not found in paragraph offset fallback:
    with patch("textwrap.wrap", return_value=["xyz"]):
        fallback_wrap = StyledText("abc\ndef").wrap(5)
        assert len(fallback_wrap) >= 1

    # StyleGroup wrap:
    group_wrapped = (S.BOLD | S.RED).wrap(10)
    assert len(group_wrapped) >= 1


def test_code_positions_properties() -> None:
    styled = StyledText("Hello ", S.RED("Red"), " World")
    positions = styled.code_positions
    assert len(positions) == 2
    assert positions[0][1] == "\x1b[31m"
    assert positions[1][1] == "\x1b[39m"

    raw_positions = styled.raw_code_positions
    assert len(raw_positions) == 2
    assert raw_positions[0][0] == 6
    assert raw_positions[1][0] == 9


def test_remove_ansi() -> None:
    ansi_str = "\x1b[1;31mError\x1b[0m: \x1b[4mDetails\x1b[24m"
    assert StyledText.remove_ansi(ansi_str) == "Error: Details"


def test_styled_text_slice_with_step() -> None:
    styled = StyledText(S.RED("ABCDE"))
    assert styled[1:4].raw == "BCD"

    with pytest.raises(ValueError, match="only supports a step of 1"):
        _ = styled[::2]


def test_styled_text_input_prompt() -> None:
    styled_prompt = StyledText(S.GREEN("Enter name: "))
    with patch("builtins.input", return_value="Alice") as mock_input:
        user_response = styled_prompt.input(reset_ansi=True)
        assert user_response == "Alice"
        mock_input.assert_called_once_with(styled_prompt.ansi)

    # Input without reset_ansi:
    with patch("builtins.input", return_value="Bob"):
        assert styled_prompt.input(reset_ansi=False) == "Bob"
