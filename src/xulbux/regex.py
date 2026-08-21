"""
Provides utilities for dynamic regex pattern generation and evaluation.

Includes a `LazyRegex` class for deferred compilation, improving
startup performance for large libraries.
"""

from .base.decorators import mypyc_attr

import regex as _rx


def quotes() -> str:
    """Matches pairs of quotes. (strings)\n
    ----------------------------------------------------------------------------------------------------
    Will create two named groups:
    *   `quote` – The quote type (single or double).
    *   `string` – Everything inside the found quote pair.\n
    ----------------------------------------------------------------------------------------------------
    **Attention:** Requires non-standard library `regex`, not standard library `re`!\n
    ----------------------------------------------------------------------------------------------------
    #### Example Usage

    ```python
    import xulbux as xx
    import regex

    pattern = xx.regex.quotes()
    text = "Some text with 'single quotes' and \\"double quotes\\"."
    matches = regex.findall(pattern, text)
    ```

    <!-- DOCS: <AttachedCode> -->
    Matches:

    ```python
    [
        ("'", "single quotes"),
        ('"', "double quotes")
    ]
    ```
    <!-- DOCS: </AttachedCode> -->"""

    return r"""(?P<quote>["'])(?P<string>(?:\\.|(?!\g<quote>).)*?)\g<quote>"""


def brackets(
    bracket1: str = "(",
    bracket2: str = ")",
    /,
    *,
    is_group: bool = False,
    strip_spaces: bool = False,
    ignore_in_strings: bool = True,
) -> str:
    """Matches everything inside pairs of brackets, including other nested brackets.\n
    ----------------------------------------------------------------------------------------------------
    *   `bracket1` – The opening bracket (e.g., `(`, `{`, `[`, …).
    *   `bracket2` – The closing bracket (e.g., `)`, `}`, `]`, …).
    *   `is_group` – Whether to create a capturing group for the content inside the brackets.
    *   `strip_spaces` – Whether to strip spaces from the bracket content or not.
    *   `ignore_in_strings` – Whether to ignore closing brackets that are inside
        strings/quotes (e.g., `'…)…'` or `"…)…"`).\n
    ----------------------------------------------------------------------------------------------------
    **Attention:** Requires non-standard library `regex`, not standard library `re`!\n
    ----------------------------------------------------------------------------------------------------
    #### Example Usages

    **Default brackets:**

    ```python
    import xulbux as xx
    import regex

    pattern = xx.regex.brackets()
    text = "This (is a test) with (nested (brackets))."
    # Use `overlapped=True` to extract nested overlapping brackets:
    matches = regex.findall(pattern, text, overlapped=True)
    ```

    <!-- DOCS: <AttachedCode> -->
    Matches:

    ```python
    [
        "(is a test)",
        "(nested (brackets))",
        "(brackets)"
    ]
    ```
    <!-- DOCS: </AttachedCode> -->

    **Custom brackets:**

    ```python
    import xulbux as xx
    import regex

    pattern = xx.regex.brackets("[", "]", is_group=True)
    text = "List of items: [item1, item2 [nested item]]"
    matches = regex.findall(pattern, text, overlapped=True)
    ```

    <!-- DOCS: <AttachedCode> -->
    Matches:

    ```python
    [
        "item1, item2 [nested item]",
        "nested item"
    ]
    ```
    <!-- DOCS: </AttachedCode> -->

    **Without ignoring strings:**

    ```python
    import xulbux as xx
    import regex

    pattern = xx.regex.brackets(ignore_in_strings=False)
    text = 'func(param = "f(x)")'
    matches = regex.findall(pattern, text, overlapped=True)
    ```

    <!-- DOCS: <AttachedCode> -->
    Matches:

    ```python
    [
        "(param = \"f(x)\")",
        "(x)"
    ]
    ```
    <!-- DOCS: </AttachedCode> -->

    **Without stripping spaces:**

    ```python
    import xulbux as xx
    import regex

    pattern = xx.regex.brackets(strip_spaces=False)
    text = " ( spaced content ) and (regular content) "
    matches = regex.findall(pattern, text)
    ```

    <!-- DOCS: <AttachedCode> -->
    Matches:

    ```python
    [
        "( spaced content )",
        "(regular content)"
    ]
    ```
    <!-- DOCS: </AttachedCode> -->"""

    gr = "" if is_group else "?:"
    b1 = _rx.escape(bracket1) if len(bracket1) == 1 else bracket1
    b2 = _rx.escape(bracket2) if len(bracket2) == 1 else bracket2
    s1 = r"\s*" if strip_spaces else ""
    s2 = "" if strip_spaces else r"\s*"

    if ignore_in_strings:
        return rf"""(?x){b1}{s1}({gr}{s2}(?:
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
        return rf"""(?x){b1}{s1}({gr}{s2}(?:
                [^{b1}{b2}]
                |{b1}(?:
                    [^{b1}{b2}]
                    |(?R)
                )*{b2}
            )*{s2}){s1}{b2}"""


def outside_strings(pattern: str = r".*", /) -> str:
    """Matches the `pattern` only when it is not found inside a string (`'…'` or `"…"`).\n
    ----------------------------------------------------------------------------------------------------
    *   `pattern` – The pattern to match outside of strings/quotes.\n
    ----------------------------------------------------------------------------------------------------
    #### Example Usage

    ```python
    import xulbux as xx
    import re

    pattern = xx.regex.outside_strings(r"\\d+")
    text = 'Number 123 and "string 456" and 789'
    matches = re.findall(pattern, text)
    ```

    <!-- DOCS: <AttachedCode> -->
    Matches:

    ```python
    [
        "123",
        "789"
    ]
    ```
    <!-- DOCS: </AttachedCode> -->"""

    return rf"""(?<!["'])(?:{pattern})(?!["'])"""


def all_except(disallowed_pattern: str, /, ignore_pattern: str = "", *, is_group: bool = False) -> str:
    """Matches everything up to the `disallowed_pattern`, unless the<br>
    `disallowed_pattern` is found inside a string/quotes (`'…'` or `"…"`).\n
    ----------------------------------------------------------------------------------------------------
    *   `disallowed_pattern` – The pattern that is not allowed to be matched.
    *   `ignore_pattern` – A pattern that, if found, will make the regex ignore the<br>
        `disallowed_pattern` (even if it contains the `disallowed_pattern` inside it):<br>
        For example if `disallowed_pattern` is `>` and `ignore_pattern` is `->`,<br>
        the `->`-arrows will be allowed, even though they have `>` in them.
    *   `is_group` – Whether to create a capturing group for the matched content.\n
    ----------------------------------------------------------------------------------------------------
    #### Example Usages

    **Single exclusion:**

    ```python
    import xulbux as xx
    import re

    pattern = xx.regex.all_except(">")
    text = "Hello > World"
    matches = re.match(pattern, text)
    ```

    <!-- DOCS: <AttachedCode> -->
    Matches:

    ```python
    [
        "Hello "
    ]
    ```
    <!-- DOCS: </AttachedCode> -->

    **Multiple exclusions:**

    ```python
    import xulbux as xx
    import re

    pattern = xx.regex.all_except(">", "->")
    text = "Arrow -> and greater > sign"
    match = re.match(pattern, text)
    ```

    <!-- DOCS: <AttachedCode> -->
    Matches:

    ```python
    [
        "Arrow -> and greater "
    ]
    ```
    <!-- DOCS: </AttachedCode> -->"""

    gr = "" if is_group else "?:"

    return rf"""(?x)({gr}
            (?:(?!{ignore_pattern}).)*
            (?:(?!{outside_strings(disallowed_pattern)}).)*
        )"""


def func_call(func_name: str | None = None, /) -> str:
    """Match a function call in code, including its arguments.\n
    ----------------------------------------------------------------------------------------------------
    *   `func_name` – The name of the function to match.
        If `None`, it will match any function call.\n
    ----------------------------------------------------------------------------------------------------
    Will create two groups:
    1.  The function name (or any function name if `func_name` is `None`).
    2.  Everything inside the function call's parentheses (the arguments).\n
    ----------------------------------------------------------------------------------------------------
    **Attention:** Requires non-standard library `regex`, not standard library `re`!\n
    ----------------------------------------------------------------------------------------------------
    #### Example Usages

    **Any function:**

    ```python
    import xulbux as xx
    import regex

    pattern = xx.regex.func_call()
    text = "Call print('hello') and input('prompt')"
    matches = regex.findall(pattern, text)
    ```

    <!-- DOCS: <AttachedCode> -->
    Matches:

    ```python
    [
        ("print", "'hello'"),
        ("input", "'prompt'")
    ]
    ```
    <!-- DOCS: </AttachedCode> -->

    **Specific function:**

    ```python
    import xulbux as xx
    import regex

    pattern = xx.regex.func_call("input")
    text = "Call print('hello') and input('prompt') and print('world')"
    matches = regex.findall(pattern, text)
    ```

    <!-- DOCS: <AttachedCode> -->
    Matches:

    ```python
    [
        ("input", "'prompt'")
    ]
    ```
    <!-- DOCS: </AttachedCode> -->"""

    if func_name in {"", None}:
        func_name = r"[\w_]+"

    return rf"""(?<=\b)({func_name})\s*{brackets("(", ")", is_group=True)}"""


def rgba_str(fix_sep: str | None = ",", *, allow_alpha: bool = True) -> str:
    """Matches an RGBA color inside a string.\n
    ----------------------------------------------------------------------------------------------------
    *   `fix_sep` – The fixed separator between the RGBA values (e.g., `,`, `;` …):<br>
        If set to nothing or `None`, any char that is not a letter or number<br>
        can be used to separate the RGBA values, including just a space.
    *   `allow_alpha` – Whether to include the alpha channel in the match.\n
    ----------------------------------------------------------------------------------------------------
    #### Valid Formats

    With `fix_sep = ','`, the RGBA color can be in the formats:
    *   `rgba(red, green, blue)`
    *   `rgba(red, green, blue, alpha)` (if `allow_alpha=True`)
    *   `(red, green, blue)`
    *   `(red, green, blue, alpha)` (if `allow_alpha=True`)
    *   `red, green, blue`
    *   `red, green, blue, alpha` (if `allow_alpha=True`)\n

    #### Valid Ranges
    *   `red` 0-255 (int: red)
    *   `green` 0-255 (int: green)
    *   `blue` 0-255 (int: blue)
    *   `alpha` 0.0-1.0 (float: opacity)\n
    ----------------------------------------------------------------------------------------------------
    #### Example Usages

    **Default pattern:**

    ```python
    import xulbux as xx
    import re

    pattern = xx.regex.rgba_str()
    text = "Color rgba(255, 128, 0) and (100, 200, 50, 0.5)"
    matches = re.findall(pattern, text)
    ```

    <!-- DOCS: <AttachedCode> -->
    Matches:

    ```python
    [
        ("255", "128", "0", ""),
        ("100", "200", "50", "0.5")
    ]
    ```
    <!-- DOCS: </AttachedCode> -->

    **No alpha allowed:**

    ```python
    import xulbux as xx
    import re

    pattern = xx.regex.rgba_str(allow_alpha=False)
    text = "Color with rgb(255, 128, 0, 0.5) and without opacity rgb(255, 0, 0)"
    matches = re.findall(pattern, text)
    ```

    <!-- DOCS: <AttachedCode> -->
    Matches:

    ```python
    [
        ("255", "128", "0"),
        ("255", "0", "0")
    ]
    ```
    <!-- DOCS: </AttachedCode> -->

    **Custom separator:**

    ```python
    import xulbux as xx
    import re

    pattern = xx.regex.rgba_str(fix_sep="|")
    text = "Color 255|128|0"
    matches = re.findall(pattern, text)
    ```

    <!-- DOCS: <AttachedCode> -->
    Matches:

    ```python
    [
        ("255", "128", "0", "")
    ]
    ```
    <!-- DOCS: </AttachedCode> -->"""

    fix_sep = _rx.escape(fix_sep) if isinstance(fix_sep, str) else r"[^0-9A-Z]"

    rgb_part = rf"""((?:0*(?:25[0-5]|2[0-4][0-9]|1?[0-9]{{1,2}})))
        (?:\s*{fix_sep}\s*)((?:0*(?:25[0-5]|2[0-4][0-9]|1?[0-9]{{1,2}})))
        (?:\s*{fix_sep}\s*)((?:0*(?:25[0-5]|2[0-4][0-9]|1?[0-9]{{1,2}})))"""

    if allow_alpha:
        return rf"""(?ix)(?:rgb|rgba)?\s*(?:
                \(?\s*{rgb_part}
                    (?:(?:\s*{fix_sep}\s*)((?:0*(?:0?\.[0-9]+|1\.0+|[0-9]+\.[0-9]+|[0-9]+))))?
                \s*\)?
            )"""
    else:
        return rf"""(?ix)(?:rgb|rgba)?\s*(?:
                \(?\s*{rgb_part}\s*\)?
            )"""


def hsla_str(fix_sep: str | None = ",", *, allow_alpha: bool = True) -> str:
    """Matches a HSLA color inside a string.\n
    ----------------------------------------------------------------------------------------------------
    *   `fix_sep` – The fixed separator between the HSLA values (e.g., `,`, `;` …):<br>
        If set to nothing or `None`, any char that is not a letter or number<br>
        can be used to separate the HSLA values, including just a space.
    *   `allow_alpha` – Whether to include the alpha channel in the match.\n
    ----------------------------------------------------------------------------------------------------
    #### Valid Formats

    With `fix_sep = ','`, the HSLA color can be in the formats:
    *   `hsla(hue, sat, light)`
    *   `hsla(hue, sat, light, alpha)` (if `allow_alpha=True`)
    *   `(hue, sat, light)`
    *   `(hue, sat, light, alpha)` (if `allow_alpha=True`)
    *   `hue, sat, light`
    *   `hue, sat, light, alpha` (if `allow_alpha=True`)\n

    #### Valid Ranges
    *   `hue` 0-360 (int: hue)
    *   `sat` 0-100 (int: saturation)
    *   `light` 0-100 (int: lightness)
    *   `alpha` 0.0-1.0 (float: opacity)\n
    ----------------------------------------------------------------------------------------------------
    #### Example Usages

    **Default pattern:**

    ```python
    import xulbux as xx
    import re

    pattern = xx.regex.hsla_str()
    text = "Color hsla(240°, 100%, 50%) and (120, 80, 60, 0.8)"
    matches = re.findall(pattern, text)
    ```

    <!-- DOCS: <AttachedCode> -->
    Matches:

    ```python
    [
        ("240", "100", "50", ""),
        ("120", "80", "60", "0.8")
    ]
    ```
    <!-- DOCS: </AttachedCode> -->

    **No alpha allowed:**

    ```python
    import xulbux as xx
    import re

    pattern = xx.regex.hsla_str(allow_alpha=False)
    text = "Color with hsl(240, 100%, 50%, 0.5) and without opacity hsl(360, 100%, 50%)"
    matches = re.findall(pattern, text)
    ```

    <!-- DOCS: <AttachedCode> -->
    Matches:

    ```python
    [
        ("240", "100", "50"),
        ("360", "100", "50")
    ]
    ```
    <!-- DOCS: </AttachedCode> -->

    **Custom separator:**

    ```python
    import xulbux as xx
    import re

    pattern = xx.regex.hsla_str(fix_sep=" ")
    text = "Color 240 100% 50%"
    matches = re.findall(pattern, text)
    ```

    <!-- DOCS: <AttachedCode> -->
    Matches:

    ```python
    [
        ("240", "100", "50", "")
    ]
    ```
    <!-- DOCS: </AttachedCode> -->"""

    fix_sep = _rx.escape(fix_sep) if isinstance(fix_sep, str) else r"[^0-9A-Z]"

    hsl_part = rf"""((?:0*(?:360|3[0-5][0-9]|[12][0-9][0-9]|[1-9]?[0-9])))(?:\s*°)?
        (?:\s*{fix_sep}\s*)((?:0*(?:100|[1-9][0-9]|[0-9])))(?:\s*%)?
        (?:\s*{fix_sep}\s*)((?:0*(?:100|[1-9][0-9]|[0-9])))(?:\s*%)?"""

    if allow_alpha:
        return rf"""(?ix)(?:hsl|hsla)?\s*(?:
                \(?\s*{hsl_part}
                    (?:(?:\s*{fix_sep}\s*)((?:0*(?:0?\.[0-9]+|1\.0+|[0-9]+\.[0-9]+|[0-9]+))))?
                \s*\)?
            )"""
    else:
        return rf"""(?ix)(?:hsl|hsla)?\s*(?:
                \(?\s*{hsl_part}\s*\)?
            )"""


def hexa_str(*, allow_alpha: bool = True) -> str:
    """Matches a HEXA color inside a string.\n
    ----------------------------------------------------------------------------------------------------
    *   `allow_alpha` – Whether to include the alpha channel in the match.\n
    ----------------------------------------------------------------------------------------------------
    #### Valid Formats

    The HEXA color can be in the formats (prefix `#`, `0x` or no prefix):
    *   `RGB`
    *   `RGBA` (if `allow_alpha=True`)
    *   `RRGGBB`
    *   `RRGGBBAA` (if `allow_alpha=True`)\n

    #### Valid Ranges
    Every channel from 0-9 and A-F (case insensitive)\n
    ----------------------------------------------------------------------------------------------------
    #### Example Usages

    **Default pattern:**

    ```python
    import xulbux as xx
    import re

    pattern = xx.regex.hexa_str()
    text = "Colors: #FF0000, 0xABCDEF, F00 and FF000080"
    matches = re.findall(pattern, text)
    ```

    <!-- DOCS: <AttachedCode> -->
    Matches:

    ```python
    [
        "FF0000",
        "ABCDEF",
        "F00",
        "FF0000FF"
    ]
    ```
    <!-- DOCS: </AttachedCode> -->

    **No alpha allowed:**

    ```python
    import xulbux as xx
    import re

    pattern = xx.regex.hexa_str(allow_alpha=False)
    text = "Without #FF0000 #F00 and with opacity #FF000080 #F008"
    matches = re.findall(pattern, text)
    ```

    <!-- DOCS: <AttachedCode> -->
    Matches:

    ```python
    [
        "FF0000",
        "F00",
        "FF0000",
        "F00"
    ]
    ```
    <!-- DOCS: </AttachedCode> -->"""

    return (
        r"(?i)(?:#|0x)?([0-9A-F]{8}|[0-9A-F]{6}|[0-9A-F]{4}|[0-9A-F]{3})"
        if allow_alpha
        else r"(?i)(?:#|0x)?([0-9A-F]{6}|[0-9A-F]{3})"
    )


@mypyc_attr(native_class=False)
class LazyRegex:
    """A class that lazily compiles and caches regex patterns on first access.\n
    ----------------------------------------------------------------------------------------------------
    *   `**patterns` – Keyword arguments where the key is the name of the pattern<br>
        and the value is the regex pattern string to compile.\n
    ----------------------------------------------------------------------------------------------------
    **Attention:** Requires non-standard library `regex`, not standard library `re`!\n
    ----------------------------------------------------------------------------------------------------
    #### Example Usage

    ```python
    PATTERNS = LazyRegex(
        email=r"(?i)[A-Z0-9._%+-]+@[A-Z0-9.-]+\\.[A-Z]{2,}",
        phone=r"\\+?\\d{1,3}[-.\\s]?\\(?\\d{1,4}\\)?[-.\\s]?\\d{1,4}[-.\\s]?\\d{1,9}",
    )

    # Accessing `email` compiles and caches it for future use:
    match = PATTERNS.email.match("test@example.com")
    # Accessing `phone` compiles and caches it for future use:
    match = PATTERNS.phone.fullmatch("+1 (555) 123-4567")
    ```"""

    def __init__(self, **patterns: str) -> None:
        self._patterns: dict[str, str] = patterns

    def __getattr__(self, name: str, /) -> _rx.Pattern[str]:
        if name in self._patterns:
            setattr(self, name, compiled := _rx.compile(self._patterns[name]))
            return compiled

        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
