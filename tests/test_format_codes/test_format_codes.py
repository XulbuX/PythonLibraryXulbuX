from xulbux.base.consts import ANSI
from xulbux.format_codes import FormatCodes

black = ANSI.SEQ_FG_COLOR.format(0, 0, 0)
bg_red = f"{ANSI.CHAR}{ANSI.START}{ANSI.CODES_MAP['bg:red']}{ANSI.END}"
default = ANSI.SEQ_FG_COLOR.format(255, 255, 255)
orange = ANSI.SEQ_FG_COLOR.format(255, 136, 119)

bold = f"{ANSI.CHAR}{ANSI.START}{ANSI.CODES_MAP['bold', 'b']}{ANSI.END}"
invert = f"{ANSI.CHAR}{ANSI.START}{ANSI.CODES_MAP['inverse', 'invert', 'in']}{ANSI.END}"
italic = f"{ANSI.CHAR}{ANSI.START}{ANSI.CODES_MAP['italic', 'i']}{ANSI.END}"
underline = f"{ANSI.CHAR}{ANSI.START}{ANSI.CODES_MAP['underline', 'u']}{ANSI.END}"

reset = f"{ANSI.CHAR}{ANSI.START}{ANSI.CODES_MAP['_']}{ANSI.END}"
reset_bg = f"{ANSI.CHAR}{ANSI.START}{ANSI.CODES_MAP['_background', '_bg']}{ANSI.END}"
reset_bold = f"{ANSI.CHAR}{ANSI.START}{ANSI.CODES_MAP['_bold', '_b']}{ANSI.END}"
reset_color = f"{ANSI.CHAR}{ANSI.START}{ANSI.CODES_MAP['_color', '_c']}{ANSI.END}"
reset_italic = f"{ANSI.CHAR}{ANSI.START}{ANSI.CODES_MAP['_italic', '_i']}{ANSI.END}"
reset_invert = f"{ANSI.CHAR}{ANSI.START}{ANSI.CODES_MAP['_inverse', '_invert', '_in']}{ANSI.END}"
reset_underline = f"{ANSI.CHAR}{ANSI.START}{ANSI.CODES_MAP['_underline', '_u']}{ANSI.END}"


def test_to_ansi():
    assert (
        FormatCodes.to_ansi("[b|#000|bg:red](He[in](l)lo) [[i|u|#F87](world)][default]![_]", default_color="#FFF")
        == f"{default}{bold}{black}{bg_red}"
        + "He"
        + invert
        + "l"
        + reset_invert
        + "lo"
        + f"{reset_bold}{default}{reset_bg}"
        + " ["
        + f"{italic}{underline}{orange}"
        + "world"
        + f"{reset_italic}{reset_underline}{default}"
        + "]"
        + default
        + "!"
        + reset
    )


def test_escape_ansi():
    ansi_string = f"{bold}Hello {orange}World!{reset}"
    escaped_string = ansi_string.replace(ANSI.CHAR, ANSI.CHAR_ESCAPED)
    assert FormatCodes.escape_ansi(ansi_string) == escaped_string


def test_escape():
    # Test basic formatting codes:
    assert FormatCodes.escape("[b]Hello[_]") == "[/b]Hello[/_]"
    assert FormatCodes.escape("[bold|italic]Text[_]") == "[/bold|italic]Text[/_]"

    # Test with colors:
    assert FormatCodes.escape("[#F87]Hello[_]") == "[/#F87]Hello[/_]"
    assert FormatCodes.escape("[rgb(255, 136, 119)]Hello[_]") == "[/rgb(255, 136, 119)]Hello[/_]"

    # Test with default color:
    assert FormatCodes.escape("[default]Hello", default_color="#FFF") == "[/default]Hello"
    assert FormatCodes.escape("[bg:default]Hello", default_color="#FFF") == "[/bg:default]Hello"

    # Test with `*` formatting code:
    assert FormatCodes.escape("[*]Hello", default_color="#FFF") == "[/*]Hello"
    assert FormatCodes.escape("[b|*]Hello", default_color="#FFF") == "[/b|*]Hello"

    # Test with auto-reset:
    assert FormatCodes.escape("[b](Hello)") == "[/b](Hello)"
    assert FormatCodes.escape("[*](Hello)", default_color="#FFF") == "[/*](Hello)"

    # Test invalid formatting codes (should remain unchanged):
    assert FormatCodes.escape("[invalid]Hello") == "[invalid]Hello"
    assert FormatCodes.escape("[default]Hello") == "[default]Hello"  # No `default_color`.
    assert FormatCodes.escape("[*]Hello") == "[/*]Hello"  # No `default_color`.

    # Test already escaped codes:
    assert FormatCodes.escape("[/b]Hello") == "[/b]Hello"
    assert FormatCodes.escape("[/*]Hello", default_color="#FFF") == "[/*]Hello"

    # Test with brightness modifiers:
    assert FormatCodes.escape("[l]Hello", default_color="#FFF") == "[/l]Hello"
    assert FormatCodes.escape("[ll]Hello", default_color="#FFF") == "[/ll]Hello"
    assert FormatCodes.escape("[+]Hello", default_color="#FFF") == "[/+]Hello"
    assert FormatCodes.escape("[++]Hello", default_color="#FFF") == "[/++]Hello"
    assert FormatCodes.escape("[d]Hello", default_color="#FFF") == "[/d]Hello"
    assert FormatCodes.escape("[dd]Hello", default_color="#FFF") == "[/dd]Hello"
    assert FormatCodes.escape("[-]Hello", default_color="#FFF") == "[/-]Hello"
    assert FormatCodes.escape("[--]Hello", default_color="#FFF") == "[/--]Hello"


def test_hyperlinks():
    url = "https://example.com"
    file_url = "file:///C:/path/to/file.txt"
    link_open = ANSI.SEQ_LINK_OPEN.format(url)
    link_open_file = ANSI.SEQ_LINK_OPEN.format(file_url)
    link_close = ANSI.SEQ_LINK_CLOSE

    # Basic link:
    assert FormatCodes.to_ansi(f"[link:{url}](click here)") == f"{link_open}click here{link_close}"

    # File URL:
    assert FormatCodes.to_ansi(f"[link:{file_url}](open file)") == f"{link_open_file}open file{link_close}"

    # Link with nested formatting in display text:
    assert FormatCodes.to_ansi(f"[link:{url}]([b](bold link))") == f"{link_open}{bold}bold link{reset_bold}{link_close}"

    # Link combined with other format keys:
    assert FormatCodes.to_ansi(f"[link:{url}|b](click here)") == f"{link_open}{bold}click here{reset_bold}{link_close}"
    bright_blue = f"{ANSI.CHAR}{ANSI.START}{ANSI.CODES_MAP['br:blue']}{ANSI.END}"
    assert FormatCodes.to_ansi(f"[link:{url}|br:blue](click here)") == (
        f"{link_open}{bright_blue}click here{reset_color}{link_close}"
    )

    # Link without display braces is invalid (left as-is):
    assert FormatCodes.to_ansi(f"[link:{url}]") == f"[link:{url}]"

    # Escape: link should be escaped:
    assert FormatCodes.escape(f"[link:{url}](click here)") == f"[/link:{url}](click here)"
    assert FormatCodes.escape(f"[link:{url}|b](click here)") == f"[/link:{url}|b](click here)"

    # Remove: osc sequences from link should be stripped, leaving only display text:
    assert FormatCodes.remove(f"[link:{url}](click here)") == "click here"
    assert FormatCodes.remove_ansi(f"{link_open}click here{link_close}") == "click here"


def test_remove_ansi():
    ansi_string = f"{bold}Hello {orange}World!{reset}"
    clean_string = "Hello World!"
    assert FormatCodes.remove_ansi(ansi_string) == clean_string


def test_remove_ansi_with_removals():
    ansi_string = f"{bold}Hello\n{orange}World!{reset}"
    clean_string = "Hello\nWorld!"
    removals = ((0, bold), (6, orange), (12, reset))
    assert FormatCodes.remove_ansi(ansi_string, get_removals=True) == (clean_string, removals)
    removals = ((0, bold), (5, orange), (11, reset))
    assert FormatCodes.remove_ansi(ansi_string, get_removals=True, _ignore_linebreaks=True) == (clean_string, removals)


def test_remove_formatting():
    format_string = "[b](Hello [#F87](World!))"
    clean_string = "Hello World!"
    assert FormatCodes.remove(format_string) == clean_string


def test_remove_formatting_with_removals():
    format_string = "[b](Hello [#F87](World!))"
    clean_string = "Hello World!"
    removals = ((0, default), (0, bold), (6, orange), (12, default), (12, reset_bold))
    assert FormatCodes.remove(format_string, default_color="#FFF", get_removals=True) == (clean_string, removals)
    format_string = "[b](Hello)\n[#F87](World!)"
    clean_string = "Hello\nWorld!"
    removals = ((0, default), (0, bold), (5, reset_bold), (6, orange), (12, default))
    assert FormatCodes.remove(format_string, default_color="#FFF", get_removals=True) == (clean_string, removals)
    removals = ((0, default), (0, bold), (5, reset_bold), (5, orange), (11, default))
    assert FormatCodes.remove(format_string, default_color="#FFF", get_removals=True, _ignore_linebreaks=True) == (
        clean_string,
        removals,
    )
