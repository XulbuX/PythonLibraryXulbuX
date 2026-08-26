from xulbux.color import hexa, rgba
import pytest


def test_hexa_init():
    # RGB string
    c1 = hexa("F00")
    assert c1.red == 255
    assert c1.green == 0
    assert c1.alpha is None

    # RGBA string
    c2 = hexa("#F008")
    assert c2.alpha is not None

    # RRGGBB string
    c3 = hexa("0xFF0000")
    assert c3.red == 255
    assert c3.alpha is None

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

    c6 = hexa(MockColor())
    assert c6.red == 255
    assert c6.alpha == 0.5

    # invalid strings
    with pytest.raises(ValueError, match="Invalid HEXA color string"):
        hexa("FF000")
    with pytest.raises(ValueError, match="Could initialize hexa"):
        hexa(None)  # type: ignore

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

    c2 = hexa("#FF000080")
    assert c2[3] == "80"
    assert c2[-1] == "80"
    assert c2[-4] == "FF"

    with pytest.raises(IndexError):
        c1[3]
    with pytest.raises(IndexError):
        c2[4]


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
    c = hexa("#FF000080")
    rgba_c = c.to_rgba()
    assert isinstance(rgba_c, rgba)
    assert rgba_c.red == 255

    hsla_c = c.to_hsla()
    assert hsla_c.hue == 0


def test_hexa_lighten_darken():
    c = hexa("#808080")
    l = c.lighten(0.5)
    assert l.red > 128
    with pytest.raises(ValueError):
        c.lighten(1.5)

    d = c.darken(0.5)
    assert d.red < 128
    with pytest.raises(ValueError):
        c.darken(-0.5)


def test_hexa_saturate_desaturate():
    c = hexa("#805050")
    s = c.saturate(0.5)
    assert s != c
    with pytest.raises(ValueError):
        c.saturate(-0.1)

    ds = c.desaturate(0.5)
    assert ds != c
    with pytest.raises(ValueError):
        c.desaturate(2.0)


def test_hexa_rotate():
    c = hexa("#FF0000")
    r = c.rotate(180)
    assert r.to_hsla().hue == 180


def test_hexa_invert():
    c = hexa("#FF800033")  # alpha 0.2
    inv = c.invert()
    assert inv.red == 0
    assert inv.green == 127
    assert inv.blue == 255

    inv2 = c.invert(invert_alpha=True)
    assert inv2.alpha == 0.8


def test_hexa_grayscale():
    c = hexa("#FF8000")
    g = c.grayscale()
    assert g.red == g.green == g.blue


def test_hexa_blend():
    c1 = hexa("#FF000080")
    c2 = hexa("#0000FF80")
    b = c1.blend(c2, 0.5)
    assert isinstance(b, hexa)

    with pytest.raises(ValueError):
        c1.blend(c2, 1.5)

    with pytest.raises(TypeError):
        c1.blend("invalid", 0.5)  # type: ignore

    b3 = hexa("#F00").blend(hexa("#00F"), 0.5)
    assert not b3.has_alpha()


def test_hexa_is_dark_light_grayscale():
    assert hexa("#000000").is_dark() is True
    assert hexa("#FFFFFF").is_light() is True
    assert hexa("#808080").is_grayscale() is True
    assert hexa("#80807F").is_grayscale() is False


def test_hexa_with_alpha():
    c = hexa("#FF0000")
    ca = c.with_alpha(0.5)
    assert ca.alpha == 0.5
    with pytest.raises(ValueError):
        c.with_alpha(1.5)


def test_hexa_complementary():
    c = hexa("#FF0000")
    comp = c.complementary()
    assert comp.to_hsla().hue == 180
