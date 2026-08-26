import xulbux.ansi
from xulbux.ansi import S, StyledText, _StyledSequence, is_base_style, is_render_segment, is_text_segment


def test_missing_catch_all():
    # `StyledText` init edge:
    st1 = StyledText("a", "b", sep=" ")

    # Text segment guards:
    is_base_style(S.BOLD)
    is_text_segment(st1)
    is_text_segment(_StyledSequence(("a",), ("b",), "c"))
    is_render_segment(st1)
    is_render_segment(S.BOLD)

    # Justification:
    st2 = StyledText("a")
    st2.rjust(5)
    st2.ljust(5)
    st2.center(5)
    st2.wrap(1)
    st2.wrap(10)

    # 1785-1787, 1793:
    st3 = StyledText("a\\nb")
    st3.wrap(1)

    # Windows config:
    xulbux.ansi._terminal_ansi_configured = False
    xulbux.ansi._config_terminal()
