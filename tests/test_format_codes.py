from xulbux._consts_ import ANSI
from xulbux import FormatCodes


black = ANSI.seq_color.format(0, 0, 0)
bg_red = f"{ANSI.char}{ANSI.start}{ANSI.codes_map[('bg:bright:red', 'bg:br:red')]}{ANSI.end}"
default = FormatCodes.__get_default_ansi("#FFF")
orange = ANSI.seq_color.format(255, 136, 119)

bold = f"{ANSI.char}{ANSI.start}{ANSI.codes_map[('bold', 'b')]}{ANSI.end}"
italic = f"{ANSI.char}{ANSI.start}{ANSI.codes_map[('italic', 'i')]}{ANSI.end}"
underline = f"{ANSI.char}{ANSI.start}{ANSI.codes_map[('underline', 'u')]}{ANSI.end}"

reset_bg = f"{ANSI.char}{ANSI.start}{ANSI.codes_map[('_background', '_bg')]}{ANSI.end}"
reset_bold = f"{ANSI.char}{ANSI.start}{ANSI.codes_map[('_bold', '_b')]}{ANSI.end}"
reset_color = f"{ANSI.char}{ANSI.start}{ANSI.codes_map[('_color', '_c')]}{ANSI.end}"
reset_italic = f"{ANSI.char}{ANSI.start}{ANSI.codes_map[('_italic', '_i')]}{ANSI.end}"
reset_underline = f"{ANSI.char}{ANSI.start}{ANSI.codes_map[('_underline', '_u')]}{ANSI.end}"


def test_codes_to_ansi():
    assert (
        FormatCodes.to_ansi("[b|#000|bg:red](Hello) [i|u|#F87](world)[default]!", "#FFF")
        == f"{default}{bold}{black}{bg_red}"
        + "Hello"
        + f"{reset_bold}{reset_color}{reset_bg}"
        + " "
        + f"{italic}{underline}{orange}"
        + "world"
        + f"{reset_italic}{reset_underline}{reset_color}{default}"
        + "!"
    )
