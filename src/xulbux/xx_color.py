"""
`rgba`:
    An RGB/RGBA color: is a tuple of 3 integers, representing the red (`0`-`255`), green (`0`-`255`), and blue (`0`-`255`).
    Also includes an optional 4th param, which is a float, that represents the alpha channel (`0.0`-`1.0`).
`hsla`:
    An HSL/HSB color: is a tuple of 3 integers, representing the hue (`0`-`360`), saturation (`0`-`100`), and lightness (`0`-`100`).
    Also includes an optional 4th param, which is a float, that represents the alpha channel (`0.0`-`1.0`).
`hexa`:
    A HEX color: is a string in the format `RGB`, `RGBA`, `RRGGBB` or `RRGGBBAA` (where `R` `G` `B` `A` are hexadecimal digits).

-------------------------------------------------------------------------------------------------------------------------------------
The `Color` class, which contains all sorts of different color-related methods:
- validate colors:
    - is valid rgba
    - is valid hsla
    - is valid hexa
    - is valid in any format
- check if a color has an alpha channel
- convert between different color formats:
    - color to rgba
    - color to hsla
    - color to hexa
- recognize colors inside strings and convert them to color types:
    - string to rgba
- convert an RGBA color to a HEX integer
- convert a HEX integer to an RGBA color
- get a colors luminance from the RGB channels
- get the optimal text color for on a colored background
- adjust different color channels:
    - brightness
    - saturation
"""

from .xx_regex import Regex

from typing import Annotated, TypeAlias, Iterator, Optional, Union
import re as _re


Int_0_255 = Annotated[int, "An integer value between 0 and 255, inclusive."]
Float_0_1 = Annotated[float, "A float value between 0.0 and 1.0, inclusive."]
Int_0_360 = Annotated[int, "An integer value between 0 and 360, inclusive."]
Int_0_100 = Annotated[int, "An integer value between 0 and 100, inclusive."]

Rgba: TypeAlias = Union[
    tuple[Int_0_255, Int_0_255, Int_0_255],
    tuple[Int_0_255, Int_0_255, Int_0_255, Float_0_1],
    list[Int_0_255],
    list[Union[Int_0_255, Float_0_1]],
    dict[str, Union[int, float]],
    "rgba",
    str,
]
Hsla: TypeAlias = Union[
    tuple[Int_0_360, Int_0_100, Int_0_100],
    tuple[Int_0_360, Int_0_100, Int_0_100, Float_0_1],
    list[Union[Int_0_360, Int_0_100]],
    list[Union[Int_0_360, Int_0_100, Float_0_1]],
    dict[str, Union[int, float]],
    "hsla",
    str,
]
Hexa: TypeAlias = Union[str, int, "hexa"]


class rgba:
    """An RGB/RGBA color: is a tuple of 3 integers, representing the red (`0`-`255`), green (`0`-`255`), and blue (`0`-`255`).\n
    Also includes an optional 4th param, which is a float, that represents the alpha channel (`0.0`-`1.0`).\n
    -----------------------------------------------------------------------------------------------------------------------------
    Includes methods:
    - `to_hsla()` to convert to HSL color
    - `to_hexa()` to convert to HEX color
    - `has_alpha()` to check if the color has an alpha channel
    - `lighten(amount)` to create a lighter version of the color
    - `darken(amount)` to create a darker version of the color
    - `saturate(amount)` to increase color saturation
    - `desaturate(amount)` to decrease color saturation
    - `rotate(degrees)` to rotate the hue by degrees
    - `invert()` to get the inverse color
    - `grayscale()` to convert to grayscale
    - `blend(other, ratio)` to blend with another color
    - `is_dark()` to check if the color is considered dark
    - `is_light()` to check if the color is considered light
    - `is_grayscale()` to check if the color is grayscale
    - `is_opaque()` to check if the color has no transparency
    - `with_alpha(alpha)` to create a new color with different alpha
    - `complementary()` to get the complementary color"""

    def __init__(self, r: int, g: int, b: int, a: Optional[float] = None, _validate: bool = True):
        if not _validate:
            self.r, self.g, self.b, self.a = r, g, b, a
            return
        if any(isinstance(x, rgba) for x in (r, g, b)):
            raise ValueError("Color is already a rgba() color")
        elif not all(isinstance(x, int) and 0 <= x <= 255 for x in (r, g, b)):
            raise ValueError(
                "RGBA color must have R G B as integers in [0, 255]: got",
                (r, g, b),
            )
        elif a is not None and not (isinstance(a, (int, float)) and 0 <= a <= 1):
            raise ValueError(f"Alpha channel must be a float/int in [0.0, 1.0]: got '{a}'")
        self.r, self.g, self.b = r, g, b
        self.a = None if a is None else (1.0 if a > 1.0 else float(a))

    def __len__(self) -> int:
        return 3 if self.a is None else 4

    def __iter__(self) -> Iterator:
        return iter((self.r, self.g, self.b) + (() if self.a is None else (self.a, )))

    def __getitem__(self, index: int) -> int | float:
        return ((self.r, self.g, self.b) + (() if self.a is None else (self.a, )))[index]

    def __repr__(self) -> str:
        return f'rgba({self.r}, {self.g}, {self.b}{"" if self.a is None else f", {self.a}"})'

    def __str__(self) -> str:
        return f'({self.r}, {self.g}, {self.b}{"" if self.a is None else f", {self.a}"})'

    def __eq__(self, other: "rgba") -> bool:
        if not isinstance(other, rgba):
            return False
        return (self.r, self.g, self.b, self.a) == (other.r, other.g, other.b, other.a)

    def dict(self) -> dict:
        """Returns the color components as a dictionary with keys `'r'`, `'g'`, `'b'` and optionally `'a'`"""
        return dict(r=self.r, g=self.g, b=self.b) if self.a is None else dict(r=self.r, g=self.g, b=self.b, a=self.a)

    def values(self) -> tuple:
        """Returns the color components as separate values `r, g, b, a`"""
        return self.r, self.g, self.b, self.a

    def to_hsla(self) -> "hsla":
        """Returns the color as a `hsla()` color"""
        return hsla(*self._rgb_to_hsl(self.r, self.g, self.b), self.a, _validate=False)

    def to_hexa(self) -> "hexa":
        """Returns the color as a `hexa()` color"""
        return hexa("", self.r, self.g, self.b, self.a)

    def has_alpha(self) -> bool:
        """Returns `True` if the color has an alpha channel and `False` otherwise"""
        return self.a is not None

    def lighten(self, amount: float) -> "rgba":
        """Increases the colors lightness by the specified amount (`0.0`-`1.0`)"""
        self.r, self.g, self.b, self.a = self.to_hsla().lighten(amount).to_rgba().values()
        return rgba(self.r, self.g, self.b, self.a, _validate=False)

    def darken(self, amount: float) -> "rgba":
        """Decreases the colors lightness by the specified amount (`0.0`-`1.0`)"""
        self.r, self.g, self.b, self.a = self.to_hsla().darken(amount).to_rgba().values()
        return rgba(self.r, self.g, self.b, self.a, _validate=False)

    def saturate(self, amount: float) -> "rgba":
        """Increases the colors saturation by the specified amount (`0.0`-`1.0`)"""
        self.r, self.g, self.b, self.a = self.to_hsla().saturate(amount).to_rgba().values()
        return rgba(self.r, self.g, self.b, self.a, _validate=False)

    def desaturate(self, amount: float) -> "rgba":
        """Decreases the colors saturation by the specified amount (`0.0`-`1.0`)"""
        self.r, self.g, self.b, self.a = self.to_hsla().desaturate(amount).to_rgba().values()
        return rgba(self.r, self.g, self.b, self.a, _validate=False)

    def rotate(self, degrees: int) -> "rgba":
        """Rotates the colors hue by the specified number of degrees"""
        self.r, self.g, self.b, self.a = self.to_hsla().rotate(degrees).to_rgba().values()
        return rgba(self.r, self.g, self.b, self.a, _validate=False)

    def invert(self, invert_alpha: bool = False) -> "rgba":
        """Inverts the color by rotating hue by 180 degrees and inverting lightness"""
        self.r, self.g, self.b = 255 - self.r, 255 - self.g, 255 - self.b
        if invert_alpha:
            self.a = 1 - self.a
        return rgba(self.r, self.g, self.b, self.a, _validate=False)

    def grayscale(self, method: str = "wcag2") -> "rgba":
        """Converts the color to grayscale using the luminance formula.\n
        ------------------------------------------------------------------
        The `method` is the luminance calculation method to use:
        - `"wcag2"` WCAG 2.0 standard (default and most accurate for perception)
        - `"wcag3"` Draft WCAG 3.0 standard with improved coefficients
        - `"simple"` Simple arithmetic mean (less accurate)
        - `"bt601"` ITU-R BT.601 standard (older TV standard)"""
        self.r = self.g = self.b = Color.luminance(self.r, self.g, self.b, method=method)
        return rgba(self.r, self.g, self.b, self.a, _validate=False)

    def blend(self, other: "rgba", ratio: float = 0.5, additive_alpha: bool = False) -> "rgba":
        """Blends the current color with another color using the specified ratio (`0.0`-`1.0`):
        - if `ratio` is `0.0` it means 100% of the current color and 0% of the `other` color (2:0 mixture)
        - if `ratio` is `0.5` it means 50% of both colors (1:1 mixture)
        - if `ratio` is `1.0` it means 0% of the current color and 100% of the `other` color (0:2 mixture)"""
        if not (isinstance(ratio, (int, float)) and 0 <= ratio <= 1):
            raise ValueError("'ratio' must be a float/int in [0.0, 1.0]")
        elif not isinstance(other, rgba):
            if Color.is_valid_rgba(other):
                other = rgba(*other, _validate=False)
            else:
                raise TypeError("'other' must be a valid RGBA color")
        ratio *= 2
        self.r = max(0, min(255, int(round((self.r * (2 - ratio)) + (other.r * ratio)))))
        self.g = max(0, min(255, int(round((self.g * (2 - ratio)) + (other.g * ratio)))))
        self.b = max(0, min(255, int(round((self.b * (2 - ratio)) + (other.b * ratio)))))
        none_alpha = self.a is None and (len(other) <= 3 or other[3] is None)
        if not none_alpha:
            self_a = 1 if self.a is None else self.a
            other_a = (other[3] if other[3] is not None else 1) if len(other) > 3 else 1
            if additive_alpha:
                self.a = max(0, min(1, (self_a * (2 - ratio)) + (other_a * ratio)))
            else:
                self.a = max(0, min(1, (self_a * (1 - (ratio / 2))) + (other_a * (ratio / 2))))
        else:
            self.a = None
        return rgba(self.r, self.g, self.b, None if none_alpha else self.a, _validate=False)

    def is_dark(self) -> bool:
        """Returns `True` if the color is considered dark (`lightness < 50%`)"""
        return self.to_hsla().is_dark()

    def is_light(self) -> bool:
        """Returns `True` if the color is considered light (`lightness >= 50%`)"""
        return not self.is_dark()

    def is_grayscale(self) -> bool:
        """Returns `True` if the color is grayscale"""
        return self.r == self.g == self.b

    def is_opaque(self) -> bool:
        """Returns `True` if the color has no transparency"""
        return self.a == 1 or self.a is None

    def with_alpha(self, alpha: float) -> "rgba":
        """Returns a new color with the specified alpha value"""
        if not (isinstance(alpha, (int, float)) and 0 <= alpha <= 1):
            raise ValueError("'alpha' must be a float/int in [0.0, 1.0]")
        return rgba(self.r, self.g, self.b, alpha, _validate=False)

    def complementary(self) -> "rgba":
        """Returns the complementary color (180 degrees on the color wheel)"""
        return self.to_hsla().complementary().to_rgba()

    def _rgb_to_hsl(self, r: int, g: int, b: int) -> tuple:
        r, g, b = r / 255.0, g / 255.0, b / 255.0
        max_c, min_c = max(r, g, b), min(r, g, b)
        l = (max_c + min_c) / 2
        if max_c == min_c:
            h = s = 0
        else:
            delta = max_c - min_c
            s = delta / (1 - abs(2 * l - 1))
            if max_c == r:
                h = ((g - b) / delta) % 6
            elif max_c == g:
                h = ((b - r) / delta) + 2
            else:
                h = ((r - g) / delta) + 4
            h /= 6
        return int(round(h * 360)), int(round(s * 100)), int(round(l * 100))


class hsla:
    """A HSL/HSLA color: is a tuple of 3 integers, representing hue (`0`-`360`), saturation (`0`-`100`), and lightness (`0`-`100`).\n
    Also includes an optional 4th param, which is a float, that represents the alpha channel (`0.0`-`1.0`).\n
    ----------------------------------------------------------------------------------------------------------------------------------
    Includes methods:
    - `to_rgba()` to convert to RGB color
    - `to_hexa()` to convert to HEX color
    - `has_alpha()` to check if the color has an alpha channel
    - `lighten(amount)` to create a lighter version of the color
    - `darken(amount)` to create a darker version of the color
    - `saturate(amount)` to increase color saturation
    - `desaturate(amount)` to decrease color saturation
    - `rotate(degrees)` to rotate the hue by degrees
    - `invert()` to get the inverse color
    - `grayscale()` to convert to grayscale
    - `blend(other, ratio)` to blend with another color
    - `is_dark()` to check if the color is considered dark
    - `is_light()` to check if the color is considered light
    - `is_grayscale()` to check if the color is grayscale
    - `is_opaque()` to check if the color has no transparency
    - `with_alpha(alpha)` to create a new color with different alpha
    - `complementary()` to get the complementary color"""

    def __init__(self, h: int, s: int, l: int, a: Optional[float] = None, _validate: bool = True):
        if not _validate:
            self.h, self.s, self.l, self.a = h, s, l, a
            return
        if any(isinstance(x, hsla) for x in (h, s, l)):
            raise ValueError("Color is already a hsla() color")
        elif not (isinstance(h, int) and (0 <= h <= 360) and all(isinstance(x, int) and (0 <= x <= 100) for x in (s, l))):
            raise ValueError(
                "HSL color must have H as integer in [0, 360] and S L as integers in [0, 100]: got",
                (h, s, l),
            )
        elif a is not None and (not isinstance(a, (int, float)) or not 0 <= a <= 1):
            raise ValueError(f"Alpha channel must be a float/int in [0.0, 1.0]: got '{a}'")
        self.h, self.s, self.l = h, s, l
        self.a = None if a is None else (1.0 if a > 1.0 else float(a))

    def __len__(self) -> int:
        return 3 if self.a is None else 4

    def __iter__(self) -> Iterator:
        return iter((self.h, self.s, self.l) + (() if self.a is None else (self.a, )))

    def __getitem__(self, index: int) -> int | float:
        return ((self.h, self.s, self.l) + (() if self.a is None else (self.a, )))[index]

    def __repr__(self) -> str:
        return f'hsla({self.h}°, {self.s}%, {self.l}%{"" if self.a is None else f", {self.a}"})'

    def __str__(self) -> str:
        return f'({self.h}°, {self.s}%, {self.l}%{"" if self.a is None else f", {self.a}"})'

    def __eq__(self, other: "hsla") -> bool:
        if not isinstance(other, hsla):
            return False
        return (self.h, self.s, self.l, self.a) == (other.h, other.s, other.l, other.a)

    def dict(self) -> dict:
        """Returns the color components as a dictionary with keys `'h'`, `'s'`, `'l'` and optionally `'a'`"""
        return dict(h=self.h, s=self.s, l=self.l) if self.a is None else dict(h=self.h, s=self.s, l=self.l, a=self.a)

    def values(self) -> tuple:
        """Returns the color components as separate values `h, s, l, a`"""
        return self.h, self.s, self.l, self.a

    def to_rgba(self) -> "rgba":
        """Returns the color as a `rgba()` color"""
        return rgba(*self._hsl_to_rgb(self.h, self.s, self.l), self.a, _validate=False)

    def to_hexa(self) -> "hexa":
        """Returns the color as a `hexa()` color"""
        r, g, b = self._hsl_to_rgb(self.h, self.s, self.l)
        return hexa("", r, g, b, self.a)

    def has_alpha(self) -> bool:
        """Returns `True` if the color has an alpha channel and `False` otherwise"""
        return self.a is not None

    def lighten(self, amount: float) -> "hsla":
        """Increases the colors lightness by the specified amount (`0.0`-`1.0`)"""
        if not (isinstance(amount, (int, float)) and 0 <= amount <= 1):
            raise ValueError("'amount' must be a float/int in [0.0, 1.0]")
        self.l = int(min(100, self.l + (100 - self.l) * amount))
        return hsla(self.h, self.s, self.l, self.a, _validate=False)

    def darken(self, amount: float) -> "hsla":
        """Decreases the colors lightness by the specified amount (`0.0`-`1.0`)"""
        if not (isinstance(amount, (int, float)) and 0 <= amount <= 1):
            raise ValueError("'amount' must be a float/int in [0.0, 1.0]")
        self.l = int(max(0, self.l * (1 - amount)))
        return hsla(self.h, self.s, self.l, self.a, _validate=False)

    def saturate(self, amount: float) -> "hsla":
        """Increases the colors saturation by the specified amount (`0.0`-`1.0`)"""
        if not (isinstance(amount, (int, float)) and 0 <= amount <= 1):
            raise ValueError("'amount' must be a float/int in [0.0, 1.0]")
        self.s = int(min(100, self.s + (100 - self.s) * amount))
        return hsla(self.h, self.s, self.l, self.a, _validate=False)

    def desaturate(self, amount: float) -> "hsla":
        """Decreases the colors saturation by the specified amount (`0.0`-`1.0`)"""
        if not (isinstance(amount, (int, float)) and 0 <= amount <= 1):
            raise ValueError("'amount' must be a float/int in [0.0, 1.0]")
        self.s = int(max(0, self.s * (1 - amount)))
        return hsla(self.h, self.s, self.l, self.a, _validate=False)

    def rotate(self, degrees: int) -> "hsla":
        """Rotates the colors hue by the specified number of degrees"""
        self.h = (self.h + degrees) % 360
        return hsla(self.h, self.s, self.l, self.a, _validate=False)

    def invert(self, invert_alpha: bool = False) -> "hsla":
        """Inverts the color by rotating hue by 180 degrees and inverting lightness"""
        self.h = (self.h + 180) % 360
        self.l = 100 - self.l
        if invert_alpha:
            self.a = 1 - self.a
        return hsla(self.h, self.s, self.l, self.a, _validate=False)

    def grayscale(self, method: str = "wcag2") -> "hsla":
        """Converts the color to grayscale using the luminance formula.\n
        ------------------------------------------------------------------
        The `method` is the luminance calculation method to use:
        - `"wcag2"` WCAG 2.0 standard (default and most accurate for perception)
        - `"wcag3"` Draft WCAG 3.0 standard with improved coefficients
        - `"simple"` Simple arithmetic mean (less accurate)
        - `"bt601"` ITU-R BT.601 standard (older TV standard)"""
        l = Color.luminance(*self._hsl_to_rgb(self.h, self.s, self.l), method=method)
        self.h, self.s, self.l, _ = rgba(l, l, l, _validate=False).to_hsla().values()
        return hsla(self.h, self.s, self.l, self.a, _validate=False)

    def blend(self, other: "hsla", ratio: float = 0.5, additive_alpha: bool = False) -> "hsla":
        """Blends the current color with another color using the specified ratio (`0.0`-`1.0`):
        - if `ratio` is `0.0` it means 100% of the current color and 0% of the `other` color (2:0 mixture)
        - if `ratio` is `0.5` it means 50% of both colors (1:1 mixture)
        - if `ratio` is `1.0` it means 0% of the current color and 100% of the `other` color (0:2 mixture)"""
        self.h, self.s, self.l, self.a = self.to_rgba().blend(Color.to_rgba(other), ratio, additive_alpha).to_hsla().values()
        return hsla(self.h, self.s, self.l, self.a, _validate=False)

    def is_dark(self) -> bool:
        """Returns `True` if the color is considered dark (`lightness < 50%`)"""
        return self.l < 50

    def is_light(self) -> bool:
        """Returns `True` if the color is considered light (`lightness >= 50%`)"""
        return not self.is_dark()

    def is_grayscale(self) -> bool:
        """Returns `True` if the color is considered grayscale"""
        return self.s == 0

    def is_opaque(self) -> bool:
        """Returns `True` if the color has no transparency"""
        return self.a == 1 or self.a is None

    def with_alpha(self, alpha: float) -> "hsla":
        """Returns a new color with the specified alpha value"""
        if not (isinstance(alpha, (int, float)) and 0 <= alpha <= 1):
            raise ValueError("'alpha' must be a float/int in [0.0, 1.0]")
        return hsla(self.h, self.s, self.l, alpha, _validate=False)

    def complementary(self) -> "hsla":
        """Returns the complementary color (180 degrees on the color wheel)"""
        return hsla((self.h + 180) % 360, self.s, self.l, self.a, _validate=False)

    def _hsl_to_rgb(self, h: int, s: int, l: int) -> tuple:
        _h, _s, _l = h / 360, s / 100, l / 100
        if _s == 0:
            r = g = b = int(_l * 255)
        else:

            def hue_to_rgb(p, q, t):
                if t < 0:
                    t += 1
                if t > 1:
                    t -= 1
                if t < 1 / 6:
                    return p + (q - p) * 6 * t
                if t < 1 / 2:
                    return q
                if t < 2 / 3:
                    return p + (q - p) * (2 / 3 - t) * 6
                return p

            q = _l * (1 + _s) if _l < 0.5 else _l + _s - _l * _s
            p = 2 * _l - q
            r = int(round(hue_to_rgb(p, q, _h + 1 / 3) * 255))
            g = int(round(hue_to_rgb(p, q, _h) * 255))
            b = int(round(hue_to_rgb(p, q, _h - 1 / 3) * 255))
        return r, g, b


class hexa:
    """A HEX color: is a string representing a hexadecimal color code with optional alpha channel.\n
    -------------------------------------------------------------------------------------------------
    Supports formats: RGB, RGBA, RRGGBB, RRGGBBAA (with or without prefix)
    Includes methods:
    - `to_rgba()` to convert to RGB color
    - `to_hsla()` to convert to HSL color
    - `has_alpha()` to check if the color has an alpha channel
    - `lighten(amount)` to create a lighter version of the color
    - `darken(amount)` to create a darker version of the color
    - `saturate(amount)` to increase color saturation
    - `desaturate(amount)` to decrease color saturation
    - `rotate(degrees)` to rotate the hue by degrees
    - `invert()` to get the inverse color
    - `grayscale()` to convert to grayscale
    - `blend(other, ratio)` to blend with another color
    - `is_dark()` to check if the color is considered dark
    - `is_light()` to check if the color is considered light
    - `is_grayscale()` to check if the color is grayscale
    - `is_opaque()` to check if the color has no transparency
    - `with_alpha(alpha)` to create a new color with different alpha
    - `complementary()` to get the complementary color"""

    def __init__(
        self,
        color: str | int,
        _r: Optional[int] = None,
        _g: Optional[int] = None,
        _b: Optional[int] = None,
        _a: Optional[float] = None,
    ):
        if all(x is not None for x in (_r, _g, _b)):
            self.r, self.g, self.b, self.a = _r, _g, _b, _a
            return
        if isinstance(color, hexa):
            raise ValueError("Color is already a hexa() color")
        if isinstance(color, str):
            if color.startswith("#"):
                color = color[1:].upper()
            elif color.startswith("0x"):
                color = color[2:].upper()
            if len(color) == 3:  # RGB
                self.r, self.g, self.b, self.a = (
                    int(color[0] * 2, 16),
                    int(color[1] * 2, 16),
                    int(color[2] * 2, 16),
                    None,
                )
            elif len(color) == 4:  # RGBA
                self.r, self.g, self.b, self.a = (
                    int(color[0] * 2, 16),
                    int(color[1] * 2, 16),
                    int(color[2] * 2, 16),
                    int(color[3] * 2, 16) / 255.0,
                )
            elif len(color) == 6:  # RRGGBB
                self.r, self.g, self.b, self.a = (
                    int(color[0:2], 16),
                    int(color[2:4], 16),
                    int(color[4:6], 16),
                    None,
                )
            elif len(color) == 8:  # RRGGBBAA
                self.r, self.g, self.b, self.a = (
                    int(color[0:2], 16),
                    int(color[2:4], 16),
                    int(color[4:6], 16),
                    int(color[6:8], 16) / 255.0,
                )
            else:
                raise ValueError(f"Invalid HEX format '{color}'")
        elif isinstance(color, int):
            self.r, self.g, self.b, self.a = Color.hex_int_to_rgba(color).values()
        else:
            raise TypeError(f"HEX color must be of type 'str' or 'int': got '{type(color)}'")

    def __len__(self) -> int:
        return 3 if self.a is None else 4

    def __iter__(self) -> Iterator:
        return iter((f"{self.r:02X}", f"{self.g:02X}", f"{self.b:02X}")
                    + (() if self.a is None else (f"{int(self.a * 255):02X}", )))

    def __getitem__(self, index: int) -> str | int:
        return ((f"{self.r:02X}", f"{self.g:02X}", f"{self.b:02X}") + (() if self.a is None else
                                                                       (f"{int(self.a * 255):02X}", )))[index]

    def __repr__(self) -> str:
        return f'hexa(#{self.r:02X}{self.g:02X}{self.b:02X}{"" if self.a is None else f"{int(self.a * 255):02X}"})'

    def __str__(self) -> str:
        return f'#{self.r:02X}{self.g:02X}{self.b:02X}{"" if self.a is None else f"{int(self.a * 255):02X}"}'

    def __eq__(self, other: "hexa") -> bool:
        """Returns whether the other color is equal to this one."""
        if not isinstance(other, hexa):
            return False
        return (self.r, self.g, self.b, self.a) == (other.r, other.g, other.b, other.a)

    def dict(self) -> dict:
        """Returns the color components as a dictionary with hex string values for keys `'r'`, `'g'`, `'b'` and optionally `'a'`"""
        return (
            dict(r=f"{self.r:02X}", g=f"{self.g:02X}", b=f"{self.b:02X}") if self.a is None else dict(
                r=f"{self.r:02X}",
                g=f"{self.g:02X}",
                b=f"{self.b:02X}",
                a=f"{int(self.a * 255):02X}",
            )
        )

    def values(self, round_alpha: bool = True) -> tuple:
        """Returns the color components as separate values `r, g, b, a`"""
        return self.r, self.g, self.b, None if self.a is None else (round(self.a, 2) if round_alpha else self.a)

    def to_rgba(self, round_alpha: bool = True) -> "rgba":
        """Returns the color as a `rgba()` color"""
        return rgba(
            self.r,
            self.g,
            self.b,
            None if self.a is None else (round(self.a, 2) if round_alpha else self.a),
            _validate=False,
        )

    def to_hsla(self, round_alpha: bool = True) -> "hsla":
        """Returns the color as a `hsla()` color"""
        return self.to_rgba(round_alpha).to_hsla()

    def has_alpha(self) -> bool:
        """Returns `True` if the color has an alpha channel and `False` otherwise"""
        return self.a is not None

    def lighten(self, amount: float) -> "hexa":
        """Increases the colors lightness by the specified amount (`0.0`-`1.0`)"""
        self.r, self.g, self.b, self.a = self.to_rgba(False).lighten(amount).values()
        return hexa("", self.r, self.g, self.b, self.a)

    def darken(self, amount: float) -> "hexa":
        """Decreases the colors lightness by the specified amount (`0.0`-`1.0`)"""
        self.r, self.g, self.b, self.a = self.to_rgba(False).darken(amount).values()
        return hexa("", self.r, self.g, self.b, self.a)

    def saturate(self, amount: float) -> "hexa":
        """Increases the colors saturation by the specified amount (`0.0`-`1.0`)"""
        self.r, self.g, self.b, self.a = self.to_rgba(False).saturate(amount).values()
        return hexa("", self.r, self.g, self.b, self.a)

    def desaturate(self, amount: float) -> "hexa":
        """Decreases the colors saturation by the specified amount (`0.0`-`1.0`)"""
        self.r, self.g, self.b, self.a = self.to_rgba(False).desaturate(amount).values()
        return hexa("", self.r, self.g, self.b, self.a)

    def rotate(self, degrees: int) -> "hexa":
        """Rotates the colors hue by the specified number of degrees"""
        self.r, self.g, self.b, self.a = self.to_rgba(False).rotate(degrees).values()
        return hexa("", self.r, self.g, self.b, self.a)

    def invert(self, invert_alpha: bool = False) -> "hexa":
        """Inverts the color by rotating hue by 180 degrees and inverting lightness"""
        self.r, self.g, self.b, self.a = self.to_rgba(False).invert().values()
        if invert_alpha:
            self.a = 1 - self.a
        return hexa("", self.r, self.g, self.b, self.a)

    def grayscale(self, method: str = "wcag2") -> "hexa":
        """Converts the color to grayscale using the luminance formula.\n
        ------------------------------------------------------------------
        The `method` is the luminance calculation method to use:
        - `"wcag2"` WCAG 2.0 standard (default and most accurate for perception)
        - `"wcag3"` Draft WCAG 3.0 standard with improved coefficients
        - `"simple"` Simple arithmetic mean (less accurate)
        - `"bt601"` ITU-R BT.601 standard (older TV standard)"""
        self.r = self.g = self.b = Color.luminance(self.r, self.g, self.b, method=method)
        return hexa("", self.r, self.g, self.b, self.a)

    def blend(self, other: "hexa", ratio: float = 0.5, additive_alpha: bool = False) -> "rgba":
        """Blends the current color with another color using the specified ratio (`0.0`-`1.0`):
        - if `ratio` is `0.0` it means 100% of the current color and 0% of the `other` color (2:0 mixture)
        - if `ratio` is `0.5` it means 50% of both colors (1:1 mixture)
        - if `ratio` is `1.0` it means 0% of the current color and 100% of the `other` color (0:2 mixture)"""
        self.r, self.g, self.b, self.a = self.to_rgba(False).blend(Color.to_rgba(other), ratio, additive_alpha).values()
        return hexa("", self.r, self.g, self.b, self.a)

    def is_dark(self) -> bool:
        """Returns `True` if the color is considered dark (`lightness < 50%`)"""
        return self.to_hsla(False).is_dark()

    def is_light(self) -> bool:
        """Returns `True` if the color is considered light (`lightness >= 50%`)"""
        return not self.is_dark()

    def is_grayscale(self) -> bool:
        """Returns `True` if the color is grayscale (`saturation == 0`)"""
        return self.to_hsla(False).is_grayscale()

    def is_opaque(self) -> bool:
        """Returns `True` if the color has no transparency (`alpha == 1.0`)"""
        return self.a == 1 or self.a is None

    def with_alpha(self, alpha: float) -> "hexa":
        """Returns a new color with the specified alpha value"""
        if not (isinstance(alpha, (int, float)) and 0 <= alpha <= 1):
            raise ValueError("'alpha' must be in [0.0, 1.0]")
        return hexa("", self.r, self.g, self.b, alpha)

    def complementary(self) -> "hexa":
        """Returns the complementary color (180 degrees on the color wheel)"""
        return self.to_hsla(False).complementary().to_hexa()


class Color:

    @staticmethod
    def is_valid_rgba(color: Rgba, allow_alpha: bool = True) -> bool:
        try:
            if isinstance(color, rgba):
                return True
            elif isinstance(color, (list, tuple)):
                if allow_alpha and Color.has_alpha(color):
                    return (
                        0 <= color[0] <= 255 and 0 <= color[1] <= 255 and 0 <= color[2] <= 255
                        and (0 <= color[3] <= 1 or color[3] is None)
                    )
                elif len(color) == 3:
                    return 0 <= color[0] <= 255 and 0 <= color[1] <= 255 and 0 <= color[2] <= 255
                else:
                    return False
            elif isinstance(color, dict):
                if allow_alpha and Color.has_alpha(color):
                    return (
                        0 <= color["r"] <= 255 and 0 <= color["g"] <= 255 and 0 <= color["b"] <= 255
                        and (0 <= color["a"] <= 1 or color["a"] is None)
                    )
                elif len(color) == 3:
                    return 0 <= color["r"] <= 255 and 0 <= color["g"] <= 255 and 0 <= color["b"] <= 255
                else:
                    return False
            elif isinstance(color, str):
                return bool(_re.fullmatch(Regex.rgba_str(allow_alpha=allow_alpha), color))
            return False
        except Exception:
            return False

    @staticmethod
    def is_valid_hsla(color: Hsla, allow_alpha: bool = True) -> bool:
        try:
            if isinstance(color, hsla):
                return True
            elif isinstance(color, (list, tuple)):
                if allow_alpha and Color.has_alpha(color):
                    return (
                        0 <= color[0] <= 360 and 0 <= color[1] <= 100 and 0 <= color[2] <= 100
                        and (0 <= color[3] <= 1 or color[3] is None)
                    )
                elif len(color) == 3:
                    return 0 <= color[0] <= 360 and 0 <= color[1] <= 100 and 0 <= color[2] <= 100
                else:
                    return False
            elif isinstance(color, dict):
                if allow_alpha and Color.has_alpha(color):
                    return (
                        0 <= color["h"] <= 360 and 0 <= color["s"] <= 100 and 0 <= color["l"] <= 100
                        and (0 <= color["a"] <= 1 or color["a"] is None)
                    )
                elif len(color) == 3:
                    return 0 <= color["h"] <= 360 and 0 <= color["s"] <= 100 and 0 <= color["l"] <= 100
                else:
                    return False
            elif isinstance(color, str):
                return bool(_re.fullmatch(Regex.hsla_str(allow_alpha=allow_alpha), color))
        except Exception:
            return False

    @staticmethod
    def is_valid_hexa(color: Hexa, allow_alpha: bool = True, get_prefix: bool = False) -> bool | tuple[bool, str]:
        try:
            if isinstance(color, hexa):
                return (True, "#") if get_prefix else True
            elif isinstance(color, int):
                is_valid = 0x000000 <= color <= (0xFFFFFFFF if allow_alpha else 0xFFFFFF)
                return (is_valid, "0x") if get_prefix else is_valid
            elif isinstance(color, str):
                color, prefix = ((color[1:], "#") if color.startswith("#") else
                                 (color[2:], "0x") if color.startswith("0x") else (color, None))
                return ((bool(_re.fullmatch(Regex.hexa_str(allow_alpha=allow_alpha), color)),
                         prefix) if get_prefix else bool(_re.fullmatch(Regex.hexa_str(allow_alpha=allow_alpha), color)))
        except Exception:
            return (False, None) if get_prefix else False

    @staticmethod
    def is_valid(color: Rgba | Hsla | Hexa, allow_alpha: bool = True) -> bool:
        return bool(
            Color.is_valid_rgba(color, allow_alpha) or Color.is_valid_hsla(color, allow_alpha)
            or Color.is_valid_hexa(color, allow_alpha)
        )

    @staticmethod
    def has_alpha(color: Rgba | Hsla | Hexa) -> bool:
        """Check if the given color has an alpha channel.\n
        ---------------------------------------------------------------------------
        Input a RGBA, HSLA or HEXA color as `color`.
        Returns `True` if the color has an alpha channel and `False` otherwise."""
        if isinstance(color, (rgba, hsla, hexa)):
            return color.has_alpha()
        if Color.is_valid_hexa(color):
            if isinstance(color, str):
                if color.startswith("#"):
                    color = color[1:]
                return len(color) == 4 or len(color) == 8
            if isinstance(color, int):
                hex_length = len(f"{color:X}")
                return hex_length == 4 or hex_length == 8
        elif isinstance(color, (list, tuple)) and len(color) == 4 and color[3] is not None:
            return True
        elif isinstance(color, dict) and len(color) == 4 and color["a"] is not None:
            return True
        return False

    @staticmethod
    def to_rgba(color: Rgba | Hsla | Hexa) -> rgba:
        """Will try to convert any color type to a color of type RGBA."""
        if isinstance(color, (hsla, hexa)):
            return color.to_rgba()
        elif Color.is_valid_hsla(color):
            return hsla(*color, _validate=False).to_rgba()
        elif Color.is_valid_hexa(color):
            return hexa(color).to_rgba()
        elif Color.is_valid_rgba(color):
            return color if isinstance(color, rgba) else (rgba(*color, _validate=False))
        raise ValueError(f"Invalid color format '{color}'")

    @staticmethod
    def to_hsla(color: Rgba | Hsla | Hexa) -> hsla:
        """Will try to convert any color type to a color of type HSLA."""
        if isinstance(color, (rgba, hexa)):
            return color.to_hsla()
        elif Color.is_valid_rgba(color):
            return rgba(*color, _validate=False).to_hsla()
        elif Color.is_valid_hexa(color):
            return hexa(color).to_hsla()
        elif Color.is_valid_hsla(color):
            return color if isinstance(color, hsla) else (hsla(*color, _validate=False))
        raise ValueError(f"Invalid color format '{color}'")

    @staticmethod
    def to_hexa(color: Rgba | Hsla | Hexa) -> hexa:
        """Will try to convert any color type to a color of type HEXA."""
        if isinstance(color, (rgba, hsla)):
            return color.to_hexa()
        elif Color.is_valid_rgba(color):
            return rgba(*color, _validate=False).to_hexa()
        elif Color.is_valid_hsla(color):
            return hsla(*color, _validate=False).to_hexa()
        elif Color.is_valid_hexa(color):
            return color if isinstance(color, hexa) else hexa(color)
        raise ValueError(f"Invalid color format '{color}'")

    @staticmethod
    def str_to_rgba(string: str, only_first: bool = False) -> Optional[rgba | list[rgba]]:
        """Will try to recognize RGBA colors inside a string and output the found ones as RGBA objects.\n
        --------------------------------------------------------------------------------------------------
        If `only_first` is `True` only the first found color will be returned (not as a list)."""
        if only_first:
            match = _re.search(Regex.rgba_str(allow_alpha=True), string)
            if not match:
                return None
            m = match.groups()
            return rgba(
                int(m[0]),
                int(m[1]),
                int(m[2]),
                ((int(m[3]) if "." not in m[3] else float(m[3])) if m[3] else None),
                _validate=False,
            )
        else:
            matches = _re.findall(Regex.rgba_str(allow_alpha=True), string)
            if not matches:
                return None
            return [
                rgba(
                    int(m[0]),
                    int(m[1]),
                    int(m[2]),
                    ((int(m[3]) if "." not in m[3] else float(m[3])) if m[3] else None),
                    _validate=False,
                ) for m in matches
            ]

    @staticmethod
    def rgba_to_hex_int(
        r: int,
        g: int,
        b: int,
        a: Optional[float] = None,
        preserve_original: bool = False,
    ) -> int:
        """Convert RGBA channels to a HEXA integer (alpha is optional).\n
        --------------------------------------------------------------------------------------------
        To preserve leading zeros, the function will add a `1` at the beginning, if the HEX integer
        would start with a `0`.
        This could affect the color a little bit, but will make sure, that it won't be interpreted
        as a completely different color, when initializing it as a `hexa()` color or changing it
        back to RGBA using `Color.hex_int_to_rgba()`.\n
        ⇾ You can disable this behavior by setting `preserve_original` to `True`"""
        r = max(0, min(255, int(r)))
        g = max(0, min(255, int(g)))
        b = max(0, min(255, int(b)))
        if a is None:
            hex_int = (r << 16) | (g << 8) | b
            if not preserve_original and (hex_int & 0xF00000) == 0:
                hex_int |= 0x010000
        else:
            a = max(0, min(255, int(a * 255)))
            hex_int = (r << 24) | (g << 16) | (b << 8) | a
            if not preserve_original and r == 0:
                hex_int |= 0x01000000
        return hex_int

    @staticmethod
    def hex_int_to_rgba(hex_int: int, preserve_original: bool = False) -> rgba:
        """Convert a HEX integer to RGBA channels.\n
        -------------------------------------------------------------------------------------------
        If the red channel is `1` after conversion, it will be set to `0`, because when converting
        from RGBA to a HEX integer, the first `0` will be set to `1` to preserve leading zeros.
        This is the correction, so the color doesn't even look slightly different.\n
        ⇾ You can disable this behavior by setting `preserve_original` to `True`"""
        if not isinstance(hex_int, int):
            raise ValueError("Input must be an integer")
        hex_str = f"{hex_int:x}"
        if len(hex_str) <= 6:
            hex_str = hex_str.zfill(6)
            return rgba(
                r if (r := int(hex_str[0:2], 16)) != 1 or preserve_original else 0,
                int(hex_str[2:4], 16),
                int(hex_str[4:6], 16),
                None,
                _validate=False,
            )
        elif len(hex_str) <= 8:
            hex_str = hex_str.zfill(8)
            return rgba(
                r if (r := int(hex_str[0:2], 16)) != 1 or preserve_original else 0,
                int(hex_str[2:4], 16),
                int(hex_str[4:6], 16),
                int(hex_str[6:8], 16) / 255.0,
                _validate=False,
            )
        else:
            raise ValueError(f"Invalid HEX integer '0x{hex_str}': expected in range [0x000000, 0xFFFFFF]")

    @staticmethod
    def luminance(r: int, g: int, b: int, output_type: Optional[type] = None, method: str = "wcag2") -> int | float:
        """Calculates the relative luminance of a color according to various standards.\n
        ----------------------------------------------------------------------------------
        The `output_type` controls the range of the returned luminance value:
        - `int` returns integer in [0, 100]
        - `float` returns float in [0.0, 1.0]
        - `None` returns integer in [0, 255]\n
        The `method` is the luminance calculation method to use:
        - `"wcag2"` WCAG 2.0 standard (default and most accurate for perception)
        - `"wcag3"` Draft WCAG 3.0 standard with improved coefficients
        - `"simple"` Simple arithmetic mean (less accurate)
        - `"bt601"` ITU-R BT.601 standard (older TV standard)"""
        _r, _g, _b = r / 255.0, g / 255.0, b / 255.0
        if method == "simple":
            luminance = (_r + _g + _b) / 3
        elif method == "bt601":
            luminance = 0.299 * _r + 0.587 * _g + 0.114 * _b
        elif method == "wcag3":
            _r = Color._linearize_srgb(_r)
            _g = Color._linearize_srgb(_g)
            _b = Color._linearize_srgb(_b)
            luminance = 0.2126729 * _r + 0.7151522 * _g + 0.0721750 * _b
        else:
            _r = Color._linearize_srgb(_r)
            _g = Color._linearize_srgb(_g)
            _b = Color._linearize_srgb(_b)
            luminance = 0.2126 * _r + 0.7152 * _g + 0.0722 * _b
        if output_type == int:
            return round(luminance * 100)
        elif output_type == float:
            return luminance
        else:
            return round(luminance * 255)

    @staticmethod
    def _linearize_srgb(c: float) -> float:
        """Helper method to linearize sRGB component following the WCAG standard."""
        if c <= 0.03928:
            return c / 12.92
        else:
            return ((c + 0.055) / 1.055)**2.4

    @staticmethod
    def text_color_for_on_bg(text_bg_color: Rgba | Hexa) -> rgba | hexa:
        was_hexa, was_int = Color.is_valid_hexa(text_bg_color), isinstance(text_bg_color, int)
        text_bg_color = Color.to_rgba(text_bg_color)
        brightness = 0.2126 * text_bg_color[0] + 0.7152 * text_bg_color[1] + 0.0722 * text_bg_color[2]
        return ((hexa("", 255, 255, 255) if was_hexa else rgba(255, 255, 255, _validate=False)) if brightness < 128 else
                ((0x000 if was_int else hexa("", 0, 0, 0)) if was_hexa else rgba(0, 0, 0, _validate=False)))

    @staticmethod
    def adjust_lightness(color: Rgba | Hexa, lightness_change: float) -> rgba | hexa:
        """In- or decrease the lightness of the input color.\n
        -----------------------------------------------------------------------------------------------------
        - color (rgba|hexa): HEX or RGBA color
        - lightness_change (float): float between -1.0 (darken by `100%`) and 1.0 (lighten by `100%`)\n
        -----------------------------------------------------------------------------------------------------
        returns (rgba|hexa): the adjusted color in the format of the input color"""
        was_hexa = Color.is_valid_hexa(color)
        color = Color.to_hsla(color)
        h, s, l, a = (
            color[0],
            color[1],
            color[2],
            color[3] if Color.has_alpha(color) else None,
        )
        l = int(max(0, min(100, l + lightness_change * 100)))
        return hsla(h, s, l, a, _validate=False).to_hexa() if was_hexa else hsla(h, s, l, a, _validate=False).to_rgba()

    @staticmethod
    def adjust_saturation(color: Rgba | Hexa, saturation_change: float) -> rgba | hexa:
        """In- or decrease the saturation of the input color.\n
        -----------------------------------------------------------------------------------------------------------
        - color (rgba|hexa): HEX or RGBA color
        - saturation_change (float): float between -1.0 (saturate by `100%`) and 1.0 (desaturate by `100%`)\n
        -----------------------------------------------------------------------------------------------------------
        returns (rgba|hexa): the adjusted color in the format of the input color"""
        was_hexa = Color.is_valid_hexa(color)
        color = Color.to_hsla(color)
        h, s, l, a = (
            color[0],
            color[1],
            color[2],
            color[3] if Color.has_alpha(color) else None,
        )
        s = int(max(0, min(100, s + saturation_change * 100)))
        return hsla(h, s, l, a, _validate=False).to_hexa() if was_hexa else hsla(h, s, l, a, _validate=False).to_rgba()
