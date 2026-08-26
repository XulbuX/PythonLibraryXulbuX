from xulbux.ansi import S, _BgColorStyle, _FgColorStyle
from xulbux.base.consts import ANSI

ESC = ANSI.CHAR


def test_fg_style_to_bg():
    # Standard FG colors:
    assert S.RED.to_bg() == S.BG.RED
    assert S.GREEN.to_bg() == S.BG.GREEN
    assert S.BLUE.to_bg() == S.BG.BLUE
    assert S.WHITE.to_bg() == S.BG.WHITE
    assert S.BLACK.to_bg() == S.BG.BLACK
    assert hasattr(S.RED, "to_fg") is False

    # Bright FG colors:
    assert S.BR.RED.to_bg() == S.BG.BR.RED
    assert S.BR.GREEN.to_bg() == S.BG.BR.GREEN
    assert S.BR.BLUE.to_bg() == S.BG.BR.BLUE
    assert hasattr(S.BR.RED, "to_fg") is False


def test_bg_style_to_fg():
    # Standard BG colors:
    assert S.BG.RED.to_fg() == S.RED
    assert S.BG.GREEN.to_fg() == S.GREEN
    assert S.BG.BLUE.to_fg() == S.BLUE
    assert S.BG.WHITE.to_fg() == S.WHITE
    assert S.BG.BLACK.to_fg() == S.BLACK
    assert hasattr(S.BG.RED, "to_bg") is False

    # Bright BG colors:
    assert S.BG.BR.RED.to_fg() == S.BR.RED
    assert S.BG.BR.GREEN.to_fg() == S.BR.GREEN
    assert S.BG.BR.BLUE.to_fg() == S.BR.BLUE
    assert hasattr(S.BG.BR.RED, "to_bg") is False


def test_fg_color_style_to_bg():
    rgb_fg_st = S.rgb(255, 96, 112)
    rgb_bg_st = rgb_fg_st.to_bg()
    assert isinstance(rgb_bg_st, _BgColorStyle)
    assert rgb_bg_st == S.BG.rgb(255, 96, 112)
    assert hasattr(rgb_fg_st, "to_fg") is False

    hex_fg_st = S.hex("#FF6070")
    hex_bg_st = hex_fg_st.to_bg()
    assert isinstance(hex_bg_st, _BgColorStyle)
    assert hex_bg_st == S.BG.hex("#FF6070")
    assert hasattr(hex_fg_st, "to_fg") is False


def test_bg_color_style_to_fg():
    rgb_bg_st = S.BG.rgb(255, 96, 112)
    rgb_fg_st = rgb_bg_st.to_fg()
    assert isinstance(rgb_fg_st, _FgColorStyle)
    assert rgb_fg_st == S.rgb(255, 96, 112)
    assert hasattr(rgb_bg_st, "to_bg") is False

    hex_bg_st = S.BG.hex("#FF6070")
    hex_fg_st = hex_bg_st.to_fg()
    assert isinstance(hex_fg_st, _FgColorStyle)
    assert hex_fg_st == S.hex("#FF6070")
    assert hasattr(hex_bg_st, "to_bg") is False


def test_style_group_to_bg_and_to_fg():
    g_fg_st = S.BOLD | S.RED
    g_bg_st = g_fg_st.to_bg()
    assert g_bg_st == (S.BOLD | S.BG.RED)
    assert g_bg_st.to_fg() == (S.BOLD | S.RED)

    complex_g_st = S.BOLD | S.ITALIC | S.rgb(10, 20, 30)
    complex_bg_st = complex_g_st.to_bg()
    assert complex_bg_st == (S.BOLD | S.ITALIC | S.BG.rgb(10, 20, 30))
    assert complex_bg_st.to_fg() == complex_g_st
