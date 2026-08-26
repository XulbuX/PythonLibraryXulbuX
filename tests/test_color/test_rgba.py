import math
from xulbux.color import rgba
import pytest


def test_rgba_init():
    color1 = rgba(255, 128, 0, 0.5)
    assert color1.red == 255
    assert color1.green == 128
    assert color1.blue == 0
    assert color1.alpha is not None and math.isclose(color1.alpha, 0.5)

    color2 = rgba(255, 128, 0)
    assert color2.alpha is None

    color_unvalidated = rgba(300, 300, 300, 2.0, _validate=False)
    assert color_unvalidated.red == 300
    assert color_unvalidated.alpha is not None and math.isclose(color_unvalidated.alpha, 2.0)

    with pytest.raises(ValueError, match="must be integers in range"):
        rgba(-1, 0, 0)
    with pytest.raises(ValueError, match="must be integers in range"):
        rgba(0, 256, 0)

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
    color_opaque = rgba(255, 128, 0)
    assert color_opaque[0] == 255
    assert color_opaque[1] == 128
    assert color_opaque[2] == 0
    assert color_opaque[-1] == 0
    assert color_opaque[-2] == 128
    assert color_opaque[-3] == 255

    color_alpha = rgba(255, 128, 0, 0.5)
    val3 = color_alpha[3]
    val_neg1 = color_alpha[-1]
    assert isinstance(val3, (int, float)) and math.isclose(val3, 0.5)
    assert isinstance(val_neg1, (int, float)) and math.isclose(val_neg1, 0.5)
    assert color_alpha[-4] == 255

    with pytest.raises(IndexError):
        color_opaque[3]
    with pytest.raises(IndexError):
        color_alpha[4]


def test_rgba_equality():
    assert rgba(255, 128, 0, 0.5) == rgba(255, 128, 0, 0.5)
    assert rgba(255, 128, 0) != rgba(255, 128, 0, 0.5)
    assert rgba(255, 128, 0) != "not a color"


def test_rgba_str_and_repr():
    assert str(rgba(255, 128, 0)) == "rgba(255, 128, 0)"
    assert repr(rgba(255, 128, 0, 0.5)) == "rgba(255, 128, 0, 0.5)"


def test_rgba_dict_and_values():
    assert rgba(255, 128, 0, 0.5).dict() == {"red": 255, "green": 128, "blue": 0, "alpha": 0.5}
    assert rgba(255, 128, 0, 0.5).values() == (255, 128, 0, 0.5)


def test_rgba_conversions():
    color1 = rgba(255, 0, 0, 0.5)
    hsla_color = color1.to_hsla()
    assert hsla_color.hue == 0
    assert hsla_color.sat == 100
    assert hsla_color.light == 50
    assert hsla_color.alpha is not None and math.isclose(hsla_color.alpha, 0.5)

    hexa_color = color1.to_hexa()
    assert hexa_color.red == 255
    assert hexa_color.alpha is not None and math.isclose(hexa_color.alpha, 0.5)


def test_rgba_lighten_darken():
    color1 = rgba(128, 128, 128)
    lightened = color1.lighten(0.5)
    assert lightened.red > 128
    with pytest.raises(ValueError):
        color1.lighten(1.5)

    darkened = color1.darken(0.5)
    assert darkened.red < 128
    with pytest.raises(ValueError):
        color1.darken(-0.5)


def test_rgba_saturate_desaturate():
    color1 = rgba(128, 100, 100)
    saturated = color1.saturate(0.5)
    assert saturated.to_hsla().sat > color1.to_hsla().sat
    with pytest.raises(ValueError):
        color1.saturate(-0.1)

    desaturated = color1.desaturate(0.5)
    assert desaturated.to_hsla().sat < color1.to_hsla().sat
    with pytest.raises(ValueError):
        color1.desaturate(2.0)


def test_rgba_rotate():
    color1 = rgba(255, 0, 0)
    rotated = color1.rotate(180)
    assert rotated.to_hsla().hue == 180


def test_rgba_invert():
    color1 = rgba(255, 128, 0, 0.2)
    inverted = color1.invert()
    assert inverted.red == 0
    assert inverted.green == 127
    assert inverted.blue == 255
    assert inverted.alpha is not None and math.isclose(inverted.alpha, 0.2)

    inverted_with_alpha = color1.invert(invert_alpha=True)
    assert inverted_with_alpha.alpha is not None and math.isclose(inverted_with_alpha.alpha, 0.8)


def test_rgba_grayscale():
    color1 = rgba(255, 128, 0)
    grayscale_color = color1.grayscale()
    assert grayscale_color.red == grayscale_color.green == grayscale_color.blue


def test_rgba_blend():
    color_red = rgba(255, 0, 0, 0.5)
    color_blue = rgba(0, 0, 255, 0.5)
    blended = color_red.blend(color_blue, 0.5)
    assert blended.red == 128
    assert blended.blue == 128
    assert blended.green == 0

    with pytest.raises(ValueError):
        color_red.blend(color_blue, 1.5)

    with pytest.raises(TypeError):
        color_red.blend("invalid", 0.5)  # pyright:ignore[reportArgumentType]

    blended_additive = color_red.blend(color_blue, 0.5, additive_alpha=True)
    assert blended_additive.alpha is not None and math.isclose(blended_additive.alpha, 1.0)

    blended_no_alpha = rgba(255, 0, 0).blend(rgba(0, 0, 255), 0.5)
    assert blended_no_alpha.alpha is None


def test_rgba_predicates():
    assert rgba(0, 0, 0).is_dark() is True
    assert rgba(255, 255, 255).is_light() is True
    assert rgba(128, 128, 128).is_grayscale() is True
    assert rgba(128, 128, 127).is_grayscale() is False


def test_rgba_with_alpha_and_complementary():
    color1 = rgba(255, 0, 0)
    color_alpha = color1.with_alpha(0.5)
    assert color_alpha.alpha is not None and math.isclose(color_alpha.alpha, 0.5)
    with pytest.raises(ValueError):
        color1.with_alpha(1.5)

    complementary_color = color1.complementary()
    assert complementary_color.to_hsla().hue == 180


def test_rgb_to_hsl_branching():
    assert rgba._rgb_to_hsl(128, 128, 128) == (0, 0, 50)
    assert rgba._rgb_to_hsl(255, 0, 0) == (0, 100, 50)
    assert rgba._rgb_to_hsl(0, 255, 0) == (120, 100, 50)
    assert rgba._rgb_to_hsl(0, 0, 255) == (240, 100, 50)
    assert rgba._rgb_to_hsl(255, 0, 128) == (330, 100, 50)
