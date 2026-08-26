from xulbux.color import hsla
import pytest


def test_hsla_init():
    c = hsla(180, 50, 50, 0.5)
    assert c.hue == 180
    assert c.sat == 50
    assert c.light == 50
    assert c.alpha == 0.5

    c2 = hsla(180, 50, 50)
    assert c2.alpha is None

    c3 = hsla(400, 200, 200, 2.0, _validate=False)
    assert c3.hue == 400

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

    c2 = hsla(180, 50, 50, 0.5)
    assert c2[3] == 0.5
    assert c2[-1] == 0.5
    assert c2[-4] == 180

    with pytest.raises(IndexError):
        c1[3]
    with pytest.raises(IndexError):
        c2[4]


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
    c = hsla(0, 100, 50, 0.5)
    rgba_c = c.to_rgba()
    assert rgba_c.red == 255
    assert rgba_c.alpha == 0.5

    hexa_c = c.to_hexa()
    assert hexa_c.red == 255
    assert hexa_c.alpha == 0.5


def test_hsla_lighten_darken():
    c = hsla(0, 0, 50)
    l = c.lighten(0.5)
    assert l.light == 75
    with pytest.raises(ValueError):
        c.lighten(1.5)

    d = c.darken(0.5)
    assert d.light == 25
    with pytest.raises(ValueError):
        c.darken(-0.5)


def test_hsla_saturate_desaturate():
    c = hsla(0, 50, 50)
    s = c.saturate(0.5)
    assert s.sat == 75
    with pytest.raises(ValueError):
        c.saturate(-0.1)

    ds = c.desaturate(0.5)
    assert ds.sat == 25
    with pytest.raises(ValueError):
        c.desaturate(2.0)


def test_hsla_rotate():
    c = hsla(180, 50, 50)
    r = c.rotate(190)
    assert r.hue == 10  # (180+190)%360 = 10


def test_hsla_invert():
    c = hsla(0, 50, 20, 0.2)
    inv = c.invert()
    assert inv.hue == 180
    assert inv.light == 80
    assert inv.alpha == 0.2

    inv2 = c.invert(invert_alpha=True)
    assert inv2.alpha == 0.8


def test_hsla_grayscale():
    c = hsla(180, 50, 50)
    g = c.grayscale()
    assert g.sat == 0


def test_hsla_blend():
    c1 = hsla(0, 100, 50, 0.5)
    c2 = hsla(240, 100, 50, 0.5)
    b = c1.blend(c2, 0.5)
    # the result will be an hsla, checking if valid
    assert b.alpha is not None

    with pytest.raises(ValueError):
        c1.blend(c2, 1.5)

    with pytest.raises(TypeError):
        c1.blend("invalid", 0.5)  # type: ignore

    b3 = hsla(180, 50, 50).blend(hsla(0, 50, 50), 0.5)
    assert b3.alpha is None


def test_hsla_is_dark_light_grayscale():
    assert hsla(0, 0, 49).is_dark() is True
    assert hsla(0, 0, 50).is_light() is True
    assert hsla(0, 0, 50).is_grayscale() is True
    assert hsla(0, 1, 50).is_grayscale() is False


def test_hsla_with_alpha():
    c = hsla(0, 0, 0)
    ca = c.with_alpha(0.5)
    assert ca.alpha == 0.5
    with pytest.raises(ValueError):
        c.with_alpha(1.5)


def test_hsla_complementary():
    c = hsla(0, 50, 50)
    comp = c.complementary()
    assert comp.hue == 180


def test_hsl_to_rgb_internal():
    # specifically trigger branching in _hsl_to_rgb
    # sat_norm == 0
    assert hsla._hsl_to_rgb(180, 0, 50) == (127, 127, 127)

    # light_norm >= 0.5
    assert hsla._hsl_to_rgb(0, 100, 75) == (255, 128, 128)

    # hue > 240 to trigger hue_pos > 1 inside _hue_to_rgb for red channel (hue_norm + 1/3 > 1)
    assert hsla._hsl_to_rgb(300, 100, 50) == (255, 0, 255)

    # hue < 120 to trigger hue_pos < 0 inside _hue_to_rgb for blue channel (hue_norm - 1/3 < 0)
    assert hsla._hsl_to_rgb(60, 100, 50) == (255, 255, 0)

    # hue_pos < 0, hue_pos > 1, etc in _hue_to_rgb
    # hue_to_rgb logic branches
    # these are typically covered by various conversions above
