import math
from xulbux.color import rgba
import pytest


def test_rgba_init():
    # Valid
    color1 = rgba(255, 128, 0, 0.5)
    assert color1.red == 255
    assert color1.green == 128
    assert color1.blue == 0
    assert math.isclose(color1.alpha, 0.5)

    color2 = rgba(255, 128, 0)
    assert color2.alpha is None

    # Validation bypassing
    color3 = rgba(300, 300, 300, 2.0, _validate=False)
    assert color3.red == 300
    assert math.isclose(color3.alpha, 2.0)

    with pytest.raises(ValueError, match="must be integers in range"):
        rgba(-1, 0, 0)
    with pytest.raises(ValueError, match="must be integers in range"):
        rgba(0, 256, 0)

    # Invalid Alpha
    with pytest.raises(ValueError, match=r"must be in range \[0\.0, 1\.0\]"):
        rgba(0, 0, 0, -0.1)
    with pytest.raises(ValueError, match=r"must be in range \[0\.0, 1\.0\]"):
        rgba(0, 0, 0, 1.5)


def test_rgba_len_and_has_alpha():
    assert len(rgba(0, 0, 0)) == 3
    assert len(rgba(0, 0, 0, 0.5)) == 4
    assert rgba(0, 0, 0).has_alpha() is False
    assert rgba(0, 0, 0, 0.5).has_alpha() is True
    assert rgba(0, 0, 0).is_opaque() is True
    assert rgba(0, 0, 0, 1.0).is_opaque() is True
    assert rgba(0, 0, 0, 0.5).is_opaque() is False


def test_rgba_iter():
    assert list(rgba(255, 128, 0)) == [255, 128, 0]
    assert list(rgba(255, 128, 0, 0.5)) == [255, 128, 0, 0.5]


def test_rgba_getitem():
    c1 = rgba(255, 128, 0)
    assert c1[0] == 255
    assert c1[1] == 128
    assert c1[2] == 0
    assert c1[-1] == 0
    assert c1[-2] == 128
    assert c1[-3] == 255

    color2 = rgba(255, 128, 0, 0.5)
    assert math.isclose(color2[3], 0.5)
    assert math.isclose(color2[-1], 0.5)
    assert color2[-4] == 255

    with pytest.raises(IndexError):
        c1[3]
    with pytest.raises(IndexError):
        color2[4]


def test_rgba_eq():
    assert rgba(255, 128, 0, 0.5) == rgba(255, 128, 0, 0.5)
    assert rgba(255, 128, 0) != rgba(255, 128, 0, 0.5)
    assert rgba(255, 128, 0) != "not a color"


def test_rgba_str_repr():
    assert str(rgba(255, 128, 0)) == "rgba(255, 128, 0)"
    assert repr(rgba(255, 128, 0, 0.5)) == "rgba(255, 128, 0, 0.5)"


def test_rgba_dict():
    assert rgba(255, 128, 0, 0.5).dict() == {"red": 255, "green": 128, "blue": 0, "alpha": 0.5}


def test_rgba_values():
    assert rgba(255, 128, 0, 0.5).values() == (255, 128, 0, 0.5)


def test_rgba_conversions():
    color1 = rgba(255, 0, 0, 0.5)
    hsla_c = color1.to_hsla()
    assert hsla_c.hue == 0
    assert hsla_c.sat == 100
    assert hsla_c.light == 50
    assert math.isclose(hsla_c.alpha, 0.5)

    hexa_c = color1.to_hexa()
    assert hexa_c.red == 255
    assert math.isclose(hexa_c.alpha, 0.5)


def test_rgba_lighten_darken():
    color1 = rgba(128, 128, 128)
    lightened1 = color1.lighten(0.5)
    assert lightened1.red > 128
    with pytest.raises(ValueError):
        color1.lighten(1.5)

    darkened1 = color1.darken(0.5)
    assert darkened1.red < 128
    with pytest.raises(ValueError):
        color1.darken(-0.5)


def test_rgba_saturate_desaturate():
    color1 = rgba(128, 100, 100)
    saturated1 = color1.saturate(0.5)
    assert saturated1.to_hsla().sat > color1.to_hsla().sat
    with pytest.raises(ValueError):
        color1.saturate(-0.1)

    ds = color1.desaturate(0.5)
    assert ds.to_hsla().sat < color1.to_hsla().sat
    with pytest.raises(ValueError):
        color1.desaturate(2.0)


def test_rgba_rotate():
    color1 = rgba(255, 0, 0)
    rotated1 = color1.rotate(180)
    assert rotated1.to_hsla().hue == 180


def test_rgba_invert():
    color1 = rgba(255, 128, 0, 0.2)
    inv1 = color1.invert()
    assert inv1.red == 0
    assert inv1.green == 127
    assert inv1.blue == 255
    assert math.isclose(inv1.alpha, 0.2)

    inv2 = color1.invert(invert_alpha=True)
    assert math.isclose(inv2.alpha, 0.8)


def test_rgba_grayscale():
    color1 = rgba(255, 128, 0)
    gray1 = color1.grayscale()
    assert gray1.red == gray1.green == gray1.blue


def test_rgba_blend():
    c1 = rgba(255, 0, 0, 0.5)
    color2 = rgba(0, 0, 255, 0.5)
    blend1 = c1.blend(color2, 0.5)
    assert blend1.red == 128
    assert blend1.blue == 128
    assert blend1.green == 0

    with pytest.raises(ValueError):
        c1.blend(color2, 1.5)

    with pytest.raises(TypeError):
        c1.blend("invalid", 0.5)

    # test additive alpha
    blend2 = c1.blend(color2, 0.5, additive_alpha=True)
    assert math.isclose(blend2.alpha, 1.0)

    # test none alpha
    b3 = rgba(255, 0, 0).blend(rgba(0, 0, 255), 0.5)
    assert b3.alpha is None


def test_rgba_is_dark_light_grayscale():
    assert rgba(0, 0, 0).is_dark() is True
    assert rgba(255, 255, 255).is_light() is True
    assert rgba(128, 128, 128).is_grayscale() is True
    assert rgba(128, 128, 127).is_grayscale() is False


def test_rgba_with_alpha():
    color1 = rgba(255, 0, 0)
    color_alpha = color1.with_alpha(0.5)
    assert math.isclose(color_alpha.alpha, 0.5)
    with pytest.raises(ValueError):
        color1.with_alpha(1.5)


def test_rgba_complementary():
    color1 = rgba(255, 0, 0)
    comp = color1.complementary()
    assert comp.to_hsla().hue == 180


def test_rgb_to_hsl_internal():
    # specifically trigger branching in _rgb_to_hsl
    # max_c == min_c
    assert rgba._rgb_to_hsl(128, 128, 128) == (0, 0, 50)
    # max_c == red_norm
    assert rgba._rgb_to_hsl(255, 0, 0) == (0, 100, 50)
    # max_c == green_norm
    assert rgba._rgb_to_hsl(0, 255, 0) == (120, 100, 50)
    # max_c == blue_norm
    assert rgba._rgb_to_hsl(0, 0, 255) == (240, 100, 50)
    # max_c == red_norm, green < blue
    assert rgba._rgb_to_hsl(255, 0, 128) == (330, 100, 50)
