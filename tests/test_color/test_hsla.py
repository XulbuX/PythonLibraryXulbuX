import math
from xulbux.color import hsla
import pytest


def test_hsla_init():
    color1 = hsla(180, 50, 50, 0.5)
    assert color1.hue == 180
    assert color1.sat == 50
    assert color1.light == 50
    assert math.isclose(color1.alpha, 0.5)  # pyright:ignore[reportArgumentType]

    color2 = hsla(180, 50, 50)
    assert color2.alpha is None

    color3 = hsla(400, 200, 200, 2.0, _validate=False)
    assert color3.hue == 400

    with pytest.raises(ValueError, match=r"range \[0, 360\]"):
        hsla(-1, 50, 50)
    with pytest.raises(ValueError, match=r"range \[0, 100\]"):
        hsla(180, -1, 50)
    with pytest.raises(ValueError, match=r"range \[0\.0, 1\.0\]"):
        hsla(180, 50, 50, -0.1)
    with pytest.raises(ValueError, match=r"range \[0\.0, 1\.0\]"):
        hsla(0, 0, 0, 1.5)


def test_hsla_len_and_has_alpha():
    assert len(hsla(0, 0, 0)) == 3
    assert len(hsla(0, 0, 0, 0.5)) == 4
    assert hsla(0, 0, 0).has_alpha() is False
    assert hsla(0, 0, 0, 0.5).has_alpha() is True
    assert hsla(0, 0, 0).is_opaque() is True
    assert hsla(0, 0, 0, 0.5).is_opaque() is False


def test_hsla_iter():
    assert list(hsla(180, 50, 50)) == [180, 50, 50]
    assert list(hsla(180, 50, 50, 0.5)) == [180, 50, 50, 0.5]


def test_hsla_getitem():
    c1 = hsla(180, 50, 50)
    assert c1[0] == 180
    assert c1[1] == 50
    assert c1[2] == 50
    assert c1[-1] == 50
    assert c1[-2] == 50
    assert c1[-3] == 180

    color2 = hsla(180, 50, 50, 0.5)
    assert math.isclose(color2[3], 0.5)  # pyright:ignore[reportArgumentType]
    assert math.isclose(color2[-1], 0.5)  # pyright:ignore[reportArgumentType]
    assert color2[-4] == 180

    with pytest.raises(IndexError):
        c1[3]
    with pytest.raises(IndexError):
        color2[4]


def test_hsla_eq():
    assert hsla(180, 50, 50, 0.5) == hsla(180, 50, 50, 0.5)
    assert hsla(180, 50, 50) != hsla(180, 50, 50, 0.5)
    assert hsla(180, 50, 50) != "not a color"


def test_hsla_str_repr():
    assert str(hsla(180, 50, 50)) == "hsla(180°, 50%, 50%)"
    assert repr(hsla(180, 50, 50, 0.5)) == "hsla(180°, 50%, 50%, 0.5)"


def test_hsla_dict():
    assert hsla(180, 50, 50, 0.5).dict() == {"hue": 180, "sat": 50, "light": 50, "alpha": 0.5}


def test_hsla_values():
    assert hsla(180, 50, 50, 0.5).values() == (180, 50, 50, 0.5)


def test_hsla_conversions():
    color1 = hsla(0, 100, 50, 0.5)
    rgba_c = color1.to_rgba()
    assert rgba_c.red == 255
    assert math.isclose(rgba_c.alpha, 0.5)  # pyright:ignore[reportArgumentType]

    hexa_c = color1.to_hexa()
    assert hexa_c.red == 255
    assert math.isclose(hexa_c.alpha, 0.5)  # pyright:ignore[reportArgumentType]


def test_hsla_lighten_darken():
    color1 = hsla(0, 0, 50)
    lightened1 = color1.lighten(0.5)
    assert lightened1.light == 75
    with pytest.raises(ValueError):
        color1.lighten(1.5)

    darkened1 = color1.darken(0.5)
    assert darkened1.light == 25
    with pytest.raises(ValueError):
        color1.darken(-0.5)


def test_hsla_saturate_desaturate():
    color1 = hsla(0, 50, 50)
    saturated1 = color1.saturate(0.5)
    assert saturated1.sat == 75
    with pytest.raises(ValueError):
        color1.saturate(-0.1)

    ds = color1.desaturate(0.5)
    assert ds.sat == 25
    with pytest.raises(ValueError):
        color1.desaturate(2.0)


def test_hsla_rotate():
    color1 = hsla(180, 50, 50)
    rotated1 = color1.rotate(190)
    assert rotated1.hue == 10  # (180+190)%360 = 10.


def test_hsla_invert():
    color1 = hsla(0, 50, 20, 0.2)
    inv1 = color1.invert()
    assert inv1.hue == 180
    assert inv1.light == 80
    assert math.isclose(inv1.alpha, 0.2)  # pyright:ignore[reportArgumentType]

    inv2 = color1.invert(invert_alpha=True)
    assert math.isclose(inv2.alpha, 0.8)  # pyright:ignore[reportArgumentType]


def test_hsla_grayscale():
    color1 = hsla(180, 50, 50)
    gray1 = color1.grayscale()
    assert gray1.sat == 0


def test_hsla_blend():
    c1 = hsla(0, 100, 50, 0.5)
    color2 = hsla(240, 100, 50, 0.5)
    blend1 = c1.blend(color2, 0.5)
    # the result will be an hsla, checking if valid:
    assert blend1.alpha is not None

    with pytest.raises(ValueError):
        c1.blend(color2, 1.5)

    with pytest.raises(TypeError):
        c1.blend("invalid", 0.5)

    b3 = hsla(180, 50, 50).blend(hsla(0, 50, 50), 0.5)
    assert b3.alpha is None


def test_hsla_is_dark_light_grayscale():
    assert hsla(0, 0, 49).is_dark() is True
    assert hsla(0, 0, 50).is_light() is True
    assert hsla(0, 0, 50).is_grayscale() is True
    assert hsla(0, 1, 50).is_grayscale() is False


def test_hsla_with_alpha():
    color1 = hsla(0, 0, 0)
    color_alpha = color1.with_alpha(0.5)
    assert math.isclose(color_alpha.alpha, 0.5)  # pyright:ignore[reportArgumentType]
    with pytest.raises(ValueError):
        color1.with_alpha(1.5)


def test_hsla_complementary():
    color1 = hsla(0, 50, 50)
    comp = color1.complementary()
    assert comp.hue == 180


def test_hsl_to_rgb_internal():
    # specifically trigger branching in _hsl_to_rgb.
    # sat_norm == 0:
    assert hsla._hsl_to_rgb(180, 0, 50) == (127, 127, 127)

    # light_norm >= 0.5:
    assert hsla._hsl_to_rgb(0, 100, 75) == (255, 128, 128)

    # hue > 240 to trigger hue_pos > 1 inside _hue_to_rgb for red channel (hue_norm + 1/3 > 1):
    assert hsla._hsl_to_rgb(300, 100, 50) == (255, 0, 255)

    # hue < 120 to trigger hue_pos < 0 inside _hue_to_rgb for blue channel (hue_norm - 1/3 < 0):
    assert hsla._hsl_to_rgb(60, 100, 50) == (255, 255, 0)

    # hue_pos < 0, hue_pos > 1, etc in _hue_to_rgb.
    # hue_to_rgb logic branches.
    # these are typically covered by various conversions above:
