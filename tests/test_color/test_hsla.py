import math
from xulbux.color import hsla
import pytest


def test_hsla_init() -> None:
    color1 = hsla(180, 50, 50, 0.5)
    assert color1.hue == 180
    assert color1.sat == 50
    assert color1.light == 50
    assert color1.alpha is not None and math.isclose(color1.alpha, 0.5)

    color2 = hsla(180, 50, 50)
    assert color2.alpha is None

    color_unvalidated = hsla(400, 200, 200, 2.0, _validate=False)
    assert color_unvalidated.hue == 400

    with pytest.raises(ValueError, match=r"range \[0, 360\]"):
        hsla(-1, 50, 50)
    with pytest.raises(ValueError, match=r"range \[0, 100\]"):
        hsla(180, -1, 50)
    with pytest.raises(ValueError, match=r"range \[0\.0, 1\.0\]"):
        hsla(180, 50, 50, -0.1)
    with pytest.raises(ValueError, match=r"range \[0\.0, 1\.0\]"):
        hsla(0, 0, 0, 1.5)


def test_hsla_len_and_has_alpha() -> None:
    assert len(hsla(0, 0, 0)) == 3
    assert len(hsla(0, 0, 0, 0.5)) == 4
    assert hsla(0, 0, 0).has_alpha() is False
    assert hsla(0, 0, 0, 0.5).has_alpha() is True
    assert hsla(0, 0, 0).is_opaque() is True
    assert hsla(0, 0, 0, 0.5).is_opaque() is False


def test_hsla_iter() -> None:
    assert list(hsla(180, 50, 50)) == [180, 50, 50]
    assert list(hsla(180, 50, 50, 0.5)) == [180, 50, 50, 0.5]


def test_hsla_getitem() -> None:
    color_opaque = hsla(180, 50, 50)
    assert color_opaque[0] == 180
    assert color_opaque[1] == 50
    assert color_opaque[2] == 50
    assert color_opaque[-1] == 50
    assert color_opaque[-2] == 50
    assert color_opaque[-3] == 180

    color_alpha = hsla(180, 50, 50, 0.5)
    val3 = color_alpha[3]
    val_neg1 = color_alpha[-1]
    assert isinstance(val3, (int, float)) and math.isclose(val3, 0.5)
    assert isinstance(val_neg1, (int, float)) and math.isclose(val_neg1, 0.5)
    assert color_alpha[-4] == 180

    with pytest.raises(IndexError):
        color_opaque[3]
    with pytest.raises(IndexError):
        color_alpha[4]


def test_hsla_equality() -> None:
    assert hsla(180, 50, 50, 0.5) == hsla(180, 50, 50, 0.5)
    assert hsla(180, 50, 50) != hsla(180, 50, 50, 0.5)
    assert hsla(180, 50, 50) != "not a color"


def test_hsla_str_and_repr() -> None:
    assert str(hsla(180, 50, 50)) == "hsla(180°, 50%, 50%)"
    assert repr(hsla(180, 50, 50, 0.5)) == "hsla(180°, 50%, 50%, 0.5)"


def test_hsla_dict_and_values() -> None:
    assert hsla(180, 50, 50, 0.5).dict() == {"hue": 180, "sat": 50, "light": 50, "alpha": 0.5}
    assert hsla(180, 50, 50, 0.5).values() == (180, 50, 50, 0.5)


def test_hsla_conversions() -> None:
    color1 = hsla(0, 100, 50, 0.5)
    assert color1.to_hsla() is color1

    rgba_color = color1.to_rgba()
    assert rgba_color.red == 255
    assert rgba_color.alpha is not None and math.isclose(rgba_color.alpha, 0.5)

    hexa_color = color1.to_hexa()
    assert hexa_color.red == 255
    assert hexa_color.alpha is not None and math.isclose(hexa_color.alpha, 0.5)


def test_hsla_lighten_darken() -> None:
    color1 = hsla(0, 0, 50)
    lightened = color1.lighten(0.5)
    assert lightened.light == 75
    with pytest.raises(ValueError):
        color1.lighten(1.5)

    darkened = color1.darken(0.5)
    assert darkened.light == 25
    with pytest.raises(ValueError):
        color1.darken(-0.5)


def test_hsla_saturate_desaturate() -> None:
    color1 = hsla(0, 50, 50)
    saturated = color1.saturate(0.5)
    assert saturated.sat == 75
    with pytest.raises(ValueError):
        color1.saturate(-0.1)

    desaturated = color1.desaturate(0.5)
    assert desaturated.sat == 25
    with pytest.raises(ValueError):
        color1.desaturate(2.0)


def test_hsla_rotate() -> None:
    color1 = hsla(180, 50, 50)
    rotated = color1.rotate(190)
    assert rotated.hue == 10


def test_hsla_invert() -> None:
    color1 = hsla(0, 50, 20, 0.2)
    inverted = color1.invert()
    assert inverted.hue == 180
    assert inverted.light == 80
    assert inverted.alpha is not None and math.isclose(inverted.alpha, 0.2)

    inverted_with_alpha = color1.invert(invert_alpha=True)
    assert inverted_with_alpha.alpha is not None and math.isclose(inverted_with_alpha.alpha, 0.8)


def test_hsla_grayscale() -> None:
    color1 = hsla(180, 50, 50)
    gray = color1.grayscale()
    assert gray.sat == 0


def test_hsla_blend() -> None:
    color1 = hsla(0, 100, 50, 0.5)
    color2 = hsla(240, 100, 50, 0.5)
    blended = color1.blend(color2, 0.5)
    assert blended.alpha is not None

    with pytest.raises(ValueError):
        color1.blend(color2, 1.5)

    with pytest.raises(TypeError):
        color1.blend("invalid", 0.5)  # pyright:ignore[reportArgumentType]

    blended_no_alpha = hsla(180, 50, 50).blend(hsla(0, 50, 50), 0.5)
    assert blended_no_alpha.alpha is None


def test_hsla_predicates() -> None:
    assert hsla(0, 0, 49).is_dark() is True
    assert hsla(0, 0, 50).is_light() is True
    assert hsla(0, 0, 50).is_grayscale() is True
    assert hsla(0, 1, 50).is_grayscale() is False


def test_hsla_with_alpha_and_complementary() -> None:
    color1 = hsla(0, 0, 0)
    color_alpha = color1.with_alpha(0.5)
    assert color_alpha.alpha is not None and math.isclose(color_alpha.alpha, 0.5)
    with pytest.raises(ValueError):
        color1.with_alpha(1.5)

    complementary_color = hsla(0, 50, 50).complementary()
    assert complementary_color.hue == 180


def test_hsl_to_rgb_branching() -> None:
    assert hsla._hsl_to_rgb(180, 0, 50) == (127, 127, 127)
    assert hsla._hsl_to_rgb(0, 100, 75) == (255, 128, 128)
    assert hsla._hsl_to_rgb(300, 100, 50) == (255, 0, 255)
    assert hsla._hsl_to_rgb(60, 100, 50) == (255, 255, 0)
