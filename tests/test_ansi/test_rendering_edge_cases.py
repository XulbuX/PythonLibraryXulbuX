from xulbux.ansi import S, StyledText, _StyledSequence, is_base_style, is_render_segment, is_text_segment


def test_missing_catch_all():
    # `StyledText` init edge:
    st = StyledText("a", "b", sep=" ")

    # Text segment guards:
    is_base_style(S.BOLD)
    is_text_segment(st)
    is_text_segment(_StyledSequence(("a",), ("b",), "c"))
    is_render_segment(st)
    is_render_segment(S.BOLD)

    # Justification:
    t2 = StyledText("a")
    t2.rjust(5)
    t2.ljust(5)
    t2.center(5)
    t2.wrap(1)
    t2.wrap(10)

    # 1785-1787, 1793:
    t3 = StyledText("a\\nb")
    t3.wrap(1)

    # Windows config:
    import xulbux.ansi

    xulbux.ansi._terminal_ansi_configured = False
    xulbux.ansi._config_terminal()
