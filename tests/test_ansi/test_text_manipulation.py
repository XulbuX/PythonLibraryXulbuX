from typing import TYPE_CHECKING
from unittest.mock import patch
from xulbux.ansi import S
import pytest

if TYPE_CHECKING:
    from xulbux.base.types import Renderable


def test_styled_text_join() -> None:
    separator = S.BR.BLACK(" | ")
    items: list[Renderable] = ["Item 1", S.RED("Item 2"), "Item 3"]
    joined = separator.join(items)

    assert joined.raw == "Item 1 | Item 2 | Item 3"
    assert "\x1b[90m | \x1b[39m" in joined.ansi
    assert "\x1b[31mItem 2\x1b[39m" in joined.ansi

    style_group_joined = (S.BOLD | S.BLUE).join(["A ", " B"])
    assert style_group_joined.raw == "A  B"


def test_styled_text_alignment_ljust_rjust_center() -> None:
    text = S.RED("Alert")
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

    # Bare style / custom color alignment:
    assert S.RED.ljust(4, "-").raw == "----"
    assert S.hex("#F67").rjust(4, "-").raw == "----"
    assert S.link("url").center(4, "-").raw == "----"


def test_styled_text_wrap() -> None:
    long_styled = S.RED("This is a long sentence that should be wrapped into multiple lines cleanly.")
    wrapped_lines = long_styled.wrap(20)

    assert len(wrapped_lines) > 1
    for line in wrapped_lines:
        assert len(line) <= 20
        assert line.ansi.startswith("\x1b[31m")

    # Edge cases for wrap:
    assert len(S("Line 1\n\nLine 2").wrap(20)) == 3
    assert len(S("Short").wrap(20)) == 1
    assert len(S("Text").wrap(0)) == 1

    # Whitespace only line where textwrap returns empty in multi-line text:
    assert len(S("   \nvalid text").wrap(5)) >= 2

    # Chunk not found in paragraph offset fallback:
    with patch("textwrap.wrap", return_value=["xyz"]):
        assert len(S("abc\ndef").wrap(5)) >= 1

    # StyleGroup wrap:
    assert len((S.BOLD | S.RED).wrap(10)) >= 1


def test_styled_text_wrap_drops_leading_whitespace_on_continuation_lines() -> None:
    text = "Auto-ignore mode (0: OFF, 1: Hardcoded only, 2: Smart) (default: 2)"
    wrapped = S(text).wrap(54)
    assert len(wrapped) == 2
    assert wrapped[0].raw == "Auto-ignore mode (0: OFF, 1: Hardcoded only, 2: Smart)"
    assert wrapped[1].raw == "(default: 2)"

    # Continuation lines drop leading whitespace, but initial indent is preserved:
    indented = "    Indented line should keep its initial indent but wrap cleanly."
    wrapped_indented = S(indented).wrap(30)
    assert wrapped_indented[0].raw.startswith("    Indented")
    assert not wrapped_indented[1].raw.startswith(" ")

    # Styled text preserves color across wrap without leading space:
    styled = S.RED("Auto-ignore mode (0: OFF, 1: Hardcoded only, 2: Smart) ") + S.BLUE("(default: 2)")
    wrapped_styled = styled.wrap(54)
    assert wrapped_styled[1].raw == "(default: 2)"
    assert "\x1b[34m" in wrapped_styled[1].ansi


def test_code_positions_properties() -> None:
    styled = S("Hello ", S.RED("Red"), " World")
    positions = styled.code_positions
    assert len(positions) == 2
    assert positions[0][1] == "\x1b[31m"
    assert positions[1][1] == "\x1b[39m"

    raw_positions = styled.raw_code_positions
    assert len(raw_positions) == 2
    assert raw_positions[0][0] == 6
    assert raw_positions[1][0] == 9


def test_s_raw_removes_ansi() -> None:
    assert S("\x1b[1;31mError\x1b[0m: \x1b[4mDetails\x1b[24m").raw == "Error: Details"


def test_styled_text_slice_with_step() -> None:
    styled = S.RED("ABCDE")
    assert styled[1:4].raw == "BCD"

    with pytest.raises(ValueError, match="only supports a step of 1"):
        _ = styled[::2]


def test_styled_text_input_prompt() -> None:
    styled_prompt = S.GREEN("Enter name: ")
    with patch("builtins.input", return_value="Alice") as mock_input:
        assert styled_prompt.input(reset_ansi=True) == "Alice"
        mock_input.assert_called_once_with(styled_prompt.ansi)

    # Input without reset_ansi:
    with patch("builtins.input", return_value="Bob"):
        assert styled_prompt.input(reset_ansi=False) == "Bob"
