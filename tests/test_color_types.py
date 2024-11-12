from XulbuX import rgba, hexa, hsla


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


def test_rgba_return_values():
    rgba_instance = rgba(*clr_rgba)
    assert rgba_instance.to_hsla() == hsla(0, 100, 50, 0.5)
    assert rgba_instance.to_hexa() == hexa("#FF00007F")
    assert rgba_instance.has_alpha() is True
    assert rgba_instance.lighten(0.5) == rgba(255, 128, 128, 0.5)
    assert rgba_instance.darken(0.5) == rgba(128, 0, 0, 0.5)
    assert rgba_instance.saturate(0.5) == rgba(255, 0, 0, 0.5)
    assert rgba_instance.desaturate(0.5) == rgba(191, 64, 64, 0.5)
    assert rgba_instance.rotate(90) == rgba(128, 255, 0, 0.5)
    assert rgba_instance.rotate(-90) == rgba(127, 0, 255, 0.5)
    assert rgba_instance.invert() == rgba(0, 255, 255, 0.5)
    assert rgba_instance.grayscale() == rgba(54, 54, 54, 0.5)
    assert rgba_instance.blend((0, 255, 0)) == rgba(255, 255, 0, 0.75)
    assert rgba_instance.is_dark() is True
    assert rgba_instance.is_light() is False
    assert rgba_instance.is_grayscale() is False
    assert rgba_instance.is_opaque() is False
    assert rgba_instance.with_alpha(0.75) == rgba(255, 0, 0, 0.75)
    assert rgba_instance.complementary() == rgba(0, 255, 255, 0.5)


def test_hsla_return_values():
    hsla_instance = hsla(*clr_hsla)
    assert hsla_instance.to_rgba() == rgba(255, 0, 0, 0.5)
    assert hsla_instance.to_hexa() == hexa("#FF00007F")
    assert hsla_instance.has_alpha() is True
    assert hsla_instance.lighten(0.5) == hsla(0, 100, 75, 0.5)
    assert hsla_instance.darken(0.5) == hsla(0, 100, 25, 0.5)
    assert hsla_instance.saturate(0.5) == hsla(0, 100, 50, 0.5)
    assert hsla_instance.desaturate(0.5) == hsla(0, 50, 50, 0.5)
    assert hsla_instance.rotate(90) == hsla(90, 100, 50, 0.5)
    assert hsla_instance.rotate(-90) == hsla(270, 100, 50, 0.5)
    assert hsla_instance.invert() == hsla(180, 100, 50, 0.5)
    assert hsla_instance.grayscale() == hsla(0, 0, 21, 0.5)
    assert hsla_instance.blend((120, 100, 50)) == hsla(60, 100, 50, 0.75)
    assert hsla_instance.is_dark() is False
    assert hsla_instance.is_light() is True
    assert hsla_instance.is_grayscale() is False
    assert hsla_instance.is_opaque() is False
    assert hsla_instance.with_alpha(0.75) == hsla(0, 100, 50, 0.75)
    assert hsla_instance.complementary() == hsla(180, 100, 50, 0.5)


def test_hexa_return_values():
    hexa_instance = hexa(clr_hexa)
    assert hexa_instance.to_rgba() == rgba(255, 0, 0, 0.5)
    assert hexa_instance.to_hsla() == hsla(0, 100, 50, 0.5)
    assert hexa_instance.has_alpha() is True
    assert hexa_instance.lighten(0.5) == hexa("#FF80807F")
    assert hexa_instance.darken(0.5) == hexa("#8000007F")
    assert hexa_instance.saturate(0.5) == hexa("#FF00007F")
    assert hexa_instance.desaturate(0.5) == hexa("#BF40407F")
    assert hexa_instance.rotate(90) == hexa("#80FF007F")
    assert hexa_instance.rotate(-90) == hexa("#7F00FF7F")
    assert hexa_instance.invert() == hexa("#00FFFF7F")
    assert hexa_instance.grayscale() == hexa("#3636367F")
    assert hexa_instance.blend("#00FF00") == hexa("#FFFF00BF")
    assert hexa_instance.is_dark() is False
    assert hexa_instance.is_light() is True
    assert hexa_instance.is_grayscale() is False
    assert hexa_instance.is_opaque() is False
    assert hexa_instance.with_alpha(0.75) == hexa("#FF0000BF")
    assert hexa_instance.complementary() == hexa("#00FFFF7F")
