from typing import TypeAlias


FormattableString: TypeAlias = str
"""A `str` object that is made to be formatted with the `.format()` method."""


class COLOR:
    """Hexa color presets."""

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
    """Text character sets."""

    class _AllTextChars:
        pass

    ALL = _AllTextChars
    """Code to signal that all characters are allowed."""

    DIGITS = "0123456789"
    """Digits: `0`-`9`"""
    FLOAT_DIGITS = DIGITS + "."
    """Digits: `0`-`9` with decimal point `.`"""
    HEX_DIGITS = DIGITS + "#abcdefABCDEF"
    """Digits: `0`-`9` Letters: `a`-`f` `A`-`F` and a hashtag `#`"""

    LOWERCASE = "abcdefghijklmnopqrstuvwxyz"
    """Lowercase letters `a`-`z`"""
    LOWERCASE_EXTENDED = LOWERCASE + "äëïöüÿàèìòùáéíóúýâêîôûãñõåæç"
    """Lowercase letters `a`-`z` with all lowercase diacritic letters."""
    UPPERCASE = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    """Uppercase letters `A`-`Z`"""
    UPPERCASE_EXTENDED = UPPERCASE + "ÄËÏÖÜÀÈÌÒÙÁÉÍÓÚÝÂÊÎÔÛÃÑÕÅÆÇß"
    """Uppercase letters `A`-`Z` with all uppercase diacritic letters."""

    LETTERS = LOWERCASE + UPPERCASE
    """Lowercase and uppercase letters `a`-`z` and `A`-`Z`"""
    LETTERS_EXTENDED = LOWERCASE_EXTENDED + UPPERCASE_EXTENDED
    """Lowercase and uppercase letters `a`-`z` `A`-`Z` and all diacritic letters."""

    SPECIAL_ASCII = " !\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
    """All ASCII special characters."""
    SPECIAL_ASCII_EXTENDED = SPECIAL_ASCII + "ø£Ø×ƒªº¿®¬½¼¡«»░▒▓│┤©╣║╗╝¢¥┐└┴┬├─┼╚╔╩╦╠═╬¤ðÐı┘┌█▄¦▀µþÞ¯´≡­±‗¾¶§÷¸°¨·¹³²■ "
    """All ASCII special characters with the extended ASCII special characters."""
    STANDARD_ASCII = SPECIAL_ASCII + DIGITS + LETTERS
    """All standard ASCII characters."""
    FULL_ASCII = SPECIAL_ASCII_EXTENDED + DIGITS + LETTERS_EXTENDED
    """All characters in the ASCII table."""


class ANSI:
    """Constants and methods for use of ANSI escape codes"""

    ESCAPED_CHAR = "\\x1b"
    """The printable ANSI escape character."""
    CHAR = char = "\x1b"
    """The ANSI escape character."""
    START = start = "["
    """The start of an ANSI escape sequence."""
    SEP = sep = ";"
    """The separator between ANSI escape sequence parts."""
    END = end = "m"
    """The end of an ANSI escape sequence."""

    @classmethod
    def seq(cls, parts: int = 1) -> FormattableString:
        """Generate an ANSI sequence with `parts` amount of placeholders."""
        return cls.CHAR + cls.START + cls.SEP.join(["{}" for _ in range(parts)]) + cls.END

    SEQ_COLOR: FormattableString = CHAR + START + "38" + SEP + "2" + SEP + "{}" + SEP + "{}" + SEP + "{}" + END
    """The ANSI escape sequence for setting the text RGB color."""
    SEQ_BG_COLOR: FormattableString = CHAR + START + "48" + SEP + "2" + SEP + "{}" + SEP + "{}" + SEP + "{}" + END
    """The ANSI escape sequence for setting the background RGB color."""

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
    """The console default color names."""

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
    """All custom format keys and their corresponding ANSI format number codes."""
