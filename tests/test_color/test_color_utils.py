import math
from collections.abc import Sequence
import xulbux.color as _color_module
from xulbux.color import hexa, hsla, rgba
import pytest


def test_rgba_to_hex_int_and_back() -> None:
    blue = _color_module.rgba_to_hex_int(0, 0, 255)
    black = _color_module.rgba_to_hex_int(0, 0, 0, 1.0)
    preserved_blue = _color_module.rgba_to_hex_int(0, 0, 255, preserve_original=True)
    preserved_black = _color_module.rgba_to_hex_int(0, 0, 0, 1.0, preserve_original=True)
    assert blue == 0x0100FF
    assert black == 0x010000FF
    assert preserved_blue == 0x0000FF
    assert preserved_black == 0x000000FF
    assert _color_module.hex_int_to_rgba(blue).as_tuple() == (0, 0, 255, None)
    assert _color_module.hex_int_to_rgba(black).as_tuple() == (0, 0, 0, 1.0)
    assert _color_module.hex_int_to_rgba(preserved_blue).as_tuple() == (0, 0, 255, None)
    assert _color_module.hex_int_to_rgba(preserved_black).as_tuple() == (0, 0, 255, None)
    assert _color_module.hex_int_to_rgba(blue, preserve_original=True).as_tuple() == (1, 0, 255, None)
    assert _color_module.hex_int_to_rgba(black, preserve_original=True).as_tuple() == (1, 0, 0, 1.0)

    with pytest.raises(ValueError):
        _color_module.rgba_to_hex_int(256, 0, 0)
    with pytest.raises(ValueError):
        _color_module.rgba_to_hex_int(0, 0, 0, 1.5)

    with pytest.raises(ValueError):
        _color_module.hex_int_to_rgba(-1)
    with pytest.raises(ValueError):
        _color_module.hex_int_to_rgba(0x100000000)


def test_is_valid_rgba() -> None:
    assert _color_module.is_valid_rgba((255, 0, 0)) is True
    assert _color_module.is_valid_rgba((255, 0, 0, 0.5)) is True
    assert _color_module.is_valid_rgba("rgb(255, 0, 0)") is True
    assert _color_module.is_valid_rgba("rgba(255, 0, 0, .5)") is True
    assert _color_module.is_valid_rgba({"red": 255, "green": 0, "blue": 0}) is True
    assert _color_module.is_valid_rgba({"red": 255, "green": 0, "blue": 0, "alpha": 0.5}) is True
    assert _color_module.is_valid_rgba(rgba(255, 0, 0)) is True
    assert _color_module.is_valid_rgba((300, 0, 0)) is False
    assert _color_module.is_valid_rgba((255, 0)) is False
    assert _color_module.is_valid_rgba((255, 0, 0, 2)) is False
    assert _color_module.is_valid_rgba("not a color") is False
    assert _color_module.is_valid_rgba((255, 0, 0), allow_alpha=False) is True
    assert _color_module.is_valid_rgba((255, 0, 0, 0.5), allow_alpha=False) is False


def test_is_valid_hsla() -> None:
    assert _color_module.is_valid_hsla((0, 100, 50)) is True
    assert _color_module.is_valid_hsla((0, 100, 50, 0.5)) is True
    assert _color_module.is_valid_hsla("hsl(0, 100%, 50%)") is True
    assert _color_module.is_valid_hsla("hsla(0, 100%, 50%, .5)") is True
    assert _color_module.is_valid_hsla({"hue": 0, "sat": 100, "light": 50}) is True
    assert _color_module.is_valid_hsla({"hue": 0, "sat": 100, "light": 50, "alpha": 0.5}) is True
    assert _color_module.is_valid_hsla(hsla(0, 100, 50)) is True
    assert _color_module.is_valid_hsla((370, 100, 50)) is False
    assert _color_module.is_valid_hsla((0, 101, 50)) is False
    assert _color_module.is_valid_hsla((0, 100, 101)) is False
    assert _color_module.is_valid_hsla((0, 100)) is False
    assert _color_module.is_valid_hsla("not a color") is False
    assert _color_module.is_valid_hsla((0, 100, 50), allow_alpha=False) is True
    assert _color_module.is_valid_hsla((0, 100, 50, 0.5), allow_alpha=False) is False
    assert _color_module.is_valid_hsla({"hue": 0}) is False


def test_is_valid_hexa() -> None:
    assert _color_module.is_valid_hexa("F00") is True
    assert _color_module.is_valid_hexa("F008") is True
    assert _color_module.is_valid_hexa("#F00") is True
    assert _color_module.is_valid_hexa("#F008") is True
    assert _color_module.is_valid_hexa("#FF0000") is True
    assert _color_module.is_valid_hexa("#FF000080") is True
    assert _color_module.is_valid_hexa(0xFF0000) is True
    assert _color_module.is_valid_hexa(0xFF000080) is True
    assert _color_module.is_valid_hexa(hexa("#FF0000")) is True
    assert _color_module.is_valid_hexa("#XX0000") is False
    assert _color_module.is_valid_hexa("#F0000") is False
    assert _color_module.is_valid_hexa("not a color") is False
    assert _color_module.is_valid_hexa("#F00", allow_alpha=False) is True
    assert _color_module.is_valid_hexa("#F008", allow_alpha=False) is False
    assert _color_module.is_valid_hexa("#F00", get_prefix=True) == (True, "#")
    assert _color_module.is_valid_hexa("0xF00", get_prefix=True) == (True, "0x")
    assert _color_module.is_valid_hexa(0xFF0000, get_prefix=True) == (True, "0x")


def test_is_valid() -> None:
    assert _color_module.is_valid((255, 0, 0)) is True
    assert _color_module.is_valid((360, 100, 50)) is True
    assert _color_module.is_valid("F008") is True
    assert _color_module.is_valid("F008", allow_alpha=False) is False
    assert _color_module.is_valid(0xFF0000) is True
    assert _color_module.is_valid(rgba(255, 0, 0)) is True
    assert _color_module.is_valid(hsla(0, 100, 50, 0.5)) is True
    assert _color_module.is_valid(hexa("#FF0000")) is True
    assert _color_module.is_valid("not a color") is False
    assert _color_module.is_valid((370, 100, 50)) is False


def test_has_alpha() -> None:
    assert _color_module.has_alpha((255, 0, 0)) is False
    assert _color_module.has_alpha((255, 0, 0, 0.5)) is True
    assert _color_module.has_alpha(rgba(255, 0, 0)) is False
    assert _color_module.has_alpha(rgba(255, 0, 0, 0.5)) is True
    assert _color_module.has_alpha(hsla(0, 100, 50)) is False
    assert _color_module.has_alpha(hsla(0, 100, 50, 0.5)) is True
    assert _color_module.has_alpha(hexa("#F00")) is False
    assert _color_module.has_alpha(hexa("#F00F")) is True
    assert _color_module.has_alpha("#FF0000") is False
    assert _color_module.has_alpha("#FF0000FF") is True
    assert _color_module.has_alpha("0xFF0000") is False
    assert _color_module.has_alpha("0xFF0000FF") is True
    assert _color_module.has_alpha("FF0000") is False
    assert _color_module.has_alpha("FF0000FF") is True
    assert _color_module.has_alpha(0xFF0000) is False
    assert _color_module.has_alpha(0xFF0000FF) is True
    assert _color_module.has_alpha("hsl(0,100%,50%)") is False
    assert _color_module.has_alpha("hsla(0,100%,50%,.5)") is True
    assert _color_module.has_alpha("rgb(0,0,0)") is False
    assert _color_module.has_alpha("rgba(0,0,0,.5)") is True
    assert _color_module.has_alpha([255, 0, 0]) is False
    assert _color_module.has_alpha([255, 0, 0, 0.5]) is True  # type:ignore[arg-type]
    assert _color_module.has_alpha({"red": 255, "green": 0, "blue": 0}) is False
    assert _color_module.has_alpha({"red": 255, "green": 0, "blue": 0, "alpha": 0.5}) is True
    assert _color_module.has_alpha("invalid") is False


def test_color_conversions() -> None:
    color_rgba = _color_module.as_rgba("#FF00007F")
    assert isinstance(color_rgba, rgba)
    assert _color_module.as_rgba(color_rgba) is color_rgba
    assert isinstance(_color_module.as_rgba(hsla(0, 100, 50)), rgba)
    assert isinstance(_color_module.as_rgba((255, 0, 0)), rgba)
    assert isinstance(_color_module.as_rgba("hsl(180, 50%, 50%)"), rgba)
    assert isinstance(_color_module.as_rgba({"hue": 0, "sat": 100, "light": 50}), rgba)
    assert isinstance(_color_module.as_rgba(0xFF0000), rgba)
    with pytest.raises(ValueError):
        _color_module.as_rgba("invalid")

    color_hsla = _color_module.as_hsla((255, 0, 0, 0.5))
    assert isinstance(color_hsla, hsla)
    assert _color_module.as_hsla(color_hsla) is color_hsla
    assert isinstance(_color_module.as_hsla(rgba(255, 0, 0)), hsla)
    assert isinstance(_color_module.as_hsla("rgb(255, 200, 200)"), hsla)
    assert isinstance(_color_module.as_hsla("#F00"), hsla)
    assert isinstance(_color_module.as_hsla({"hue": 0, "sat": 100, "light": 50}), hsla)
    assert isinstance(_color_module.as_hsla(0xFF0000), hsla)
    with pytest.raises(ValueError):
        _color_module.as_hsla("invalid")

    color_hexa = _color_module.as_hexa((255, 0, 0, 0.5))
    assert isinstance(color_hexa, hexa)
    assert _color_module.as_hexa(color_hexa) is color_hexa
    assert isinstance(_color_module.as_hexa(rgba(255, 0, 0)), hexa)
    assert isinstance(_color_module.as_hexa(hsla(0, 100, 50)), hexa)
    assert isinstance(_color_module.as_hexa("rgb(255, 200, 200)"), hexa)
    assert isinstance(_color_module.as_hexa("#F00"), hexa)
    assert isinstance(_color_module.as_hexa({"hue": 0, "sat": 100, "light": 50}), hexa)
    assert isinstance(_color_module.as_hexa(0xFF0000), hexa)
    with pytest.raises(ValueError):
        _color_module.as_hexa("invalid")


def test_str_to_rgba() -> None:
    color = _color_module.extract_rgba("The color is rgb(255, 0, 0, 0.5).", only_first=True)
    assert isinstance(color, rgba)
    assert color.as_tuple() == (255, 0, 0, 0.5)

    color_opaque = _color_module.extract_rgba("rgba(255,0,0,1)", only_first=True)
    assert isinstance(color_opaque, rgba)
    assert color_opaque.alpha is not None and math.isclose(color_opaque.alpha, 1.0)

    colors = _color_module.extract_rgba("first color: rgb(255, 0, 0) | second color: rgba(0,255,0,.5) third: rgba(0,0,0,1)")
    assert isinstance(colors, Sequence)
    assert len(colors) == 3
    assert colors[0].as_tuple() == (255, 0, 0, None)
    assert colors[1].as_tuple() == (0, 255, 0, 0.5)
    assert colors[2].alpha is not None and math.isclose(colors[2].alpha, 1.0)
    assert _color_module.extract_rgba("No colors here") is None
    assert _color_module.extract_rgba("No colors here", only_first=True) is None


def test_str_to_hsla() -> None:
    color = _color_module.extract_hsla("hsl(180, 50%, 50%)", only_first=True)
    assert isinstance(color, hsla)
    color_opaque = _color_module.extract_hsla("hsla(180, 50%, 50%, 1)", only_first=True)
    assert isinstance(color_opaque, hsla)
    assert color_opaque.alpha is not None and math.isclose(color_opaque.alpha, 1.0)

    colors = _color_module.extract_hsla("hsl(0, 100%, 50%) hsla(120, 100%, 50%, 0.5) hsla(0,0%,0%,1)")
    assert isinstance(colors, Sequence)
    assert len(colors) == 3
    assert colors[2].alpha is not None and math.isclose(colors[2].alpha, 1.0)
    assert _color_module.extract_hsla("No colors here") is None
    assert _color_module.extract_hsla("No colors here", only_first=True) is None


def test_luminance() -> None:
    assert _color_module.luminance(255, 0, 0) == 54
    assert _color_module.luminance(255, 0, 0, output_type=int) == 21
    assert 0.20 < _color_module.luminance(255, 0, 0, output_type=float) < 0.22
    assert _color_module.luminance(0, 0, 0) == 0
    assert _color_module.luminance(255, 255, 255) == 255
    assert _color_module.luminance(128, 128, 128) == 55

    assert _color_module.luminance(255, 0, 0, method="simple") == 85
    assert _color_module.luminance(255, 0, 0, method="bt601") == 76
    assert _color_module.luminance(255, 0, 0, method="wcag3") == 54
    with pytest.raises(ValueError):
        _color_module.luminance(256, 0, 0)


def test_fg_for_on_bg() -> None:
    text_color_dark = _color_module.fg_for_on_bg(rgba(0, 0, 0))
    assert isinstance(text_color_dark, rgba)
    assert text_color_dark.as_tuple() == (255, 255, 255, None)

    text_color_light = _color_module.fg_for_on_bg(rgba(255, 255, 255))
    assert isinstance(text_color_light, rgba)
    assert text_color_light.as_tuple() == (0, 0, 0, None)

    text_color_hexa_dark = _color_module.fg_for_on_bg(hexa("#000000"))
    assert isinstance(text_color_hexa_dark, hexa)
    assert str(text_color_hexa_dark) == "#FFFFFF"

    text_color_hexa_light = _color_module.fg_for_on_bg(hexa("#FFFFFF"))
    assert isinstance(text_color_hexa_light, hexa)
    assert str(text_color_hexa_light) == "#000000"

    assert _color_module.fg_for_on_bg(0x000000) == 0xFFFFFF
    assert _color_module.fg_for_on_bg(0xFFFFFF) == 0x000000


def test_adjust_lightness() -> None:
    color_red = rgba(128, 0, 0)
    lightened = _color_module.adjust_lightness(color_red, 0.5)
    assert isinstance(lightened, rgba)
    assert lightened.as_tuple()[:-1] > color_red.as_tuple()[:-1]

    color_light_red = rgba(255, 128, 128)
    darkened = _color_module.adjust_lightness(color_light_red, -0.5)
    assert isinstance(darkened, rgba)
    assert darkened.as_tuple()[:-1] < color_light_red.as_tuple()[:-1]

    lightened_hexa = _color_module.adjust_lightness(hexa("#800000"), 0.5)
    assert isinstance(lightened_hexa, hexa)
    assert lightened_hexa.is_light() is True

    with pytest.raises(ValueError):
        _color_module.adjust_lightness(color_red, 2.0)


def test_adjust_saturation() -> None:
    color_base = rgba(128, 80, 80)
    saturated = _color_module.adjust_saturation(color_base, 0.25)
    assert isinstance(saturated, rgba)
    assert saturated.as_hsla().sat > color_base.as_hsla().sat

    desaturated_hexa = _color_module.adjust_saturation(hexa("#FF0000"), -1.0)
    assert isinstance(desaturated_hexa, hexa)
    assert desaturated_hexa.is_grayscale() is True

    with pytest.raises(ValueError):
        _color_module.adjust_saturation(color_base, 2.0)


def test_parse_rgba_internal() -> None:
    assert _color_module._parse_rgba((255, 0, 0)).red == 255
    rgba_parsed = _color_module._parse_rgba((255, 0, 0, 0.5))
    assert rgba_parsed.alpha is not None and math.isclose(rgba_parsed.alpha, 0.5)
    assert _color_module._parse_rgba({"red": 255, "green": 0, "blue": 0}).red == 255
    assert _color_module._parse_rgba({"red": 255, "green": 0, "blue": 0, "alpha": 0.5}).alpha is not None
    assert _color_module._parse_rgba(rgba(255, 0, 0)).red == 255
    assert _color_module._parse_rgba("rgb(255, 0, 0)").red == 255

    with pytest.raises(ValueError):
        _color_module._parse_rgba("invalid")
    with pytest.raises(ValueError):
        _color_module._parse_rgba((255, 0))  # type:ignore[arg-type]
    with pytest.raises(ValueError):
        _color_module._parse_rgba({"red": 255})  # type:ignore[arg-type]


def test_parse_hsla_internal() -> None:
    assert _color_module._parse_hsla((180, 50, 50)).hue == 180
    hsla_parsed = _color_module._parse_hsla((180, 50, 50, 0.5))
    assert hsla_parsed.alpha is not None and math.isclose(hsla_parsed.alpha, 0.5)
    assert _color_module._parse_hsla({"hue": 180, "sat": 50, "light": 50}).hue == 180
    assert _color_module._parse_hsla({"hue": 180, "sat": 50, "light": 50, "alpha": 0.5}).alpha is not None
    assert _color_module._parse_hsla(hsla(180, 50, 50)).hue == 180
    assert _color_module._parse_hsla("hsl(180, 50%, 50%)").hue == 180

    with pytest.raises(ValueError):
        _color_module._parse_hsla("invalid")
    with pytest.raises(ValueError):
        _color_module._parse_hsla((180, 50))  # type:ignore[arg-type]
    with pytest.raises(ValueError):
        _color_module._parse_hsla({"hue": 180})  # type:ignore[arg-type]
