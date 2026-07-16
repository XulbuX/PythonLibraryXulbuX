"""
This module provides the `rgba`, `hsla` and `hexa` classes, which offer
methods to manipulate colors in their respective color spaces.<br>

This module also provides the `Color` class, which
includes methods to work with colors in various formats.
"""

from __future__ import annotations

from .base.types import RgbaDict, HslaDict, HexaDict, AnyRgba, AnyHsla, AnyHexa, Rgba, Hsla, Hexa
from .regex import Regex

from typing import Iterator, Optional, Literal, Any, overload, cast
import re as _re


class rgba:
    """An RGB/RGBA color object that includes a bunch of methods to manipulate the color.\n
    ----------------------------------------------------------------------------------------
    *   `red` – The red channel in range [0, 255] inclusive.
    *   `green` – The green channel in range [0, 255] inclusive.
    *   `blue` – The blue channel in range [0, 255] inclusive.
    *   `alpha` – The alpha channel in range [0.0, 1.0] inclusive<br>
        or `None` if the color has no alpha channel.
    ----------------------------------------------------------------------------------------
    Includes methods:
    *   `to_hsla()` to convert to HSL color
    *   `to_hexa()` to convert to HEX color
    *   `has_alpha()` to check if the color has an alpha channel
    *   `lighten(amount)` to create a lighter version of the color
    *   `darken(amount)` to create a darker version of the color
    *   `saturate(amount)` to increase color saturation
    *   `desaturate(amount)` to decrease color saturation
    *   `rotate(degrees)` to rotate the hue by degrees
    *   `invert()` to get the inverse color
    *   `grayscale()` to convert to grayscale
    *   `blend(other, ratio)` to blend with another color
    *   `is_dark()` to check if the color is considered dark
    *   `is_light()` to check if the color is considered light
    *   `is_grayscale()` to check if the color is grayscale
    *   `is_opaque()` to check if the color has no transparency
    *   `with_alpha(alpha)` to create a new color with different alpha
    *   `complementary()` to get the complementary color"""

    def __init__(self, red: int, green: int, blue: int, alpha: Optional[float] = None, /, *, _validate: bool = True):
        self.red: int
        """The red channel in range [0, 255] inclusive."""
        self.green: int
        """The green channel in range [0, 255] inclusive."""
        self.blue: int
        """The blue channel in range [0, 255] inclusive."""
        self.alpha: Optional[float]
        """The alpha channel in range [0.0, 1.0] inclusive or `None` if not set."""

        if not _validate:
            self.red, self.green, self.blue, self.alpha = red, green, blue, alpha
            return

        if not all((0 <= ch <= 255) for ch in (red, green, blue)):
            raise ValueError(
                "The 'red', 'green' and 'blue' parameters must be integers "
                f"in range [0, 255] inclusive, got {red=!r} {green=!r} {blue=!r}"
            )
        if alpha is not None and not (0.0 <= alpha <= 1.0):
            raise ValueError(f"The 'alpha' parameter must be in range [0.0, 1.0] inclusive, got {alpha!r}")

        self.red, self.green, self.blue = red, green, blue
        self.alpha = None if alpha is None else (1.0 if alpha > 1.0 else float(alpha))

    def __len__(self) -> int:
        """The number of components in the color (3 or 4)."""

        return 3 if self.alpha is None else 4

    def __iter__(self) -> Iterator[int | Optional[float]]:
        return iter((self.red, self.green, self.blue) + (() if self.alpha is None else (self.alpha, )))

    @overload
    def __getitem__(self, index: Literal[0, 1, 2], /) -> int:
        ...

    @overload
    def __getitem__(self, index: Literal[3], /) -> Optional[float]:
        ...

    @overload
    def __getitem__(self, index: int, /) -> int | Optional[float]:
        ...

    def __getitem__(self, index: int, /) -> int | Optional[float]:
        return ((self.red, self.green, self.blue) + (() if self.alpha is None else (self.alpha, )))[index]

    def __eq__(self, other: object, /) -> bool:
        """Check if two `rgba` objects are the same color."""

        if not isinstance(other, rgba):
            return False
        return (self.red, self.green, self.blue, self.alpha) == (other.red, other.green, other.blue, other.alpha)

    def __ne__(self, other: object, /) -> bool:
        """Check if two `rgba` objects are different colors."""

        return not self.__eq__(other)

    def __repr__(self) -> str:
        return f"rgba({self.red}, {self.green}, {self.blue}{'' if self.alpha is None else f', {self.alpha}'})"

    def __str__(self) -> str:
        return self.__repr__()

    def dict(self) -> RgbaDict:
        """Returns the color components as a dictionary with keys `"red"`, `"green"`, `"blue"` and optionally `"alpha"`."""

        return RgbaDict(red=self.red, green=self.green, blue=self.blue, alpha=self.alpha)

    def values(self) -> tuple[int, int, int, Optional[float]]:
        """Returns the color components as separate values `red, green, blue, alpha`."""

        return self.red, self.green, self.blue, self.alpha

    def to_hsla(self) -> hsla:
        """Returns the color as `hsla()` color object."""

        hue, sat, light = self._rgb_to_hsl(self.red, self.green, self.blue)
        return hsla(hue, sat, light, self.alpha, _validate=False)

    def to_hexa(self) -> hexa:
        """Returns the color as `hexa()` color object."""

        return hexa(_red=self.red, _green=self.green, _blue=self.blue, _alpha=self.alpha)

    def has_alpha(self) -> bool:
        """Returns `True` if the color has an alpha channel and `False` otherwise."""

        return self.alpha is not None

    def lighten(self, amount: float, /) -> rgba:
        """Increases the colors lightness by the specified amount in range [0.0, 1.0] inclusive."""

        if not (0.0 <= amount <= 1.0):
            raise ValueError(f"The 'amount' parameter must be in range [0.0, 1.0] inclusive, got {amount!r}")

        self.red, self.green, self.blue, self.alpha = self.to_hsla().lighten(amount).to_rgba().values()
        return rgba(self.red, self.green, self.blue, self.alpha, _validate=False)

    def darken(self, amount: float, /) -> rgba:
        """Decreases the colors lightness by the specified amount in range [0.0, 1.0] inclusive."""

        if not (0.0 <= amount <= 1.0):
            raise ValueError(f"The 'amount' parameter must be in range [0.0, 1.0] inclusive, got {amount!r}")

        self.red, self.green, self.blue, self.alpha = self.to_hsla().darken(amount).to_rgba().values()
        return rgba(self.red, self.green, self.blue, self.alpha, _validate=False)

    def saturate(self, amount: float, /) -> rgba:
        """Increases the colors saturation by the specified amount in range [0.0, 1.0] inclusive."""

        if not (0.0 <= amount <= 1.0):
            raise ValueError(f"The 'amount' parameter must be in range [0.0, 1.0] inclusive, got {amount!r}")

        self.red, self.green, self.blue, self.alpha = self.to_hsla().saturate(amount).to_rgba().values()
        return rgba(self.red, self.green, self.blue, self.alpha, _validate=False)

    def desaturate(self, amount: float, /) -> rgba:
        """Decreases the colors saturation by the specified amount in range [0.0, 1.0] inclusive."""

        if not (0.0 <= amount <= 1.0):
            raise ValueError(f"The 'amount' parameter must be in range [0.0, 1.0] inclusive, got {amount!r}")

        self.red, self.green, self.blue, self.alpha = self.to_hsla().desaturate(amount).to_rgba().values()
        return rgba(self.red, self.green, self.blue, self.alpha, _validate=False)

    def rotate(self, degrees: int, /) -> rgba:
        """Rotates the colors hue by the specified number of degrees."""

        self.red, self.green, self.blue, self.alpha = self.to_hsla().rotate(degrees).to_rgba().values()
        return rgba(self.red, self.green, self.blue, self.alpha, _validate=False)

    def invert(self, *, invert_alpha: bool = False) -> rgba:
        """Inverts the color by rotating hue by 180 degrees and inverting lightness."""

        self.red, self.green, self.blue = 255 - self.red, 255 - self.green, 255 - self.blue
        if invert_alpha and self.alpha is not None:
            self.alpha = 1 - self.alpha
        return rgba(self.red, self.green, self.blue, self.alpha, _validate=False)

    def grayscale(self, *, method: Literal["wcag2", "wcag3", "simple", "bt601"] = "wcag2") -> rgba:
        """Converts the color to grayscale using the luminance formula.\n
        -------------------------------------------------------------------------------
        *   `method` – The luminance calculation method to use:
            -   `"wcag2"` WCAG 2.0 standard (default and most accurate for perception)
            -   `"wcag3"` draft WCAG 3.0 standard with improved coefficients
            -   `"simple"` simple arithmetic mean (less accurate)
            -   `"bt601"` ITU-R BT.601 standard (older TV standard)"""

        # The `method` param is validated in `Color.luminance()`.

        self.red = self.green = self.blue = int(Color.luminance(self.red, self.green, self.blue, method=method))
        return rgba(self.red, self.green, self.blue, self.alpha, _validate=False)

    def blend(self, other: Rgba, /, ratio: float = 0.5, *, additive_alpha: bool = False) -> rgba:
        """Blends the current color with another color using the specified ratio in range [0.0, 1.0] inclusive.\n
        ----------------------------------------------------------------------------------------------------------
        *   `other` – The other RGBA color to blend with.
        *   `ratio` – The blend ratio between the two colors:
            -   If `ratio` is `0.0` it means 100% of the current color and 0% of the `other` color (2:0 mixture).
            -   If `ratio` is `0.5` it means 50% of both colors (1:1 mixture).
            -   If `ratio` is `1.0` it means 0% of the current color and 100% of the `other` color (0:2 mixture).
        *   `additive_alpha` – Whether to blend the alpha channels additively or not."""

        if not (0.0 <= ratio <= 1.0):
            raise ValueError(f"The 'ratio' parameter must be in range [0.0, 1.0] inclusive, got {ratio!r}")

        other_rgba = Color.to_rgba(other)
        ratio *= 2

        self.red = int(max(0, min(255, int((self.red * (2 - ratio)) + (other_rgba.red * ratio) + 0.5))))
        self.green = int(max(0, min(255, int((self.green * (2 - ratio)) + (other_rgba.green * ratio) + 0.5))))
        self.blue = int(max(0, min(255, int((self.blue * (2 - ratio)) + (other_rgba.blue * ratio) + 0.5))))
        none_alpha = self.alpha is None and (len(other_rgba) <= 3 or other_rgba[3] is None)

        if not none_alpha:
            self_a: float = 1.0 if self.alpha is None else self.alpha
            other_a: float = cast(float, 1.0 if other_rgba[3] is None else other_rgba[3]) if len(other_rgba) > 3 else 1.0

            if additive_alpha:
                self.alpha = max(0, min(1, (self_a * (2 - ratio)) + (other_a * ratio)))
            else:
                self.alpha = max(0, min(1, (self_a * (1 - (ratio / 2))) + (other_a * (ratio / 2))))

        else:
            self.alpha = None

        return rgba(self.red, self.green, self.blue, None if none_alpha else self.alpha, _validate=False)

    def is_dark(self) -> bool:
        """Returns `True` if the color is considered dark (`lightness < 50%`)."""

        return self.to_hsla().is_dark()

    def is_light(self) -> bool:
        """Returns `True` if the color is considered light (`lightness >= 50%`)."""

        return not self.is_dark()

    def is_grayscale(self) -> bool:
        """Returns `True` if the color is grayscale."""

        return self.red == self.green == self.blue

    def is_opaque(self) -> bool:
        """Returns `True` if the color has no transparency."""

        return self.alpha == 1 or self.alpha is None

    def with_alpha(self, alpha: float, /) -> rgba:
        """Returns a new color with the specified alpha value."""

        if not (0.0 <= alpha <= 1.0):
            raise ValueError(f"The 'alpha' parameter must be in range [0.0, 1.0] inclusive, got {alpha!r}")

        return rgba(self.red, self.green, self.blue, alpha, _validate=False)

    def complementary(self) -> rgba:
        """Returns the complementary color (180 degrees on the color wheel)."""

        return self.to_hsla().complementary().to_rgba()

    @staticmethod
    def _rgb_to_hsl(red: int, green: int, blue: int) -> tuple[int, int, int]:
        """Internal method to convert RGB to HSL color space."""

        _red, _green, _blue = red / 255.0, green / 255.0, blue / 255.0
        max_c, min_c = max(_red, _green, _blue), min(_red, _green, _blue)
        light = (max_c + min_c) / 2

        if max_c == min_c:
            hue = sat = 0.0

        else:
            delta = max_c - min_c
            sat = delta / (1 - abs(2 * light - 1))

            if max_c == _red:
                hue = ((_green - _blue) / delta) % 6
            elif max_c == _green:
                hue = ((_blue - _red) / delta) + 2
            else:
                hue = ((_red - _green) / delta) + 4

            hue /= 6

        return int(round(hue * 360)), int(round(sat * 100)), int(round(light * 100))


class hsla:
    """A HSL/HSLA color object that includes a bunch of methods to manipulate the color.\n
    ---------------------------------------------------------------------------------------
    *   `hue` – The hue channel in range [0, 360] inclusive.
    *   `sat` – The saturation channel in range [0, 100] inclusive.
    *   `light` – The lightness channel in range [0, 100] inclusive.
    *   `alpha` – The alpha channel in range [0.0, 1.0] inclusive<br>
        or `None` if the color has no alpha channel.
    ---------------------------------------------------------------------------------------
    Includes methods:
    *   `to_rgba()` to convert to RGB color
    *   `to_hexa()` to convert to HEX color
    *   `has_alpha()` to check if the color has an alpha channel
    *   `lighten(amount)` to create a lighter version of the color
    *   `darken(amount)` to create a darker version of the color
    *   `saturate(amount)` to increase color saturation
    *   `desaturate(amount)` to decrease color saturation
    *   `rotate(degrees)` to rotate the hue by degrees
    *   `invert()` to get the inverse color
    *   `grayscale()` to convert to grayscale
    *   `blend(other, ratio)` to blend with another color
    *   `is_dark()` to check if the color is considered dark
    *   `is_light()` to check if the color is considered light
    *   `is_grayscale()` to check if the color is grayscale
    *   `is_opaque()` to check if the color has no transparency
    *   `with_alpha(alpha)` to create a new color with different alpha
    *   `complementary()` to get the complementary color"""

    def __init__(self, hue: int, sat: int, light: int, alpha: Optional[float] = None, /, *, _validate: bool = True):
        self.hue: int
        """The hue channel in range [0, 360] inclusive."""
        self.sat: int
        """The saturation channel in range [0, 100] inclusive."""
        self.light: int
        """The lightness channel in range [0, 100] inclusive."""
        self.alpha: Optional[float]
        """The alpha channel in range [0.0, 1.0] inclusive or `None` if not set."""

        if not _validate:
            self.hue, self.sat, self.light, self.alpha = hue, sat, light, alpha
            return

        if not (0 <= hue <= 360):
            raise ValueError(f"The 'hue' parameter must be in range [0, 360] inclusive, got {hue!r}")
        if not all((0 <= ch <= 100) for ch in (sat, light)):
            raise ValueError(f"The 'sat' and 'light' parameters must be in range [0, 100] inclusive, got {sat=!r} {light=!r}")
        if alpha is not None and not (0.0 <= alpha <= 1.0):
            raise ValueError(f"The 'alpha' parameter must be in range [0.0, 1.0] inclusive, got {alpha!r}")

        self.hue, self.sat, self.light = hue, sat, light
        self.alpha = None if alpha is None else (1.0 if alpha > 1.0 else float(alpha))

    def __len__(self) -> int:
        """The number of components in the color (3 or 4)."""

        return 3 if self.alpha is None else 4

    def __iter__(self) -> Iterator[int | Optional[float]]:
        return iter((self.hue, self.sat, self.light) + (() if self.alpha is None else (self.alpha, )))

    @overload
    def __getitem__(self, index: Literal[0, 1, 2], /) -> int:
        ...

    @overload
    def __getitem__(self, index: Literal[3], /) -> Optional[float]:
        ...

    @overload
    def __getitem__(self, index: int, /) -> int | Optional[float]:
        ...

    def __getitem__(self, index: int, /) -> int | Optional[float]:
        return ((self.hue, self.sat, self.light) + (() if self.alpha is None else (self.alpha, )))[index]

    def __eq__(self, other: object, /) -> bool:
        """Check if two `hsla` objects are the same color."""

        if not isinstance(other, hsla):
            return False
        return (self.hue, self.sat, self.light, self.alpha) == (other.hue, other.sat, other.light, other.alpha)

    def __ne__(self, other: object, /) -> bool:
        """Check if two `hsla` objects are different colors."""

        return not self.__eq__(other)

    def __repr__(self) -> str:
        return f"hsla({self.hue}°, {self.sat}%, {self.light}%{'' if self.alpha is None else f', {self.alpha}'})"

    def __str__(self) -> str:
        return self.__repr__()

    def dict(self) -> HslaDict:
        """Returns the color components as a dictionary with keys `"hue"`, `"sat"`, `"light"` and optionally `"alpha"`."""

        return HslaDict(hue=self.hue, sat=self.sat, light=self.light, alpha=self.alpha)

    def values(self) -> tuple[int, int, int, Optional[float]]:
        """Returns the color components as separate values `hue, sat, light, alpha`."""

        return self.hue, self.sat, self.light, self.alpha

    def to_rgba(self) -> rgba:
        """Returns the color as `rgba()` color object."""

        red, green, blue = self._hsl_to_rgb(self.hue, self.sat, self.light)
        return rgba(red, green, blue, self.alpha, _validate=False)

    def to_hexa(self) -> hexa:
        """Returns the color as `hexa()` color object."""

        red, green, blue = self._hsl_to_rgb(self.hue, self.sat, self.light)
        return hexa(_red=red, _green=green, _blue=blue, _alpha=self.alpha)

    def has_alpha(self) -> bool:
        """Returns `True` if the color has an alpha channel and `False` otherwise."""

        return self.alpha is not None

    def lighten(self, amount: float, /) -> hsla:
        """Increases the colors lightness by the specified amount in range [0.0, 1.0] inclusive."""

        if not (0.0 <= amount <= 1.0):
            raise ValueError(f"The 'amount' parameter must be in range [0.0, 1.0] inclusive, got {amount!r}")

        self.light = int(min(100, self.light + (100 - self.light) * amount))
        return hsla(self.hue, self.sat, self.light, self.alpha, _validate=False)

    def darken(self, amount: float, /) -> hsla:
        """Decreases the colors lightness by the specified amount in range [0.0, 1.0] inclusive."""

        if not (0.0 <= amount <= 1.0):
            raise ValueError(f"The 'amount' parameter must be in range [0.0, 1.0] inclusive, got {amount!r}")

        self.light = int(max(0, self.light * (1 - amount)))
        return hsla(self.hue, self.sat, self.light, self.alpha, _validate=False)

    def saturate(self, amount: float, /) -> hsla:
        """Increases the colors saturation by the specified amount in range [0.0, 1.0] inclusive."""

        if not (0.0 <= amount <= 1.0):
            raise ValueError(f"The 'amount' parameter must be in range [0.0, 1.0] inclusive, got {amount!r}")

        self.sat = int(min(100, self.sat + (100 - self.sat) * amount))
        return hsla(self.hue, self.sat, self.light, self.alpha, _validate=False)

    def desaturate(self, amount: float, /) -> hsla:
        """Decreases the colors saturation by the specified amount in range [0.0, 1.0] inclusive."""

        if not (0.0 <= amount <= 1.0):
            raise ValueError(f"The 'amount' parameter must be in range [0.0, 1.0] inclusive, got {amount!r}")

        self.sat = int(max(0, self.sat * (1 - amount)))
        return hsla(self.hue, self.sat, self.light, self.alpha, _validate=False)

    def rotate(self, degrees: int, /) -> hsla:
        """Rotates the colors hue by the specified number of degrees."""

        self.hue = (self.hue + degrees) % 360
        return hsla(self.hue, self.sat, self.light, self.alpha, _validate=False)

    def invert(self, *, invert_alpha: bool = False) -> hsla:
        """Inverts the color by rotating hue by 180 degrees and inverting lightness."""

        self.hue = (self.hue + 180) % 360
        self.light = 100 - self.light
        if invert_alpha and self.alpha is not None:
            self.alpha = 1 - self.alpha
        return hsla(self.hue, self.sat, self.light, self.alpha, _validate=False)

    def grayscale(self, *, method: Literal["wcag2", "wcag3", "simple", "bt601"] = "wcag2") -> hsla:
        """Converts the color to grayscale using the luminance formula.\n
        -------------------------------------------------------------------------------
        *   `method` – the luminance calculation method to use:
            -   `"wcag2"` WCAG 2.0 standard (default and most accurate for perception)
            -   `"wcag3"` draft WCAG 3.0 standard with improved coefficients
            -   `"simple"` simple arithmetic mean (less accurate)
            -   `"bt601"` ITU-R BT.601 standard (older TV standard)"""

        # The `method` param is validated in `Color.luminance()`.

        red, green, blue = self._hsl_to_rgb(self.hue, self.sat, self.light)
        light = int(Color.luminance(red, green, blue, output_type=None, method=method))

        self.hue, self.sat, self.light, _ = rgba(light, light, light, _validate=False).to_hsla().values()
        return hsla(self.hue, self.sat, self.light, self.alpha, _validate=False)

    def blend(self, other: Hsla, /, ratio: float = 0.5, *, additive_alpha: bool = False) -> hsla:
        """Blends the current color with another color using the specified ratio in range [0.0, 1.0] inclusive.\n
        ----------------------------------------------------------------------------------------------------------
        *   `other` – The other HSLA color to blend with.
        *   `ratio` – The blend ratio between the two colors:
            -   If `ratio` is `0.0` it means 100% of the current color and 0% of the `other` color (2:0 mixture).
            -   If `ratio` is `0.5` it means 50% of both colors (1:1 mixture).
            -   If `ratio` is `1.0` it means 0% of the current color and 100% of the `other` color (0:2 mixture).
        *   `additive_alpha` – whether to blend the alpha channels additively or not."""

        if not Color.is_valid_hsla(other):
            raise TypeError(f"The 'other' parameter must be a valid HSLA color, got {type(other)}")
        if not (0.0 <= ratio <= 1.0):
            raise ValueError(f"The 'ratio' parameter must be in range [0.0, 1.0] inclusive, got {ratio!r}")

        self.hue, self.sat, self.light, self.alpha = self.to_rgba().blend(
            Color.to_rgba(other), ratio, additive_alpha=additive_alpha
        ).to_hsla().values()
        return hsla(self.hue, self.sat, self.light, self.alpha, _validate=False)

    def is_dark(self) -> bool:
        """Returns `True` if the color is considered dark (`lightness < 50%`)."""

        return self.light < 50

    def is_light(self) -> bool:
        """Returns `True` if the color is considered light (`lightness >= 50%`)."""

        return not self.is_dark()

    def is_grayscale(self) -> bool:
        """Returns `True` if the color is considered grayscale."""

        return self.sat == 0

    def is_opaque(self) -> bool:
        """Returns `True` if the color has no transparency."""

        return self.alpha == 1 or self.alpha is None

    def with_alpha(self, alpha: float, /) -> hsla:
        """Returns a new color with the specified alpha value."""

        if not isinstance(alpha, float):
            raise TypeError(f"The 'alpha' parameter must be a float, got {type(alpha)}")
        elif not (0.0 <= alpha <= 1.0):
            raise ValueError(f"The 'alpha' parameter must be in range [0.0, 1.0] inclusive, got {alpha!r}")

        return hsla(self.hue, self.sat, self.light, alpha, _validate=False)

    def complementary(self) -> hsla:
        """Returns the complementary color (180 degrees on the color wheel)."""

        return hsla((self.hue + 180) % 360, self.sat, self.light, self.alpha, _validate=False)

    @classmethod
    def _hsl_to_rgb(cls, hue: int, sat: int, light: int) -> tuple[int, int, int]:
        """Internal method to convert HSL to RGB color space."""

        _hue, _sat, _light = hue / 360, sat / 100, light / 100

        if _sat == 0:
            red = green = blue = int(_light * 255)

        else:
            chroma_max = _light * (1 + _sat) if _light < 0.5 else _light + _sat - _light * _sat
            chroma_min = 2 * _light - chroma_max

            red = int(round(cls._hue_to_rgb(chroma_min, chroma_max, _hue + 1 / 3) * 255))
            green = int(round(cls._hue_to_rgb(chroma_min, chroma_max, _hue) * 255))
            blue = int(round(cls._hue_to_rgb(chroma_min, chroma_max, _hue - 1 / 3) * 255))

        return red, green, blue

    @staticmethod
    def _hue_to_rgb(chroma_min: float, chroma_max: float, hue_pos: float) -> float:
        if hue_pos < 0:
            hue_pos += 1
        if hue_pos > 1:
            hue_pos -= 1
        if hue_pos < 1 / 6:
            return chroma_min + (chroma_max - chroma_min) * 6 * hue_pos
        if hue_pos < 1 / 2:
            return chroma_max
        if hue_pos < 2 / 3:
            return chroma_min + (chroma_max - chroma_min) * (2 / 3 - hue_pos) * 6
        return chroma_min


class hexa:
    """A HEXA color object that includes a bunch of methods to manipulate the color.\n
    ----------------------------------------------------------------------------------------------
    *   `color` – The HEXA color string (prefix optional) or HEX integer, that can be in formats:
        -   `RGB` short format without alpha (only for strings)
        -   `RGBA` short format with alpha (only for strings)
        -   `RRGGBB` long format without alpha (for strings and HEX integers)
        -   `RRGGBBAA` long format with alpha (for strings and HEX integers)
    ----------------------------------------------------------------------------------------------
    Includes methods:
    *   `to_rgba()` to convert to RGB color
    *   `to_hsla()` to convert to HSL color
    *   `has_alpha()` to check if the color has an alpha channel
    *   `lighten(amount)` to create a lighter version of the color
    *   `darken(amount)` to create a darker version of the color
    *   `saturate(amount)` to increase color saturation
    *   `desaturate(amount)` to decrease color saturation
    *   `rotate(degrees)` to rotate the hue by degrees
    *   `invert()` to get the inverse color
    *   `grayscale()` to convert to grayscale
    *   `blend(other, ratio)` to blend with another color
    *   `is_dark()` to check if the color is considered dark
    *   `is_light()` to check if the color is considered light
    *   `is_grayscale()` to check if the color is grayscale
    *   `is_opaque()` to check if the color has no transparency
    *   `with_alpha(alpha)` to create a new color with different alpha
    *   `complementary()` to get the complementary color"""

    def __init__(
        self,
        color: Optional[str | int] = None,
        /,
        *,
        _red: Optional[int] = None,
        _green: Optional[int] = None,
        _blue: Optional[int] = None,
        _alpha: Optional[float] = None,
    ) -> None:
        self.red: int
        """The red channel in range [0, 255] inclusive."""
        self.green: int
        """The green channel in range [0, 255] inclusive."""
        self.blue: int
        """The blue channel in range [0, 255] inclusive."""
        self.alpha: Optional[float]
        """The alpha channel in range [0.0, 1.0] inclusive or `None` if not set."""

        if all(ch is not None for ch in (_red, _green, _blue)):
            self.red, self.green, self.blue, self.alpha = cast(int, _red), cast(int, _green), cast(int, _blue), _alpha
            return

        if isinstance(color, hexa):
            raise ValueError("Color is already a hexa() color object.")

        elif isinstance(color, str):
            if color.startswith("#"):
                color = color[1:].upper()
            elif color.startswith("0x"):
                color = color[2:].upper()

            if len(color) == 3:  # RGB
                self.red, self.green, self.blue, self.alpha = (
                    int(color[0] * 2, 16),
                    int(color[1] * 2, 16),
                    int(color[2] * 2, 16),
                    None,
                )
            elif len(color) == 4:  # RGBA
                self.red, self.green, self.blue, self.alpha = (
                    int(color[0] * 2, 16),
                    int(color[1] * 2, 16),
                    int(color[2] * 2, 16),
                    int(color[3] * 2, 16) / 255.0,
                )
            elif len(color) == 6:  # RRGGBB
                self.red, self.green, self.blue, self.alpha = (
                    int(color[0:2], 16),
                    int(color[2:4], 16),
                    int(color[4:6], 16),
                    None,
                )
            elif len(color) == 8:  # RRGGBBAA
                self.red, self.green, self.blue, self.alpha = (
                    int(color[0:2], 16),
                    int(color[2:4], 16),
                    int(color[4:6], 16),
                    int(color[6:8], 16) / 255.0,
                )
            else:
                raise ValueError(f"Invalid HEXA color string '{color}'. Must be in formats RGB, RGBA, RRGGBB or RRGGBBAA.")

        elif isinstance(color, int):
            self.red, self.green, self.blue, self.alpha = Color.hex_int_to_rgba(color).values()

    def __len__(self) -> int:
        """The number of components in the color (3 or 4)."""

        return 3 if self.alpha is None else 4

    def __iter__(self) -> Iterator[str]:
        return iter((f"{self.red:02X}", f"{self.green:02X}", f"{self.blue:02X}")
                    + (() if self.alpha is None else (f"{int(self.alpha * 255):02X}", )))

    def __getitem__(self, index: int, /) -> str:
        return ((f"{self.red:02X}", f"{self.green:02X}", f"{self.blue:02X}") \
                + (() if self.alpha is None else (f"{int(self.alpha * 255):02X}", )))[index]

    def __eq__(self, other: object, /) -> bool:
        """Check if two `hexa` objects are the same color."""

        if not isinstance(other, hexa):
            return False
        return (self.red, self.green, self.blue, self.alpha) == (other.red, other.green, other.blue, other.alpha)

    def __ne__(self, other: object, /) -> bool:
        """Check if two `hexa` objects are different colors."""

        return not self.__eq__(other)

    def __repr__(self) -> str:
        alpha = "" if self.alpha is None else f"{int(self.alpha * 255):02X}"
        return f"hexa(#{self.red:02X}{self.green:02X}{self.blue:02X}{alpha})"

    def __str__(self) -> str:
        alpha = "" if self.alpha is None else f"{int(self.alpha * 255):02X}"
        return f"#{self.red:02X}{self.green:02X}{self.blue:02X}{alpha}"

    def dict(self) -> HexaDict:
        """Returns the color components as a dictionary with hex string values<br>
        for keys `"red"`, `"green"`, `"blue"` and optionally `"alpha"`."""

        return HexaDict(
            red=f"{self.red:02X}",
            green=f"{self.green:02X}",
            blue=f"{self.blue:02X}",
            alpha=(None if self.alpha is None else f"{int(self.alpha * 255):02X}"),
        )

    def values(self, *, round_alpha: bool = True) -> tuple[int, int, int, Optional[float]]:
        """Returns the color components as separate values `red, green, blue, alpha`."""

        return self.red, self.green, self.blue, None if self.alpha is None else (
            round(self.alpha, 2) if round_alpha else self.alpha
        )

    def to_rgba(self, *, round_alpha: bool = True) -> rgba:
        """Returns the color as `rgba()` color object."""

        return rgba(
            self.red,
            self.green,
            self.blue,
            None if self.alpha is None else (round(self.alpha, 2) if round_alpha else self.alpha),
            _validate=False,
        )

    def to_hsla(self, *, round_alpha: bool = True) -> hsla:
        """Returns the color as `hsla()` color object."""

        return self.to_rgba(round_alpha=round_alpha).to_hsla()

    def has_alpha(self) -> bool:
        """Returns `True` if the color has an alpha channel and `False` otherwise."""

        return self.alpha is not None

    def lighten(self, amount: float, /) -> hexa:
        """Increases the colors lightness by the specified amount in range [0.0, 1.0] inclusive."""

        if not (0.0 <= amount <= 1.0):
            raise ValueError(f"The 'amount' parameter must be in range [0.0, 1.0] inclusive, got {amount!r}")

        self.red, self.green, self.blue, self.alpha = self.to_rgba(round_alpha=False).lighten(amount).values()
        return hexa(_red=self.red, _green=self.green, _blue=self.blue, _alpha=self.alpha)

    def darken(self, amount: float, /) -> hexa:
        """Decreases the colors lightness by the specified amount in range [0.0, 1.0] inclusive."""

        if not (0.0 <= amount <= 1.0):
            raise ValueError(f"The 'amount' parameter must be in range [0.0, 1.0] inclusive, got {amount!r}")

        self.red, self.green, self.blue, self.alpha = self.to_rgba(round_alpha=False).darken(amount).values()
        return hexa(_red=self.red, _green=self.green, _blue=self.blue, _alpha=self.alpha)

    def saturate(self, amount: float, /) -> hexa:
        """Increases the colors saturation by the specified amount in range [0.0, 1.0] inclusive."""

        if not (0.0 <= amount <= 1.0):
            raise ValueError(f"The 'amount' parameter must be in range [0.0, 1.0] inclusive, got {amount!r}")

        self.red, self.green, self.blue, self.alpha = self.to_rgba(round_alpha=False).saturate(amount).values()
        return hexa(_red=self.red, _green=self.green, _blue=self.blue, _alpha=self.alpha)

    def desaturate(self, amount: float, /) -> hexa:
        """Decreases the colors saturation by the specified amount in range [0.0, 1.0] inclusive."""

        if not (0.0 <= amount <= 1.0):
            raise ValueError(f"The 'amount' parameter must be in range [0.0, 1.0] inclusive, got {amount!r}")

        self.red, self.green, self.blue, self.alpha = self.to_rgba(round_alpha=False).desaturate(amount).values()
        return hexa(_red=self.red, _green=self.green, _blue=self.blue, _alpha=self.alpha)

    def rotate(self, degrees: int, /) -> hexa:
        """Rotates the colors hue by the specified number of degrees."""

        self.red, self.green, self.blue, self.alpha = self.to_rgba(round_alpha=False).rotate(degrees).values()
        return hexa(_red=self.red, _green=self.green, _blue=self.blue, _alpha=self.alpha)

    def invert(self, *, invert_alpha: bool = False) -> hexa:
        """Inverts the color by rotating hue by 180 degrees and inverting lightness."""

        self.red, self.green, self.blue, self.alpha = self.to_rgba(round_alpha=False).invert().values()
        if invert_alpha and self.alpha is not None:
            self.alpha = 1 - self.alpha
        return hexa(_red=self.red, _green=self.green, _blue=self.blue, _alpha=self.alpha)

    def grayscale(self, *, method: Literal["wcag2", "wcag3", "simple", "bt601"] = "wcag2") -> hexa:
        """Converts the color to grayscale using the luminance formula.\n
        -------------------------------------------------------------------------------
        *   `method` – The luminance calculation method to use:
            -   `"wcag2"` WCAG 2.0 standard (default and most accurate for perception)
            -   `"wcag3"` draft WCAG 3.0 standard with improved coefficients
            -   `"simple"` simple arithmetic mean (less accurate)
            -   `"bt601"` ITU-R BT.601 standard (older TV standard)"""

        # The `method` param is validated in `Color.luminance()`.

        self.red = self.green = self.blue = int(Color.luminance(self.red, self.green, self.blue, method=method))
        return hexa(_red=self.red, _green=self.green, _blue=self.blue, _alpha=self.alpha)

    def blend(self, other: Hexa, /, ratio: float = 0.5, *, additive_alpha: bool = False) -> hexa:
        """Blends the current color with another color using the specified ratio in range [0.0, 1.0] inclusive.\n
        ----------------------------------------------------------------------------------------------------------
        *   `other` – The other HEXA color to blend with.
        *   `ratio` – The blend ratio between the two colors:
            -   If `ratio` is `0.0` it means 100% of the current color and 0% of the `other` color (2:0 mixture).
            -   If `ratio` is `0.5` it means 50% of both colors (1:1 mixture).
            -   If `ratio` is `1.0` it means 0% of the current color and 100% of the `other` color (0:2 mixture).
        *   `additive_alpha` – Whether to blend the alpha channels additively or not."""

        if not Color.is_valid_hexa(other):
            raise TypeError(f"The 'other' parameter must be a valid HEXA color, got {type(other)}")
        if not (0.0 <= ratio <= 1.0):
            raise ValueError(f"The 'ratio' parameter must be in range [0.0, 1.0] inclusive, got {ratio!r}")

        self.red, self.green, self.blue, self.alpha = self.to_rgba(round_alpha=False).blend(
            Color.to_rgba(other),
            ratio,
            additive_alpha=additive_alpha,
        ).values()
        return hexa(_red=self.red, _green=self.green, _blue=self.blue, _alpha=self.alpha)

    def is_dark(self) -> bool:
        """Returns `True` if the color is considered dark (`lightness < 50%`)."""

        return self.to_hsla(round_alpha=False).is_dark()

    def is_light(self) -> bool:
        """Returns `True` if the color is considered light (`lightness >= 50%`)."""

        return not self.is_dark()

    def is_grayscale(self) -> bool:
        """Returns `True` if the color is grayscale (`saturation == 0`)."""

        return self.to_hsla(round_alpha=False).is_grayscale()

    def is_opaque(self) -> bool:
        """Returns `True` if the color has no transparency (`alpha == 1.0`)."""

        return self.alpha == 1 or self.alpha is None

    def with_alpha(self, alpha: float, /) -> hexa:
        """Returns a new color with the specified alpha value."""

        if not isinstance(alpha, float):
            raise TypeError(f"The 'alpha' parameter must be a float, got {type(alpha)}")
        elif not (0.0 <= alpha <= 1.0):
            raise ValueError(f"The 'alpha' parameter must be in range [0.0, 1.0] inclusive, got {alpha!r}")

        return hexa(_red=self.red, _green=self.green, _blue=self.blue, _alpha=alpha)

    def complementary(self) -> hexa:
        """Returns the complementary color (180 degrees on the color wheel)."""

        return self.to_hsla(round_alpha=False).complementary().to_hexa()


class Color:
    """This class includes methods to work with colors in different formats."""

    @classmethod
    def is_valid_rgba(cls, color: AnyRgba, /, *, allow_alpha: bool = True) -> bool:
        """Check if the given color is a valid RGBA color.\n
        --------------------------------------------------------------------
        *   `color` – The color to check (can be in any supported format).
        *   `allow_alpha` – Whether to allow alpha channel in the color."""
        try:
            if isinstance(color, rgba):
                return True

            elif isinstance(color, (list, tuple)):
                array_color = cast(list[Any] | tuple[Any, ...], color)

                if (allow_alpha \
                    and len(array_color) == 4
                    and all(isinstance(val, int) for val in array_color[:3])
                    and isinstance(array_color[3], (float, type(None)))
                ):
                    return (
                        0 <= array_color[0] <= 255 and 0 <= array_color[1] <= 255 and 0 <= array_color[2] <= 255
                        and (array_color[3] is None or 0 <= array_color[3] <= 1)
                    )
                elif len(array_color) == 3 and all(isinstance(val, int) for val in array_color):
                    return 0 <= array_color[0] <= 255 and 0 <= array_color[1] <= 255 and 0 <= array_color[2] <= 255
                else:
                    return False

            elif isinstance(color, dict):
                dict_color = cast(dict[str, Any], color)

                if (allow_alpha \
                    and len(dict_color) == 4
                    and all(isinstance(dict_color.get(ch), int) for ch in ("red", "green", "blue"))
                    and isinstance(dict_color.get("alpha", "no alpha"), (float, type(None)))
                ):
                    return (
                        0 <= dict_color["red"] <= 255 and 0 <= dict_color["green"] <= 255 and 0 <= dict_color["blue"] <= 255
                        and (dict_color["alpha"] is None or 0 <= dict_color["alpha"] <= 1)
                    )
                elif len(dict_color) == 3 and all(isinstance(dict_color.get(ch), int) for ch in ("red", "green", "blue")):
                    return 0 <= dict_color["red"] <= 255 and 0 <= dict_color["green"] <= 255 and 0 <= dict_color["blue"] <= 255
                else:
                    return False

            elif isinstance(color, str):
                return bool(_re.fullmatch(Regex.rgba_str(fix_sep=None, allow_alpha=allow_alpha), color))

        except Exception:
            pass
        return False

    @classmethod
    def is_valid_hsla(cls, color: AnyHsla, /, *, allow_alpha: bool = True) -> bool:
        """Check if the given color is a valid HSLA color.\n
        --------------------------------------------------------------------
        *   `color` – The color to check (can be in any supported format).
        *   `allow_alpha` – Whether to allow alpha channel in the color."""

        try:
            if isinstance(color, hsla):
                return True

            elif isinstance(color, (list, tuple)):
                array_color = cast(list[Any] | tuple[Any, ...], color)

                if (allow_alpha \
                    and len(array_color) == 4
                    and all(isinstance(val, int) for val in array_color[:3])
                    and isinstance(array_color[3], (float, type(None)))
                ):
                    return (
                        0 <= array_color[0] <= 360 and 0 <= array_color[1] <= 100 and 0 <= array_color[2] <= 100
                        and (array_color[3] is None or 0 <= array_color[3] <= 1)
                    )
                elif len(array_color) == 3 and all(isinstance(val, int) for val in array_color):
                    return 0 <= array_color[0] <= 360 and 0 <= array_color[1] <= 100 and 0 <= array_color[2] <= 100
                else:
                    return False

            elif isinstance(color, dict):
                dict_color = cast(dict[str, Any], color)

                if (allow_alpha \
                    and len(dict_color) == 4
                    and all(isinstance(dict_color.get(ch), int) for ch in ("hue", "sat", "light"))
                    and isinstance(dict_color.get("alpha", "no alpha"), (float, type(None)))
                ):
                    return (
                        0 <= dict_color["hue"] <= 360 and 0 <= dict_color["sat"] <= 100 and 0 <= dict_color["light"] <= 100
                        and (dict_color["alpha"] is None or 0 <= dict_color["alpha"] <= 1)
                    )
                elif len(dict_color) == 3 and all(isinstance(dict_color.get(ch), int) for ch in ("hue", "sat", "light")):
                    return 0 <= dict_color["hue"] <= 360 and 0 <= dict_color["sat"] <= 100 and 0 <= dict_color["light"] <= 100
                else:
                    return False

            elif isinstance(color, str):
                return bool(_re.fullmatch(Regex.hsla_str(fix_sep=None, allow_alpha=allow_alpha), color))

        except Exception:
            pass
        return False

    @overload
    @classmethod
    def is_valid_hexa(
        cls,
        color: AnyHexa,
        /,
        *,
        allow_alpha: bool = True,
        get_prefix: Literal[True],
    ) -> tuple[bool, Optional[Literal["#", "0x"]]]:
        ...

    @overload
    @classmethod
    def is_valid_hexa(
        cls,
        color: AnyHexa,
        /,
        *,
        allow_alpha: bool = True,
        get_prefix: Literal[False] = False,
    ) -> bool:
        ...

    @overload
    @classmethod
    def is_valid_hexa(
        cls,
        color: AnyHexa,
        /,
        *,
        allow_alpha: bool = True,
        get_prefix: bool = False,
    ) -> bool | tuple[bool, Optional[Literal["#", "0x"]]]:
        ...

    @classmethod
    def is_valid_hexa(
        cls,
        color: AnyHexa,
        /,
        *,
        allow_alpha: bool = True,
        get_prefix: bool = False,
    ) -> bool | tuple[bool, Optional[Literal["#", "0x"]]]:
        """Check if the given color is a valid HEXA color.\n
        ------------------------------------------------------------------------------------------------------
        *   `color` – The color to check (can be in any supported format).
        *   `allow_alpha` – Whether to allow alpha channel in the color.
        *   `get_prefix` – If true, the prefix used in the color (if any) is returned along with validity."""

        try:
            if isinstance(color, hexa):
                return (True, "#") if get_prefix else True

            elif isinstance(color, int):
                is_valid = 0x000000 <= color <= (0xFFFFFFFF if allow_alpha else 0xFFFFFF)
                return (is_valid, "0x") if get_prefix else is_valid

            elif isinstance(color, str):
                prefix: Optional[Literal["#", "0x"]]
                color, prefix = ((color[1:], "#") if color.startswith("#") else
                                 (color[2:], "0x") if color.startswith("0x") else (color, None))
                return (
                    (bool(_re.fullmatch(Regex.hexa_str(allow_alpha=allow_alpha), color)), prefix) \
                    if get_prefix else bool(_re.fullmatch(Regex.hexa_str(allow_alpha=allow_alpha), color))
                )

        except Exception:
            pass
        return (False, None) if get_prefix else False

    @classmethod
    def is_valid(cls, color: AnyRgba | AnyHsla | AnyHexa, /, *, allow_alpha: bool = True) -> bool:
        """Check if the given color is a valid RGBA, HSLA or HEXA color.\n
        --------------------------------------------------------------------
        *   `color` – The color to check (can be in any supported format).
        *   `allow_alpha` – Whether to allow alpha channel in the color."""

        return bool(
            cls.is_valid_rgba(color, allow_alpha=allow_alpha) \
            or cls.is_valid_hsla(color, allow_alpha=allow_alpha) \
            or cls.is_valid_hexa(color, allow_alpha=allow_alpha)
        )

    @classmethod
    def has_alpha(cls, color: Rgba | Hsla | Hexa, /) -> bool:
        """Check if the given color has an alpha channel.\n
        ----------------------------------------------------------------------
        *   `color` – The color to check (can be in any supported format)."""

        if isinstance(color, (rgba, hsla, hexa)):
            return color.has_alpha()

        if cls.is_valid_hexa(color):
            if isinstance(color, str):
                if color.startswith("#"):
                    color = color[1:]
                elif color.startswith("0x"):
                    color = color[2:]
                return len(color) == 4 or len(color) == 8
            if isinstance(color, int):
                hex_length = len(f"{color:X}")
                return hex_length == 4 or hex_length == 8

        elif isinstance(color, str):
            if parsed_rgba := cls.str_to_rgba(color, only_first=True):
                return parsed_rgba.has_alpha()
            if parsed_hsla := cls.str_to_hsla(color, only_first=True):
                return parsed_hsla.has_alpha()

        elif isinstance(color, (list, tuple)) and len(color) == 4:
            return True
        elif isinstance(color, dict) and len(color) == 4:
            return True

        return False

    @classmethod
    def to_rgba(cls, color: Rgba | Hsla | Hexa, /) -> rgba:
        """Will try to convert any color type to a color of type RGBA.\n
        ------------------------------------------------------------------------
        *   `color` – The color to convert (can be in any supported format)."""

        if isinstance(color, (hsla, hexa)):
            return color.to_rgba()
        elif cls.is_valid_hsla(color):
            return cls._parse_hsla(cast(Hsla, color)).to_rgba()
        elif cls.is_valid_hexa(color):
            return hexa(cast(str | int, color)).to_rgba()
        elif cls.is_valid_rgba(color):
            return cls._parse_rgba(cast(Rgba, color))
        raise ValueError(f"Could not convert color {color!r} to RGBA.")

    @classmethod
    def to_hsla(cls, color: Rgba | Hsla | Hexa, /) -> hsla:
        """Will try to convert any color type to a color of type HSLA.\n
        ------------------------------------------------------------------------
        *   `color` – The color to convert (can be in any supported format)."""

        if isinstance(color, (rgba, hexa)):
            return color.to_hsla()
        elif cls.is_valid_rgba(color):
            return cls._parse_rgba(cast(Rgba, color)).to_hsla()
        elif cls.is_valid_hexa(color):
            return hexa(cast(str | int, color)).to_hsla()
        elif cls.is_valid_hsla(color):
            return cls._parse_hsla(cast(Hsla, color))
        raise ValueError(f"Could not convert color {color!r} to HSLA.")

    @classmethod
    def to_hexa(cls, color: Rgba | Hsla | Hexa, /) -> hexa:
        """Will try to convert any color type to a color of type HEXA.\n
        ------------------------------------------------------------------------
        *   `color` – The color to convert (can be in any supported format)."""

        if isinstance(color, (rgba, hsla)):
            return color.to_hexa()
        elif cls.is_valid_rgba(color):
            return cls._parse_rgba(cast(Rgba, color)).to_hexa()
        elif cls.is_valid_hsla(color):
            return cls._parse_hsla(cast(Hsla, color)).to_hexa()
        elif cls.is_valid_hexa(color):
            return color if isinstance(color, hexa) else hexa(cast(str | int, color))
        raise ValueError(f"Could not convert color {color!r} to HEXA")

    @overload
    @classmethod
    def str_to_rgba(cls, string: str, /, *, only_first: Literal[True]) -> Optional[rgba]:
        ...

    @overload
    @classmethod
    def str_to_rgba(cls, string: str, /, *, only_first: Literal[False] = False) -> Optional[list[rgba]]:
        ...

    @overload
    @classmethod
    def str_to_rgba(cls, string: str, /, *, only_first: bool = False) -> Optional[rgba | list[rgba]]:
        ...

    @classmethod
    def str_to_rgba(cls, string: str, /, *, only_first: bool = False) -> Optional[rgba | list[rgba]]:
        """Will try to recognize RGBA colors inside a string and output the found ones as RGBA objects.\n
        ------------------------------------------------------------------------------------------------------------------
        *   `string` – The string to search for RGBA colors.
        *   `only_first` – If true, only the first found color will be returned, otherwise a list of all found colors."""

        if only_first:
            if not (match := _re.search(Regex.rgba_str(allow_alpha=True), string)):
                return None

            groups = match.groups()
            return rgba(
                int(groups[0]),
                int(groups[1]),
                int(groups[2]),
                ((int(groups[3]) if "." not in groups[3] else float(groups[3])) if groups[3] else None),
                _validate=False,
            )

        else:
            if not (matches := _re.findall(Regex.rgba_str(allow_alpha=True), string)):
                return None

            return [
                rgba(
                    int(match[0]),
                    int(match[1]),
                    int(match[2]),
                    ((int(match[3]) if "." not in match[3] else float(match[3])) if match[3] else None),
                    _validate=False,
                ) for match in matches
            ]

    @overload
    @classmethod
    def str_to_hsla(cls, string: str, /, *, only_first: Literal[True]) -> Optional[hsla]:
        ...

    @overload
    @classmethod
    def str_to_hsla(cls, string: str, /, *, only_first: Literal[False] = False) -> Optional[list[hsla]]:
        ...

    @overload
    @classmethod
    def str_to_hsla(cls, string: str, /, *, only_first: bool = False) -> Optional[hsla | list[hsla]]:
        ...

    @classmethod
    def str_to_hsla(cls, string: str, /, *, only_first: bool = False) -> Optional[hsla | list[hsla]]:
        """Will try to recognize HSLA colors inside a string and output the found ones as HSLA objects.\n
        ------------------------------------------------------------------------------------------------------------------
        *   `string` – The string to search for HSLA colors.
        *   `only_first` – If true, only the first found color will be returned, otherwise a list of all found colors."""

        if only_first:
            if not (match := _re.search(Regex.hsla_str(allow_alpha=True), string)):
                return None

            groups = match.groups()
            return hsla(
                int(groups[0]),
                int(groups[1]),
                int(groups[2]),
                ((int(groups[3]) if "." not in groups[3] else float(groups[3])) if groups[3] else None),
                _validate=False,
            )

        else:
            if not (matches := _re.findall(Regex.hsla_str(allow_alpha=True), string)):
                return None

            return [
                hsla(
                    int(match[0]),
                    int(match[1]),
                    int(match[2]),
                    ((int(match[3]) if "." not in match[3] else float(match[3])) if match[3] else None),
                    _validate=False,
                ) for match in matches
            ]

    @classmethod
    def rgba_to_hex_int(
        cls,
        red: int,
        green: int,
        blue: int,
        alpha: Optional[float] = None,
        /,
        *,
        preserve_original: bool = False,
    ) -> int:
        """Convert RGBA channels to a HEXA integer (alpha is optional).\n
        -----------------------------------------------------------------------------------------------
        *   `red`, `green`, `blue` – The red, green, and blue channels in range [0, 255] inclusive.
        *   `alpha` – The alpha channel in range [0.0, 1.0] inclusive or `None` if not set.
        *   `preserve_original` – Whether to preserve the original color exactly (explained below).
        -----------------------------------------------------------------------------------------------
        To preserve leading zeros, the function will add a `1` at the beginning,<br>
        if the HEX integer would start with a `0`.\n
        This could affect the color a little bit, but will make sure, that it won't be interpreted<br>
        as a completely different color, when initializing it as a `hexa()` color or changing it<br>
        back to RGBA using `Color.hex_int_to_rgba()`."""

        if not all((0 <= ch <= 255) for ch in (red, green, blue)):
            raise ValueError(
                "The 'red', 'green' and 'blue' parameters must be integers "
                f"in [0, 255], got {red=!r} {green=!r} {blue=!r}"
            )
        if alpha is not None and not (0.0 <= alpha <= 1.0):
            raise ValueError(f"The 'alpha' parameter must be a float in [0.0, 1.0] or None, got {alpha!r}")

        red = max(0, min(255, int(red)))
        green = max(0, min(255, int(green)))
        blue = max(0, min(255, int(blue)))

        if alpha is None:
            hex_int = (red << 16) | (green << 8) | blue
            if not preserve_original and (hex_int & 0xF00000) == 0:
                hex_int |= 0x010000
        else:
            alpha = max(0, min(255, int(alpha * 255)))
            hex_int = (red << 24) | (green << 16) | (blue << 8) | alpha
            if not preserve_original and red == 0:
                hex_int |= 0x01000000

        return hex_int

    @classmethod
    def hex_int_to_rgba(cls, hex_int: int, /, *, preserve_original: bool = False) -> rgba:
        """Convert a HEX integer to RGBA channels.\n
        -----------------------------------------------------------------------------------------------
        *   `hex_int` – The HEX integer to convert.
        *   `preserve_original` – Whether to preserve the original color exactly (explained below).
        -----------------------------------------------------------------------------------------------
        If the red channel is `1` after conversion, it will be set to `0`, because when converting<br>
        from RGBA to a HEX integer, the first `0` will be set to `1` to preserve leading zeros.\n
        This is the correction, so the color doesn't even look slightly different."""

        if not (0 <= hex_int <= 0xFFFFFFFF):
            raise ValueError(f"Expected HEX integer in range [0x000000, 0xFFFFFFFF] inclusive, got 0x{hex_int:X}")

        if len(hex_str := f"{hex_int:X}") <= 6:
            hex_str = hex_str.zfill(6)
            return rgba(
                red if (red := int(hex_str[0:2], 16)) != 1 or preserve_original else 0,
                int(hex_str[2:4], 16),
                int(hex_str[4:6], 16),
                None,
                _validate=False,
            )

        elif len(hex_str) <= 8:
            hex_str = hex_str.zfill(8)
            return rgba(
                red if (red := int(hex_str[0:2], 16)) != 1 or preserve_original else 0,
                int(hex_str[2:4], 16),
                int(hex_str[4:6], 16),
                int(hex_str[6:8], 16) / 255.0,
                _validate=False,
            )

        else:
            raise ValueError(f"Could not convert HEX integer 0x{hex_int:X} to RGBA color.")

    @overload
    @classmethod
    def luminance(
        cls,
        red: int,
        green: int,
        blue: int,
        /,
        *,
        output_type: type[int],
        method: Literal["wcag2", "wcag3", "simple", "bt601"] = "wcag2",
    ) -> int:
        ...

    @overload
    @classmethod
    def luminance(
        cls,
        red: int,
        green: int,
        blue: int,
        /,
        *,
        output_type: type[float],
        method: Literal["wcag2", "wcag3", "simple", "bt601"] = "wcag2",
    ) -> float:
        ...

    @overload
    @classmethod
    def luminance(
        cls,
        red: int,
        green: int,
        blue: int,
        /,
        *,
        output_type: None = None,
        method: Literal["wcag2", "wcag3", "simple", "bt601"] = "wcag2",
    ) -> int:
        ...

    @overload
    @classmethod
    def luminance(
        cls,
        red: int,
        green: int,
        blue: int,
        /,
        *,
        output_type: Optional[type[int | float]] = None,
        method: Literal["wcag2", "wcag3", "simple", "bt601"] = "wcag2",
    ) -> int | float:
        ...

    @classmethod
    def luminance(
        cls,
        red: int,
        green: int,
        blue: int,
        /,
        *,
        output_type: Optional[type[int | float]] = None,
        method: Literal["wcag2", "wcag3", "simple", "bt601"] = "wcag2",
    ) -> int | float:
        """Calculates the relative luminance of a color according to various standards.\n
        -------------------------------------------------------------------------------------------
        *   `red`, `green`, `blue` – The red, green and blue channels in range [0, 255] inclusive.
        *   `output_type` – The range of the returned luminance value:
            -   `int` returns integer in range [0, 100] inclusive.
            -   `float` returns float in range [0.0, 1.0] inclusive.
            -   `None` returns integer in range [0, 255] inclusive.
        *   `method` – The luminance calculation method to use:
            -   `"wcag2"` WCAG 2.0 standard (default and most accurate for perception)
            -   `"wcag3"` draft WCAG 3.0 standard with improved coefficients
            -   `"simple"` simple arithmetic mean (less accurate)
            -   `"bt601"` ITU-R BT.601 standard (older TV standard)"""

        if not all(0 <= ch <= 255 for ch in (red, green, blue)):
            raise ValueError(
                "The 'red', 'green' and 'blue' parameters must be integers "
                f"in [0, 255], got {red=!r} {green=!r} {blue=!r}"
            )

        _red, _green, _blue = red / 255.0, green / 255.0, blue / 255.0

        if method == "simple":
            luminance = (_red + _green + _blue) / 3
        elif method == "bt601":
            luminance = 0.299 * _red + 0.587 * _green + 0.114 * _blue
        elif method == "wcag3":
            _red = cls._linearize_srgb(_red)
            _green = cls._linearize_srgb(_green)
            _blue = cls._linearize_srgb(_blue)
            luminance = 0.2126729 * _red + 0.7151522 * _green + 0.0721750 * _blue
        else:
            _red = cls._linearize_srgb(_red)
            _green = cls._linearize_srgb(_green)
            _blue = cls._linearize_srgb(_blue)
            luminance = 0.2126 * _red + 0.7152 * _green + 0.0722 * _blue

        if output_type == int:
            return round(luminance * 100)
        elif output_type == float:
            return luminance
        else:
            return round(luminance * 255)

    @overload
    @classmethod
    def text_color_for_on_bg(cls, text_bg_color: rgba, /) -> rgba:
        ...

    @overload
    @classmethod
    def text_color_for_on_bg(cls, text_bg_color: hexa, /) -> hexa:
        ...

    @overload
    @classmethod
    def text_color_for_on_bg(cls, text_bg_color: int, /) -> int:
        ...

    @overload
    @classmethod
    def text_color_for_on_bg(cls, text_bg_color: Rgba | Hexa, /) -> rgba | hexa | int:
        ...

    @classmethod
    def text_color_for_on_bg(cls, text_bg_color: Rgba | Hexa, /) -> rgba | hexa | int:
        """Returns either black or white text color for optimal contrast on the given background color.\n
        --------------------------------------------------------------------------------------------------
        *   `text_bg_color` – The background color (can be in RGBA or HEXA format)."""

        was_hexa, was_int = cls.is_valid_hexa(text_bg_color), isinstance(text_bg_color, int)

        text_bg_rgba = cls.to_rgba(text_bg_color)
        brightness = 0.2126 * text_bg_rgba[0] + 0.7152 * text_bg_rgba[1] + 0.0722 * text_bg_rgba[2]

        return (
            (0xFFFFFF if was_int else hexa(_red=255, _green=255, _blue=255)) if was_hexa \
            else rgba(255, 255, 255, _validate=False)
        ) if brightness < 128 else (
            (0x000 if was_int else hexa(_red=0, _green=0, _blue=0)) if was_hexa \
            else rgba(0, 0, 0, _validate=False)
        )

    @overload
    @classmethod
    def adjust_lightness(cls, color: rgba, light_change: float, /) -> rgba:
        ...

    @overload
    @classmethod
    def adjust_lightness(cls, color: hexa, light_change: float, /) -> hexa:
        ...

    @overload
    @classmethod
    def adjust_lightness(cls, color: Rgba | Hexa, light_change: float, /) -> rgba | hexa:
        ...

    @classmethod
    def adjust_lightness(cls, color: Rgba | Hexa, light_change: float, /) -> rgba | hexa:
        """In- or decrease the lightness of the input color.\n
        ---------------------------------------------------------------------
        *   `color` – The color to adjust (can be in RGBA or HEXA format).
        *   `light_change` – The amount to change the lightness by,<br>
            in range `-1.0` (darken by 100%) and `1.0` (lighten by 100%)."""

        if not (-1.0 <= light_change <= 1.0):
            raise ValueError(f"The 'light_change' parameter must be in range [-1.0, 1.0] inclusive, got {light_change!r}")

        was_hexa = cls.is_valid_hexa(color)
        hsla_color = cls.to_hsla(color)

        hue, sat, light, alpha = (
            int(hsla_color[0]), int(hsla_color[1]), int(hsla_color[2]), \
            hsla_color[3] if hsla_color.has_alpha() else None
        )
        light = int(max(0, min(100, light + light_change * 100)))

        return (
            hsla(hue, sat, light, alpha, _validate=False).to_hexa() if was_hexa \
            else hsla(hue, sat, light, alpha, _validate=False).to_rgba()
        )

    @overload
    @classmethod
    def adjust_saturation(cls, color: rgba, sat_change: float, /) -> rgba:
        ...

    @overload
    @classmethod
    def adjust_saturation(cls, color: hexa, sat_change: float, /) -> hexa:
        ...

    @overload
    @classmethod
    def adjust_saturation(cls, color: Rgba | Hexa, sat_change: float, /) -> rgba | hexa:
        ...

    @classmethod
    def adjust_saturation(cls, color: Rgba | Hexa, sat_change: float, /) -> rgba | hexa:
        """In- or decrease the saturation of the input color.\n
        --------------------------------------------------------------------------
        *   `color` – The color to adjust (can be in RGBA or HEXA format).
        *   `sat_change` – The amount to change the saturation by,<br>
            in range `-1.0` (saturate by 100%) and `1.0` (desaturate by 100%)."""

        if not (-1.0 <= sat_change <= 1.0):
            raise ValueError(f"The 'sat_change' parameter must be in range [-1.0, 1.0] inclusive, got {sat_change!r}")

        was_hexa = cls.is_valid_hexa(color)
        hsla_color = cls.to_hsla(color)

        hue, sat, light, alpha = (
            int(hsla_color[0]), int(hsla_color[1]), int(hsla_color[2]), \
            hsla_color[3] if hsla_color.has_alpha() else None
        )
        sat = int(max(0, min(100, sat + sat_change * 100)))

        return (
            hsla(hue, sat, light, alpha, _validate=False).to_hexa() if was_hexa \
            else hsla(hue, sat, light, alpha, _validate=False).to_rgba()
        )

    @classmethod
    def _parse_rgba(cls, color: Rgba, /) -> rgba:
        """Internal method to parse a color to an RGBA object."""

        if isinstance(color, rgba):
            return color

        elif isinstance(color, (list, tuple)):
            array_color = cast(list[Any] | tuple[Any, ...], color)
            if len(array_color) == 4:
                return rgba(
                    int(array_color[0]),
                    int(array_color[1]),
                    int(array_color[2]),
                    float(array_color[3]),
                    _validate=False,
                )
            elif len(array_color) == 3:
                return rgba(int(array_color[0]), int(array_color[1]), int(array_color[2]), None, _validate=False)
            raise ValueError(f"Could not parse RGBA color: {color!r}")

        elif isinstance(color, dict):
            dict_color = cast(dict[str, Any], color)
            return rgba(
                int(dict_color["red"]),
                int(dict_color["green"]),
                int(dict_color["blue"]),
                dict_color.get("alpha"),
                _validate=False,
            )

        elif isinstance(color, str):
            if parsed := cls.str_to_rgba(color, only_first=True):
                return parsed

        raise ValueError(f"Could not parse RGBA color: {color!r}")

    @classmethod
    def _parse_hsla(cls, color: Hsla, /) -> hsla:
        """Internal method to parse a color to an HSLA object."""

        if isinstance(color, hsla):
            return color

        elif isinstance(color, (list, tuple)):
            array_color = cast(list[Any] | tuple[Any, ...], color)
            if len(color) == 4:
                return hsla(
                    int(array_color[0]),
                    int(array_color[1]),
                    int(array_color[2]),
                    float(array_color[3]),
                    _validate=False,
                )
            elif len(color) == 3:
                return hsla(int(array_color[0]), int(array_color[1]), int(array_color[2]), None, _validate=False)
            raise ValueError(f"Could not parse HSLA color: {color!r}")

        elif isinstance(color, dict):
            dict_color = cast(dict[str, Any], color)
            return hsla(
                int(dict_color["hue"]),
                int(dict_color["sat"]),
                int(dict_color["light"]),
                dict_color.get("alpha"),
                _validate=False,
            )

        elif isinstance(color, str):
            if parsed := cls.str_to_hsla(color, only_first=True):
                return parsed

        raise ValueError(f"Could not parse HSLA color: {color!r}")

    @staticmethod
    def _linearize_srgb(component: float, /) -> float:
        """Helper method to linearize sRGB component following the WCAG standard."""

        if not (0.0 <= component <= 1.0):
            raise ValueError(f"The 'component' parameter must be in range [0.0, 1.0] inclusive, got {component!r}")

        if component <= 0.03928:
            return component / 12.92
        else:
            return ((component + 0.055) / 1.055)**2.4
