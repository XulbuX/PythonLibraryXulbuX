import math
import xulbux.color as _color_module
from xulbux.color import hexa, hsla, rgba
import pytest


def test_rgba_to_hex_int_and_back():
    blue = _color_module.rgba_to_hex_int(0, 0, 255)
    black = _color_module.rgba_to_hex_int(0, 0, 0, 1.0)
    preserved_blue = _color_module.rgba_to_hex_int(0, 0, 255, preserve_original=True)
    preserved_black = _color_module.rgba_to_hex_int(0, 0, 0, 1.0, preserve_original=True)
    assert blue == 0x0100FF
    assert black == 0x010000FF
    assert preserved_blue == 0x0000FF
    assert preserved_black == 0x000000FF
    assert _color_module.hex_int_to_rgba(blue).values() == (0, 0, 255, None)
    assert _color_module.hex_int_to_rgba(black).values() == (0, 0, 0, 1.0)
    assert _color_module.hex_int_to_rgba(preserved_blue).values() == (0, 0, 255, None)
    assert _color_module.hex_int_to_rgba(preserved_black).values() == (0, 0, 255, None)
    assert _color_module.hex_int_to_rgba(blue, preserve_original=True).values() == (1, 0, 255, None)
    assert _color_module.hex_int_to_rgba(black, preserve_original=True).values() == (1, 0, 0, 1.0)

    with pytest.raises(ValueError):
        _color_module.rgba_to_hex_int(256, 0, 0)
    with pytest.raises(ValueError):
        _color_module.rgba_to_hex_int(0, 0, 0, 1.5)

    with pytest.raises(ValueError):
        _color_module.hex_int_to_rgba(-1)
    with pytest.raises(ValueError):
        _color_module.hex_int_to_rgba(0x100000000)


def test_is_valid_rgba():
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


def test_is_valid_hsla():
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


def test_is_valid_hexa():
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


def test_is_valid():
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


def test_has_alpha():
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
    # hsla string:
    assert _color_module.has_alpha("hsl(0,100%,50%)") is False
    assert _color_module.has_alpha("hsla(0,100%,50%,.5)") is True
    # rgb string:
    assert _color_module.has_alpha("rgb(0,0,0)") is False
    assert _color_module.has_alpha("rgba(0,0,0,.5)") is True
    # dicts and lists:
    assert _color_module.has_alpha([255, 0, 0]) is False
    assert _color_module.has_alpha([255, 0, 0, 0.5]) is True
    assert _color_module.has_alpha({"red": 255, "green": 0, "blue": 0}) is False
    assert _color_module.has_alpha({"red": 255, "green": 0, "blue": 0, "alpha": 0.5}) is True
    # invalid:
    assert _color_module.has_alpha("invalid") is False


def test_color_conversions():
    # rgba:
    c1 = _color_module.to_rgba("#FF00007F")
    assert isinstance(c1, rgba)
    assert _color_module.to_rgba(c1) is c1
    assert isinstance(_color_module.to_rgba(hsla(0, 100, 50)), rgba)
    assert isinstance(_color_module.to_rgba((255, 0, 0)), rgba)
    assert isinstance(_color_module.to_rgba({"hue": 0, "sat": 100, "light": 50}), rgba)
    assert isinstance(_color_module.to_rgba(0xFF0000), rgba)
    with pytest.raises(ValueError):
        _color_module.to_rgba("invalid")

    # hsla:
    color2 = _color_module.to_hsla((255, 0, 0, 0.5))
    assert isinstance(color2, hsla)
    assert _color_module.to_hsla(color2) is color2
    assert isinstance(_color_module.to_hsla(rgba(255, 0, 0)), hsla)
    assert isinstance(_color_module.to_hsla("#F00"), hsla)
    assert isinstance(_color_module.to_hsla({"hue": 0, "sat": 100, "light": 50}), hsla)
    assert isinstance(_color_module.to_hsla(0xFF0000), hsla)
    with pytest.raises(ValueError):
        _color_module.to_hsla("invalid")

    # hexa:
    color3 = _color_module.to_hexa((255, 0, 0, 0.5))
    assert isinstance(color3, hexa)
    assert _color_module.to_hexa(color3) is color3
    assert isinstance(_color_module.to_hexa(rgba(255, 0, 0)), hexa)
    assert isinstance(_color_module.to_hexa(hsla(0, 100, 50)), hexa)
    assert isinstance(_color_module.to_hexa("#F00"), hexa)
    assert isinstance(_color_module.to_hexa({"hue": 0, "sat": 100, "light": 50}), hexa)
    assert isinstance(_color_module.to_hexa(0xFF0000), hexa)
    with pytest.raises(ValueError):
        _color_module.to_hexa("invalid")


def test_str_to_rgba():
    color = _color_module.str_to_rgba("The color is rgb(255, 0, 0, 0.5).", only_first=True)
    assert isinstance(color, rgba)
    assert color.values() == (255, 0, 0, 0.5)

    color2 = _color_module.str_to_rgba("rgba(255,0,0,1)", only_first=True)
    assert isinstance(color2, rgba)
    assert math.isclose(color2.alpha, 1.0)  # pyright:ignore[reportArgumentType]

    colors = _color_module.str_to_rgba("first color: rgb(255, 0, 0) | second color: rgba(0,255,0,.5) third: rgba(0,0,0,1)")
    assert len(colors) == 3  # pyright:ignore[reportArgumentType]
    assert colors[0].values() == (255, 0, 0, None)  # pyright:ignore[reportOptionalSubscript, reportUnknownMemberType]
    assert colors[1].values() == (0, 255, 0, 0.5)  # pyright:ignore[reportOptionalSubscript, reportUnknownMemberType]
    assert math.isclose(colors[2].alpha, 1.0)  # pyright:ignore[reportArgumentType, reportOptionalSubscript, reportUnknownMemberType]
    assert _color_module.str_to_rgba("No colors here") is None
    assert _color_module.str_to_rgba("No colors here", only_first=True) is None


def test_str_to_hsla():
    color = _color_module.str_to_hsla("hsl(180, 50%, 50%)", only_first=True)
    assert isinstance(color, hsla)
    color2 = _color_module.str_to_hsla("hsla(180, 50%, 50%, 1)", only_first=True)
    assert isinstance(color2, hsla)
    assert math.isclose(color2.alpha, 1.0)  # pyright:ignore[reportArgumentType]

    colors = _color_module.str_to_hsla("hsl(0, 100%, 50%) hsla(120, 100%, 50%, 0.5) hsla(0,0%,0%,1)")
    assert len(colors) == 3  # pyright:ignore[reportArgumentType]
    assert math.isclose(colors[2].alpha, 1.0)  # pyright:ignore[reportArgumentType, reportOptionalSubscript, reportUnknownMemberType]
    assert _color_module.str_to_hsla("No colors here") is None
    assert _color_module.str_to_hsla("No colors here", only_first=True) is None


def test_luminance():
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


def test_text_color_for_on_bg():
    text_color = _color_module.text_color_for_on_bg(rgba(0, 0, 0))
    assert isinstance(text_color, rgba)
    assert text_color.values() == (255, 255, 255, None)
    text_color = _color_module.text_color_for_on_bg(rgba(255, 255, 255))
    assert isinstance(text_color, rgba)
    assert text_color.values() == (0, 0, 0, None)

    # hexa:
    text_color = _color_module.text_color_for_on_bg(hexa("#000000"))
    assert isinstance(text_color, hexa)
    assert str(text_color) == "#FFFFFF"

    text_color = _color_module.text_color_for_on_bg(hexa("#FFFFFF"))
    assert isinstance(text_color, hexa)
    assert str(text_color) == "#000000"

    # int:
    assert _color_module.text_color_for_on_bg(0x000000) == 0xFFFFFF
    assert _color_module.text_color_for_on_bg(0xFFFFFF) == 0x000000


def test_adjust_lightness():
    color = rgba(128, 0, 0)
    lightened = _color_module.adjust_lightness(color, 0.5)
    assert isinstance(lightened, rgba)
    assert lightened.values()[:-1] > color.values()[:-1]

    color2 = rgba(255, 128, 128)
    darkened = _color_module.adjust_lightness(color2, -0.5)
    assert isinstance(darkened, rgba)
    assert darkened.values()[:-1] < color2.values()[:-1]

    lightened2 = _color_module.adjust_lightness(hexa("#800000"), 0.5)
    assert isinstance(lightened2, hexa)
    assert lightened2.is_light() is True

    with pytest.raises(ValueError):
        _color_module.adjust_lightness(color, 2.0)


def test_adjust_saturation():
    color = rgba(128, 80, 80)
    saturated = _color_module.adjust_saturation(color, 0.25)
    assert isinstance(saturated, rgba)
    assert saturated.to_hsla().sat > color.to_hsla().sat

    desaturated = _color_module.adjust_saturation(hexa("#FF0000"), -1.0)
    assert isinstance(desaturated, hexa)
    assert desaturated.is_grayscale() is True

    with pytest.raises(ValueError):
        _color_module.adjust_saturation(color, 2.0)


def test_parse_rgba_internal():
    assert _color_module._parse_rgba((255, 0, 0)).red == 255
    assert math.isclose(_color_module._parse_rgba((255, 0, 0, 0.5)).alpha, 0.5)  # pyright:ignore[reportArgumentType]
    assert _color_module._parse_rgba({"red": 255, "green": 0, "blue": 0}).red == 255
    assert math.isclose(_color_module._parse_rgba({"red": 255, "green": 0, "blue": 0, "alpha": 0.5}).alpha, 0.5)  # pyright:ignore[reportArgumentType]
    assert _color_module._parse_rgba(rgba(255, 0, 0)).red == 255
    assert _color_module._parse_rgba("rgb(255, 0, 0)").red == 255
    with pytest.raises(ValueError):
        _color_module._parse_rgba("invalid")
    with pytest.raises(ValueError):
        _color_module._parse_rgba((255, 0))  # pyright:ignore[reportArgumentType]
    with pytest.raises(ValueError):
        _color_module._parse_rgba({"red": 255})  # pyright:ignore[reportArgumentType]


def test_parse_hsla_internal():
    assert _color_module._parse_hsla((180, 50, 50)).hue == 180
    assert math.isclose(_color_module._parse_hsla((180, 50, 50, 0.5)).alpha, 0.5)  # pyright:ignore[reportArgumentType]
    assert _color_module._parse_hsla({"hue": 180, "sat": 50, "light": 50}).hue == 180
    assert math.isclose(_color_module._parse_hsla({"hue": 180, "sat": 50, "light": 50, "alpha": 0.5}).alpha, 0.5)  # pyright:ignore[reportArgumentType]
    assert _color_module._parse_hsla(hsla(180, 50, 50)).hue == 180
    assert _color_module._parse_hsla("hsl(180, 50%, 50%)").hue == 180
    with pytest.raises(ValueError):
        _color_module._parse_hsla("invalid")
    with pytest.raises(ValueError):
        _color_module._parse_hsla((180, 50))  # pyright:ignore[reportArgumentType]
    with pytest.raises(ValueError):
        _color_module._parse_hsla({"hue": 180})  # pyright:ignore[reportArgumentType]
