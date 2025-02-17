from dataclasses import dataclass
from typing import TypeAlias


FormattableString: TypeAlias = str


@dataclass
class COLOR:
    """Color presets used in the XulbuX library."""

    text = "#A5D6FF"
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
    green = "#7EE787"
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
    """Strings with only certain text characters."""

    # CODE TO SIGNAL, ALL CHARACTERS ARE ALLOWED
    all = _AllTextCharacters

    # DIGIT SETS
    digits: str = "0123456789"
    float_digits: str = digits + "."
    hex_digits: str = digits + "#abcdefABCDEF"

    # LETTER CATEGORIES
    lowercase: str = "abcdefghijklmnopqrstuvwxyz"
    lowercase_extended: str = lowercase + "äëïöüÿàèìòùáéíóúýâêîôûãñõåæç"
    uppercase: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    uppercase_extended: str = uppercase + "ÄËÏÖÜÀÈÌÒÙÁÉÍÓÚÝÂÊÎÔÛÃÑÕÅÆÇß"

    # COMBINED LETTER SETS
    letters: str = lowercase + uppercase
    letters_extended: str = lowercase_extended + uppercase_extended

    # ASCII sets
    special_ascii: str = " !\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
    special_ascii_extended: str = special_ascii + "ø£Ø×ƒªº¿®¬½¼¡«»░▒▓│┤©╣║╗╝¢¥┐└┴┬├─┼╚╔╩╦╠═╬¤ðÐı┘┌█▄¦▀µþÞ¯´≡­±‗¾¶§÷¸°¨·¹³²■ "
    standard_ascii: str = special_ascii + digits + letters
    full_ascii: str = special_ascii_extended + digits + letters_extended


class ANSI:
    """Constants and class-methods for use of ANSI escape codes."""

    escaped_char: str = "\\x1b"
    CHAR = char = "\x1b"
    START = start = "["
    SEP = sep = ";"
    END = end = "m"
    default_color_modifiers: dict[str, str] = {"lighten": "+l", "darken": "-d"}

    @classmethod
    def seq(cls, parts: int = 1) -> str:
        """Generate an ANSI sequence with `parts` amount of placeholders."""
        return cls.CHAR + cls.START + cls.SEP.join(["{}" for _ in range(parts)]) + cls.END

    seq_color: FormattableString = CHAR + START + "38" + SEP + "2" + SEP + "{}" + SEP + "{}" + SEP + "{}" + END
    seq_bg_color: FormattableString = CHAR + START + "48" + SEP + "2" + SEP + "{}" + SEP + "{}" + SEP + "{}" + END

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
