from xulbux.ansi import S, _BgColorStyle, _FgColorStyle
from xulbux.base.consts import ANSI

ESC = ANSI.CHAR


# ************************************************** COLOR CONVERSION TESTS ***************************************************


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
    fg_rgb = S.rgb(255, 96, 112)
    bg_rgb = fg_rgb.to_bg()
    assert isinstance(bg_rgb, _BgColorStyle)
    assert bg_rgb == S.BG.rgb(255, 96, 112)
    assert hasattr(fg_rgb, "to_fg") is False

    fg_hex = S.hex("#FF6070")
    bg_hex = fg_hex.to_bg()
    assert isinstance(bg_hex, _BgColorStyle)
    assert bg_hex == S.BG.hex("#FF6070")
    assert hasattr(fg_hex, "to_fg") is False


def test_bg_color_style_to_fg():
    bg_rgb = S.BG.rgb(255, 96, 112)
    fg_rgb = bg_rgb.to_fg()
    assert isinstance(fg_rgb, _FgColorStyle)
    assert fg_rgb == S.rgb(255, 96, 112)
    assert hasattr(bg_rgb, "to_bg") is False

    bg_hex = S.BG.hex("#FF6070")
    fg_hex = bg_hex.to_fg()
    assert isinstance(fg_hex, _FgColorStyle)
    assert fg_hex == S.hex("#FF6070")
    assert hasattr(bg_hex, "to_bg") is False


def test_style_group_to_bg_and_to_fg():
    fg_group = S.BOLD | S.RED
    bg_group = fg_group.to_bg()
    assert bg_group == (S.BOLD | S.BG.RED)
    assert bg_group.to_fg() == (S.BOLD | S.RED)

    complex_group = S.BOLD | S.ITALIC | S.rgb(10, 20, 30)
    bg_complex = complex_group.to_bg()
    assert bg_complex == (S.BOLD | S.ITALIC | S.BG.rgb(10, 20, 30))
    assert bg_complex.to_fg() == complex_group
