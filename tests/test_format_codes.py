from xulbux._consts_ import ANSI
from xulbux import FormatCodes


black = ANSI.seq_color.format(0, 0, 0)
bg_red = f"{ANSI.char}{ANSI.start}{ANSI.codes_map['bg:red']}{ANSI.end}"
default = ANSI.seq_color.format(255, 255, 255)
orange = ANSI.seq_color.format(255, 136, 119)

bold = f"{ANSI.char}{ANSI.start}{ANSI.codes_map[('bold', 'b')]}{ANSI.end}"
invert = f"{ANSI.char}{ANSI.start}{ANSI.codes_map[('inverse', 'invert', 'in')]}{ANSI.end}"
italic = f"{ANSI.char}{ANSI.start}{ANSI.codes_map[('italic', 'i')]}{ANSI.end}"
underline = f"{ANSI.char}{ANSI.start}{ANSI.codes_map[('underline', 'u')]}{ANSI.end}"

reset = f"{ANSI.char}{ANSI.start}{ANSI.codes_map['_']}{ANSI.end}"
reset_bg = f"{ANSI.char}{ANSI.start}{ANSI.codes_map[('_background', '_bg')]}{ANSI.end}"
reset_bold = f"{ANSI.char}{ANSI.start}{ANSI.codes_map[('_bold', '_b')]}{ANSI.end}"
reset_color = f"{ANSI.char}{ANSI.start}{ANSI.codes_map[('_color', '_c')]}{ANSI.end}"
reset_italic = f"{ANSI.char}{ANSI.start}{ANSI.codes_map[('_italic', '_i')]}{ANSI.end}"
reset_invert = f"{ANSI.char}{ANSI.start}{ANSI.codes_map[('_inverse', '_invert', '_in')]}{ANSI.end}"
reset_underline = f"{ANSI.char}{ANSI.start}{ANSI.codes_map[('_underline', '_u')]}{ANSI.end}"


def test_to_ansi():
    assert (
        FormatCodes.to_ansi("[b|#000|bg:red](He[in](l)lo) [[i|u|#F87](world)][default]![_]",
                            default_color="#FFF") == f"{default}{bold}{black}{bg_red}" + "He" + invert + "l" + reset_invert
        + "lo" + f"{reset_bold}{default}{reset_bg}" + " [" + f"{italic}{underline}{orange}" + "world"
        + f"{reset_italic}{reset_underline}{default}" + "]" + default + "!" + reset
    )


def test_escape_ansi():
    ansi_string = f"{bold}Hello {orange}World!{reset}"
    escaped_string = ansi_string.replace(ANSI.char, ANSI.escaped_char)
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
    removals = ((0, bold), (6, orange), (12, default), (12, reset_bold))
    assert FormatCodes.remove_formatting(format_string, get_removals=True) == (clean_string, removals)
