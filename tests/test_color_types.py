from xulbux.color import rgba, hexa, hsla


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


################################################## rgba TESTS ##################################################


def test_rgba_return_values():
    assert_rgba_equal(rgba(255, 0, 0, 0.5), (255, 0, 0, 0.5))
    assert_hsla_equal(rgba(255, 0, 0, 0.5).to_hsla(), (0, 100, 50, 0.5))
    assert_hexa_equal(rgba(255, 0, 0, 0.5).to_hexa(), "#FF00007F")
    assert rgba(255, 0, 0, 0.5).has_alpha() is True
    assert_rgba_equal(rgba(255, 0, 0, 0.5).lighten(0.5), (255, 128, 128, 0.5))
    assert_rgba_equal(rgba(255, 0, 0, 0.5).darken(0.5), (128, 0, 0, 0.5))
    assert_rgba_equal(rgba(170, 128, 128, 0.5).saturate(0.5), (212, 84, 84, 0.5))
    assert_rgba_equal(rgba(255, 0, 0, 0.5).saturate(0.5), (255, 0, 0, 0.5))
    assert_rgba_equal(rgba(255, 0, 0, 0.5).desaturate(0.5), (191, 64, 64, 0.5))
    assert_rgba_equal(rgba(255, 0, 0, 0.5).rotate(90), (128, 255, 0, 0.5))
    assert_rgba_equal(rgba(255, 0, 0, 0.5).rotate(-90), (127, 0, 255, 0.5))
    assert_rgba_equal(rgba(255, 0, 0, 0.5).invert(), (0, 255, 255, 0.5))
    assert_rgba_equal(rgba(255, 0, 0, 0.5).grayscale(), (54, 54, 54, 0.5))
    assert_rgba_equal(rgba(255, 0, 0, 0.5).blend((0, 255, 0)), (255, 255, 0, 0.75))
    assert rgba(255, 0, 0, 0.5).is_dark() is False
    assert rgba(255, 0, 0, 0.5).is_light() is True
    assert rgba(128, 128, 128, 0.5).is_grayscale() is True
    assert rgba(255, 0, 0, 0.5).is_grayscale() is False
    assert rgba(255, 0, 0).is_opaque() is True
    assert rgba(255, 0, 0, 1.0).is_opaque() is True
    assert rgba(255, 0, 0, 0.5).is_opaque() is False
    assert_rgba_equal(rgba(255, 0, 0, 0.5).with_alpha(0.75), (255, 0, 0, 0.75))
    assert_rgba_equal(rgba(255, 0, 0, 0.5).complementary(), (0, 255, 255, 0.5))


def test_rgba_construction():
    assert rgba(100, 150, 200).values() == (100, 150, 200, None)
    assert rgba(100, 150, 200, 0.5).values() == (100, 150, 200, 0.5)
    assert rgba(0, 0, 0).values() == (0, 0, 0, None)
    assert rgba(255, 255, 255).values() == (255, 255, 255, None)
    try:
        rgba(300, 150, 200)
        assert False, "Should raise ValueError for invalid RGB values"
    except ValueError:
        pass
    try:
        rgba(100, 150, 200, 2.0)
        assert False, "Should raise ValueError for invalid alpha value"
    except ValueError:
        pass


def test_rgba_dunder_methods():
    assert len(rgba(100, 150, 200)) == 3
    assert len(rgba(100, 150, 200, 0.5)) == 4
    color = rgba(100, 150, 200, 0.5)
    assert color[0] == 100
    assert color[1] == 150
    assert color[2] == 200
    assert color[3] == 0.5
    assert rgba(100, 150, 200) == rgba(100, 150, 200)
    assert rgba(100, 150, 200) != rgba(200, 100, 150)
    assert str(rgba(100, 150, 200)) == "rgba(100, 150, 200)"
    assert str(rgba(100, 150, 200, 0.5)) == "rgba(100, 150, 200, 0.5)"
    assert repr(rgba(100, 150, 200)) == "rgba(100, 150, 200)"
    assert repr(rgba(100, 150, 200, 0.5)) == "rgba(100, 150, 200, 0.5)"


################################################## hsla TESTS ##################################################


def test_hsla_return_values():
    assert_hsla_equal(hsla(0, 100, 50, 0.5), (0, 100, 50, 0.5))
    assert_rgba_equal(hsla(0, 100, 50, 0.5).to_rgba(), (255, 0, 0, 0.5))
    assert_hexa_equal(hsla(0, 100, 50, 0.5).to_hexa(), "#FF00007F")
    assert hsla(0, 100, 50, 0.5).has_alpha() is True
    assert_hsla_equal(hsla(0, 100, 50, 0.5).lighten(0.5), (0, 100, 75, 0.5))
    assert_hsla_equal(hsla(0, 100, 50, 0.5).darken(0.5), (0, 100, 25, 0.5))
    assert_hsla_equal(hsla(0, 20, 50, 0.5).saturate(0.5), (0, 60, 50, 0.5))
    assert_hsla_equal(hsla(0, 100, 50, 0.5).saturate(0.5), (0, 100, 50, 0.5))
    assert_hsla_equal(hsla(0, 100, 50, 0.5).desaturate(0.5), (0, 50, 50, 0.5))
    assert_hsla_equal(hsla(0, 100, 50, 0.5).rotate(90), (90, 100, 50, 0.5))
    assert_hsla_equal(hsla(0, 100, 50, 0.5).rotate(-90), (270, 100, 50, 0.5))
    assert_hsla_equal(hsla(0, 100, 50, 0.5).invert(), (180, 100, 50, 0.5))
    assert_hsla_equal(hsla(0, 100, 50, 0.5).grayscale(), (0, 0, 21, 0.5))
    assert_hsla_equal(hsla(0, 100, 50, 0.5).blend((120, 100, 50)), (60, 100, 50, 0.75))
    assert hsla(0, 100, 50, 0.5).is_dark() is False
    assert hsla(0, 100, 50, 0.5).is_light() is True
    assert hsla(0, 0, 50, 0.5).is_grayscale() is True
    assert hsla(0, 100, 50, 0.5).is_grayscale() is False
    assert hsla(0, 100, 50).is_opaque() is True
    assert hsla(0, 100, 50, 1.0).is_opaque() is True
    assert hsla(0, 100, 50, 0.5).is_opaque() is False
    assert_hsla_equal(hsla(0, 100, 50, 0.5).with_alpha(0.75), (0, 100, 50, 0.75))
    assert_hsla_equal(hsla(0, 100, 50, 0.5).complementary(), (180, 100, 50, 0.5))


def test_hsla_construction():
    assert hsla(210, 50, 60).values() == (210, 50, 60, None)
    assert hsla(210, 50, 60, 0.5).values() == (210, 50, 60, 0.5)
    assert hsla(0, 0, 0).values() == (0, 0, 0, None)
    assert hsla(360, 100, 100).values() == (360, 100, 100, None)
    try:
        hsla(361, 50, 60)
        assert False, "Should raise ValueError for invalid hue value"
    except ValueError:
        pass
    try:
        hsla(210, 101, 60)
        assert False, "Should raise ValueError for invalid saturation value"
    except ValueError:
        pass


def test_hsla_dunder_methods():
    assert len(hsla(210, 50, 60)) == 3
    assert len(hsla(210, 50, 60, 0.5)) == 4
    color = hsla(210, 50, 60, 0.5)
    assert color[0] == 210
    assert color[1] == 50
    assert color[2] == 60
    assert color[3] == 0.5
    assert hsla(210, 50, 60) == hsla(210, 50, 60)
    assert hsla(210, 50, 60) != hsla(210, 60, 50)
    assert str(hsla(210, 50, 60)) == "hsla(210°, 50%, 60%)"
    assert str(hsla(210, 50, 60, 0.5)) == "hsla(210°, 50%, 60%, 0.5)"
    assert repr(hsla(210, 50, 60)) == "hsla(210°, 50%, 60%)"
    assert repr(hsla(210, 50, 60, 0.5)) == "hsla(210°, 50%, 60%, 0.5)"


################################################## hexa TESTS ##################################################


def test_hexa_return_values():
    assert_hexa_equal(hexa("#F008"), "#FF000088")
    assert_rgba_equal(hexa("#FF00007F").to_rgba(), (255, 0, 0, 0.5))
    assert_hsla_equal(hexa("#FF00007F").to_hsla(), (0, 100, 50, 0.5))
    assert hexa("#FF00007F").has_alpha() is True
    assert_hexa_equal(hexa("#FF00007F").lighten(0.5), "#FF80807F")
    assert_hexa_equal(hexa("#FF00007F").darken(0.5), "#8000007F")
    assert_hexa_equal(hexa("#AA80807F").saturate(0.5), "#D454547F")
    assert_hexa_equal(hexa("#FF00007F").saturate(0.5), "#FF00007F")
    assert_hexa_equal(hexa("#FF00007F").desaturate(0.5), "#BF40407F")
    assert_hexa_equal(hexa("#FF00007F").rotate(90), "#80FF007F")
    assert_hexa_equal(hexa("#FF00007F").rotate(-90), "#7F00FF7F")
    assert_hexa_equal(hexa("#FF00007F").invert(), "#00FFFF7F")
    assert_hexa_equal(hexa("#FF00007F").grayscale(), "#3636367F")
    assert_hexa_equal(hexa("#FF00007F").blend("#00FF00"), "#FFFF00BF")
    assert hexa("#FF00007F").is_dark() is False
    assert hexa("#FF00007F").is_light() is True
    assert hexa("#8080807F").is_grayscale() is True
    assert hexa("#FF00007F").is_grayscale() is False
    assert hexa("#F00").is_opaque() is True
    assert hexa("#F00F").is_opaque() is True
    assert hexa("#FF00007F").is_opaque() is False
    assert_hexa_equal(hexa("#FF00007F").with_alpha(0.75), "#FF0000BF")
    assert_hexa_equal(hexa("#FF00007F").complementary(), "#00FFFF7F")


def test_hexa_construction():
    assert hexa("#F00").values() == (255, 0, 0, None)
    assert hexa("#F008").values(True) == (255, 0, 0, 0.53)
    assert hexa("#FF0000").values() == (255, 0, 0, None)
    assert hexa("#FF000080").values() == (255, 0, 0, 0.5)
    assert hexa(0xFF0000).values() == (255, 0, 0, None)
    assert hexa(0xFF000080).values() == (255, 0, 0, 0.5)
    try:
        hexa("#XX0000")
        assert False, "Should raise ValueError for invalid hex digits"
    except ValueError:
        pass
    try:
        hexa("#F0000")
        assert False, "Should raise ValueError for invalid length"
    except ValueError:
        pass


def test_hexa_dunder_methods():
    assert len(hexa("#F00")) == 3
    assert len(hexa("#F008")) == 4
    color = hexa("#F008")
    assert color[0] == "FF"
    assert color[1] == "00"
    assert color[2] == "00"
    assert color[3] == "88"
    assert hexa("#F00") == hexa("#F00")
    assert hexa("#F00") != hexa("#0F0")
    assert str(hexa("#F00")) == "#FF0000"
    assert str(hexa("#F008")) == "#FF000088"
    assert repr(hexa("#F00")) == "hexa(#FF0000)"
    assert repr(hexa("#F008")) == "hexa(#FF000088)"
