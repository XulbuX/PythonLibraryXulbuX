from typing import TypeAlias, Optional
import regex as _rx
import re as _re


Pattern: TypeAlias = _re.Pattern[str] | _rx.Pattern[str]
Match: TypeAlias = _re.Match[str] | _rx.Match[str]


class Regex:

    @staticmethod
    def quotes() -> str:
        """Matches pairs of quotes. (strings)\n
        --------------------------------------------------------------------------------
        Will create two named groups:
        - `quote` the quote type (single or double)
        - `string` everything inside the found quote pair\n
        ---------------------------------------------------------------------------------
        Attention: Requires non-standard library `regex`, not standard library `re`!"""
        return r"""(?P<quote>["'])(?P<string>(?:\\.|(?!\g<quote>).)*?)\g<quote>"""

    @staticmethod
    def brackets(
        bracket1: str = "(",
        bracket2: str = ")",
        is_group: bool = False,
        strip_spaces: bool = True,
        ignore_in_strings: bool = True,
    ) -> str:
        """Matches everything inside pairs of brackets, including other nested brackets.\n
        ---------------------------------------------------------------------------------------
        - `bracket1` -⠀the opening bracket (e.g. `(`, `{`, `[` ...)
        - `bracket2` -⠀the closing bracket (e.g. `)`, `}`, `]` ...)
        - `is_group` -⠀whether to create a capturing group for the content inside the brackets
        - `strip_spaces` -⠀whether to ignore spaces around the content inside the brackets
        - `ignore_in_strings` -⠀whether to ignore closing brackets that are inside
          strings/quotes (e.g. `'…)…'` or `"…)…"`)\n
        ---------------------------------------------------------------------------------------
        Attention: Requires non-standard library `regex`, not standard library `re`!"""
        if not isinstance(bracket1, str):
            raise TypeError(f"The 'bracket1' parameter must be a string, got {type(bracket1)}")
        if not isinstance(bracket2, str):
            raise TypeError(f"The 'bracket2' parameter must be a string, got {type(bracket2)}")
        if not isinstance(is_group, bool):
            raise TypeError(f"The 'is_group' parameter must be a boolean, got {type(is_group)}")
        if not isinstance(strip_spaces, bool):
            raise TypeError(f"The 'strip_spaces' parameter must be a boolean, got {type(strip_spaces)}")
        if not isinstance(ignore_in_strings, bool):
            raise TypeError(f"The 'ignore_in_strings' parameter must be a boolean, got {type(ignore_in_strings)}")

        g = "" if is_group else "?:"
        b1 = _rx.escape(bracket1) if len(bracket1) == 1 else bracket1
        b2 = _rx.escape(bracket2) if len(bracket2) == 1 else bracket2
        s1 = r"\s*" if strip_spaces else ""
        s2 = "" if strip_spaces else r"\s*"

        if ignore_in_strings:
            return rf"""{b1}{s1}({g}{s2}(?:
                [^{b1}{b2}"']
                |"(?:\\.|[^"\\])*"
                |'(?:\\.|[^'\\])*'
                |{b1}(?:
                    [^{b1}{b2}"']
                    |"(?:\\.|[^"\\])*"
                    |'(?:\\.|[^'\\])*'
                    |(?R)
                )*{b2}
            )*{s2}){s1}{b2}"""
        else:
            return rf"""{b1}{s1}({g}{s2}(?:
                [^{b1}{b2}]
                |{b1}(?:
                    [^{b1}{b2}]
                    |(?R)
                )*{b2}
            )*{s2}){s1}{b2}"""

    @staticmethod
    def outside_strings(pattern: str = r".*") -> str:
        """Matches the `pattern` only when it is not found inside a string (`'...'` or `"..."`)."""
        if not isinstance(pattern, str):
            raise TypeError(f"The 'pattern' parameter must be a string, got {type(pattern)}")

        return rf"""(?<!["'])(?:{pattern})(?!["'])"""

    @staticmethod
    def all_except(disallowed_pattern: str, ignore_pattern: str = "", is_group: bool = False) -> str:
        """Matches everything up to the `disallowed_pattern`, unless the
        `disallowed_pattern` is found inside a string/quotes (`'…'` or `"…"`).\n
        -------------------------------------------------------------------------------------
        - `disallowed_pattern` -⠀the pattern that is not allowed to be matched
        - `ignore_pattern` -⠀a pattern that, if found, will make the regex ignore the
          `disallowed_pattern` (even if it contains the `disallowed_pattern` inside it):<br>
          For example if `disallowed_pattern` is `>` and `ignore_pattern` is `->`,
          the `->`-arrows will be allowed, even though they have `>` in them.
        - `is_group` -⠀whether to create a capturing group for the matched content"""
        if not isinstance(disallowed_pattern, str):
            raise TypeError(f"The 'disallowed_pattern' parameter must be a string, got {type(disallowed_pattern)}")
        if not isinstance(ignore_pattern, str):
            raise TypeError(f"The 'ignore_pattern' parameter must be a string, got {type(ignore_pattern)}")
        if not isinstance(is_group, bool):
            raise TypeError(f"The 'is_group' parameter must be a boolean, got {type(is_group)}")

        g = "" if is_group else "?:"

        return rf"""({g}
            (?:(?!{ignore_pattern}).)*
            (?:(?!{Regex.outside_strings(disallowed_pattern)}).)*
        )"""

    @staticmethod
    def func_call(func_name: Optional[str] = None) -> str:
        """Match a function call, and get back two groups:
        1. function name
        2. the function's arguments\n
        If no `func_name` is given, it will match any function call.\n
        ---------------------------------------------------------------------------------
        Attention: Requires non-standard library `regex`, not standard library `re`!"""
        if func_name is None:
            func_name = r"[\w_]+"
        else:
            if not isinstance(func_name, str):
                raise TypeError(f"The 'func_name' parameter must be a string or None, got {type(func_name)}")

        return rf"""(?<=\b)({func_name})\s*{Regex.brackets("(", ")", is_group=True)}"""

    @staticmethod
    def rgba_str(fix_sep: Optional[str] = ",", allow_alpha: bool = True) -> str:
        """Matches an RGBA color inside a string.\n
        ----------------------------------------------------------------------------------
        - `fix_sep` -⠀the fixed separator between the RGBA values (e.g. `,`, `;` ...)<br>
          If set to nothing or `None`, any char that is not a letter or number
          can be used to separate the RGBA values, including just a space.
        - `allow_alpha` -⠀whether to include the alpha channel in the match\n
        ----------------------------------------------------------------------------------
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
        - `a` 0.0-1.0 (float: opacity)"""
        if fix_sep in {"", None}:
            fix_sep = r"[^0-9A-Z]"
        elif isinstance(fix_sep, str):
            fix_sep = _re.escape(fix_sep)
        else:
            raise TypeError(f"The 'fix_sep' parameter must be a string or None, got {type(fix_sep)}")

        if not isinstance(allow_alpha, bool):
            raise TypeError(f"The 'allow_alpha' parameter must be a boolean, got {type(allow_alpha)}")

        rgb_part = rf"""((?:0*(?:25[0-5]|2[0-4][0-9]|1?[0-9]{{1,2}})))
            (?:\s*{fix_sep}\s*)((?:0*(?:25[0-5]|2[0-4][0-9]|1?[0-9]{{1,2}})))
            (?:\s*{fix_sep}\s*)((?:0*(?:25[0-5]|2[0-4][0-9]|1?[0-9]{{1,2}})))"""

        return rf"""(?ix)(?:rgb|rgba)?\s*(?:
            \(?\s*{rgb_part}
                (?:(?:\s*{fix_sep}\s*)((?:0*(?:0?\.[0-9]+|1\.0+|[0-9]+\.[0-9]+|[0-9]+))))?
            \s*\)?
        )""" if allow_alpha else \
        rf"""(?ix)(?:rgb|rgba)?\s*(?:
            \(?\s*{rgb_part}\s*\)?
        )"""

    @staticmethod
    def hsla_str(fix_sep: str = ",", allow_alpha: bool = True) -> str:
        """Matches a HSLA color inside a string.\n
        ----------------------------------------------------------------------------------
        - `fix_sep` -⠀the fixed separator between the HSLA values (e.g. `,`, `;` ...)<br>
          If set to nothing or `None`, any char that is not a letter or number
          can be used to separate the HSLA values, including just a space.
        - `allow_alpha` -⠀whether to include the alpha channel in the match\n
        ----------------------------------------------------------------------------------
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
        - `a` 0.0-1.0 (float: opacity)"""
        if fix_sep in {"", None}:
            fix_sep = r"[^0-9A-Z]"
        elif isinstance(fix_sep, str):
            fix_sep = _re.escape(fix_sep)
        else:
            raise TypeError(f"The 'fix_sep' parameter must be a string or None, got {type(fix_sep)}")

        if not isinstance(allow_alpha, bool):
            raise TypeError(f"The 'allow_alpha' parameter must be a boolean, got {type(allow_alpha)}")

        hsl_part = rf"""((?:0*(?:360|3[0-5][0-9]|[12][0-9][0-9]|[1-9]?[0-9])))(?:\s*°)?
            (?:\s*{fix_sep}\s*)((?:0*(?:100|[1-9][0-9]|[0-9])))(?:\s*%)?
            (?:\s*{fix_sep}\s*)((?:0*(?:100|[1-9][0-9]|[0-9])))(?:\s*%)?"""

        return rf"""(?ix)(?:hsl|hsla)?\s*(?:
            \(?\s*{hsl_part}
                (?:(?:\s*{fix_sep}\s*)((?:0*(?:0?\.[0-9]+|1\.0+|[0-9]+\.[0-9]+|[0-9]+))))?
            \s*\)?
        )""" if allow_alpha else \
        rf"""(?ix)(?:hsl|hsla)?\s*(?:
            \(?\s*{hsl_part}\s*\)?
        )"""

    @staticmethod
    def hexa_str(allow_alpha: bool = True) -> str:
        """Matches a HEXA color inside a string.\n
        ----------------------------------------------------------------------
        - `allow_alpha` -⠀whether to include the alpha channel in the match\n
        ----------------------------------------------------------------------
        The HEXA color can be in the formats (prefix `#`, `0x` or no prefix):
        - `RGB`
        - `RGBA` (if `allow_alpha=True`)
        - `RRGGBB`
        - `RRGGBBAA` (if `allow_alpha=True`)\n
        #### Valid ranges:
        every channel from 0-9 and A-F (case insensitive)"""
        if not isinstance(allow_alpha, bool):
            raise TypeError(f"The 'allow_alpha' parameter must be a boolean, got {type(allow_alpha)}")

        return r"(?i)(?:#|0x)?([0-9A-F]{8}|[0-9A-F]{6}|[0-9A-F]{4}|[0-9A-F]{3})" \
            if allow_alpha else r"(?i)(?:#|0x)?([0-9A-F]{6}|[0-9A-F]{3})"
