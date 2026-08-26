import xulbux.console as _console_module
from xulbux.ansi import S
import pytest


def test_style_resolvers():
    # FG styles:
    assert _console_module._as_fg_style(None) is not None
    assert _console_module._as_fg_style(S.RED) == S.RED
    assert _console_module._as_fg_style("#FF0000") is not None
    assert _console_module._as_fg_style((255, 0, 0)) is not None

    # BG styles:
    assert _console_module._as_bg_style(S.BG.BLUE) == S.BG.BLUE
    assert _console_module._as_bg_style("#0000FF") is not None
    assert _console_module._as_bg_style((0, 0, 255)) is not None

    # Title colors:
    title_bg, title_fg = _console_module._resolve_title_colors(S.BG.BLUE)
    assert title_bg == S.BG.BLUE
    assert title_fg == S.BLACK

    # Invalid errors:
    with pytest.raises(ValueError, match=r"The 'border_style' parameter must be a valid style.*got 'invalid_style'"):
        _console_module._as_fg_style("invalid_style", param_name="border_style")

    with pytest.raises(ValueError, match=r"The 'box_bg_color' parameter must be a valid background style.*got 'bad_color'"):
        _console_module._as_bg_style("bad_color", param_name="box_bg_color")

    with pytest.raises(ValueError, match=r"The 'title_bg_color' parameter must be a valid background style.*got 'bad_title'"):
        _console_module._resolve_title_colors("bad_title")
