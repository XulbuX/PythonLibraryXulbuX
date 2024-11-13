from XulbuX import rgba, hexa, hsla
import pytest


clr_rgba = (255, 0, 0, 0.5)
clr_hexa = "#FF00007F"
clr_hsla = (0, 100, 50, 0.5)


def test_rgba_instances():
    assert isinstance(rgba(*clr_rgba), rgba)
    assert isinstance(rgba(*clr_rgba).to_hsla(), hsla)
    assert isinstance(rgba(*clr_rgba).to_hexa(), hexa)
    assert isinstance(rgba(*clr_rgba).has_alpha(), bool)
    assert isinstance(rgba(*clr_rgba).lighten(0.5), rgba)
    assert isinstance(rgba(*clr_rgba).darken(0.5), rgba)
    assert isinstance(rgba(*clr_rgba).saturate(0.5), rgba)
    assert isinstance(rgba(*clr_rgba).desaturate(0.5), rgba)
    assert isinstance(rgba(*clr_rgba).rotate(90), rgba)
    assert isinstance(rgba(*clr_rgba).rotate(-90), rgba)
    assert isinstance(rgba(*clr_rgba).invert(), rgba)
    assert isinstance(rgba(*clr_rgba).grayscale(), rgba)
    assert isinstance(rgba(*clr_rgba).blend((0, 255, 0)), rgba)
    assert isinstance(rgba(*clr_rgba).is_dark(), bool)
    assert isinstance(rgba(*clr_rgba).is_light(), bool)
    assert isinstance(rgba(*clr_rgba).is_grayscale(), bool)
    assert isinstance(rgba(*clr_rgba).is_opaque(), bool)
    assert isinstance(rgba(*clr_rgba).with_alpha(0.5), rgba)
    assert isinstance(rgba(*clr_rgba).complementary(), rgba)


def test_hsla_instances():
    assert isinstance(hsla(*clr_hsla), hsla)
    assert isinstance(hsla(*clr_hsla).to_rgba(), rgba)
    assert isinstance(hsla(*clr_hsla).to_hexa(), hexa)
    assert isinstance(hsla(*clr_hsla).has_alpha(), bool)
    assert isinstance(hsla(*clr_hsla).lighten(0.5), hsla)
    assert isinstance(hsla(*clr_hsla).darken(0.5), hsla)
    assert isinstance(hsla(*clr_hsla).saturate(0.5), hsla)
    assert isinstance(hsla(*clr_hsla).desaturate(0.5), hsla)
    assert isinstance(hsla(*clr_hsla).rotate(90), hsla)
    assert isinstance(hsla(*clr_hsla).rotate(-90), hsla)
    assert isinstance(hsla(*clr_hsla).invert(), hsla)
    assert isinstance(hsla(*clr_hsla).grayscale(), hsla)
    assert isinstance(hsla(*clr_hsla).blend((120, 100, 50)), hsla)
    assert isinstance(hsla(*clr_hsla).is_dark(), bool)
    assert isinstance(hsla(*clr_hsla).is_light(), bool)
    assert isinstance(hsla(*clr_hsla).is_grayscale(), bool)
    assert isinstance(hsla(*clr_hsla).is_opaque(), bool)
    assert isinstance(hsla(*clr_hsla).with_alpha(0.5), hsla)
    assert isinstance(hsla(*clr_hsla).complementary(), hsla)


def test_hexa_instances():
    assert isinstance(hexa(clr_hexa), hexa)
    assert isinstance(hexa(clr_hexa).to_rgba(), rgba)
    assert isinstance(hexa(clr_hexa).to_hsla(), hsla)
    assert isinstance(hexa(clr_hexa).has_alpha(), bool)
    assert isinstance(hexa(clr_hexa).lighten(0.5), hexa)
    assert isinstance(hexa(clr_hexa).darken(0.5), hexa)
    assert isinstance(hexa(clr_hexa).saturate(0.5), hexa)
    assert isinstance(hexa(clr_hexa).desaturate(0.5), hexa)
    assert isinstance(hexa(clr_hexa).rotate(90), hexa)
    assert isinstance(hexa(clr_hexa).rotate(-90), hexa)
    assert isinstance(hexa(clr_hexa).invert(), hexa)
    assert isinstance(hexa(clr_hexa).grayscale(), hexa)
    assert isinstance(hexa(clr_hexa).blend("#0F0"), hexa)
    assert isinstance(hexa(clr_hexa).is_dark(), bool)
    assert isinstance(hexa(clr_hexa).is_light(), bool)
    assert isinstance(hexa(clr_hexa).is_grayscale(), bool)
    assert isinstance(hexa(clr_hexa).is_opaque(), bool)
    assert isinstance(hexa(clr_hexa).with_alpha(0.5), hexa)
    assert isinstance(hexa(clr_hexa).complementary(), hexa)


# ! DONT'T CHANGE VALUES ! #
clr_rgba = (255, 0, 0, 0.5)
clr_hexa = "#FF00007F"
clr_hsla = (0, 100, 50, 0.5)


def assert_rgba_equal(actual: rgba, expected: tuple):
    assert isinstance(actual, rgba)
    assert actual[0] == expected[0]
    assert actual[1] == expected[1]
    assert actual[2] == expected[2]
    assert actual[3] == expected[3]


def assert_hsla_equal(actual: hsla, expected: tuple):
    assert isinstance(actual, hsla)
    assert actual[0] == expected[0]
    assert actual[1] == expected[1]
    assert actual[2] == expected[2]
    assert actual[3] == expected[3]


def assert_hexa_equal(actual: hexa, expected: str):
    assert isinstance(actual, hexa)
    assert str(actual) == expected


def test_rgba_return_values():
    rgba_instance = rgba(*clr_rgba)
    assert_hsla_equal(rgba_instance.to_hsla(), (0, 100, 50, 0.5))
    assert_hexa_equal(rgba_instance.to_hexa(), "#FF00007F")
    assert rgba_instance.has_alpha() is True
    assert_rgba_equal(rgba_instance.lighten(0.5), (255, 128, 128, 0.5))
    assert_rgba_equal(rgba_instance.darken(0.5), (128, 0, 0, 0.5))
    assert_rgba_equal(rgba_instance.saturate(0.5), (255, 0, 0, 0.5))
    assert_rgba_equal(rgba_instance.desaturate(0.5), (191, 64, 64, 0.5))
    assert_rgba_equal(rgba_instance.rotate(90), (128, 255, 0, 0.5))
    assert_rgba_equal(rgba_instance.rotate(-90), (127, 0, 255, 0.5))
    assert_rgba_equal(rgba_instance.invert(), (0, 255, 255, 0.5))
    assert_rgba_equal(rgba_instance.grayscale(), (54, 54, 54, 0.5))
    assert_rgba_equal(rgba_instance.blend((0, 255, 0)), (255, 255, 0, 0.75))
    assert rgba_instance.is_dark() is True
    assert rgba_instance.is_light() is False
    assert rgba_instance.is_grayscale() is False
    assert rgba_instance.is_opaque() is False
    assert_rgba_equal(rgba_instance.with_alpha(0.75), (255, 0, 0, 0.75))
    assert_rgba_equal(rgba_instance.complementary(), (0, 255, 255, 0.5))


def test_hsla_return_values():
    hsla_instance = hsla(*clr_hsla)
    assert_rgba_equal(hsla_instance.to_rgba(), (255, 0, 0, 0.5))
    assert_hexa_equal(hsla_instance.to_hexa(), "#FF00007F")
    assert hsla_instance.has_alpha() is True
    assert_hsla_equal(hsla_instance.lighten(0.5), (0, 100, 75, 0.5))
    assert_hsla_equal(hsla_instance.darken(0.5), (0, 100, 25, 0.5))
    assert_hsla_equal(hsla_instance.saturate(0.5), (0, 100, 50, 0.5))
    assert_hsla_equal(hsla_instance.desaturate(0.5), (0, 50, 50, 0.5))
    assert_hsla_equal(hsla_instance.rotate(90), (90, 100, 50, 0.5))
    assert_hsla_equal(hsla_instance.rotate(-90), (270, 100, 50, 0.5))
    assert_hsla_equal(hsla_instance.invert(), (180, 100, 50, 0.5))
    assert_hsla_equal(hsla_instance.grayscale(), (0, 0, 21, 0.5))
    assert_hsla_equal(hsla_instance.blend((120, 100, 50)), (60, 100, 50, 0.75))
    assert hsla_instance.is_dark() is False
    assert hsla_instance.is_light() is True
    assert hsla_instance.is_grayscale() is False
    assert hsla_instance.is_opaque() is False
    assert_hsla_equal(hsla_instance.with_alpha(0.75), (0, 100, 50, 0.75))
    assert_hsla_equal(hsla_instance.complementary(), (180, 100, 50, 0.5))


def test_hexa_return_values():
    hexa_instance = hexa(clr_hexa)
    assert_rgba_equal(hexa_instance.to_rgba(), (255, 0, 0, 0.5))
    assert_hsla_equal(hexa_instance.to_hsla(), (0, 100, 50, 0.5))
    assert hexa_instance.has_alpha() is True
    assert_hexa_equal(hexa_instance.lighten(0.5), "#FF80807F")
    assert_hexa_equal(hexa_instance.darken(0.5), "#8000007F")
    assert_hexa_equal(hexa_instance.saturate(0.5), "#FF00007F")
    assert_hexa_equal(hexa_instance.desaturate(0.5), "#BF40407F")
    assert_hexa_equal(hexa_instance.rotate(90), "#80FF007F")
    assert_hexa_equal(hexa_instance.rotate(-90), "#7F00FF7F")
    assert_hexa_equal(hexa_instance.invert(), "#00FFFF7F")
    assert_hexa_equal(hexa_instance.grayscale(), "#3636367F")
    assert_hexa_equal(hexa_instance.blend("#00FF00"), "#FFFF00BF")
    assert hexa_instance.is_dark() is False
    assert hexa_instance.is_light() is True
    assert hexa_instance.is_grayscale() is False
    assert hexa_instance.is_opaque() is False
    assert_hexa_equal(hexa_instance.with_alpha(0.75), "#FF0000BF")
    assert_hexa_equal(hexa_instance.complementary(), "#00FFFF7F")
