from XulbuX import Color


def test_rgba_to_hex_int_and_back():
    blue = Color.rgba_to_hex_int(0, 0, 255)
    black = Color.rgba_to_hex_int(0, 0, 0, 1)
    _blue = Color.rgba_to_hex_int(0, 0, 255, preserve_original=True)
    _black = Color.rgba_to_hex_int(0, 0, 0, 1, preserve_original=True)
    assert blue == 0x0100FF
    assert black == 0x010000FF
    assert _blue == 0x0000FF
    assert _black == 0x000000FF
    assert Color.hex_int_to_rgba(blue) == (0, 0, 255, None)
    assert Color.hex_int_to_rgba(black) == (0, 0, 0, 1.0)
    assert Color.hex_int_to_rgba(_blue) == (0, 0, 255, None)
    assert Color.hex_int_to_rgba(_black) == (0, 0, 255, None)
    assert Color.hex_int_to_rgba(blue, preserve_original=True) == (1, 0, 255, None)
    assert Color.hex_int_to_rgba(black, preserve_original=True) == (1, 0, 0, 1.0)
