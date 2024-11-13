from XulbuX import rgba, hexa, hsla


# ! DONT'T CHANGE VALUES ! #
clr_rgba = (255, 0, 0, 0.5)
clr_hexa = "#FF00007F"
clr_hsla = (0, 100, 50, 0.5)


####################### FUNCTIONS FOR CHECKING CUSTOM TYPE VALUES #######################


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


######################################## TESTING ########################################


def test_rgba_return_values():
    assert_rgba_equal(rgba(*clr_rgba), clr_rgba)
    assert_hsla_equal(rgba(*clr_rgba).to_hsla(), (0, 100, 50, 0.5))
    assert_hexa_equal(rgba(*clr_rgba).to_hexa(), "#FF00007F")
    assert rgba(*clr_rgba).has_alpha() is True
    assert_rgba_equal(rgba(*clr_rgba).lighten(0.5), (255, 128, 128, 0.5))
    assert_rgba_equal(rgba(*clr_rgba).darken(0.5), (128, 0, 0, 0.5))
    assert_rgba_equal(rgba(*clr_rgba).saturate(0.5), (255, 0, 0, 0.5))
    assert_rgba_equal(rgba(*clr_rgba).desaturate(0.5), (191, 64, 64, 0.5))
    assert_rgba_equal(rgba(*clr_rgba).rotate(90), (128, 255, 0, 0.5))
    assert_rgba_equal(rgba(*clr_rgba).rotate(-90), (127, 0, 255, 0.5))
    assert_rgba_equal(rgba(*clr_rgba).invert(), (0, 255, 255, 0.5))
    assert_rgba_equal(rgba(*clr_rgba).grayscale(), (54, 54, 54, 0.5))
    assert_rgba_equal(rgba(*clr_rgba).blend((0, 255, 0)), (255, 255, 0, 0.75))
    assert rgba(*clr_rgba).is_dark() is True
    assert rgba(*clr_rgba).is_light() is False
    assert rgba(*clr_rgba).is_grayscale() is False
    assert rgba(*clr_rgba).is_opaque() is False
    assert_rgba_equal(rgba(*clr_rgba).with_alpha(0.75), (255, 0, 0, 0.75))
    assert_rgba_equal(rgba(*clr_rgba).complementary(), (0, 255, 255, 0.5))


def test_hsla_return_values():
    assert_hsla_equal(hsla(*clr_hsla), clr_hsla)
    assert_rgba_equal(hsla(*clr_hsla).to_rgba(), (255, 0, 0, 0.5))
    assert_hexa_equal(hsla(*clr_hsla).to_hexa(), "#FF00007F")
    assert hsla(*clr_hsla).has_alpha() is True
    assert_hsla_equal(hsla(*clr_hsla).lighten(0.5), (0, 100, 75, 0.5))
    assert_hsla_equal(hsla(*clr_hsla).darken(0.5), (0, 100, 25, 0.5))
    assert_hsla_equal(hsla(*clr_hsla).saturate(0.5), (0, 100, 50, 0.5))
    assert_hsla_equal(hsla(*clr_hsla).desaturate(0.5), (0, 50, 50, 0.5))
    assert_hsla_equal(hsla(*clr_hsla).rotate(90), (90, 100, 50, 0.5))
    assert_hsla_equal(hsla(*clr_hsla).rotate(-90), (270, 100, 50, 0.5))
    assert_hsla_equal(hsla(*clr_hsla).invert(), (180, 100, 50, 0.5))
    assert_hsla_equal(hsla(*clr_hsla).grayscale(), (0, 0, 21, 0.5))
    assert_hsla_equal(hsla(*clr_hsla).blend((120, 100, 50)), (60, 100, 50, 0.75))
    assert hsla(*clr_hsla).is_dark() is False
    assert hsla(*clr_hsla).is_light() is True
    assert hsla(*clr_hsla).is_grayscale() is False
    assert hsla(*clr_hsla).is_opaque() is False
    assert_hsla_equal(hsla(*clr_hsla).with_alpha(0.75), (0, 100, 50, 0.75))
    assert_hsla_equal(hsla(*clr_hsla).complementary(), (180, 100, 50, 0.5))


def test_hexa_return_values():
    assert_hexa_equal(hexa(clr_hexa), clr_hexa)
    assert_rgba_equal(hexa(clr_hexa).to_rgba(), (255, 0, 0, 0.5))
    assert_hsla_equal(hexa(clr_hexa).to_hsla(), (0, 100, 50, 0.5))
    assert hexa(clr_hexa).has_alpha() is True
    assert_hexa_equal(hexa(clr_hexa).lighten(0.5), "#FF80807F")
    assert_hexa_equal(hexa(clr_hexa).darken(0.5), "#8000007F")
    assert_hexa_equal(hexa(clr_hexa).saturate(0.5), "#FF00007F")
    assert_hexa_equal(hexa(clr_hexa).desaturate(0.5), "#BF40407F")
    assert_hexa_equal(hexa(clr_hexa).rotate(90), "#80FF007F")
    assert_hexa_equal(hexa(clr_hexa).rotate(-90), "#7F00FF7F")
    assert_hexa_equal(hexa(clr_hexa).invert(), "#00FFFF7F")
    assert_hexa_equal(hexa(clr_hexa).grayscale(), "#3636367F")
    assert_hexa_equal(hexa(clr_hexa).blend("#00FF00"), "#FFFF00BF")
    assert hexa(clr_hexa).is_dark() is False
    assert hexa(clr_hexa).is_light() is True
    assert hexa(clr_hexa).is_grayscale() is False
    assert hexa(clr_hexa).is_opaque() is False
    assert_hexa_equal(hexa(clr_hexa).with_alpha(0.75), "#FF0000BF")
    assert_hexa_equal(hexa(clr_hexa).complementary(), "#00FFFF7F")
