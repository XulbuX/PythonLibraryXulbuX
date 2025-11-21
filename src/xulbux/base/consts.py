"""
This module contains constant values used throughout the library.
"""

from .types import FormattableString, AllTextChars


class COLOR:
    """Hexadecimal color presets."""

    WHITE = "#F1F2FF"
    LIGHT_GRAY = "#B6B7C0"
    GRAY = "#7B7C8D"
    DARK_GRAY = "#67686C"
    BLACK = "#202125"
    RED = "#FF606A"
    CORAL = "#FF7069"
    ORANGE = "#FF876A"
    TANGERINE = "#FF9962"
    GOLD = "#FFAF60"
    YELLOW = "#FFD260"
    LIME = "#C9F16E"
    GREEN = "#7EE787"
    NEON_GREEN = "#4CFF85"
    TEAL = "#50EAAF"
    CYAN = "#3EDEE6"
    ICE = "#77DBEF"
    LIGHT_BLUE = "#60AAFF"
    BLUE = "#8085FF"
    LAVENDER = "#9B7DFF"
    PURPLE = "#AD68FF"
    MAGENTA = "#C860FF"
    PINK = "#F162EF"
    ROSE = "#FF609F"


class CHARS:
    """Character set constants for text validation and filtering."""

    ALL = AllTextChars()
    """Sentinel value indicating all characters are allowed."""

    DIGITS = "0123456789"
    """Numeric digits: `0`-`9`"""
    FLOAT_DIGITS = "." + DIGITS
    """Numeric digits with decimal point: `0`-`9` and `.`"""
    HEX_DIGITS = "#" + DIGITS + "abcdefABCDEF"
    """Hexadecimal digits: `0`-`9`, `a`-`f`, `A`-`F`, and `#`"""

    LOWERCASE = "abcdefghijklmnopqrstuvwxyz"
    """Lowercase ASCII letters: `a`-`z`"""
    LOWERCASE_EXTENDED = LOWERCASE + "äëïöüÿàèìòùáéíóúýâêîôûãñõåæç"
    """Lowercase ASCII letters with diacritic marks."""
    UPPERCASE = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    """Uppercase ASCII letters: `A`-`Z`"""
    UPPERCASE_EXTENDED = UPPERCASE + "ÄËÏÖÜÀÈÌÒÙÁÉÍÓÚÝÂÊÎÔÛÃÑÕÅÆÇß"
    """Uppercase ASCII letters with diacritic marks."""

    LETTERS = LOWERCASE + UPPERCASE
    """All ASCII letters: `a`-`z` and `A`-`Z`"""
    LETTERS_EXTENDED = LOWERCASE_EXTENDED + UPPERCASE_EXTENDED
    """All ASCII letters with diacritic marks."""

    SPECIAL_ASCII = " !\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
    """Standard ASCII special characters and symbols."""
    SPECIAL_ASCII_EXTENDED = SPECIAL_ASCII + "ø£Ø×ƒªº¿®¬½¼¡«»░▒▓│┤©╣║╗╝¢¥┐└┴┬├─┼╚╔╩╦╠═╬¤ðÐı┘┌█▄¦▀µþÞ¯´≡­±‗¾¶§÷¸°¨·¹³²■ "
    """Standard and extended ASCII special characters."""
    STANDARD_ASCII = DIGITS + LETTERS + SPECIAL_ASCII
    """All standard ASCII characters (letters, digits, and symbols)."""
    FULL_ASCII = DIGITS + LETTERS_EXTENDED + SPECIAL_ASCII_EXTENDED
    """Complete ASCII character set including extended characters."""


class ANSI:
    """Constants and utilities for ANSI escape code sequences."""

    ESCAPED_CHAR = "\\x1b"
    """Printable ANSI escape character."""
    CHAR = "\x1b"
    """ANSI escape character."""
    START = "["
    """Start of an ANSI escape sequence."""
    SEP = ";"
    """Separator between ANSI escape sequence parts."""
    END = "m"
    """End of an ANSI escape sequence."""

    @classmethod
    def seq(cls, placeholders: int = 1) -> FormattableString:
        """Generates an ANSI escape sequence with the specified number of placeholders."""
        return cls.CHAR + cls.START + cls.SEP.join(["{}" for _ in range(placeholders)]) + cls.END

    SEQ_COLOR: FormattableString = CHAR + START + "38" + SEP + "2" + SEP + "{}" + SEP + "{}" + SEP + "{}" + END
    """ANSI escape sequence with three placeholders for setting the RGB text color."""
    SEQ_BG_COLOR: FormattableString = CHAR + START + "48" + SEP + "2" + SEP + "{}" + SEP + "{}" + SEP + "{}" + END
    """ANSI escape sequence with three placeholders for setting the RGB background color."""

    COLOR_MAP: tuple[str, ...] = (
        ########### DEFAULT CONSOLE COLOR NAMES ############
        "black",
        "red",
        "green",
        "yellow",
        "blue",
        "magenta",
        "cyan",
        "white",
    )
    """The standard terminal color names."""

    CODES_MAP: dict[str | tuple[str, ...], int] = {
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
    """Dictionary mapping format keys to their corresponding ANSI code numbers."""
