"""
This module provides the `Regex` class, which includes methods
to dynamically generate complex regex patterns for common use cases.
"""

from typing import Optional
import regex as _rx
import re as _re

try:
    from mypy_extensions import mypyc_attr  # type: ignore[import]
except ImportError:

    def __mypyc_attr_decorator(cls):
        return cls

    def mypyc_attr(*args, **kwargs):  # type: ignore[misc]
        return __mypyc_attr_decorator


class Regex:
    """This class provides methods to dynamically generate complex regex patterns for common use cases."""

    @classmethod
    def quotes(cls) -> str:
        """Matches pairs of quotes. (strings)\n
        --------------------------------------------------------------------------------
        Will create two named groups:
        - `quote` the quote type (single or double)
        - `string` everything inside the found quote pair\n
        ---------------------------------------------------------------------------------
        Attention: Requires non-standard library `regex`, not standard library `re`!"""
        return r"""(?P<quote>["'])(?P<string>(?:\\.|(?!\g<quote>).)*?)\g<quote>"""

    @classmethod
    def brackets(
        cls,
        bracket1: str = "(",
        bracket2: str = ")",
        is_group: bool = False,
        strip_spaces: bool = False,
        ignore_in_strings: bool = True,
    ) -> str:
        """Matches everything inside pairs of brackets, including other nested brackets.\n
        ---------------------------------------------------------------------------------------
        - `bracket1` -⠀the opening bracket (e.g. `(`, `{`, `[` ...)
        - `bracket2` -⠀the closing bracket (e.g. `)`, `}`, `]` ...)
        - `is_group` -⠀whether to create a capturing group for the content inside the brackets
        - `strip_spaces` -⠀whether to strip spaces from the bracket content or not
        - `ignore_in_strings` -⠀whether to ignore closing brackets that are inside
          strings/quotes (e.g. `'…)…'` or `"…)…"`)\n
        ---------------------------------------------------------------------------------------
        Attention: Requires non-standard library `regex`, not standard library `re`!"""
        g = "" if is_group else "?:"
        b1 = _rx.escape(bracket1) if len(bracket1) == 1 else bracket1
        b2 = _rx.escape(bracket2) if len(bracket2) == 1 else bracket2
        s1 = r"\s*" if strip_spaces else ""
        s2 = "" if strip_spaces else r"\s*"

        if ignore_in_strings:
            return cls._clean( \
                rf"""{b1}{s1}({g}{s2}(?:
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
            )
        else:
            return cls._clean( \
                rf"""{b1}{s1}({g}{s2}(?:
                    [^{b1}{b2}]
                    |{b1}(?:
                        [^{b1}{b2}]
                        |(?R)
                    )*{b2}
                )*{s2}){s1}{b2}"""
            )

    @classmethod
    def outside_strings(cls, pattern: str = r".*") -> str:
        """Matches the `pattern` only when it is not found inside a string (`'...'` or `"..."`)."""
        return rf"""(?<!["'])(?:{pattern})(?!["'])"""

    @classmethod
    def all_except(cls, disallowed_pattern: str, ignore_pattern: str = "", is_group: bool = False) -> str:
        """Matches everything up to the `disallowed_pattern`, unless the
        `disallowed_pattern` is found inside a string/quotes (`'…'` or `"…"`).\n
        -------------------------------------------------------------------------------------
        - `disallowed_pattern` -⠀the pattern that is not allowed to be matched
        - `ignore_pattern` -⠀a pattern that, if found, will make the regex ignore the
          `disallowed_pattern` (even if it contains the `disallowed_pattern` inside it):<br>
          For example if `disallowed_pattern` is `>` and `ignore_pattern` is `->`,
          the `->`-arrows will be allowed, even though they have `>` in them.
        - `is_group` -⠀whether to create a capturing group for the matched content"""
        g = "" if is_group else "?:"

        return cls._clean( \
            rf"""({g}
                (?:(?!{ignore_pattern}).)*
                (?:(?!{cls.outside_strings(disallowed_pattern)}).)*
            )"""
        )

    @classmethod
    def func_call(cls, func_name: Optional[str] = None) -> str:
        """Match a function call, and get back two groups:
        1. function name
        2. the function's arguments\n
        If no `func_name` is given, it will match any function call.\n
        ---------------------------------------------------------------------------------
        Attention: Requires non-standard library `regex`, not standard library `re`!"""
        if func_name in {"", None}:
            func_name = r"[\w_]+"

        return rf"""(?<=\b)({func_name})\s*{cls.brackets("(", ")", is_group=True)}"""

    @classmethod
    def rgba_str(cls, fix_sep: Optional[str] = ",", allow_alpha: bool = True) -> str:
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
        fix_sep = _re.escape(fix_sep) if isinstance(fix_sep, str) else r"[^0-9A-Z]"

        rgb_part = rf"""((?:0*(?:25[0-5]|2[0-4][0-9]|1?[0-9]{{1,2}})))
            (?:\s*{fix_sep}\s*)((?:0*(?:25[0-5]|2[0-4][0-9]|1?[0-9]{{1,2}})))
            (?:\s*{fix_sep}\s*)((?:0*(?:25[0-5]|2[0-4][0-9]|1?[0-9]{{1,2}})))"""

        if allow_alpha:
            return cls._clean( \
                rf"""(?ix)(?:rgb|rgba)?\s*(?:
                    \(?\s*{rgb_part}
                        (?:(?:\s*{fix_sep}\s*)((?:0*(?:0?\.[0-9]+|1\.0+|[0-9]+\.[0-9]+|[0-9]+))))?
                    \s*\)?
                )"""
            )
        else:
            return cls._clean( \
                rf"""(?ix)(?:rgb|rgba)?\s*(?:
                    \(?\s*{rgb_part}\s*\)?
                )"""
            )

    @classmethod
    def hsla_str(cls, fix_sep: Optional[str] = ",", allow_alpha: bool = True) -> str:
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
        fix_sep = _re.escape(fix_sep) if isinstance(fix_sep, str) else r"[^0-9A-Z]"

        hsl_part = rf"""((?:0*(?:360|3[0-5][0-9]|[12][0-9][0-9]|[1-9]?[0-9])))(?:\s*°)?
            (?:\s*{fix_sep}\s*)((?:0*(?:100|[1-9][0-9]|[0-9])))(?:\s*%)?
            (?:\s*{fix_sep}\s*)((?:0*(?:100|[1-9][0-9]|[0-9])))(?:\s*%)?"""

        if allow_alpha:
            return cls._clean( \
                rf"""(?ix)(?:hsl|hsla)?\s*(?:
                    \(?\s*{hsl_part}
                        (?:(?:\s*{fix_sep}\s*)((?:0*(?:0?\.[0-9]+|1\.0+|[0-9]+\.[0-9]+|[0-9]+))))?
                    \s*\)?
                )"""
            )
        else:
            return cls._clean( \
                rf"""(?ix)(?:hsl|hsla)?\s*(?:
                    \(?\s*{hsl_part}\s*\)?
                )"""
            )

    @classmethod
    def hexa_str(cls, allow_alpha: bool = True) -> str:
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
        return r"(?i)(?:#|0x)?([0-9A-F]{8}|[0-9A-F]{6}|[0-9A-F]{4}|[0-9A-F]{3})" \
            if allow_alpha else r"(?i)(?:#|0x)?([0-9A-F]{6}|[0-9A-F]{3})"

    @classmethod
    def _clean(cls, pattern: str) -> str:
        """Internal method to make a multiline-string regex pattern into a single-line pattern."""
        return "".join(l.strip() for l in pattern.splitlines()).strip()


@mypyc_attr(native_class=False)
class LazyRegex:
    """A class that lazily compiles and caches regex patterns on first access.\n
    --------------------------------------------------------------------------------
    - `**patterns` -⠀keyword arguments where the key is the name of the pattern and
      the value is the regex pattern string to compile\n
    --------------------------------------------------------------------------------
    #### Example usage:
    ```python
    PATTERNS = LazyRegex(
        email=r"(?i)[A-Z0-9._%+-]+@[A-Z0-9.-]+\\.[A-Z]{2,}",
        phone=r"\\+?\\d{1,3}[-.\\s]?\\(?\\d{1,4}\\)?[-.\\s]?\\d{1,4}[-.\\s]?\\d{1,9}",
    )

    email_pattern = PATTERNS.email  # Compiles and caches the EMAIL pattern
    phone_pattern = PATTERNS.phone  # Compiles and caches the PHONE pattern
    ```"""

    def __init__(self, **patterns: str):
        self._patterns = patterns

    def __getattr__(self, name: str) -> _rx.Pattern:
        if name in self._patterns:
            setattr(self, name, compiled := _rx.compile(self._patterns[name]))
            return compiled

        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
