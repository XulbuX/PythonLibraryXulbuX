from dataclasses import dataclass
from typing import TypeAlias


FormattableString: TypeAlias = str
"""A `str` object that is made to be formatted with the `.format()` method."""


@dataclass
class COLOR:
    """Color presets used in the `xulbux` library."""

    text = "#A5D6FF"
    """The default text color used in the `xulbux` library."""

    white = "#F1F2FF"
    lightgray = "#B6B7C0"
    gray = "#7B7C8D"
    darkgray = "#67686C"
    black = "#202125"
    red = "#FF606A"
    coral = "#FF7069"
    orange = "#FF876A"
    tangerine = "#FF9962"
    gold = "#FFAF60"
    yellow = "#FFD260"
    lime = "#C9F16E"
    green = "#7EE787"
    neongreen = "#4CFF85"
    teal = "#50EAAF"
    cyan = "#3EDEE6"
    ice = "#77DBEF"
    lightblue = "#60AAFF"
    blue = "#8085FF"
    lavender = "#9B7DFF"
    purple = "#AD68FF"
    magenta = "#C860FF"
    pink = "#F162EF"
    rose = "#FF609F"


class _AllTextCharacters:
    pass


@dataclass
class CHARS:
    """Text character sets."""

    all = _AllTextCharacters
    """Code to signal that all characters are allowed."""

    digits: str = "0123456789"
    """Digits: `0`-`9`"""
    float_digits: str = digits + "."
    """Digits: `0`-`9` with decimal point `.`"""
    hex_digits: str = digits + "#abcdefABCDEF"
    """Digits: `0`-`9` Letters: `a`-`f` `A`-`F` and a hashtag `#`"""

    lowercase: str = "abcdefghijklmnopqrstuvwxyz"
    """Lowercase letters `a`-`z`"""
    lowercase_extended: str = lowercase + "äëïöüÿàèìòùáéíóúýâêîôûãñõåæç"
    """Lowercase letters `a`-`z` with all lowercase diacritic letters."""
    uppercase: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    """Uppercase letters `A`-`Z`"""
    uppercase_extended: str = uppercase + "ÄËÏÖÜÀÈÌÒÙÁÉÍÓÚÝÂÊÎÔÛÃÑÕÅÆÇß"
    """Uppercase letters `A`-`Z` with all uppercase diacritic letters."""

    letters: str = lowercase + uppercase
    """Lowercase and uppercase letters `a`-`z` and `A`-`Z`"""
    letters_extended: str = lowercase_extended + uppercase_extended
    """Lowercase and uppercase letters `a`-`z` `A`-`Z` and all diacritic letters."""

    special_ascii: str = " !\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
    """All ASCII special characters."""
    special_ascii_extended: str = special_ascii + "ø£Ø×ƒªº¿®¬½¼¡«»░▒▓│┤©╣║╗╝¢¥┐└┴┬├─┼╚╔╩╦╠═╬¤ðÐı┘┌█▄¦▀µþÞ¯´≡­±‗¾¶§÷¸°¨·¹³²■ "
    """All ASCII special characters with the extended ASCII special characters."""
    standard_ascii: str = special_ascii + digits + letters
    """All standard ASCII characters."""
    full_ascii: str = special_ascii_extended + digits + letters_extended
    """All characters in the ASCII table."""


class ANSI:
    """Constants and class-methods for use of ANSI escape codes."""

    escaped_char: str = "\\x1b"
    """The printable ANSI escape character."""
    CHAR = char = "\x1b"
    """The ANSI escape character."""
    START = start = "["
    """The start of an ANSI escape sequence."""
    SEP = sep = ";"
    """The separator between ANSI escape sequence parts."""
    END = end = "m"
    """The end of an ANSI escape sequence."""
    default_color_modifiers: dict[str, str] = {"lighten": "+l", "darken": "-d"}
    """Characters to modify the lightness of the default color with."""

    @classmethod
    def seq(cls, parts: int = 1) -> FormattableString:
        """Generate an ANSI sequence with `parts` amount of placeholders."""
        return cls.CHAR + cls.START + cls.SEP.join(["{}" for _ in range(parts)]) + cls.END

    seq_color: FormattableString = CHAR + START + "38" + SEP + "2" + SEP + "{}" + SEP + "{}" + SEP + "{}" + END
    """The ANSI escape sequence for setting the text RGB color."""
    seq_bg_color: FormattableString = CHAR + START + "48" + SEP + "2" + SEP + "{}" + SEP + "{}" + SEP + "{}" + END
    """The ANSI escape sequence for setting the background RGB color."""

    color_map: list[str] = [
        ########### DEFAULT CONSOLE COLOR NAMES ############
        "black",
        "red",
        "green",
        "yellow",
        "blue",
        "magenta",
        "cyan",
        "white",
    ]
    """The console default color names."""

    codes_map: dict[str | tuple[str, ...], int] = {
        ################# SPECIFIC RESETS ##################
        "_": 0,
        ("_bold", "_b"): 22,
        ("_dim", "_d"): 22,
        ("_italic", "_i"): 23,
        ("_underline", "_u"): 24,
        ("_double-underline", "_du"): 24,
        ("_inverse", "_invert", "_in"): 27,
        ("_hidden", "_hide", "_h"): 28,
        ("_strikethrough", "_s"): 29,
        ("_color", "_c"): 39,
        ("_background", "_bg"): 49,
        ################### TEXT STYLES ####################
        ("bold", "b"): 1,
        ("dim", "d"): 2,
        ("italic", "i"): 3,
        ("underline", "u"): 4,
        ("inverse", "invert", "in"): 7,
        ("hidden", "hide", "h"): 8,
        ("strikethrough", "s"): 9,
        ("double-underline", "du"): 21,
        ################## DEFAULT COLORS ##################
        "black": 30,
        "red": 31,
        "green": 32,
        "yellow": 33,
        "blue": 34,
        "magenta": 35,
        "cyan": 36,
        "white": 37,
        ############## BRIGHT DEFAULT COLORS ###############
        "br:black": 90,
        "br:red": 91,
        "br:green": 92,
        "br:yellow": 93,
        "br:blue": 94,
        "br:magenta": 95,
        "br:cyan": 96,
        "br:white": 97,
        ############ DEFAULT BACKGROUND COLORS #############
        "bg:black": 40,
        "bg:red": 41,
        "bg:green": 42,
        "bg:yellow": 43,
        "bg:blue": 44,
        "bg:magenta": 45,
        "bg:cyan": 46,
        "bg:white": 47,
        ######### BRIGHT DEFAULT BACKGROUND COLORS #########
        "bg:br:black": 100,
        "bg:br:red": 101,
        "bg:br:green": 102,
        "bg:br:yellow": 103,
        "bg:br:blue": 104,
        "bg:br:magenta": 105,
        "bg:br:cyan": 106,
        "bg:br:white": 107,
    }
    """All custom format keys and their corresponding ANSI format number codes."""
