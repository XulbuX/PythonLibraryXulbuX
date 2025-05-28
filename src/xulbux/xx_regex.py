from typing import TypeAlias, Optional
import regex as _rx
import re as _re


Pattern: TypeAlias = _re.Pattern[str] | _rx.Pattern[str]
Match: TypeAlias = _re.Match[str] | _rx.Match[str]


class Regex:

    @staticmethod
    def quotes() -> str:
        """Matches everything inside quotes. (strings)\n
        --------------------------------------------------------------------------------
        Will create two named groups:
        - `quote` the quote type (single or double)
        - `string` everything inside the found quote pair\n
        --------------------------------------------------------------------------------
        Attention: Requires non standard library `regex` not standard library `re`!"""
        return r'(?P<quote>[\'"])(?P<string>(?:\\.|(?!\g<quote>).)*?)\g<quote>'

    @staticmethod
    def brackets(
        bracket1: str = "(",
        bracket2: str = ")",
        is_group: bool = False,
        strip_spaces: bool = True,
        ignore_in_strings: bool = True,
    ) -> str:
        """Matches everything inside brackets, including other nested brackets.\n
        --------------------------------------------------------------------------------
        If `is_group` is true, you will be able to reference the matched content as a
        group (e.g. `match.group(…)` or `r'\\…'`).
        If `strip_spaces` is true, it will ignore spaces around the content inside the
        brackets.
        If `ignore_in_strings` is true and a bracket is inside a string (e.g. `'...'`
        or `"..."`), it will not be counted as the matching closing bracket.\n
        --------------------------------------------------------------------------------
        Attention: Requires non standard library `regex` not standard library `re`!"""
        g, b1, b2, s1, s2 = (
            "" if is_group else "?:",
            _rx.escape(bracket1) if len(bracket1) == 1 else bracket1,
            _rx.escape(bracket2) if len(bracket2) == 1 else bracket2,
            r"\s*" if strip_spaces else "",
            "" if strip_spaces else r"\s*",
        )
        if ignore_in_strings:
            return rf'{b1}{s1}({g}{s2}(?:[^{b1}{b2}"\']|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|{b1}(?:[^{b1}{b2}"\']|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|(?R))*{b2})*{s2}){s1}{b2}'
        else:
            return rf"{b1}{s1}({g}{s2}(?:[^{b1}{b2}]|{b1}(?:[^{b1}{b2}]|(?R))*{b2})*{s2}){s1}{b2}"

    @staticmethod
    def outside_strings(pattern: str = r".*") -> str:
        """Matches the `pattern` only when it is not found inside a string (`'...'` or `"..."`)."""
        return rf'(?<!["\'])(?:{pattern})(?!["\'])'

    @staticmethod
    def all_except(disallowed_pattern: str, ignore_pattern: str = "", is_group: bool = False) -> str:
        """Matches everything except `disallowed_pattern`, unless the `disallowed_pattern`
        is found inside a string (`'...'` or `"..."`).\n
        ------------------------------------------------------------------------------------
        The `ignore_pattern` is just always ignored. For example if `disallowed_pattern` is
        `>` and `ignore_pattern` is `->`, the `->`-arrows will be allowed, even though they
        have `>` in them.
        If `is_group` is true, you will be able to reference the matched content as a group
        (e.g. `match.group(…)` or `r'\\…'`)."""
        return rf'({"" if is_group else "?:"}(?:(?!{ignore_pattern}).)*(?:(?!{Regex.outside_strings(disallowed_pattern)}).)*)'

    @staticmethod
    def func_call(func_name: Optional[str] = None) -> str:
        """Match a function call, and get back two groups:
        1. function name
        2. the function's arguments\n
        If no `func_name` is given, it will match any function call.\n
        --------------------------------------------------------------------------------
        Attention: Requires non standard library `regex` not standard library `re`!"""
        return (
            r"(?<=\b)(" + (r"[\w_]+" if func_name is None else func_name) + r")\s*" + Regex.brackets("(", ")", is_group=True)
        )

    @staticmethod
    def rgba_str(fix_sep: str = ",", allow_alpha: bool = True) -> str:
        """Matches an RGBA color inside a string.\n
        ----------------------------------------------------------------------------
        The RGBA color can be in the formats (for `fix_sep = ','`):
        - `rgba(r, g, b)`
        - `rgba(r, g, b, a)` (if `allow_alpha=True`)
        - `(r, g, b)`
        - `(r, g, b, a)` (if `allow_alpha=True`)
        - `r, g, b`
        - `r, g, b, a` (if `allow_alpha=True`)\n
        #### Valid ranges:
        - `r` 0-255 (int: red)
        - `g` 0-255 (int: green)
        - `b` 0-255 (int: blue)
        - `a` 0.0-1.0 (float: opacity)\n
        ----------------------------------------------------------------------------
        If the `fix_sep` is set to nothing, any char that is not a letter or number
        can be used to separate the RGBA values, including just a space."""
        if fix_sep in (None, ""):
            fix_sep = r"[^0-9A-Z]"
        else:
            fix_sep = _re.escape(fix_sep)
        rgb_part = rf"""((?:0*(?:25[0-5]|2[0-4][0-9]|1?[0-9]{{1,2}})))
            (?:\s*{fix_sep}\s*)((?:0*(?:25[0-5]|2[0-4][0-9]|1?[0-9]{{1,2}})))
            (?:\s*{fix_sep}\s*)((?:0*(?:25[0-5]|2[0-4][0-9]|1?[0-9]{{1,2}})))"""
        return (
            rf"""(?ix)
            (?:rgb|rgba)?\s*(?:\(?\s*{rgb_part}
                (?:(?:\s*{fix_sep}\s*)((?:0*(?:0?\.[0-9]+|1\.0+|[0-9]+\.[0-9]+|[0-9]+))))?
            \s*\)?)""" if allow_alpha else rf"(?ix)(?:rgb|rgba)?\s*(?:\(?\s*{rgb_part}\s*\)?)"
        )

    @staticmethod
    def hsla_str(fix_sep: str = ",", allow_alpha: bool = True) -> str:
        """Matches a HSLA color inside a string.\n
        ----------------------------------------------------------------------------
        The HSLA color can be in the formats (for `fix_sep = ','`):
        - `hsla(h, s, l)`
        - `hsla(h, s, l, a)` (if `allow_alpha=True`)
        - `(h, s, l)`
        - `(h, s, l, a)` (if `allow_alpha=True`)
        - `h, s, l`
        - `h, s, l, a` (if `allow_alpha=True`)\n
        #### Valid ranges:
        - `h` 0-360 (int: hue)
        - `s` 0-100 (int: saturation)
        - `l` 0-100 (int: lightness)
        - `a` 0.0-1.0 (float: opacity)\n
        ----------------------------------------------------------------------------
        If the `fix_sep` is set to nothing, any char that is not a letter or number
        can be used to separate the HSLA values, including just a space."""
        if fix_sep in (None, ""):
            fix_sep = r"[^0-9A-Z]"
        else:
            fix_sep = _re.escape(fix_sep)
        hsl_part = rf"""((?:0*(?:360|3[0-5][0-9]|[12][0-9][0-9]|[1-9]?[0-9]))(?:\s*°)?)
            (?:\s*{fix_sep}\s*)((?:0*(?:100|[1-9][0-9]|[0-9]))(?:\s*%)?)
            (?:\s*{fix_sep}\s*)((?:0*(?:100|[1-9][0-9]|[0-9]))(?:\s*%)?)"""
        return (
            rf"""(?ix)
            (?:hsl|hsla)?\s*(?:\(?\s*{hsl_part}
                (?:(?:\s*{fix_sep}\s*)((?:0*(?:0?\.[0-9]+|1\.0+|[0-9]+\.[0-9]+|[0-9]+))))?
            \s*\)?)""" if allow_alpha else rf"(?ix)(?:hsl|hsla)?\s*(?:\(?\s*{hsl_part}\s*\)?)"
        )

    @staticmethod
    def hexa_str(allow_alpha: bool = True) -> str:
        """Matches a HEXA color inside a string.\n
        ----------------------------------------------------------------------
        The HEXA color can be in the formats (prefix `#`, `0x` or no prefix):
        - `RGB`
        - `RGBA` (if `allow_alpha=True`)
        - `RRGGBB`
        - `RRGGBBAA` (if `allow_alpha=True`)\n
        #### Valid ranges:
        every channel from 0-9 and A-F (case insensitive)"""
        return (
            r"(?i)^(?:#|0x)?[0-9A-F]{8}|[0-9A-F]{6}|[0-9A-F]{4}|[0-9A-F]{3}$"
            if allow_alpha else r"(?i)^(?:#|0x)?[0-9A-F]{6}|[0-9A-F]{3}$"
        )
