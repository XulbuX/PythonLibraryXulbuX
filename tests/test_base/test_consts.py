from xulbux.base.consts import ANSI, CHARS


def test_chars_constants() -> None:
    assert CHARS.DIGITS == "0123456789"
    assert CHARS.FLOAT_DIGITS == ".0123456789"
    assert "#" in CHARS.HEX_DIGITS
    assert "a" in CHARS.LOWERCASE and "z" in CHARS.LOWERCASE
    assert "ä" in CHARS.LOWERCASE_EXTENDED
    assert "A" in CHARS.UPPERCASE and "Z" in CHARS.UPPERCASE
    assert "Ä" in CHARS.UPPERCASE_EXTENDED
    assert CHARS.LETTERS == CHARS.LOWERCASE + CHARS.UPPERCASE
    assert CHARS.LETTERS_EXTENDED == CHARS.LOWERCASE_EXTENDED + CHARS.UPPERCASE_EXTENDED
    assert " " in CHARS.SPECIAL_ASCII
    assert "ø" in CHARS.SPECIAL_ASCII_EXTENDED
    assert CHARS.STANDARD_ASCII == CHARS.DIGITS + CHARS.LETTERS + CHARS.SPECIAL_ASCII
    assert CHARS.FULL_ASCII == CHARS.DIGITS + CHARS.LETTERS_EXTENDED + CHARS.SPECIAL_ASCII_EXTENDED


def test_ansi_escape_constants_and_sequences() -> None:
    assert ANSI.CHAR == "\x1b"
    assert ANSI.CHAR_ESCAPED == r"\x1b"

    assert ANSI.SEQ_FG_COLOR.format(255, 0, 0) == "\x1b[38;2;255;0;0m"
    assert ANSI.SEQ_BG_COLOR.format(0, 255, 0) == "\x1b[48;2;0;255;0m"

    url = "https://example.com"
    assert ANSI.SEQ_LINK_OPEN.format(url) == f"\x1b]8;;{url}\x1b\\"
    assert ANSI.SEQ_LINK_CLOSE == "\x1b]8;;\x1b\\"

    assert ANSI.SEQ_PATTERN.search("\x1b[31mHello\x1b[0m") is not None
