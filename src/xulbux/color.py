"""
This module provides the `rgba`, `hsla` and `hexa` classes, which offer
methods to manipulate colors in their respective color spaces.<br>

This module also provides the `Color` class, which
includes methods to work with colors in various formats.
"""

from .base.types import AnyRgba, AnyHsla, AnyHexa, Rgba, Hsla, Hexa
from .regex import Regex

from typing import Iterator, Optional, Literal, cast
import re as _re


class rgba:
    """An RGB/RGBA color object that includes a bunch of methods to manipulate the color.\n
    ----------------------------------------------------------------------------------------
    - `r` -⠀the red channel in range [0, 255] inclusive
    - `g` -⠀the green channel in range [0, 255] inclusive
    - `b` -⠀the blue channel in range [0, 255] inclusive
    - `a` -⠀the alpha channel in range [0.0, 1.0] inclusive
      or `None` if the color has no alpha channel\n
    ----------------------------------------------------------------------------------------
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
        self.r: int
        """The red channel in range [0, 255] inclusive."""
        self.g: int
        """The green channel in range [0, 255] inclusive."""
        self.b: int
        """The blue channel in range [0, 255] inclusive."""
        self.a: Optional[float]
        """The alpha channel in range [0.0, 1.0] inclusive or `None` if not set."""

        if not _validate:
            self.r, self.g, self.b, self.a = r, g, b, a
            return

        if not all((0 <= x <= 255) for x in (r, g, b)):
            raise ValueError(
                f"The 'r', 'g' and 'b' parameters must be integers in range [0, 255] inclusive, got {r=} {g=} {b=}"
            )
        if a is not None and not (0.0 <= a <= 1.0):
            raise ValueError(f"The 'a' parameter must be in range [0.0, 1.0] inclusive, got {a!r}")

        self.r, self.g, self.b = r, g, b
        self.a = None if a is None else (1.0 if a > 1.0 else float(a))

    def __len__(self) -> int:
        return 3 if self.a is None else 4

    def __iter__(self) -> Iterator:
        return iter((self.r, self.g, self.b) + (() if self.a is None else (self.a, )))

    def __getitem__(self, index: int) -> int | float:
        return ((self.r, self.g, self.b) + (() if self.a is None else (self.a, )))[index]

    def __repr__(self) -> str:
        return f"rgba({self.r}, {self.g}, {self.b}{'' if self.a is None else f', {self.a}'})"

    def __str__(self) -> str:
        return f"({self.r}, {self.g}, {self.b}{'' if self.a is None else f', {self.a}'})"

    def __eq__(self, other: "rgba") -> bool:  # type: ignore[override]
        if not isinstance(other, rgba):
            return False
        else:
            return (self.r, self.g, self.b, self.a) == (other.r, other.g, other.b, other.a)

    def dict(self) -> dict:
        """Returns the color components as a dictionary with keys `"r"`, `"g"`, `"b"` and optionally `"a"`."""
        return dict(r=self.r, g=self.g, b=self.b) if self.a is None else dict(r=self.r, g=self.g, b=self.b, a=self.a)

    def values(self) -> tuple:
        """Returns the color components as separate values `r, g, b, a`."""
        return self.r, self.g, self.b, self.a

    def to_hsla(self) -> "hsla":
        """Returns the color as `hsla()` color object."""
        return hsla(*self._rgb_to_hsl(self.r, self.g, self.b), self.a, _validate=False)  # type: ignore[positional-arguments]

    def to_hexa(self) -> "hexa":
        """Returns the color as `hexa()` color object."""
        return hexa("", self.r, self.g, self.b, self.a)

    def has_alpha(self) -> bool:
        """Returns `True` if the color has an alpha channel and `False` otherwise."""
        return self.a is not None

    def lighten(self, amount: float) -> "rgba":
        """Increases the colors lightness by the specified amount in range [0.0, 1.0] inclusive."""
        if not isinstance(amount, float):
            raise TypeError(f"The 'amount' parameter must be a float, got {type(amount)}")
        elif not (0.0 <= amount <= 1.0):
            raise ValueError(f"The 'amount' parameter must be in range [0.0, 1.0] inclusive, got {amount!r}")

        self.r, self.g, self.b, self.a = self.to_hsla().lighten(amount).to_rgba().values()
        return rgba(self.r, self.g, self.b, self.a, _validate=False)

    def darken(self, amount: float) -> "rgba":
        """Decreases the colors lightness by the specified amount in range [0.0, 1.0] inclusive."""
        if not isinstance(amount, float):
            raise TypeError(f"The 'amount' parameter must be a float, got {type(amount)}")
        elif not (0.0 <= amount <= 1.0):
            raise ValueError(f"The 'amount' parameter must be in range [0.0, 1.0] inclusive, got {amount!r}")

        self.r, self.g, self.b, self.a = self.to_hsla().darken(amount).to_rgba().values()
        return rgba(self.r, self.g, self.b, self.a, _validate=False)

    def saturate(self, amount: float) -> "rgba":
        """Increases the colors saturation by the specified amount in range [0.0, 1.0] inclusive."""
        if not isinstance(amount, float):
            raise TypeError(f"The 'amount' parameter must be a float, got {type(amount)}")
        elif not (0.0 <= amount <= 1.0):
            raise ValueError(f"The 'amount' parameter must be in range [0.0, 1.0] inclusive, got {amount!r}")

        self.r, self.g, self.b, self.a = self.to_hsla().saturate(amount).to_rgba().values()
        return rgba(self.r, self.g, self.b, self.a, _validate=False)

    def desaturate(self, amount: float) -> "rgba":
        """Decreases the colors saturation by the specified amount in range [0.0, 1.0] inclusive."""
        if not isinstance(amount, float):
            raise TypeError(f"The 'amount' parameter must be a float, got {type(amount)}")
        elif not (0.0 <= amount <= 1.0):
            raise ValueError(f"The 'amount' parameter must be in range [0.0, 1.0] inclusive, got {amount!r}")

        self.r, self.g, self.b, self.a = self.to_hsla().desaturate(amount).to_rgba().values()
        return rgba(self.r, self.g, self.b, self.a, _validate=False)

    def rotate(self, degrees: int) -> "rgba":
        """Rotates the colors hue by the specified number of degrees."""
        if not isinstance(degrees, int):
            raise TypeError(f"The 'degrees' parameter must be an integer, got {type(degrees)}")

        self.r, self.g, self.b, self.a = self.to_hsla().rotate(degrees).to_rgba().values()
        return rgba(self.r, self.g, self.b, self.a, _validate=False)

    def invert(self, invert_alpha: bool = False) -> "rgba":
        """Inverts the color by rotating hue by 180 degrees and inverting lightness."""
        if not isinstance(invert_alpha, bool):
            raise TypeError(f"The 'invert_alpha' parameter must be a boolean, got {type(invert_alpha)}")

        self.r, self.g, self.b = 255 - self.r, 255 - self.g, 255 - self.b
        if invert_alpha and self.a is not None:
            self.a = 1 - self.a

        return rgba(self.r, self.g, self.b, self.a, _validate=False)

    def grayscale(self, method: Literal["wcag2", "wcag3", "simple", "bt601"] = "wcag2") -> "rgba":
        """Converts the color to grayscale using the luminance formula.\n
        ---------------------------------------------------------------------------
        - `method` -⠀the luminance calculation method to use:
          * `"wcag2"` WCAG 2.0 standard (default and most accurate for perception)
          * `"wcag3"` Draft WCAG 3.0 standard with improved coefficients
          * `"simple"` Simple arithmetic mean (less accurate)
          * `"bt601"` ITU-R BT.601 standard (older TV standard)"""
        # THE 'method' PARAM IS CHECKED IN 'Color.luminance()'
        self.r = self.g = self.b = int(Color.luminance(self.r, self.g, self.b, method=method))
        return rgba(self.r, self.g, self.b, self.a, _validate=False)

    def blend(self, other: Rgba, ratio: float = 0.5, additive_alpha: bool = False) -> "rgba":
        """Blends the current color with another color using the specified ratio in range [0.0, 1.0] inclusive.\n
        ----------------------------------------------------------------------------------------------------------
        - `other` -⠀the other RGBA color to blend with
        - `ratio` -⠀the blend ratio between the two colors:
          * if `ratio` is `0.0` it means 100% of the current color and 0% of the `other` color (2:0 mixture)
          * if `ratio` is `0.5` it means 50% of both colors (1:1 mixture)
          * if `ratio` is `1.0` it means 0% of the current color and 100% of the `other` color (0:2 mixture)
        - `additive_alpha` -⠀whether to blend the alpha channels additively or not"""
        if not isinstance(other, rgba):
            if Color.is_valid_rgba(other):
                other = Color.to_rgba(other)
            else:
                raise TypeError(f"The 'other' parameter must be a valid RGBA color, got {type(other)}")
        if not isinstance(ratio, float):
            raise TypeError(f"The 'ratio' parameter must be a float, got {type(ratio)}")
        elif not (0.0 <= ratio <= 1.0):
            raise ValueError(f"The 'ratio' parameter must be in range [0.0, 1.0] inclusive, got {ratio!r}")
        if not isinstance(additive_alpha, bool):
            raise TypeError(f"The 'additive_alpha' parameter must be a boolean, got {type(additive_alpha)}")

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
        """Returns `True` if the color is considered dark (`lightness < 50%`)."""
        return self.to_hsla().is_dark()

    def is_light(self) -> bool:
        """Returns `True` if the color is considered light (`lightness >= 50%`)."""
        return not self.is_dark()

    def is_grayscale(self) -> bool:
        """Returns `True` if the color is grayscale."""
        return self.r == self.g == self.b

    def is_opaque(self) -> bool:
        """Returns `True` if the color has no transparency."""
        return self.a == 1 or self.a is None

    def with_alpha(self, alpha: float) -> "rgba":
        """Returns a new color with the specified alpha value."""
        if not isinstance(alpha, float):
            raise TypeError(f"The 'alpha' parameter must be a float, got {type(alpha)}")
        elif not (0.0 <= alpha <= 1.0):
            raise ValueError(f"The 'alpha' parameter must be in range [0.0, 1.0] inclusive, got {alpha!r}")

        return rgba(self.r, self.g, self.b, alpha, _validate=False)

    def complementary(self) -> "rgba":
        """Returns the complementary color (180 degrees on the color wheel)."""
        return self.to_hsla().complementary().to_rgba()

    def _rgb_to_hsl(self, r: int, g: int, b: int) -> tuple:
        """Internal method to convert RGB to HSL color space."""
        _r, _g, _b = r / 255.0, g / 255.0, b / 255.0
        max_c, min_c = max(_r, _g, _b), min(_r, _g, _b)
        l = (max_c + min_c) / 2

        if max_c == min_c:
            h = s = 0
        else:
            delta = max_c - min_c
            s = delta / (1 - abs(2 * l - 1))

            if max_c == _r:
                h = ((_g - _b) / delta) % 6
            elif max_c == _g:
                h = ((_b - _r) / delta) + 2
            else:
                h = ((_r - _g) / delta) + 4
            h /= 6

        return int(round(h * 360)), int(round(s * 100)), int(round(l * 100))


class hsla:
    """A HSL/HSLA color object that includes a bunch of methods to manipulate the color.\n
    ---------------------------------------------------------------------------------------
    - `h` -⠀the hue channel in range [0, 360] inclusive
    - `s` -⠀the saturation channel in range [0, 100] inclusive
    - `l` -⠀the lightness channel in range [0, 100] inclusive
    - `a` -⠀the alpha channel in range [0.0, 1.0] inclusive
      or `None` if the color has no alpha channel\n
    ---------------------------------------------------------------------------------------
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
        self.h: int
        """The hue channel in range [0, 360] inclusive."""
        self.s: int
        """The saturation channel in range [0, 100] inclusive."""
        self.l: int
        """The lightness channel in range [0, 100] inclusive."""
        self.a: Optional[float]
        """The alpha channel in range [0.0, 1.0] inclusive or `None` if not set."""

        if not _validate:
            self.h, self.s, self.l, self.a = h, s, l, a
            return

        if not (0 <= h <= 360):
            raise ValueError(f"The 'h' parameter must be in range [0, 360] inclusive, got {h!r}")
        if not all((0 <= x <= 100) for x in (s, l)):
            raise ValueError(f"The 's' and 'l' parameters must be in range [0, 100] inclusive, got {s=} {l=}")
        if a is not None and not (0.0 <= a <= 1.0):
            raise ValueError(f"The 'a' parameter must be in range [0.0, 1.0] inclusive, got {a!r}")

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

    def __eq__(self, other: "hsla") -> bool:  # type: ignore[override]
        if not isinstance(other, hsla):
            return False
        else:
            return (self.h, self.s, self.l, self.a) == (other.h, other.s, other.l, other.a)

    def dict(self) -> dict:
        """Returns the color components as a dictionary with keys `"h"`, `"s"`, `"l"` and optionally `"a"`."""
        return dict(h=self.h, s=self.s, l=self.l) if self.a is None else dict(h=self.h, s=self.s, l=self.l, a=self.a)

    def values(self) -> tuple:
        """Returns the color components as separate values `h, s, l, a`."""
        return self.h, self.s, self.l, self.a

    def to_rgba(self) -> "rgba":
        """Returns the color as `rgba()` color object."""
        return rgba(*self._hsl_to_rgb(self.h, self.s, self.l), self.a, _validate=False)  # type: ignore[positional-arguments]

    def to_hexa(self) -> "hexa":
        """Returns the color as `hexa()` color object."""
        r, g, b = self._hsl_to_rgb(self.h, self.s, self.l)
        return hexa("", r, g, b, self.a)

    def has_alpha(self) -> bool:
        """Returns `True` if the color has an alpha channel and `False` otherwise."""
        return self.a is not None

    def lighten(self, amount: float) -> "hsla":
        """Increases the colors lightness by the specified amount in range [0.0, 1.0] inclusive."""
        if not isinstance(amount, float):
            raise TypeError(f"The 'amount' parameter must be a float, got {type(amount)}")
        elif not (0.0 <= amount <= 1.0):
            raise ValueError(f"The 'amount' parameter must be in range [0.0, 1.0] inclusive, got {amount!r}")

        self.l = int(min(100, self.l + (100 - self.l) * amount))
        return hsla(self.h, self.s, self.l, self.a, _validate=False)

    def darken(self, amount: float) -> "hsla":
        """Decreases the colors lightness by the specified amount in range [0.0, 1.0] inclusive."""
        if not isinstance(amount, float):
            raise TypeError(f"The 'amount' parameter must be a float, got {type(amount)}")
        elif not (0.0 <= amount <= 1.0):
            raise ValueError(f"The 'amount' parameter must be in range [0.0, 1.0] inclusive, got {amount!r}")

        self.l = int(max(0, self.l * (1 - amount)))
        return hsla(self.h, self.s, self.l, self.a, _validate=False)

    def saturate(self, amount: float) -> "hsla":
        """Increases the colors saturation by the specified amount in range [0.0, 1.0] inclusive."""
        if not isinstance(amount, float):
            raise TypeError(f"The 'amount' parameter must be a float, got {type(amount)}")
        elif not (0.0 <= amount <= 1.0):
            raise ValueError(f"The 'amount' parameter must be in range [0.0, 1.0] inclusive, got {amount!r}")

        self.s = int(min(100, self.s + (100 - self.s) * amount))
        return hsla(self.h, self.s, self.l, self.a, _validate=False)

    def desaturate(self, amount: float) -> "hsla":
        """Decreases the colors saturation by the specified amount in range [0.0, 1.0] inclusive."""
        if not isinstance(amount, float):
            raise TypeError(f"The 'amount' parameter must be a float, got {type(amount)}")
        elif not (0.0 <= amount <= 1.0):
            raise ValueError(f"The 'amount' parameter must be in range [0.0, 1.0] inclusive, got {amount!r}")

        self.s = int(max(0, self.s * (1 - amount)))
        return hsla(self.h, self.s, self.l, self.a, _validate=False)

    def rotate(self, degrees: int) -> "hsla":
        """Rotates the colors hue by the specified number of degrees."""
        if not isinstance(degrees, int):
            raise TypeError(f"The 'degrees' parameter must be an integer, got {type(degrees)}")

        self.h = (self.h + degrees) % 360
        return hsla(self.h, self.s, self.l, self.a, _validate=False)

    def invert(self, invert_alpha: bool = False) -> "hsla":
        """Inverts the color by rotating hue by 180 degrees and inverting lightness."""
        if not isinstance(invert_alpha, bool):
            raise TypeError(f"The 'invert_alpha' parameter must be a boolean, got {type(invert_alpha)}")

        self.h = (self.h + 180) % 360
        self.l = 100 - self.l
        if invert_alpha and self.a is not None:
            self.a = 1 - self.a

        return hsla(self.h, self.s, self.l, self.a, _validate=False)

    def grayscale(self, method: Literal["wcag2", "wcag3", "simple", "bt601"] = "wcag2") -> "hsla":
        """Converts the color to grayscale using the luminance formula.\n
        ---------------------------------------------------------------------------
        - `method` -⠀the luminance calculation method to use:
          * `"wcag2"` WCAG 2.0 standard (default and most accurate for perception)
          * `"wcag3"` Draft WCAG 3.0 standard with improved coefficients
          * `"simple"` Simple arithmetic mean (less accurate)
          * `"bt601"` ITU-R BT.601 standard (older TV standard)"""
        # THE 'method' PARAM IS CHECKED IN 'Color.luminance()'
        l = int(Color.luminance(*self._hsl_to_rgb(self.h, self.s, self.l), method=method))
        self.h, self.s, self.l, _ = rgba(l, l, l, _validate=False).to_hsla().values()
        return hsla(self.h, self.s, self.l, self.a, _validate=False)

    def blend(self, other: Hsla, ratio: float = 0.5, additive_alpha: bool = False) -> "hsla":
        """Blends the current color with another color using the specified ratio in range [0.0, 1.0] inclusive.\n
        ----------------------------------------------------------------------------------------------------------
        - `other` -⠀the other HSLA color to blend with
        - `ratio` -⠀the blend ratio between the two colors:
          * if `ratio` is `0.0` it means 100% of the current color and 0% of the `other` color (2:0 mixture)
          * if `ratio` is `0.5` it means 50% of both colors (1:1 mixture)
          * if `ratio` is `1.0` it means 0% of the current color and 100% of the `other` color (0:2 mixture)
        - `additive_alpha` -⠀whether to blend the alpha channels additively or not"""
        if not Color.is_valid_hsla(other):
            raise TypeError(f"The 'other' parameter must be a valid HSLA color, got {type(other)}")
        if not isinstance(ratio, float):
            raise TypeError(f"The 'ratio' parameter must be a float, got {type(ratio)}")
        elif not (0.0 <= ratio <= 1.0):
            raise ValueError(f"The 'ratio' parameter must be in range [0.0, 1.0] inclusive, got {ratio!r}")
        if not isinstance(additive_alpha, bool):
            raise TypeError(f"The 'additive_alpha' parameter must be a boolean, got {type(additive_alpha)}")

        self.h, self.s, self.l, self.a = self.to_rgba().blend(Color.to_rgba(other), ratio, additive_alpha).to_hsla().values()
        return hsla(self.h, self.s, self.l, self.a, _validate=False)

    def is_dark(self) -> bool:
        """Returns `True` if the color is considered dark (`lightness < 50%`)."""
        return self.l < 50

    def is_light(self) -> bool:
        """Returns `True` if the color is considered light (`lightness >= 50%`)."""
        return not self.is_dark()

    def is_grayscale(self) -> bool:
        """Returns `True` if the color is considered grayscale."""
        return self.s == 0

    def is_opaque(self) -> bool:
        """Returns `True` if the color has no transparency."""
        return self.a == 1 or self.a is None

    def with_alpha(self, alpha: float) -> "hsla":
        """Returns a new color with the specified alpha value."""
        if not isinstance(alpha, float):
            raise TypeError(f"The 'alpha' parameter must be a float, got {type(alpha)}")
        elif not (0.0 <= alpha <= 1.0):
            raise ValueError(f"The 'alpha' parameter must be in range [0.0, 1.0] inclusive, got {alpha!r}")

        return hsla(self.h, self.s, self.l, alpha, _validate=False)

    def complementary(self) -> "hsla":
        """Returns the complementary color (180 degrees on the color wheel)."""
        return hsla((self.h + 180) % 360, self.s, self.l, self.a, _validate=False)

    def _hsl_to_rgb(self, h: int, s: int, l: int) -> tuple:
        """Internal method to convert HSL to RGB color space."""
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
    """A HEXA color object that includes a bunch of methods to manipulate the color.\n
    --------------------------------------------------------------------------------------------
    - `color` -⠀the HEXA color string (prefix optional) or HEX integer, that can be in formats:
      * `RGB` short format without alpha (only for strings)
      * `RGBA` short format with alpha (only for strings)
      * `RRGGBB` long format without alpha (for strings and HEX integers)
      * `RRGGBBAA` long format with alpha (for strings and HEX integers)
    --------------------------------------------------------------------------------------------
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
        self.r: int
        """The red channel in range [0, 255] inclusive."""
        self.g: int
        """The green channel in range [0, 255] inclusive."""
        self.b: int
        """The blue channel in range [0, 255] inclusive."""
        self.a: Optional[float]
        """The alpha channel in range [0.0, 1.0] inclusive or `None` if not set."""

        if all(x is not None for x in (_r, _g, _b)):
            self.r, self.g, self.b, self.a = cast(int, _r), cast(int, _g), cast(int, _b), _a
            return

        if isinstance(color, hexa):
            raise ValueError("Color is already a hexa() color object.")

        elif isinstance(color, str):
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
                raise ValueError(f"Invalid HEXA color string '{color}'. Must be in formats RGB, RGBA, RRGGBB or RRGGBBAA.")

        elif isinstance(color, int):
            self.r, self.g, self.b, self.a = Color.hex_int_to_rgba(color).values()
        else:
            raise TypeError(f"The 'color' parameter must be a string or integer, got {type(color)}")

    def __len__(self) -> int:
        return 3 if self.a is None else 4

    def __iter__(self) -> Iterator:
        return iter((f"{self.r:02X}", f"{self.g:02X}", f"{self.b:02X}")
                    + (() if self.a is None else (f"{int(self.a * 255):02X}", )))

    def __getitem__(self, index: int) -> str | int:
        return ((f"{self.r:02X}", f"{self.g:02X}", f"{self.b:02X}") \
                + (() if self.a is None else (f"{int(self.a * 255):02X}", )))[index]

    def __repr__(self) -> str:
        return f'hexa(#{self.r:02X}{self.g:02X}{self.b:02X}{"" if self.a is None else f"{int(self.a * 255):02X}"})'

    def __str__(self) -> str:
        return f'#{self.r:02X}{self.g:02X}{self.b:02X}{"" if self.a is None else f"{int(self.a * 255):02X}"}'

    def __eq__(self, other: "hexa") -> bool:  # type: ignore[override]
        """Returns whether the other color is equal to this one."""
        if not isinstance(other, hexa):
            return False
        else:
            return (self.r, self.g, self.b, self.a) == (other.r, other.g, other.b, other.a)

    def dict(self) -> dict:
        """Returns the color components as a dictionary with hex string values for keys `"r"`, `"g"`, `"b"` and optionally `"a"`."""
        return (
            dict(r=f"{self.r:02X}", g=f"{self.g:02X}", b=f"{self.b:02X}") if self.a is None else dict(
                r=f"{self.r:02X}",
                g=f"{self.g:02X}",
                b=f"{self.b:02X}",
                a=f"{int(self.a * 255):02X}",
            )
        )

    def values(self, round_alpha: bool = True) -> tuple:
        """Returns the color components as separate values `r, g, b, a`."""
        if not isinstance(round_alpha, bool):
            raise TypeError(f"The 'round_alpha' parameter must be a boolean, got {type(round_alpha)}")

        return self.r, self.g, self.b, None if self.a is None else (round(self.a, 2) if round_alpha else self.a)

    def to_rgba(self, round_alpha: bool = True) -> "rgba":
        """Returns the color as `rgba()` color object."""
        if not isinstance(round_alpha, bool):
            raise TypeError(f"The 'round_alpha' parameter must be a boolean, got {type(round_alpha)}")

        return rgba(
            self.r,
            self.g,
            self.b,
            None if self.a is None else (round(self.a, 2) if round_alpha else self.a),
            _validate=False,
        )

    def to_hsla(self, round_alpha: bool = True) -> "hsla":
        """Returns the color as `hsla()` color object."""
        if not isinstance(round_alpha, bool):
            raise TypeError(f"The 'round_alpha' parameter must be a boolean, got {type(round_alpha)}")

        return self.to_rgba(round_alpha).to_hsla()

    def has_alpha(self) -> bool:
        """Returns `True` if the color has an alpha channel and `False` otherwise."""
        return self.a is not None

    def lighten(self, amount: float) -> "hexa":
        """Increases the colors lightness by the specified amount in range [0.0, 1.0] inclusive."""
        if not isinstance(amount, float):
            raise TypeError(f"The 'amount' parameter must be a float, got {type(amount)}")
        elif not (0.0 <= amount <= 1.0):
            raise ValueError(f"The 'amount' parameter must be in range [0.0, 1.0] inclusive, got {amount!r}")

        self.r, self.g, self.b, self.a = self.to_rgba(False).lighten(amount).values()
        return hexa("", self.r, self.g, self.b, self.a)

    def darken(self, amount: float) -> "hexa":
        """Decreases the colors lightness by the specified amount in range [0.0, 1.0] inclusive."""
        if not isinstance(amount, float):
            raise TypeError(f"The 'amount' parameter must be a float, got {type(amount)}")
        elif not (0.0 <= amount <= 1.0):
            raise ValueError(f"The 'amount' parameter must be in range [0.0, 1.0] inclusive, got {amount!r}")

        self.r, self.g, self.b, self.a = self.to_rgba(False).darken(amount).values()
        return hexa("", self.r, self.g, self.b, self.a)

    def saturate(self, amount: float) -> "hexa":
        """Increases the colors saturation by the specified amount in range [0.0, 1.0] inclusive."""
        if not isinstance(amount, float):
            raise TypeError(f"The 'amount' parameter must be a float, got {type(amount)}")
        elif not (0.0 <= amount <= 1.0):
            raise ValueError(f"The 'amount' parameter must be in range [0.0, 1.0] inclusive, got {amount!r}")

        self.r, self.g, self.b, self.a = self.to_rgba(False).saturate(amount).values()
        return hexa("", self.r, self.g, self.b, self.a)

    def desaturate(self, amount: float) -> "hexa":
        """Decreases the colors saturation by the specified amount in range [0.0, 1.0] inclusive."""
        if not isinstance(amount, float):
            raise TypeError(f"The 'amount' parameter must be a float, got {type(amount)}")
        elif not (0.0 <= amount <= 1.0):
            raise ValueError(f"The 'amount' parameter must be in range [0.0, 1.0] inclusive, got {amount!r}")

        self.r, self.g, self.b, self.a = self.to_rgba(False).desaturate(amount).values()
        return hexa("", self.r, self.g, self.b, self.a)

    def rotate(self, degrees: int) -> "hexa":
        """Rotates the colors hue by the specified number of degrees."""
        if not isinstance(degrees, int):
            raise TypeError(f"The 'degrees' parameter must be an integer, got {type(degrees)}")

        self.r, self.g, self.b, self.a = self.to_rgba(False).rotate(degrees).values()
        return hexa("", self.r, self.g, self.b, self.a)

    def invert(self, invert_alpha: bool = False) -> "hexa":
        """Inverts the color by rotating hue by 180 degrees and inverting lightness."""
        if not isinstance(invert_alpha, bool):
            raise TypeError(f"The 'invert_alpha' parameter must be a boolean, got {type(invert_alpha)}")

        self.r, self.g, self.b, self.a = self.to_rgba(False).invert().values()
        if invert_alpha and self.a is not None:
            self.a = 1 - self.a

        return hexa("", self.r, self.g, self.b, self.a)

    def grayscale(self, method: Literal["wcag2", "wcag3", "simple", "bt601"] = "wcag2") -> "hexa":
        """Converts the color to grayscale using the luminance formula.\n
        ---------------------------------------------------------------------------
        - `method` -⠀the luminance calculation method to use:
          * `"wcag2"` WCAG 2.0 standard (default and most accurate for perception)
          * `"wcag3"` Draft WCAG 3.0 standard with improved coefficients
          * `"simple"` Simple arithmetic mean (less accurate)
          * `"bt601"` ITU-R BT.601 standard (older TV standard)"""
        # THE 'method' PARAM IS CHECKED IN 'Color.luminance()'
        self.r = self.g = self.b = int(Color.luminance(self.r, self.g, self.b, method=method))
        return hexa("", self.r, self.g, self.b, self.a)

    def blend(self, other: Hexa, ratio: float = 0.5, additive_alpha: bool = False) -> "hexa":
        """Blends the current color with another color using the specified ratio in range [0.0, 1.0] inclusive.\n
        ----------------------------------------------------------------------------------------------------------
        - `other` -⠀the other HEXA color to blend with
        - `ratio` -⠀the blend ratio between the two colors:
          * if `ratio` is `0.0` it means 100% of the current color and 0% of the `other` color (2:0 mixture)
          * if `ratio` is `0.5` it means 50% of both colors (1:1 mixture)
          * if `ratio` is `1.0` it means 0% of the current color and 100% of the `other` color (0:2 mixture)
        - `additive_alpha` -⠀whether to blend the alpha channels additively or not"""
        if not Color.is_valid_hexa(other):
            raise TypeError(f"The 'other' parameter must be a valid HEXA color, got {type(other)}")
        if not isinstance(ratio, float):
            raise TypeError(f"The 'ratio' parameter must be a float, got {type(ratio)}")
        elif not (0.0 <= ratio <= 1.0):
            raise ValueError(f"The 'ratio' parameter must be in range [0.0, 1.0] inclusive, got {ratio!r}")
        if not isinstance(additive_alpha, bool):
            raise TypeError(f"The 'additive_alpha' parameter must be a boolean, got {type(additive_alpha)}")

        self.r, self.g, self.b, self.a = self.to_rgba(False).blend(Color.to_rgba(other), ratio, additive_alpha).values()
        return hexa("", self.r, self.g, self.b, self.a)

    def is_dark(self) -> bool:
        """Returns `True` if the color is considered dark (`lightness < 50%`)."""
        return self.to_hsla(False).is_dark()

    def is_light(self) -> bool:
        """Returns `True` if the color is considered light (`lightness >= 50%`)."""
        return not self.is_dark()

    def is_grayscale(self) -> bool:
        """Returns `True` if the color is grayscale (`saturation == 0`)."""
        return self.to_hsla(False).is_grayscale()

    def is_opaque(self) -> bool:
        """Returns `True` if the color has no transparency (`alpha == 1.0`)."""
        return self.a == 1 or self.a is None

    def with_alpha(self, alpha: float) -> "hexa":
        """Returns a new color with the specified alpha value."""
        if not isinstance(alpha, float):
            raise TypeError(f"The 'alpha' parameter must be a float, got {type(alpha)}")
        elif not (0.0 <= alpha <= 1.0):
            raise ValueError(f"The 'alpha' parameter must be in range [0.0, 1.0] inclusive, got {alpha!r}")

        return hexa("", self.r, self.g, self.b, alpha)

    def complementary(self) -> "hexa":
        """Returns the complementary color (180 degrees on the color wheel)."""
        return self.to_hsla(False).complementary().to_hexa()


class Color:
    """This class includes methods to work with colors in different formats."""

    @staticmethod
    def is_valid_rgba(color: AnyRgba, allow_alpha: bool = True) -> bool:
        """Check if the given color is a valid RGBA color.\n
        -----------------------------------------------------------------
        - `color` -⠀the color to check (can be in any supported format)
        - `allow_alpha` -⠀whether to allow alpha channel in the color"""
        if not isinstance(allow_alpha, bool):
            raise TypeError(f"The 'new_tab_size' parameter must be an boolean, got {type(allow_alpha)}")

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

        except Exception:
            pass
        return False

    @staticmethod
    def is_valid_hsla(color: AnyHsla, allow_alpha: bool = True) -> bool:
        """Check if the given color is a valid HSLA color.\n
        -----------------------------------------------------------------
        - `color` -⠀the color to check (can be in any supported format)
        - `allow_alpha` -⠀whether to allow alpha channel in the color"""
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
            pass
        return False

    @staticmethod
    def is_valid_hexa(
        color: AnyHexa,
        allow_alpha: bool = True,
        get_prefix: bool = False,
    ) -> bool | tuple[bool, Optional[Literal["#", "0x"]]]:
        """Check if the given color is a valid HEXA color.\n
        ---------------------------------------------------------------------------------------------------
        - `color` -⠀the color to check (can be in any supported format)
        - `allow_alpha` -⠀whether to allow alpha channel in the color
        - `get_prefix` -⠀if true, the prefix used in the color (if any) is returned along with validity"""
        try:
            if isinstance(color, hexa):
                return (True, "#") if get_prefix else True

            elif isinstance(color, int):
                is_valid = 0x000000 <= color <= (0xFFFFFFFF if allow_alpha else 0xFFFFFF)
                return (is_valid, "0x") if get_prefix else is_valid

            elif isinstance(color, str):
                color, prefix = ((color[1:], "#") if color.startswith("#") else
                                 (color[2:], "0x") if color.startswith("0x") else (color, None))
                return (
                    (bool(_re.fullmatch(Regex.hexa_str(allow_alpha=allow_alpha), color)), prefix) \
                    if get_prefix else bool(_re.fullmatch(Regex.hexa_str(allow_alpha=allow_alpha), color))
                )

        except Exception:
            pass
        return (False, None) if get_prefix else False

    @staticmethod
    def is_valid(color: AnyRgba | AnyHsla | AnyHexa, allow_alpha: bool = True) -> bool:
        """Check if the given color is a valid RGBA, HSLA or HEXA color.\n
        -------------------------------------------------------------------
        - `color` -⠀the color to check (can be in any supported format)
        - `allow_alpha` -⠀whether to allow alpha channel in the color"""
        return bool(
            Color.is_valid_rgba(color, allow_alpha) \
            or Color.is_valid_hsla(color, allow_alpha) \
            or Color.is_valid_hexa(color, allow_alpha)
        )

    @staticmethod
    def has_alpha(color: Rgba | Hsla | Hexa) -> bool:
        """Check if the given color has an alpha channel.\n
        ---------------------------------------------------------------------------
        - `color` -⠀the color to check (can be in any supported format)"""
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
        """Will try to convert any color type to a color of type RGBA.\n
        ---------------------------------------------------------------------
        - `color` -⠀the color to convert (can be in any supported format)"""
        if isinstance(color, (hsla, hexa)):
            return color.to_rgba()
        elif Color.is_valid_hsla(color):
            return hsla(*cast(hsla, color), _validate=False).to_rgba()
        elif Color.is_valid_hexa(color):
            return hexa(cast(str | int, color)).to_rgba()
        elif Color.is_valid_rgba(color):
            return color if isinstance(color, rgba) else (rgba(*cast(rgba, color), _validate=False))
        raise ValueError(f"Could not convert color '{color!r}' to RGBA.")

    @staticmethod
    def to_hsla(color: Rgba | Hsla | Hexa) -> hsla:
        """Will try to convert any color type to a color of type HSLA.\n
        ---------------------------------------------------------------------
        - `color` -⠀the color to convert (can be in any supported format)"""
        if isinstance(color, (rgba, hexa)):
            return color.to_hsla()
        elif Color.is_valid_rgba(color):
            return rgba(*cast(rgba, color), _validate=False).to_hsla()
        elif Color.is_valid_hexa(color):
            return hexa(cast(str | int, color)).to_hsla()
        elif Color.is_valid_hsla(color):
            return color if isinstance(color, hsla) else (hsla(*cast(hsla, color), _validate=False))
        raise ValueError(f"Could not convert color '{color!r}' to HSLA.")

    @staticmethod
    def to_hexa(color: Rgba | Hsla | Hexa) -> hexa:
        """Will try to convert any color type to a color of type HEXA.\n
        ---------------------------------------------------------------------
        - `color` -⠀the color to convert (can be in any supported format)"""
        if isinstance(color, (rgba, hsla)):
            return color.to_hexa()
        elif Color.is_valid_rgba(color):
            return rgba(*cast(rgba, color), _validate=False).to_hexa()
        elif Color.is_valid_hsla(color):
            return hsla(*cast(hsla, color), _validate=False).to_hexa()
        elif Color.is_valid_hexa(color):
            return color if isinstance(color, hexa) else hexa(cast(str | int, color))
        raise ValueError(f"Could not convert color '{color}' to HEXA")

    @staticmethod
    def str_to_rgba(string: str, only_first: bool = False) -> Optional[rgba | list[rgba]]:
        """Will try to recognize RGBA colors inside a string and output the found ones as RGBA objects.\n
        ---------------------------------------------------------------------------------------------------------------
        - `string` -⠀the string to search for RGBA colors
        - `only_first` -⠀if true, only the first found color will be returned, otherwise a list of all found colors"""
        if only_first:
            if not (match := _re.search(Regex.rgba_str(allow_alpha=True), string)):
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
            if not (matches := _re.findall(Regex.rgba_str(allow_alpha=True), string)):
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
        - `r`, `g`, `b` -⠀the red, green and blue channels (`0` – `255`)
        - `a` -⠀the alpha channel (`0.0` – `1.0`) or `None` if not set
        - `preserve_original` -⠀whether to preserve the original color exactly (explained below)\n
        --------------------------------------------------------------------------------------------
        To preserve leading zeros, the function will add a `1` at the beginning, if the HEX integer
        would start with a `0`.
        This could affect the color a little bit, but will make sure, that it won't be interpreted
        as a completely different color, when initializing it as a `hexa()` color or changing it
        back to RGBA using `Color.hex_int_to_rgba()`."""
        if not all((0 <= c <= 255) for c in (r, g, b)):
            raise ValueError(f"The 'r', 'g' and 'b' parameters must be integers in [0, 255], got {r=} {g=} {b=}")
        if a is not None and not (0.0 <= a <= 1.0):
            raise ValueError(f"The 'a' parameter must be a float in [0.0, 1.0] or None, got {a!r}")

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
        - `hex_int` -⠀the HEX integer to convert
        - `preserve_original` -⠀whether to preserve the original color exactly (explained below)\n
        -------------------------------------------------------------------------------------------
        If the red channel is `1` after conversion, it will be set to `0`, because when converting
        from RGBA to a HEX integer, the first `0` will be set to `1` to preserve leading zeros.
        This is the correction, so the color doesn't even look slightly different."""
        if not (0 <= hex_int <= 0xFFFFFFFF):
            raise ValueError(f"Expected HEX integer in range [0x000000, 0xFFFFFFFF] inclusive, got 0x{hex_int:X}")

        if len(hex_str := f"{hex_int:X}") <= 6:
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
            raise ValueError(f"Could not convert HEX integer 0x{hex_int:X} to RGBA color.")

    @staticmethod
    def luminance(
        r: int,
        g: int,
        b: int,
        output_type: Optional[type] = None,
        method: Literal["wcag2", "wcag3", "simple", "bt601"] = "wcag2",
    ) -> int | float:
        """Calculates the relative luminance of a color according to various standards.\n
        ----------------------------------------------------------------------------------
        - `r`, `g`, `b` -⠀the red, green and blue channels in range [0, 255] inclusive
        - `output_type` -⠀the range of the returned luminance value:
          * `int` returns integer in range [0, 100] inclusive
          * `float` returns float in range [0.0, 1.0] inclusive
          * `None` returns integer in range [0, 255] inclusive
        - `method` -⠀the luminance calculation method to use:
          * `"wcag2"` WCAG 2.0 standard (default and most accurate for perception)
          * `"wcag3"` Draft WCAG 3.0 standard with improved coefficients
          * `"simple"` Simple arithmetic mean (less accurate)
          * `"bt601"` ITU-R BT.601 standard (older TV standard)"""
        if not all(0 <= c <= 255 for c in (r, g, b)):
            raise ValueError(f"The 'r', 'g' and 'b' parameters must be integers in [0, 255], got {r=} {g=} {b=}")
        if output_type not in {int, float, None}:
            raise TypeError(f"The 'output_type' parameter must be either 'int', 'float' or 'None', got {output_type!r}")

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
        """Helper method to linearize sRGB component following the WCAG standard.\n
        ----------------------------------------------------------------------------
        - `c` -⠀the sRGB component value in range [0.0, 1.0] inclusive"""
        if not (0.0 <= c <= 1.0):
            raise ValueError(f"The 'c' parameter must be in range [0.0, 1.0] inclusive, got {c!r}")

        if c <= 0.03928:
            return c / 12.92
        else:
            return ((c + 0.055) / 1.055)**2.4

    @staticmethod
    def text_color_for_on_bg(text_bg_color: Rgba | Hexa) -> rgba | hexa | int:
        """Returns either black or white text color for optimal contrast on the given background color.\n
        --------------------------------------------------------------------------------------------------
        - `text_bg_color` -⠀the background color (can be in RGBA or HEXA format)"""
        was_hexa, was_int = Color.is_valid_hexa(text_bg_color), isinstance(text_bg_color, int)

        text_bg_color = Color.to_rgba(text_bg_color)
        brightness = 0.2126 * text_bg_color[0] + 0.7152 * text_bg_color[1] + 0.0722 * text_bg_color[2]

        return (
            (0xFFFFFF if was_int else hexa("", 255, 255, 255)) if was_hexa \
            else rgba(255, 255, 255, _validate=False)
        ) if brightness < 128 else (
            (0x000 if was_int else hexa("", 0, 0, 0)) if was_hexa \
            else rgba(0, 0, 0, _validate=False)
        )

    @staticmethod
    def adjust_lightness(color: Rgba | Hexa, lightness_change: float) -> rgba | hexa:
        """In- or decrease the lightness of the input color.\n
        ------------------------------------------------------------------
        - `color` -⠀the color to adjust (can be in RGBA or HEXA format)
        - `lightness_change` -⠀the amount to change the lightness by,
          in range `-1.0` (darken by 100%) and `1.0` (lighten by 100%)"""
        was_hexa = Color.is_valid_hexa(color)

        if not (-1.0 <= lightness_change <= 1.0):
            raise ValueError(
                f"The 'lightness_change' parameter must be in range [-1.0, 1.0] inclusive, got {lightness_change!r}"
            )

        hsla_color: hsla = Color.to_hsla(color)

        h, s, l, a = (
            int(hsla_color[0]), int(hsla_color[1]), int(hsla_color[2]), \
            hsla_color[3] if Color.has_alpha(hsla_color) else None
        )
        l = int(max(0, min(100, l + lightness_change * 100)))

        return (
            hsla(h, s, l, a, _validate=False).to_hexa() if was_hexa \
            else hsla(h, s, l, a, _validate=False).to_rgba()
        )

    @staticmethod
    def adjust_saturation(color: Rgba | Hexa, saturation_change: float) -> rgba | hexa:
        """In- or decrease the saturation of the input color.\n
        -----------------------------------------------------------------------
        - `color` -⠀the color to adjust (can be in RGBA or HEXA format)
        - `saturation_change` -⠀the amount to change the saturation by,
          in range `-1.0` (saturate by 100%) and `1.0` (desaturate by 100%)"""
        was_hexa = Color.is_valid_hexa(color)

        if not (-1.0 <= saturation_change <= 1.0):
            raise ValueError(
                f"The 'saturation_change' parameter must be in range [-1.0, 1.0] inclusive, got {saturation_change!r}"
            )

        hsla_color: hsla = Color.to_hsla(color)

        h, s, l, a = (
            int(hsla_color[0]), int(hsla_color[1]), int(hsla_color[2]), \
            hsla_color[3] if Color.has_alpha(hsla_color) else None
        )
        s = int(max(0, min(100, s + saturation_change * 100)))

        return (
            hsla(h, s, l, a, _validate=False).to_hexa() if was_hexa \
            else hsla(h, s, l, a, _validate=False).to_rgba()
        )
