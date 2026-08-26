import math
from xulbux.color import hexa, rgba
import pytest


def test_hexa_init():
    # RGB string
    c1 = hexa("F00")
    assert c1.red == 255
    assert c1.green == 0
    assert c1.alpha is None

    # RGBA string
    color2 = hexa("#F008")
    assert color2.alpha is not None

    # RRGGBB string
    color3 = hexa("0xFF0000")
    assert color3.red == 255
    assert color3.alpha is None

    # RRGGBBAA string
    c4 = hexa("#FF000080")
    assert c4.alpha is not None

    # from int
    c5 = hexa(0xFF000080)
    assert c5.red == 255

    # from object with attrs
    class MockColor:
        red = 255
        green = 0
        blue = 0
        alpha = 0.5

    color6 = hexa(MockColor())  # pyright:ignore[reportArgumentType]
    assert color6.red == 255
    assert math.isclose(color6.alpha, 0.5)  # pyright:ignore[reportArgumentType]

    # invalid strings
    with pytest.raises(ValueError, match="Invalid HEXA color string"):
        hexa("FF000")
    with pytest.raises(ValueError, match="Could initialize hexa"):
        hexa(None)

    # kwargs
    c7 = hexa(_red=255, _green=0, _blue=0, _alpha=0.5)
    assert c7.red == 255

    # hexa copy
    c8 = hexa(c1)
    assert c8.red == 255


def test_hexa_iter():
    assert list(hexa("F00")) == ["FF", "00", "00"]
    assert list(hexa("#FF000080")) == ["FF", "00", "00", "80"]


def test_hexa_getitem():
    c1 = hexa("F00")
    assert c1[0] == "FF"
    assert c1[1] == "00"
    assert c1[2] == "00"
    assert c1[-1] == "00"
    assert c1[-2] == "00"
    assert c1[-3] == "FF"

    color2 = hexa("#FF000080")
    assert color2[3] == "80"
    assert color2[-1] == "80"
    assert color2[-4] == "FF"

    with pytest.raises(IndexError):
        c1[3]
    with pytest.raises(IndexError):
        color2[4]


def test_hexa_eq():
    assert hexa("F00") == hexa("#FF0000")
    assert hexa("F00") != hexa("#0F0")
    assert hexa("F00") != "not a color"


def test_hexa_str_repr():
    assert str(hexa("F00")) == "#FF0000"
    assert repr(hexa("#FF000080")) == "hexa(#FF000080)"


def test_hexa_dict():
    assert hexa("#FF000080").dict() == {"red": "FF", "green": "00", "blue": "00", "alpha": "80"}
    assert hexa("#FF0000").dict() == {"red": "FF", "green": "00", "blue": "00", "alpha": None}


def test_hexa_values():
    assert hexa("#FF000080").values() == (255, 0, 0, 0.5)
    assert hexa("#FF000080").values(round_alpha=False) != (255, 0, 0, 0.5)  # actually 128/255


def test_hexa_conversions():
    color1 = hexa("#FF000080")
    rgba_c = color1.to_rgba()
    assert isinstance(rgba_c, rgba)
    assert rgba_c.red == 255

    hsla_c = color1.to_hsla()
    assert hsla_c.hue == 0


def test_hexa_lighten_darken():
    color1 = hexa("#808080")
    lightened1 = color1.lighten(0.5)
    assert lightened1.red > 128
    with pytest.raises(ValueError):
        color1.lighten(1.5)

    darkened1 = color1.darken(0.5)
    assert darkened1.red < 128
    with pytest.raises(ValueError):
        color1.darken(-0.5)


def test_hexa_saturate_desaturate():
    color1 = hexa("#805050")
    saturated1 = color1.saturate(0.5)
    assert saturated1 != color1
    with pytest.raises(ValueError):
        color1.saturate(-0.1)

    ds = color1.desaturate(0.5)
    assert ds != color1
    with pytest.raises(ValueError):
        color1.desaturate(2.0)


def test_hexa_rotate():
    color1 = hexa("#FF0000")
    rotated1 = color1.rotate(180)
    assert rotated1.to_hsla().hue == 180


def test_hexa_invert():
    color1 = hexa("#FF800033")  # alpha 0.2
    inv1 = color1.invert()
    assert inv1.red == 0
    assert inv1.green == 127
    assert inv1.blue == 255

    inv2 = color1.invert(invert_alpha=True)
    assert math.isclose(inv2.alpha, 0.8)  # pyright:ignore[reportArgumentType]


def test_hexa_grayscale():
    color1 = hexa("#FF8000")
    gray1 = color1.grayscale()
    assert gray1.red == gray1.green == gray1.blue


def test_hexa_blend():
    c1 = hexa("#FF000080")
    color2 = hexa("#0000FF80")
    blend1 = c1.blend(color2, 0.5)
    assert isinstance(blend1, hexa)

    with pytest.raises(ValueError):
        c1.blend(color2, 1.5)

    with pytest.raises(TypeError):
        c1.blend("invalid", 0.5)

    b3 = hexa("#F00").blend(hexa("#00F"), 0.5)
    assert not b3.has_alpha()


def test_hexa_is_dark_light_grayscale():
    assert hexa("#000000").is_dark() is True
    assert hexa("#FFFFFF").is_light() is True
    assert hexa("#808080").is_grayscale() is True
    assert hexa("#80807F").is_grayscale() is False


def test_hexa_with_alpha():
    color1 = hexa("#FF0000")
    color_alpha = color1.with_alpha(0.5)
    assert math.isclose(color_alpha.alpha, 0.5)  # pyright:ignore[reportArgumentType]
    with pytest.raises(ValueError):
        color1.with_alpha(1.5)


def test_hexa_complementary():
    color1 = hexa("#FF0000")
    comp = color1.complementary()
    assert comp.to_hsla().hue == 180
