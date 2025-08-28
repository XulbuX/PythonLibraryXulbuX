from xulbux.base.consts import ANSI
from xulbux.format_codes import FormatCodes


black = ANSI.SEQ_COLOR.format(0, 0, 0)
bg_red = f"{ANSI.CHAR}{ANSI.START}{ANSI.CODES_MAP['bg:red']}{ANSI.END}"
default = ANSI.SEQ_COLOR.format(255, 255, 255)
orange = ANSI.SEQ_COLOR.format(255, 136, 119)

bold = f"{ANSI.CHAR}{ANSI.START}{ANSI.CODES_MAP[('bold', 'b')]}{ANSI.END}"
invert = f"{ANSI.CHAR}{ANSI.START}{ANSI.CODES_MAP[('inverse', 'invert', 'in')]}{ANSI.END}"
italic = f"{ANSI.CHAR}{ANSI.START}{ANSI.CODES_MAP[('italic', 'i')]}{ANSI.END}"
underline = f"{ANSI.CHAR}{ANSI.START}{ANSI.CODES_MAP[('underline', 'u')]}{ANSI.END}"

reset = f"{ANSI.CHAR}{ANSI.START}{ANSI.CODES_MAP['_']}{ANSI.END}"
reset_bg = f"{ANSI.CHAR}{ANSI.START}{ANSI.CODES_MAP[('_background', '_bg')]}{ANSI.END}"
reset_bold = f"{ANSI.CHAR}{ANSI.START}{ANSI.CODES_MAP[('_bold', '_b')]}{ANSI.END}"
reset_color = f"{ANSI.CHAR}{ANSI.START}{ANSI.CODES_MAP[('_color', '_c')]}{ANSI.END}"
reset_italic = f"{ANSI.CHAR}{ANSI.START}{ANSI.CODES_MAP[('_italic', '_i')]}{ANSI.END}"
reset_invert = f"{ANSI.CHAR}{ANSI.START}{ANSI.CODES_MAP[('_inverse', '_invert', '_in')]}{ANSI.END}"
reset_underline = f"{ANSI.CHAR}{ANSI.START}{ANSI.CODES_MAP[('_underline', '_u')]}{ANSI.END}"


def test_to_ansi():
    assert (
        FormatCodes.to_ansi("[b|#000|bg:red](He[in](l)lo) [[i|u|#F87](world)][default]![_]",
                            default_color="#FFF") == f"{default}{bold}{black}{bg_red}" + "He" + invert + "l" + reset_invert
        + "lo" + f"{reset_bold}{default}{reset_bg}" + " [" + f"{italic}{underline}{orange}" + "world"
        + f"{reset_italic}{reset_underline}{default}" + "]" + default + "!" + reset
    )


def test_escape_ansi():
    ansi_string = f"{bold}Hello {orange}World!{reset}"
    escaped_string = ansi_string.replace(ANSI.CHAR, ANSI.ESCAPED_CHAR)
    assert FormatCodes.escape_ansi(ansi_string) == escaped_string


def test_remove_ansi():
    ansi_string = f"{bold}Hello {orange}World!{reset}"
    clean_string = "Hello World!"
    assert FormatCodes.remove_ansi(ansi_string) == clean_string


def test_remove_ansi_with_removals():
    ansi_string = f"{bold}Hello {orange}World!{reset}"
    clean_string = "Hello World!"
    removals = ((0, bold), (6, orange), (12, reset))
    assert FormatCodes.remove_ansi(ansi_string, get_removals=True) == (clean_string, removals)


def test_remove_formatting():
    format_string = "[b](Hello [#F87](World!))"
    clean_string = "Hello World!"
    assert FormatCodes.remove_formatting(format_string) == clean_string


def test_remove_formatting_with_removals():
    format_string = "[b](Hello [#F87](World!))"
    clean_string = "Hello World!"
    removals = ((0, default), (0, bold), (6, orange), (12, default), (12, reset_bold))
    assert FormatCodes.remove_formatting(format_string, default_color="#FFF", get_removals=True) == (clean_string, removals)
