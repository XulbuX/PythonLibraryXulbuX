from xulbux import Color, rgba, hsla, hexa


def test_rgba_to_hex_int_and_back():
    blue = Color.rgba_to_hex_int(0, 0, 255)
    black = Color.rgba_to_hex_int(0, 0, 0, 1)
    _blue = Color.rgba_to_hex_int(0, 0, 255, preserve_original=True)
    _black = Color.rgba_to_hex_int(0, 0, 0, 1, preserve_original=True)
    assert blue == 0x0100FF
    assert black == 0x010000FF
    assert _blue == 0x0000FF
    assert _black == 0x000000FF
    assert Color.hex_int_to_rgba(blue).values() == (0, 0, 255, None)
    assert Color.hex_int_to_rgba(black).values() == (0, 0, 0, 1.0)
    assert Color.hex_int_to_rgba(_blue).values() == (0, 0, 255, None)
    assert Color.hex_int_to_rgba(_black).values() == (0, 0, 255, None)
    assert Color.hex_int_to_rgba(blue, preserve_original=True).values() == (1, 0, 255, None)
    assert Color.hex_int_to_rgba(black, preserve_original=True).values() == (1, 0, 0, 1.0)


def test_is_valid_rgba():
    assert Color.is_valid_rgba((255, 0, 0)) is True
    assert Color.is_valid_rgba((255, 0, 0, 0.5)) is True
    assert Color.is_valid_rgba("rgb(255, 0, 0)") is True
    assert Color.is_valid_rgba("rgba(255, 0, 0, .5)") is True
    assert Color.is_valid_rgba({"r": 255, "g": 0, "b": 0}) is True
    assert Color.is_valid_rgba({"r": 255, "g": 0, "b": 0, "a": 0.5}) is True
    assert Color.is_valid_rgba(rgba(255, 0, 0)) is True
    assert Color.is_valid_rgba((300, 0, 0)) is False
    assert Color.is_valid_rgba((255, 0)) is False  # type: ignore[assignment]
    assert Color.is_valid_rgba((255, 0, 0, 2)) is False
    assert Color.is_valid_rgba("not a color") is False
    assert Color.is_valid_rgba((255, 0, 0), allow_alpha=False) is True
    assert Color.is_valid_rgba((255, 0, 0, 0.5), allow_alpha=False) is False


def test_is_valid_hsla():
    assert Color.is_valid_hsla((0, 100, 50)) is True
    assert Color.is_valid_hsla((0, 100, 50, 0.5)) is True
    assert Color.is_valid_hsla("hsl(0, 100%, 50%)") is True
    assert Color.is_valid_hsla("hsla(0, 100%, 50%, .5)") is True
    assert Color.is_valid_hsla({"h": 0, "s": 100, "l": 50}) is True
    assert Color.is_valid_hsla({"h": 0, "s": 100, "l": 50, "a": 0.5}) is True
    assert Color.is_valid_hsla(hsla(0, 100, 50)) is True
    assert Color.is_valid_hsla((370, 100, 50)) is False
    assert Color.is_valid_hsla((0, 101, 50)) is False
    assert Color.is_valid_hsla((0, 100, 101)) is False
    assert Color.is_valid_hsla((0, 100)) is False  # type: ignore[assignment]
    assert Color.is_valid_hsla("not a color") is False
    assert Color.is_valid_hsla((0, 100, 50), allow_alpha=False) is True
    assert Color.is_valid_hsla((0, 100, 50, 0.5), allow_alpha=False) is False


def test_is_valid_hexa():
    assert Color.is_valid_hexa("F00") is True
    assert Color.is_valid_hexa("F008") is True
    assert Color.is_valid_hexa("#F00") is True
    assert Color.is_valid_hexa("#F008") is True
    assert Color.is_valid_hexa("#FF0000") is True
    assert Color.is_valid_hexa("#FF000080") is True
    assert Color.is_valid_hexa(0xFF0000) is True
    assert Color.is_valid_hexa(0xFF000080) is True
    assert Color.is_valid_hexa(hexa("#FF0000")) is True
    assert Color.is_valid_hexa("#XX0000") is False
    assert Color.is_valid_hexa("#F0000") is False
    assert Color.is_valid_hexa("not a color") is False
    assert Color.is_valid_hexa("#F00", allow_alpha=False) is True
    assert Color.is_valid_hexa("#F008", allow_alpha=False) is False
    assert Color.is_valid_hexa("#F00", get_prefix=True) == (True, "#")
    assert Color.is_valid_hexa("0xF00", get_prefix=True) == (True, "0x")
    assert Color.is_valid_hexa(0xFF0000, get_prefix=True) == (True, "0x")


def test_is_valid():
    assert Color.is_valid((255, 0, 0)) is True
    assert Color.is_valid((360, 100, 50)) is True
    assert Color.is_valid("F008") is True
    assert Color.is_valid("F008", allow_alpha=False) is False
    assert Color.is_valid(0xFF0000) is True
    assert Color.is_valid(rgba(255, 0, 0)) is True
    assert Color.is_valid(hsla(0, 100, 50, 0.5)) is True
    assert Color.is_valid(hexa("#FF0000")) is True
    assert Color.is_valid("not a color") is False
    assert Color.is_valid((370, 100, 50)) is False


def test_has_alpha():
    assert Color.has_alpha((255, 0, 0)) is False
    assert Color.has_alpha((255, 0, 0, 0.5)) is True
    assert Color.has_alpha(rgba(255, 0, 0)) is False
    assert Color.has_alpha(rgba(255, 0, 0, 0.5)) is True
    assert Color.has_alpha(hsla(0, 100, 50)) is False
    assert Color.has_alpha(hsla(0, 100, 50, 0.5)) is True
    assert Color.has_alpha(hexa("#F00")) is False
    assert Color.has_alpha(hexa("#F00F")) is True
    assert Color.has_alpha("#FF0000") is False
    assert Color.has_alpha("#FF0000FF") is True
    assert Color.has_alpha(0xFF0000) is False
    assert Color.has_alpha(0xFF0000FF) is True


def test_color_conversions():
    rgba_color = Color.to_rgba("#FF00007F")
    assert isinstance(rgba_color, rgba)
    assert rgba_color.values() == (255, 0, 0, 0.5)
    hsla_color = Color.to_hsla((255, 0, 0, 0.5))
    assert isinstance(hsla_color, hsla)
    assert hsla_color.values() == (0, 100, 50, 0.5)
    hexa_color = Color.to_hexa((255, 0, 0, 0.5))
    assert isinstance(hexa_color, hexa)
    assert str(hexa_color) == "#FF00007F"


def test_str_to_rgba():
    color = Color.str_to_rgba("The color is rgb(255, 0, 0, 0.5).", only_first=True)
    assert isinstance(color, rgba)
    assert color.values() == (255, 0, 0, 0.5)
    colors = Color.str_to_rgba("first color: rgb(255, 0, 0) | second color: rgba(0,255,0,.5)")
    assert len(colors) == 2  # type: ignore[assignment]
    assert colors[0].values() == (255, 0, 0, None)  # type: ignore
    assert colors[1].values() == (0, 255, 0, 0.5)  # type: ignore
    assert Color.str_to_rgba("No colors here") is None


def test_luminance():
    assert Color.luminance(255, 0, 0) == 54
    assert Color.luminance(255, 0, 0, int) == 21
    assert 0.20 < Color.luminance(255, 0, 0, float) < 0.22
    assert Color.luminance(0, 0, 0) == 0
    assert Color.luminance(255, 255, 255) == 255
    assert Color.luminance(128, 128, 128) == 55


def test_text_color_for_on_bg():
    text_color = Color.text_color_for_on_bg(rgba(0, 0, 0))
    assert isinstance(text_color, rgba)
    assert text_color.values() == (255, 255, 255, None)
    text_color = Color.text_color_for_on_bg(rgba(255, 255, 255))
    assert isinstance(text_color, rgba)
    assert text_color.values() == (0, 0, 0, None)
    text_color = Color.text_color_for_on_bg(hexa("#000000"))
    assert isinstance(text_color, hexa)
    assert str(text_color) == "#FFFFFF"


def test_adjust_lightness():
    color = rgba(128, 0, 0)
    lightened = Color.adjust_lightness(rgba(128, 0, 0), 0.5)
    assert isinstance(lightened, rgba)
    assert lightened.values()[:-1] > color.values()[:-1]
    color = rgba(255, 128, 128)
    darkened = Color.adjust_lightness(color, -0.5)
    assert isinstance(darkened, rgba)
    assert darkened.values()[:-1] < color.values()[:-1]
    lightened = Color.adjust_lightness(hexa("#800000"), 0.5)
    assert isinstance(lightened, hexa)
    assert lightened.is_light() is True


def test_adjust_saturation():
    color = hsla(0, 50, 50)
    saturated = Color.adjust_saturation(color, 0.5)
    assert isinstance(saturated, rgba)
    assert saturated.to_hsla().s > color.s
    color = hsla(0, 100, 50)
    desaturated = Color.adjust_saturation(color, -0.5)
    assert isinstance(desaturated, rgba)
    assert desaturated.to_hsla().s < color.s
    desaturated = Color.adjust_saturation(hexa("#FF0000"), -1.0)
    assert isinstance(desaturated, hexa)
    assert desaturated.is_grayscale() is True
