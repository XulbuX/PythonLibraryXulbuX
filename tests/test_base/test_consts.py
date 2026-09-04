from xulbux.base.consts import ANSI, CHARS, KEYS


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


def test_keys_constants() -> None:
    assert isinstance(KEYS.UP, frozenset)
    assert "\x1b[A" in KEYS.UP
    assert "\x1b[B" in KEYS.DOWN
    assert "\x1b[D" in KEYS.LEFT
    assert "\x1b[C" in KEYS.RIGHT
    assert KEYS.UP | KEYS.DOWN | KEYS.LEFT | KEYS.RIGHT == KEYS.ARROWS

    assert "\x1b[H" in KEYS.HOME and "\x1b[7~" in KEYS.HOME
    assert "\x1b[F" in KEYS.END and "\x1b[8~" in KEYS.END
    assert "\x1b[5~" in KEYS.PAGE_UP
    assert "\x1b[6~" in KEYS.PAGE_DOWN
    assert "\x1b[2~" in KEYS.INSERT
    assert "\x1b[3~" in KEYS.DELETE
    assert "\x08" in KEYS.BACKSPACE and "\x7f" in KEYS.BACKSPACE and "\x1b[127u" in KEYS.BACKSPACE
    assert "\t" in KEYS.TAB and "\x1b[9u" in KEYS.TAB
    assert "\x1b[Z" in KEYS.BACKTAB and "\x1b[9;2u" in KEYS.BACKTAB

    assert "\r" in KEYS.ENTER and "\x1b[13u" in KEYS.ENTER
    assert "\n" in KEYS.CTRL_ENTER and "\x1b[13;5u" in KEYS.CTRL_ENTER and "\x00\n" in KEYS.CTRL_ENTER
    assert KEYS.ENTER.isdisjoint(KEYS.CTRL_ENTER)
    assert "\x1b[13;2u" in KEYS.SHIFT_ENTER
    assert "\x1b" in KEYS.ESCAPE and "\x1b[27u" in KEYS.ESCAPE
    assert " " in KEYS.SPACE and "\x1b[32u" in KEYS.SPACE

    assert "\x1bOP" in KEYS.F1 and "\x1b[[A" in KEYS.F1
    assert "\x1bOQ" in KEYS.F2 and "\x1b[[B" in KEYS.F2
    assert "\x1bOR" in KEYS.F3 and "\x1b[[C" in KEYS.F3
    assert "\x1bOS" in KEYS.F4 and "\x1b[[D" in KEYS.F4
    assert "\x1b[15~" in KEYS.F5 and "\x1b[[E" in KEYS.F5
    assert "\x1b[17~" in KEYS.F6
    assert "\x1b[18~" in KEYS.F7
    assert "\x1b[19~" in KEYS.F8
    assert "\x1b[20~" in KEYS.F9
    assert "\x1b[21~" in KEYS.F10
    assert "\x1b[23~" in KEYS.F11
    assert "\x1b[24~" in KEYS.F12
    assert KEYS() is not None
