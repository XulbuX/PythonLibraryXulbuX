import math
from xulbux.color import hexa, rgba
import pytest


def test_hexa_init() -> None:
    color_short = hexa("F00")
    assert color_short.red == 255
    assert color_short.green == 0
    assert color_short.alpha is None

    color_short_alpha = hexa("#F008")
    assert color_short_alpha.alpha is not None

    color_full = hexa("0xFF0000")
    assert color_full.red == 255
    assert color_full.alpha is None

    color_full_alpha = hexa("#FF000080")
    assert color_full_alpha.alpha is not None

    color_int = hexa(0xFF000080)
    assert color_int.red == 255

    class CustomColorObject:
        red = 255
        green = 0
        blue = 0
        alpha = 0.5

    color_from_obj = hexa(CustomColorObject())  # type:ignore[arg-type]
    assert color_from_obj.red == 255
    assert color_from_obj.alpha is not None and math.isclose(color_from_obj.alpha, 0.5)

    with pytest.raises(ValueError, match="Invalid HEXA color string"):
        hexa("FF000")
    with pytest.raises(ValueError, match="Could initialize hexa"):
        hexa(None)

    color_kwargs = hexa(_red=255, _green=0, _blue=0, _alpha=0.5)
    assert color_kwargs.red == 255

    color_copy = hexa(color_short)
    assert color_copy.red == 255


def test_hexa_iter() -> None:
    assert list(hexa("F00")) == ["FF", "00", "00"]
    assert list(hexa("#FF000080")) == ["FF", "00", "00", "80"]


def test_hexa_getitem() -> None:
    color_opaque = hexa("F00")
    assert color_opaque[0] == "FF"
    assert color_opaque[1] == "00"
    assert color_opaque[2] == "00"
    assert color_opaque[-1] == "00"
    assert color_opaque[-2] == "00"
    assert color_opaque[-3] == "FF"

    color_alpha = hexa("#FF000080")
    assert color_alpha[3] == "80"
    assert color_alpha[-1] == "80"
    assert color_alpha[-4] == "FF"

    with pytest.raises(IndexError):
        color_opaque[3]
    with pytest.raises(IndexError):
        color_alpha[4]


def test_hexa_equality() -> None:
    assert hexa("F00") == hexa("#FF0000")
    assert hexa("F00") != hexa("#0F0")
    assert hexa("F00") != "not a color"


def test_hexa_str_and_repr() -> None:
    assert str(hexa("F00")) == "#FF0000"
    assert repr(hexa("#FF000080")) == "hexa(#FF000080)"


def test_hexa_dict() -> None:
    assert hexa("#FF000080").dict() == {"red": "FF", "green": "00", "blue": "00", "alpha": "80"}
    assert hexa("#FF0000").dict() == {"red": "FF", "green": "00", "blue": "00", "alpha": None}


def test_hexa_values() -> None:
    assert hexa("#FF000080").values() == (255, 0, 0, 0.5)
    assert hexa("#FF000080").values(round_alpha=False) != (255, 0, 0, 0.5)


def test_hexa_conversions() -> None:
    color1 = hexa("#FF000080")
    assert color1.to_hexa() is color1

    rgba_color = color1.to_rgba()
    assert isinstance(rgba_color, rgba)
    assert rgba_color.red == 255

    hsla_color = color1.to_hsla()
    assert hsla_color.hue == 0


def test_hexa_lighten_darken() -> None:
    color1 = hexa("#808080")
    lightened = color1.lighten(0.5)
    assert lightened.red > 128
    with pytest.raises(ValueError):
        color1.lighten(1.5)

    darkened = color1.darken(0.5)
    assert darkened.red < 128
    with pytest.raises(ValueError):
        color1.darken(-0.5)


def test_hexa_saturate_desaturate() -> None:
    color1 = hexa("#805050")
    saturated = color1.saturate(0.5)
    assert saturated != color1
    with pytest.raises(ValueError):
        color1.saturate(-0.1)

    desaturated = color1.desaturate(0.5)
    assert desaturated != color1
    with pytest.raises(ValueError):
        color1.desaturate(2.0)


def test_hexa_rotate() -> None:
    color1 = hexa("#FF0000")
    rotated = color1.rotate(180)
    assert rotated.to_hsla().hue == 180


def test_hexa_invert() -> None:
    color1 = hexa("#FF800033")
    inverted = color1.invert()
    assert inverted.red == 0
    assert inverted.green == 127
    assert inverted.blue == 255

    inverted_with_alpha = color1.invert(invert_alpha=True)
    assert inverted_with_alpha.alpha is not None and math.isclose(inverted_with_alpha.alpha, 0.8)


def test_hexa_grayscale() -> None:
    color1 = hexa("#FF8000")
    gray = color1.grayscale()
    assert gray.red == gray.green == gray.blue


def test_hexa_blend() -> None:
    color1 = hexa("#FF000080")
    color2 = hexa("#0000FF80")
    blended = color1.blend(color2, 0.5)
    assert isinstance(blended, hexa)

    with pytest.raises(ValueError):
        color1.blend(color2, 1.5)

    with pytest.raises(TypeError):
        color1.blend("invalid", 0.5)  # pyright:ignore[reportArgumentType]

    blended_no_alpha = hexa("#F00").blend(hexa("#00F"), 0.5)
    assert not blended_no_alpha.has_alpha()


def test_hexa_predicates() -> None:
    assert hexa("#000000").is_dark() is True
    assert hexa("#FFFFFF").is_light() is True
    assert hexa("#808080").is_grayscale() is True
    assert hexa("#80807F").is_grayscale() is False


def test_hexa_with_alpha_and_complementary() -> None:
    color1 = hexa("#FF0000")
    color_alpha = color1.with_alpha(0.5)
    assert color_alpha.alpha is not None and math.isclose(color_alpha.alpha, 0.5)
    with pytest.raises(ValueError):
        color1.with_alpha(1.5)

    complementary_color = hexa("#FF0000").complementary()
    assert complementary_color.to_hsla().hue == 180
