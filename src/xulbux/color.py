"""
Provides robust handling for RGBA, HSLA, and HEXA color spaces.

Includes dedicated classes for each color model and utility methods
for interpolating, lightening, darkening, and blending colors.
"""

from __future__ import annotations

from . import regex as _regex_module
from .base.types import Hexa, HexaDict, Hsla, HslaDict, Rgba, RgbaDict

from typing import TYPE_CHECKING, Any, Literal, TypeGuard, cast, overload
import regex as _rx

if TYPE_CHECKING:
    from collections.abc import Iterator


_SRGB_LINEAR_LUT: tuple[float, ...] = tuple([
    (ch / 255.0 / 12.92) if (ch / 255.0 <= 0.03928) else (((ch / 255.0 + 0.055) / 1.055) ** 2.4) for ch in range(256)
])


class _ColorBase:
    alpha: float | None

    def __len__(self) -> int:
        """The number of components in the color (3 or 4)."""

        return 3 if self.alpha is None else 4

    def has_alpha(self) -> bool:
        """Returns `True` if the color has an alpha channel and `False` otherwise."""

        return self.alpha is not None

    def is_opaque(self) -> bool:
        """Returns `True` if the color has no transparency."""

        return self.alpha == 1 or self.alpha is None


class rgba(_ColorBase):
    """An RGB/RGBA color object that includes a bunch of methods to manipulate the color.\n
    ----------------------------------------------------------------------------------------------------
    *   `red` – The red channel in range [0, 255] inclusive.
    *   `green` – The green channel in range [0, 255] inclusive.
    *   `blue` – The blue channel in range [0, 255] inclusive.
    *   `alpha` – The alpha channel in range [0.0, 1.0] inclusive<br>
        or `None` if the color has no alpha channel.\n
    ----------------------------------------------------------------------------------------------------
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

    def __init__(self, red: int, green: int, blue: int, alpha: float | None = None, /, *, _validate: bool = True) -> None:
        self.red: int
        """The red channel in range [0, 255] inclusive."""
        self.green: int
        """The green channel in range [0, 255] inclusive."""
        self.blue: int
        """The blue channel in range [0, 255] inclusive."""
        self.alpha: float | None
        """The alpha channel in range [0.0, 1.0] inclusive or `None` if not set."""

        if not _validate:
            self.red, self.green, self.blue, self.alpha = red, green, blue, alpha
            return

        if not (0 <= red <= 255 and 0 <= green <= 255 and 0 <= blue <= 255):
            raise ValueError(
                "The 'red', 'green' and 'blue' parameters must be integers "
                f"in range [0, 255] inclusive, got {red=!r} {green=!r} {blue=!r}"
            )
        if alpha is not None and not (0.0 <= alpha <= 1.0):
            raise ValueError(f"The 'alpha' parameter must be in range [0.0, 1.0] inclusive, got {alpha!r}")

        self.red, self.green, self.blue = red, green, blue
        self.alpha = None if alpha is None else float(alpha)

    def __iter__(self) -> Iterator[int | float | None]:
        yield self.red
        yield self.green
        yield self.blue

        if self.alpha is not None:
            yield self.alpha

    @overload
    def __getitem__(self, index: Literal[0, 1, 2], /) -> int: ...
    @overload
    def __getitem__(self, index: Literal[3], /) -> float | None: ...
    @overload
    def __getitem__(self, index: int, /) -> int | float | None: ...

    def __getitem__(self, index: int, /) -> int | float | None:
        if index == 0 or (index == -3 and self.alpha is None) or (index == -4 and self.alpha is not None):
            return self.red
        elif index == 1 or (index == -2 and self.alpha is None) or (index == -3 and self.alpha is not None):
            return self.green
        elif index == 2 or (index == -1 and self.alpha is None) or (index == -2 and self.alpha is not None):
            return self.blue
        elif (index == 3 or index == -1) and self.alpha is not None:
            return self.alpha

        raise IndexError("Rgba index out of range")

    def __eq__(self, other: object, /) -> bool:
        """Check if two `rgba` objects are the same color."""

        if not isinstance(other, rgba):
            return False
        return (self.red, self.green, self.blue, self.alpha) == (other.red, other.green, other.blue, other.alpha)

    def __repr__(self) -> str:
        return f"rgba({self.red}, {self.green}, {self.blue}{'' if self.alpha is None else f', {self.alpha}'})"

    def __str__(self) -> str:
        return self.__repr__()

    def dict(self) -> RgbaDict:
        """Returns the color components as a dictionary with keys `"red"`, `"green"`, `"blue"` and optionally `"alpha"`."""

        return RgbaDict(red=self.red, green=self.green, blue=self.blue, alpha=self.alpha)

    def values(self) -> tuple[int, int, int, float | None]:
        """Returns the color components as separate values `red, green, blue, alpha`."""

        return self.red, self.green, self.blue, self.alpha

    def to_hsla(self) -> hsla:
        """Returns the color as `hsla()` color object."""

        hue, sat, light = self._rgb_to_hsl(self.red, self.green, self.blue)
        return hsla(hue, sat, light, self.alpha, _validate=False)

    def to_hexa(self) -> hexa:
        """Returns the color as `hexa()` color object."""

        return hexa(_red=self.red, _green=self.green, _blue=self.blue, _alpha=self.alpha)

    def lighten(self, amount: float, /) -> rgba:
        """Increases the colors lightness by the specified amount in range [0.0, 1.0] inclusive."""

        if not (0.0 <= amount <= 1.0):
            raise ValueError(f"The 'amount' parameter must be in range [0.0, 1.0] inclusive, got {amount!r}")

        return self.to_hsla().lighten(amount).to_rgba()

    def darken(self, amount: float, /) -> rgba:
        """Decreases the colors lightness by the specified amount in range [0.0, 1.0] inclusive."""

        if not (0.0 <= amount <= 1.0):
            raise ValueError(f"The 'amount' parameter must be in range [0.0, 1.0] inclusive, got {amount!r}")

        return self.to_hsla().darken(amount).to_rgba()

    def saturate(self, amount: float, /) -> rgba:
        """Increases the colors saturation by the specified amount in range [0.0, 1.0] inclusive."""

        if not (0.0 <= amount <= 1.0):
            raise ValueError(f"The 'amount' parameter must be in range [0.0, 1.0] inclusive, got {amount!r}")

        return self.to_hsla().saturate(amount).to_rgba()

    def desaturate(self, amount: float, /) -> rgba:
        """Decreases the colors saturation by the specified amount in range [0.0, 1.0] inclusive."""

        if not (0.0 <= amount <= 1.0):
            raise ValueError(f"The 'amount' parameter must be in range [0.0, 1.0] inclusive, got {amount!r}")

        return self.to_hsla().desaturate(amount).to_rgba()

    def rotate(self, degrees: int, /) -> rgba:
        """Rotates the colors hue by the specified number of degrees."""

        return self.to_hsla().rotate(degrees).to_rgba()

    def invert(self, *, invert_alpha: bool = False) -> rgba:
        """Inverts the color by rotating hue by 180 degrees and inverting lightness."""

        alpha = (1.0 - self.alpha if self.alpha is not None else None) if invert_alpha else self.alpha
        return rgba(255 - self.red, 255 - self.green, 255 - self.blue, alpha, _validate=False)

    def grayscale(self, *, method: Literal["wcag2", "wcag3", "simple", "bt601"] = "wcag2") -> rgba:
        """Converts the color to grayscale using the luminance formula.\n
        ----------------------------------------------------------------------------------------------------
        *   `method` – The luminance calculation method to use:
            -   `"wcag2"` WCAG 2.0 standard (default and most accurate for perception)
            -   `"wcag3"` draft WCAG 3.0 standard with improved coefficients
            -   `"simple"` simple arithmetic mean (less accurate)
            -   `"bt601"` ITU-R BT.601 standard (older TV standard)"""

        # The `method` param is validated in `luminance()`.

        gray = int(luminance(self.red, self.green, self.blue, method=method))
        return rgba(gray, gray, gray, self.alpha, _validate=False)

    def blend(self, other: Rgba, /, ratio: float = 0.5, *, additive_alpha: bool = False) -> rgba:
        """Blends the current color with another color
        using the specified ratio in range [0.0, 1.0] inclusive.\n
        ----------------------------------------------------------------------------------------------------
        *   `other` – The other RGBA color to blend with.
        *   `ratio` – The blend ratio between the two colors:
            -   If `ratio` is `0.0` it means 100% of the current color
                and 0% of the `other` color (2:0 mixture).
            -   If `ratio` is `0.5` it means 50% of both colors (1:1 mixture).
            -   If `ratio` is `1.0` it means 0% of the current color
                and 100% of the `other` color (0:2 mixture).
        *   `additive_alpha` – Whether to blend the alpha channels additively or not."""

        if not is_valid_rgba(other):
            raise TypeError(f"The 'other' parameter must be a valid RGBA color, got {other!r}")
        if not (0.0 <= ratio <= 1.0):
            raise ValueError(f"The 'ratio' parameter must be in range [0.0, 1.0] inclusive, got {ratio!r}")

        other_rgba = to_rgba(other)

        red = int(max(0, min(255, int((self.red * (1 - ratio)) + (other_rgba.red * ratio) + 0.5))))
        green = int(max(0, min(255, int((self.green * (1 - ratio)) + (other_rgba.green * ratio) + 0.5))))
        blue = int(max(0, min(255, int((self.blue * (1 - ratio)) + (other_rgba.blue * ratio) + 0.5))))
        none_alpha = self.alpha is None and (len(other_rgba) <= 3 or other_rgba[3] is None)

        if not none_alpha:
            self_a: float = 1.0 if self.alpha is None else self.alpha
            other_a: float = cast("float", 1.0 if other_rgba[3] is None else other_rgba[3]) if len(other_rgba) > 3 else 1.0

            if additive_alpha:
                # Additive blend calculation
                ratio2 = ratio * 2
                alpha = max(0.0, min(1.0, (self_a * (2 - ratio2)) + (other_a * ratio2)))
            else:
                alpha = max(0.0, min(1.0, (self_a * (1 - ratio)) + (other_a * ratio)))

        else:
            alpha = None

        return rgba(red, green, blue, alpha, _validate=False)

    def is_dark(self) -> bool:
        """Returns `True` if the color is considered dark (`lightness < 50%`)."""

        return self.to_hsla().is_dark()

    def is_light(self) -> bool:
        """Returns `True` if the color is considered light (`lightness >= 50%`)."""

        return not self.is_dark()

    def is_grayscale(self) -> bool:
        """Returns `True` if the color is grayscale."""

        return self.red == self.green == self.blue

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

        red_norm, green_norm, blue_norm = red / 255.0, green / 255.0, blue / 255.0
        max_c, min_c = max(red_norm, green_norm, blue_norm), min(red_norm, green_norm, blue_norm)
        light = (max_c + min_c) / 2

        if max_c == min_c:
            hue = sat = 0.0

        else:
            delta = max_c - min_c
            sat = delta / (1 - abs(2 * light - 1))

            if max_c == red_norm:
                hue = ((green_norm - blue_norm) / delta) % 6
            elif max_c == green_norm:
                hue = ((blue_norm - red_norm) / delta) + 2
            else:
                hue = ((red_norm - green_norm) / delta) + 4

            hue /= 6

        return round(hue * 360), round(sat * 100), round(light * 100)


class hsla(_ColorBase):
    """A HSL/HSLA color object that includes a bunch of methods to manipulate the color.\n
    ----------------------------------------------------------------------------------------------------
    *   `hue` – The hue channel in range [0, 360] inclusive.
    *   `sat` – The saturation channel in range [0, 100] inclusive.
    *   `light` – The lightness channel in range [0, 100] inclusive.
    *   `alpha` – The alpha channel in range [0.0, 1.0] inclusive<br>
        or `None` if the color has no alpha channel.\n
    ----------------------------------------------------------------------------------------------------
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

    def __init__(self, hue: int, sat: int, light: int, alpha: float | None = None, /, *, _validate: bool = True) -> None:
        self.hue: int
        """The hue channel in range [0, 360] inclusive."""
        self.sat: int
        """The saturation channel in range [0, 100] inclusive."""
        self.light: int
        """The lightness channel in range [0, 100] inclusive."""
        self.alpha: float | None
        """The alpha channel in range [0.0, 1.0] inclusive or `None` if not set."""

        if not _validate:
            self.hue, self.sat, self.light, self.alpha = hue, sat, light, alpha
            return

        if not (0 <= hue <= 360):
            raise ValueError(f"The 'hue' parameter must be in range [0, 360] inclusive, got {hue!r}")
        if not (0 <= sat <= 100 and 0 <= light <= 100):
            raise ValueError(f"The 'sat' and 'light' parameters must be in range [0, 100] inclusive, got {sat=!r} {light=!r}")
        if alpha is not None and not (0.0 <= alpha <= 1.0):
            raise ValueError(f"The 'alpha' parameter must be in range [0.0, 1.0] inclusive, got {alpha!r}")

        self.hue, self.sat, self.light = hue, sat, light
        self.alpha = None if alpha is None else float(alpha)

    def __iter__(self) -> Iterator[int | float | None]:
        yield self.hue
        yield self.sat
        yield self.light

        if self.alpha is not None:
            yield self.alpha

    @overload
    def __getitem__(self, index: Literal[0, 1, 2], /) -> int: ...
    @overload
    def __getitem__(self, index: Literal[3], /) -> float | None: ...
    @overload
    def __getitem__(self, index: int, /) -> int | float | None: ...

    def __getitem__(self, index: int, /) -> int | float | None:
        if index == 0 or (index == -3 and self.alpha is None) or (index == -4 and self.alpha is not None):
            return self.hue
        elif index == 1 or (index == -2 and self.alpha is None) or (index == -3 and self.alpha is not None):
            return self.sat
        elif index == 2 or (index == -1 and self.alpha is None) or (index == -2 and self.alpha is not None):
            return self.light
        elif (index == 3 or index == -1) and self.alpha is not None:
            return self.alpha

        raise IndexError("Hsla index out of range")

    def __eq__(self, other: object, /) -> bool:
        """Check if two `hsla` objects are the same color."""

        if not isinstance(other, hsla):
            return False
        return (self.hue, self.sat, self.light, self.alpha) == (other.hue, other.sat, other.light, other.alpha)

    def __repr__(self) -> str:
        return f"hsla({self.hue}°, {self.sat}%, {self.light}%{'' if self.alpha is None else f', {self.alpha}'})"

    def __str__(self) -> str:
        return self.__repr__()

    def dict(self) -> HslaDict:
        """Returns the color components as a dictionary with keys `"hue"`, `"sat"`, `"light"` and optionally `"alpha"`."""

        return HslaDict(hue=self.hue, sat=self.sat, light=self.light, alpha=self.alpha)

    def values(self) -> tuple[int, int, int, float | None]:
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

    def lighten(self, amount: float, /) -> hsla:
        """Increases the colors lightness by the specified amount in range [0.0, 1.0] inclusive."""

        if not (0.0 <= amount <= 1.0):
            raise ValueError(f"The 'amount' parameter must be in range [0.0, 1.0] inclusive, got {amount!r}")

        return hsla(self.hue, self.sat, int(min(100, self.light + (100 - self.light) * amount)), self.alpha, _validate=False)

    def darken(self, amount: float, /) -> hsla:
        """Decreases the colors lightness by the specified amount in range [0.0, 1.0] inclusive."""

        if not (0.0 <= amount <= 1.0):
            raise ValueError(f"The 'amount' parameter must be in range [0.0, 1.0] inclusive, got {amount!r}")

        return hsla(self.hue, self.sat, int(max(0, self.light * (1 - amount))), self.alpha, _validate=False)

    def saturate(self, amount: float, /) -> hsla:
        """Increases the colors saturation by the specified amount in range [0.0, 1.0] inclusive."""

        if not (0.0 <= amount <= 1.0):
            raise ValueError(f"The 'amount' parameter must be in range [0.0, 1.0] inclusive, got {amount!r}")

        return hsla(self.hue, int(min(100, self.sat + (100 - self.sat) * amount)), self.light, self.alpha, _validate=False)

    def desaturate(self, amount: float, /) -> hsla:
        """Decreases the colors saturation by the specified amount in range [0.0, 1.0] inclusive."""

        if not (0.0 <= amount <= 1.0):
            raise ValueError(f"The 'amount' parameter must be in range [0.0, 1.0] inclusive, got {amount!r}")

        return hsla(self.hue, int(max(0, self.sat * (1 - amount))), self.light, self.alpha, _validate=False)

    def rotate(self, degrees: int, /) -> hsla:
        """Rotates the colors hue by the specified number of degrees."""

        return hsla((self.hue + degrees) % 360, self.sat, self.light, self.alpha, _validate=False)

    def invert(self, *, invert_alpha: bool = False) -> hsla:
        """Inverts the color by rotating hue by 180 degrees and inverting lightness."""

        alpha = (1.0 - self.alpha if self.alpha is not None else None) if invert_alpha else self.alpha
        return hsla((self.hue + 180) % 360, self.sat, 100 - self.light, alpha, _validate=False)

    def grayscale(self, *, method: Literal["wcag2", "wcag3", "simple", "bt601"] = "wcag2") -> hsla:
        """Converts the color to grayscale using the luminance formula.\n
        ----------------------------------------------------------------------------------------------------
        *   `method` – The luminance calculation method to use:
            -   `"wcag2"` WCAG 2.0 standard (default and most accurate for perception)
            -   `"wcag3"` draft WCAG 3.0 standard with improved coefficients
            -   `"simple"` simple arithmetic mean (less accurate)
            -   `"bt601"` ITU-R BT.601 standard (older TV standard)"""

        # The `method` param is validated in `luminance()`.

        red, green, blue = self._hsl_to_rgb(self.hue, self.sat, self.light)
        light = int(luminance(red, green, blue, output_type=None, method=method))
        hue, sat, light_val, _ = rgba(light, light, light, _validate=False).to_hsla().values()
        return hsla(hue, sat, light_val, self.alpha, _validate=False)

    def blend(self, other: Hsla, /, ratio: float = 0.5, *, additive_alpha: bool = False) -> hsla:
        """Blends the current color with another color
        using the specified ratio in range [0.0, 1.0] inclusive.\n
        ----------------------------------------------------------------------------------------------------
        *   `other` – The other HSLA color to blend with.
        *   `ratio` – The blend ratio between the two colors:
            -   If `ratio` is `0.0` it means 100% of the current color
                and 0% of the `other` color (2:0 mixture).
            -   If `ratio` is `0.5` it means 50% of both colors (1:1 mixture).
            -   If `ratio` is `1.0` it means 0% of the current color
                and 100% of the `other` color (0:2 mixture).
        *   `additive_alpha` – whether to blend the alpha channels additively or not."""

        if not is_valid_hsla(other):
            raise TypeError(f"The 'other' parameter must be a valid HSLA color, got {other!r}")
        if not (0.0 <= ratio <= 1.0):
            raise ValueError(f"The 'ratio' parameter must be in range [0.0, 1.0] inclusive, got {ratio!r}")

        return self.to_rgba().blend(to_rgba(other), ratio, additive_alpha=additive_alpha).to_hsla()

    def is_dark(self) -> bool:
        """Returns `True` if the color is considered dark (`lightness < 50%`)."""

        return self.light < 50

    def is_light(self) -> bool:
        """Returns `True` if the color is considered light (`lightness >= 50%`)."""

        return not self.is_dark()

    def is_grayscale(self) -> bool:
        """Returns `True` if the color is considered grayscale."""

        return self.sat == 0

    def with_alpha(self, alpha: float, /) -> hsla:
        """Returns a new color with the specified alpha value."""

        if not (0.0 <= alpha <= 1.0):
            raise ValueError(f"The 'alpha' parameter must be in range [0.0, 1.0] inclusive, got {alpha!r}")

        return hsla(self.hue, self.sat, self.light, alpha, _validate=False)

    def complementary(self) -> hsla:
        """Returns the complementary color (180 degrees on the color wheel)."""

        return hsla((self.hue + 180) % 360, self.sat, self.light, self.alpha, _validate=False)

    @classmethod
    def _hsl_to_rgb(cls, hue: int, sat: int, light: int) -> tuple[int, int, int]:
        """Internal method to convert HSL to RGB color space."""

        hue_norm, sat_norm, light_norm = hue / 360, sat / 100, light / 100

        if sat_norm == 0:
            red = green = blue = int(light_norm * 255)

        else:
            chroma_max = light_norm * (1 + sat_norm) if light_norm < 0.5 else light_norm + sat_norm - light_norm * sat_norm
            chroma_min = 2 * light_norm - chroma_max

            red = round(cls._hue_to_rgb(chroma_min, chroma_max, hue_norm + 1 / 3) * 255)
            green = round(cls._hue_to_rgb(chroma_min, chroma_max, hue_norm) * 255)
            blue = round(cls._hue_to_rgb(chroma_min, chroma_max, hue_norm - 1 / 3) * 255)

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


class hexa(_ColorBase):
    """A HEXA color object that includes a bunch of methods to manipulate the color.\n
    ----------------------------------------------------------------------------------------------------
    *   `color` – The HEXA color string (prefix optional) or HEX integer, that can be in formats:
        -   `RGB` short format without alpha (only for strings)
        -   `RGBA` short format with alpha (only for strings)
        -   `RRGGBB` long format without alpha (for strings and HEX integers)
        -   `RRGGBBAA` long format with alpha (for strings and HEX integers)\n
    ----------------------------------------------------------------------------------------------------
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
        color: Hexa | None = None,
        /,
        *,
        _red: int | None = None,
        _green: int | None = None,
        _blue: int | None = None,
        _alpha: float | None = None,
    ) -> None:
        self.red: int
        """The red channel in range [0, 255] inclusive."""
        self.green: int
        """The green channel in range [0, 255] inclusive."""
        self.blue: int
        """The blue channel in range [0, 255] inclusive."""
        self.alpha: float | None
        """The alpha channel in range [0.0, 1.0] inclusive or `None` if not set."""

        if _red is not None and _green is not None and _blue is not None:
            self.red, self.green, self.blue, self.alpha = _red, _green, _blue, _alpha
            return

        if isinstance(color, hexa):
            self.red, self.green, self.blue, self.alpha = color.red, color.green, color.blue, color.alpha

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
                raise ValueError(f"Invalid HEXA color string '{color}'\nMust be in formats RGB, RGBA, RRGGBB or RRGGBBAA")

        elif isinstance(color, int):
            self.red, self.green, self.blue, self.alpha = hex_int_to_rgba(color).values()

        elif color is not None and hasattr(color, "red") and hasattr(color, "green") and hasattr(color, "blue"):
            self.red, self.green, self.blue, self.alpha = (
                int(color.red),
                int(color.green),
                int(color.blue),
                getattr(color, "alpha", None),
            )

        else:
            raise ValueError(
                f"Could initialize hexa() color object from {color!r}\n"
                "Must be a HEXA string, HEX integer, or an object with 'red', 'green', 'blue', and optionally 'alpha' attrs"
            )

    def __iter__(self) -> Iterator[str]:
        yield f"{self.red:02X}"
        yield f"{self.green:02X}"
        yield f"{self.blue:02X}"

        if self.alpha is not None:
            yield f"{int(self.alpha * 255):02X}"

    def __getitem__(self, index: int, /) -> str:
        if index == 0 or (index == -3 and self.alpha is None) or (index == -4 and self.alpha is not None):
            return f"{self.red:02X}"
        elif index == 1 or (index == -2 and self.alpha is None) or (index == -3 and self.alpha is not None):
            return f"{self.green:02X}"
        elif index == 2 or (index == -1 and self.alpha is None) or (index == -2 and self.alpha is not None):
            return f"{self.blue:02X}"
        elif (index == 3 or index == -1) and self.alpha is not None:
            return f"{int(self.alpha * 255):02X}"

        raise IndexError("Hexa index out of range")

    def __eq__(self, other: object, /) -> bool:
        """Check if two `hexa` objects are the same color."""

        if not isinstance(other, hexa):
            return False
        return (self.red, self.green, self.blue, self.alpha) == (other.red, other.green, other.blue, other.alpha)

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

    def values(self, *, round_alpha: bool = True) -> tuple[int, int, int, float | None]:
        """Returns the color components as separate values `red, green, blue, alpha`."""

        return (
            self.red,
            self.green,
            self.blue,
            None if self.alpha is None else (round(self.alpha, 2) if round_alpha else self.alpha),
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

    def lighten(self, amount: float, /) -> hexa:
        """Increases the colors lightness by the specified amount in range [0.0, 1.0] inclusive."""

        if not (0.0 <= amount <= 1.0):
            raise ValueError(f"The 'amount' parameter must be in range [0.0, 1.0] inclusive, got {amount!r}")

        red, green, blue, alpha = self.to_rgba(round_alpha=False).lighten(amount).values()
        return hexa(_red=red, _green=green, _blue=blue, _alpha=alpha)

    def darken(self, amount: float, /) -> hexa:
        """Decreases the colors lightness by the specified amount in range [0.0, 1.0] inclusive."""

        if not (0.0 <= amount <= 1.0):
            raise ValueError(f"The 'amount' parameter must be in range [0.0, 1.0] inclusive, got {amount!r}")

        red, green, blue, alpha = self.to_rgba(round_alpha=False).darken(amount).values()
        return hexa(_red=red, _green=green, _blue=blue, _alpha=alpha)

    def saturate(self, amount: float, /) -> hexa:
        """Increases the colors saturation by the specified amount in range [0.0, 1.0] inclusive."""

        if not (0.0 <= amount <= 1.0):
            raise ValueError(f"The 'amount' parameter must be in range [0.0, 1.0] inclusive, got {amount!r}")

        red, green, blue, alpha = self.to_rgba(round_alpha=False).saturate(amount).values()
        return hexa(_red=red, _green=green, _blue=blue, _alpha=alpha)

    def desaturate(self, amount: float, /) -> hexa:
        """Decreases the colors saturation by the specified amount in range [0.0, 1.0] inclusive."""

        if not (0.0 <= amount <= 1.0):
            raise ValueError(f"The 'amount' parameter must be in range [0.0, 1.0] inclusive, got {amount!r}")

        red, green, blue, alpha = self.to_rgba(round_alpha=False).desaturate(amount).values()
        return hexa(_red=red, _green=green, _blue=blue, _alpha=alpha)

    def rotate(self, degrees: int, /) -> hexa:
        """Rotates the colors hue by the specified number of degrees."""

        red, green, blue, alpha = self.to_rgba(round_alpha=False).rotate(degrees).values()
        return hexa(_red=red, _green=green, _blue=blue, _alpha=alpha)

    def invert(self, *, invert_alpha: bool = False) -> hexa:
        """Inverts the color by rotating hue by 180 degrees and inverting lightness."""

        red, green, blue, alpha = self.to_rgba(round_alpha=False).invert(invert_alpha=invert_alpha).values()
        return hexa(_red=red, _green=green, _blue=blue, _alpha=alpha)

    def grayscale(self, *, method: Literal["wcag2", "wcag3", "simple", "bt601"] = "wcag2") -> hexa:
        """Converts the color to grayscale using the luminance formula.\n
        ----------------------------------------------------------------------------------------------------
        *   `method` – The luminance calculation method to use:
            -   `"wcag2"` WCAG 2.0 standard (default and most accurate for perception)
            -   `"wcag3"` draft WCAG 3.0 standard with improved coefficients
            -   `"simple"` simple arithmetic mean (less accurate)
            -   `"bt601"` ITU-R BT.601 standard (older TV standard)"""

        # The `method` param is validated in `luminance()`.

        gray = int(luminance(self.red, self.green, self.blue, method=method))
        return hexa(_red=gray, _green=gray, _blue=gray, _alpha=self.alpha)

    def blend(self, other: Hexa, /, ratio: float = 0.5, *, additive_alpha: bool = False) -> hexa:
        """Blends the current color with another color
        using the specified ratio in range [0.0, 1.0] inclusive.\n
        ----------------------------------------------------------------------------------------------------
        *   `other` – The other HEXA color to blend with.
        *   `ratio` – The blend ratio between the two colors:
            -   If `ratio` is `0.0` it means 100% of the current color
                and 0% of the `other` color (2:0 mixture).
            -   If `ratio` is `0.5` it means 50% of both colors (1:1 mixture).
            -   If `ratio` is `1.0` it means 0% of the current color
                and 100% of the `other` color (0:2 mixture).
        *   `additive_alpha` – Whether to blend the alpha channels additively or not."""

        if not is_valid_hexa(other):
            raise TypeError(f"The 'other' parameter must be a valid HEXA color, got {other!r}")
        if not (0.0 <= ratio <= 1.0):
            raise ValueError(f"The 'ratio' parameter must be in range [0.0, 1.0] inclusive, got {ratio!r}")

        red, green, blue, alpha = (
            self.to_rgba(round_alpha=False).blend(to_rgba(other), ratio, additive_alpha=additive_alpha).values()
        )
        return hexa(_red=red, _green=green, _blue=blue, _alpha=alpha)

    def is_dark(self) -> bool:
        """Returns `True` if the color is considered dark (`lightness < 50%`)."""

        return self.to_hsla(round_alpha=False).is_dark()

    def is_light(self) -> bool:
        """Returns `True` if the color is considered light (`lightness >= 50%`)."""

        return not self.is_dark()

    def is_grayscale(self) -> bool:
        """Returns `True` if the color is grayscale (`saturation == 0`)."""

        return self.red == self.green == self.blue

    def with_alpha(self, alpha: float, /) -> hexa:
        """Returns a new color with the specified alpha value."""

        if not (0.0 <= alpha <= 1.0):
            raise ValueError(f"The 'alpha' parameter must be in range [0.0, 1.0] inclusive, got {alpha!r}")

        return hexa(_red=self.red, _green=self.green, _blue=self.blue, _alpha=alpha)

    def complementary(self) -> hexa:
        """Returns the complementary color (180 degrees on the color wheel)."""

        return self.to_hsla(round_alpha=False).complementary().to_hexa()


def is_valid_rgba(color: object, /, *, allow_alpha: bool = True) -> TypeGuard[Rgba]:
    """Check if the given color is a valid RGBA color.\n
    ----------------------------------------------------------------------------------------------------
    *   `color` – The color to check (can be in any supported format).
    *   `allow_alpha` – Whether to allow alpha channel in the color."""

    if isinstance(color, rgba):
        return True

    elif isinstance(color, (list, tuple)):
        color_seq = cast("list[Any] | tuple[Any, ...]", color)
        if (
            allow_alpha
            and len(color_seq) == 4
            and (isinstance(color_seq[0], int) and isinstance(color_seq[1], int) and isinstance(color_seq[2], int))
            and isinstance(color_seq[3], (float, type(None)))
        ):
            return (
                0 <= color_seq[0] <= 255
                and 0 <= color_seq[1] <= 255
                and 0 <= color_seq[2] <= 255
                and (color_seq[3] is None or 0 <= color_seq[3] <= 1)
            )
        elif len(color_seq) == 3 and (
            isinstance(color_seq[0], int) and isinstance(color_seq[1], int) and isinstance(color_seq[2], int)
        ):
            return 0 <= color_seq[0] <= 255 and 0 <= color_seq[1] <= 255 and 0 <= color_seq[2] <= 255
        else:
            return False

    elif isinstance(color, dict):
        color_dict = cast("dict[str, Any]", color)
        if (
            allow_alpha
            and len(color_dict) == 4
            and (
                isinstance(color_dict.get("red"), int)
                and isinstance(color_dict.get("green"), int)
                and isinstance(color_dict.get("blue"), int)
            )
            and isinstance(color_dict.get("alpha", "no alpha"), (float, type(None)))
        ):
            return (
                0 <= color_dict["red"] <= 255
                and 0 <= color_dict["green"] <= 255
                and 0 <= color_dict["blue"] <= 255
                and (color_dict["alpha"] is None or 0 <= color_dict["alpha"] <= 1)
            )
        elif len(color_dict) == 3 and (
            isinstance(color_dict.get("red"), int)
            and isinstance(color_dict.get("green"), int)
            and isinstance(color_dict.get("blue"), int)
        ):
            return 0 <= color_dict["red"] <= 255 and 0 <= color_dict["green"] <= 255 and 0 <= color_dict["blue"] <= 255
        else:
            return False

    elif isinstance(color, str):
        return bool(_rx.fullmatch(_regex_module.rgba_str(fix_sep=None, allow_alpha=allow_alpha), color))
    return False


def is_valid_hsla(color: object, /, *, allow_alpha: bool = True) -> TypeGuard[Hsla]:
    """Check if the given color is a valid HSLA color.\n
    ----------------------------------------------------------------------------------------------------
    *   `color` – The color to check (can be in any supported format).
    *   `allow_alpha` – Whether to allow alpha channel in the color."""

    if isinstance(color, hsla):
        return True

    elif isinstance(color, (list, tuple)):
        color_seq = cast("list[Any] | tuple[Any, ...]", color)
        if (
            allow_alpha
            and len(color_seq) == 4
            and (isinstance(color_seq[0], int) and isinstance(color_seq[1], int) and isinstance(color_seq[2], int))
            and isinstance(color_seq[3], (float, type(None)))
        ):
            return (
                0 <= color_seq[0] <= 360
                and 0 <= color_seq[1] <= 100
                and 0 <= color_seq[2] <= 100
                and (color_seq[3] is None or 0 <= color_seq[3] <= 1)
            )
        elif len(color_seq) == 3 and (
            isinstance(color_seq[0], int) and isinstance(color_seq[1], int) and isinstance(color_seq[2], int)
        ):
            return 0 <= color_seq[0] <= 360 and 0 <= color_seq[1] <= 100 and 0 <= color_seq[2] <= 100
        else:
            return False

    elif isinstance(color, dict):
        color_dict = cast("dict[str, Any]", color)
        if (
            allow_alpha
            and len(color_dict) == 4
            and (
                isinstance(color_dict.get("hue"), int)
                and isinstance(color_dict.get("sat"), int)
                and isinstance(color_dict.get("light"), int)
            )
            and isinstance(color_dict.get("alpha", "no alpha"), (float, type(None)))
        ):
            return (
                0 <= color_dict["hue"] <= 360
                and 0 <= color_dict["sat"] <= 100
                and 0 <= color_dict["light"] <= 100
                and (color_dict["alpha"] is None or 0 <= color_dict["alpha"] <= 1)
            )
        elif len(color_dict) == 3 and (
            isinstance(color_dict.get("hue"), int)
            and isinstance(color_dict.get("sat"), int)
            and isinstance(color_dict.get("light"), int)
        ):
            return 0 <= color_dict["hue"] <= 360 and 0 <= color_dict["sat"] <= 100 and 0 <= color_dict["light"] <= 100
        else:
            return False

    elif isinstance(color, str):
        return bool(_rx.fullmatch(_regex_module.hsla_str(fix_sep=None, allow_alpha=allow_alpha), color))
    return False


@overload
def is_valid_hexa(
    color: object, /, *, allow_alpha: bool = True, get_prefix: Literal[True]
) -> tuple[bool, Literal["#", "0x"] | None]: ...
@overload
def is_valid_hexa(color: object, /, *, allow_alpha: bool = True, get_prefix: Literal[False] = False) -> TypeGuard[Hexa]: ...
@overload
def is_valid_hexa(
    color: object, /, *, allow_alpha: bool = True, get_prefix: bool = False
) -> TypeGuard[Hexa] | tuple[bool, Literal["#", "0x"] | None]: ...


def is_valid_hexa(
    color: object, /, *, allow_alpha: bool = True, get_prefix: bool = False
) -> TypeGuard[Hexa] | tuple[bool, Literal["#", "0x"] | None]:
    """Check if the given color is a valid HEXA color.\n
    ----------------------------------------------------------------------------------------------------
    *   `color` – The color to check (can be in any supported format).
    *   `allow_alpha` – Whether to allow alpha channel in the color.
    *   `get_prefix` – If true, the prefix used in the color (if any)
        is returned along with validity."""

    if isinstance(color, hexa):
        return (True, "#") if get_prefix else True

    elif isinstance(color, int):
        is_valid_int = 0x000000 <= color <= (0xFFFFFFFF if allow_alpha else 0xFFFFFF)
        return (is_valid_int, "0x") if get_prefix else is_valid_int

    elif isinstance(color, str):
        prefix: Literal["#", "0x"] | None
        color, prefix = (
            (color[1:], "#") if color.startswith("#") else (color[2:], "0x") if color.startswith("0x") else (color, None)
        )
        return (
            (bool(_rx.fullmatch(_regex_module.hexa_str(allow_alpha=allow_alpha), color)), prefix)
            if get_prefix
            else bool(_rx.fullmatch(_regex_module.hexa_str(allow_alpha=allow_alpha), color))
        )
    return (False, None) if get_prefix else False


def is_valid(color: object, /, *, allow_alpha: bool = True) -> TypeGuard[Rgba | Hsla | Hexa]:
    """Check if the given color is a valid RGBA, HSLA or HEXA color.\n
    ----------------------------------------------------------------------------------------------------
    *   `color` – The color to check (can be in any supported format).
    *   `allow_alpha` – Whether to allow alpha channel in the color."""

    return bool(
        is_valid_rgba(color, allow_alpha=allow_alpha)
        or is_valid_hsla(color, allow_alpha=allow_alpha)
        or is_valid_hexa(color, allow_alpha=allow_alpha)
    )


def has_alpha(color: Rgba | Hsla | Hexa, /) -> bool:
    """Check if the given color has an alpha channel.\n
    ----------------------------------------------------------------------------------------------------
    *   `color` – The color to check (can be in any supported format)."""

    if isinstance(color, (rgba, hsla, hexa)):
        return color.has_alpha()

    if is_valid_hexa(color):
        if isinstance(color, str):
            if color.startswith("#"):
                color = color[1:]
            elif color.startswith("0x"):
                color = color[2:]
            return len(color) == 4 or len(color) == 8

        # It must be an int if it's a valid hexa and not a string (hexa object handled above)
        hex_length = len(f"{cast('int', color):X}")
        return hex_length == 4 or hex_length == 8

    if isinstance(color, str):
        if parsed_rgba := str_to_rgba(color, only_first=True):
            return parsed_rgba.has_alpha()
        if parsed_hsla := str_to_hsla(color, only_first=True):
            return parsed_hsla.has_alpha()

    elif (isinstance(color, (list, tuple)) and len(color) == 4) or (isinstance(color, dict) and len(color) == 4):
        return True

    return False


def to_rgba(color: Rgba | Hsla | Hexa, /) -> rgba:
    """Will try to convert any color type to a color of type RGBA.\n
    ----------------------------------------------------------------------------------------------------
    *   `color` – The color to convert (can be in any supported format)."""

    if isinstance(color, (hsla, hexa)):
        return color.to_rgba()
    elif is_valid_hsla(color):
        return _parse_hsla(color).to_rgba()
    elif is_valid_hexa(color):
        return hexa(color).to_rgba()
    elif is_valid_rgba(color):
        return _parse_rgba(color)

    raise ValueError(f"Could not convert color {color!r} to RGBA\nMust be a valid RGBA, HSLA, or HEXA color")


def to_hsla(color: Rgba | Hsla | Hexa, /) -> hsla:
    """Will try to convert any color type to a color of type HSLA.\n
    ----------------------------------------------------------------------------------------------------
    *   `color` – The color to convert (can be in any supported format)."""

    if isinstance(color, (rgba, hexa)):
        return color.to_hsla()
    elif is_valid_rgba(color):
        return _parse_rgba(color).to_hsla()
    elif is_valid_hexa(color):
        return hexa(color).to_hsla()
    elif is_valid_hsla(color):
        return _parse_hsla(color)

    raise ValueError(f"Could not convert color {color!r} to HSLA\nMust be a valid RGBA, HSLA, or HEXA color")


def to_hexa(color: Rgba | Hsla | Hexa, /) -> hexa:
    """Will try to convert any color type to a color of type HEXA.\n
    ----------------------------------------------------------------------------------------------------
    *   `color` – The color to convert (can be in any supported format)."""

    if isinstance(color, (rgba, hsla)):
        return color.to_hexa()
    elif is_valid_rgba(color):
        return _parse_rgba(color).to_hexa()
    elif is_valid_hsla(color):
        return _parse_hsla(color).to_hexa()
    elif is_valid_hexa(color):
        return color if isinstance(color, hexa) else hexa(color)

    raise ValueError(f"Could not convert color {color!r} to HEXA\nMust be a valid RGBA, HSLA, or HEXA color")


@overload
def str_to_rgba(string: str, /, *, only_first: Literal[True]) -> rgba | None: ...
@overload
def str_to_rgba(string: str, /, *, only_first: Literal[False] = False) -> list[rgba] | None: ...
@overload
def str_to_rgba(string: str, /, *, only_first: bool = False) -> rgba | list[rgba] | None: ...


def str_to_rgba(string: str, /, *, only_first: bool = False) -> rgba | list[rgba] | None:
    """Will try to recognize RGBA colors inside a string and output the found ones as RGBA objects.\n
    ----------------------------------------------------------------------------------------------------
    *   `string` – The string to search for RGBA colors.
    *   `only_first` – If true, only the first found color will be returned,
        otherwise a list of all found colors."""

    if only_first:
        if not (match := _rx.search(_regex_module.rgba_str(allow_alpha=True), string)):
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
        if not (matches := _rx.findall(_regex_module.rgba_str(allow_alpha=True), string)):
            return None

        return [
            rgba(
                int(match[0]),
                int(match[1]),
                int(match[2]),
                ((int(match[3]) if "." not in match[3] else float(match[3])) if match[3] else None),
                _validate=False,
            )
            for match in matches
        ]


@overload
def str_to_hsla(string: str, /, *, only_first: Literal[True]) -> hsla | None: ...
@overload
def str_to_hsla(string: str, /, *, only_first: Literal[False] = False) -> list[hsla] | None: ...
@overload
def str_to_hsla(string: str, /, *, only_first: bool = False) -> hsla | list[hsla] | None: ...


def str_to_hsla(string: str, /, *, only_first: bool = False) -> hsla | list[hsla] | None:
    """Will try to recognize HSLA colors inside a string and output the found ones as HSLA objects.\n
    ----------------------------------------------------------------------------------------------------
    *   `string` – The string to search for HSLA colors.
    *   `only_first` – If true, only the first found color will be returned,
        otherwise a list of all found colors."""

    if only_first:
        if not (match := _rx.search(_regex_module.hsla_str(allow_alpha=True), string)):
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
        if not (matches := _rx.findall(_regex_module.hsla_str(allow_alpha=True), string)):
            return None

        return [
            hsla(
                int(match[0]),
                int(match[1]),
                int(match[2]),
                ((int(match[3]) if "." not in match[3] else float(match[3])) if match[3] else None),
                _validate=False,
            )
            for match in matches
        ]


def rgba_to_hex_int(red: int, green: int, blue: int, alpha: float | None = None, /, *, preserve_original: bool = False) -> int:
    """Convert RGBA channels to a HEXA integer (alpha is optional).\n
    ----------------------------------------------------------------------------------------------------
    *   `red`, `green`, `blue` – The red, green, and blue channels in range [0, 255] inclusive.
    *   `alpha` – The alpha channel in range [0.0, 1.0] inclusive or `None` if not set.
    *   `preserve_original` – Whether to preserve the original color exactly (explained below).\n
    ----------------------------------------------------------------------------------------------------
    To preserve leading zeros, the function will add a `1` at the beginning,<br>
    if the HEX integer would start with a `0`.\n
    This could affect the color a little bit, but will make sure, that it won't be interpreted<br>
    as a completely different color, when initializing it as a `hexa()` color or changing it<br>
    back to RGBA using `hex_int_to_rgba()`."""

    if not (0 <= red <= 255 and 0 <= green <= 255 and 0 <= blue <= 255):
        raise ValueError(
            f"The 'red', 'green' and 'blue' parameters must be integers in [0, 255], got {red=!r} {green=!r} {blue=!r}"
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


def hex_int_to_rgba(hex_int: int, /, *, preserve_original: bool = False) -> rgba:
    """Convert a HEX integer to RGBA channels.\n
    ----------------------------------------------------------------------------------------------------
    *   `hex_int` – The HEX integer to convert.
    *   `preserve_original` – Whether to preserve the original color exactly (explained below).\n
    ----------------------------------------------------------------------------------------------------
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

    else:
        hex_str = hex_str.zfill(8)
        return rgba(
            red if (red := int(hex_str[0:2], 16)) != 1 or preserve_original else 0,
            int(hex_str[2:4], 16),
            int(hex_str[4:6], 16),
            int(hex_str[6:8], 16) / 255.0,
            _validate=False,
        )


@overload
def luminance(
    red: int,
    green: int,
    blue: int,
    /,
    *,
    output_type: type[int],
    method: Literal["wcag2", "wcag3", "simple", "bt601"] = "wcag2",
) -> int: ...
@overload
def luminance(
    red: int,
    green: int,
    blue: int,
    /,
    *,
    output_type: type[float],
    method: Literal["wcag2", "wcag3", "simple", "bt601"] = "wcag2",
) -> float: ...
@overload
def luminance(
    red: int,
    green: int,
    blue: int,
    /,
    *,
    output_type: None = None,
    method: Literal["wcag2", "wcag3", "simple", "bt601"] = "wcag2",
) -> int: ...
@overload
def luminance(
    red: int,
    green: int,
    blue: int,
    /,
    *,
    output_type: type[int | float] | None = None,
    method: Literal["wcag2", "wcag3", "simple", "bt601"] = "wcag2",
) -> int | float: ...


def luminance(
    red: int,
    green: int,
    blue: int,
    /,
    *,
    output_type: type[int | float] | None = None,
    method: Literal["wcag2", "wcag3", "simple", "bt601"] = "wcag2",
) -> int | float:
    """Calculates the relative luminance of a color according to various standards.\n
    ----------------------------------------------------------------------------------------------------
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

    if not (0 <= red <= 255 and 0 <= green <= 255 and 0 <= blue <= 255):
        raise ValueError(
            f"The 'red', 'green' and 'blue' parameters must be integers in [0, 255], got {red=!r} {green=!r} {blue=!r}"
        )

    match method:
        case "simple":
            luminance = (red / 255.0 + green / 255.0 + blue / 255.0) / 3
        case "bt601":
            luminance = 0.299 * red / 255.0 + 0.587 * green / 255.0 + 0.114 * blue / 255.0
        case "wcag3":
            luminance = (
                0.2126729 * _SRGB_LINEAR_LUT[red] + 0.7151522 * _SRGB_LINEAR_LUT[green] + 0.0721750 * _SRGB_LINEAR_LUT[blue]
            )
        case _:
            luminance = 0.2126 * _SRGB_LINEAR_LUT[red] + 0.7152 * _SRGB_LINEAR_LUT[green] + 0.0722 * _SRGB_LINEAR_LUT[blue]

    if output_type is int:
        return round(luminance * 100)
    elif output_type is float:
        return luminance
    else:
        return round(luminance * 255)


@overload
def fg_for_on_bg(text_bg_color: rgba, /) -> rgba: ...
@overload
def fg_for_on_bg(text_bg_color: hexa, /) -> hexa: ...
@overload
def fg_for_on_bg(text_bg_color: int, /) -> int: ...
@overload
def fg_for_on_bg(text_bg_color: Rgba | Hexa, /) -> rgba | hexa | int: ...


def fg_for_on_bg(text_bg_color: Rgba | Hexa, /) -> rgba | hexa | int:
    """Returns either black or white text color for optimal contrast on the given background color.\n
    ----------------------------------------------------------------------------------------------------
    *   `text_bg_color` – The background color (can be in RGBA or HEXA format)."""

    was_hexa, was_int = is_valid_hexa(text_bg_color), isinstance(text_bg_color, int)

    text_bg_rgba = to_rgba(text_bg_color)
    brightness = 0.2126 * text_bg_rgba[0] + 0.7152 * text_bg_rgba[1] + 0.0722 * text_bg_rgba[2]

    return (
        (
            (0xFFFFFF if was_int else hexa(_red=255, _green=255, _blue=255))
            if was_hexa
            else rgba(255, 255, 255, _validate=False)
        )
        if brightness < 128
        else ((0x000 if was_int else hexa(_red=0, _green=0, _blue=0)) if was_hexa else rgba(0, 0, 0, _validate=False))
    )


@overload
def adjust_lightness(color: rgba, light_change: float, /) -> rgba: ...
@overload
def adjust_lightness(color: hexa, light_change: float, /) -> hexa: ...
@overload
def adjust_lightness(color: Rgba | Hexa, light_change: float, /) -> rgba | hexa: ...


def adjust_lightness(color: Rgba | Hexa, light_change: float, /) -> rgba | hexa:
    """In- or decrease the lightness of the input color.\n
    ----------------------------------------------------------------------------------------------------
    *   `color` – The color to adjust (can be in RGBA or HEXA format).
    *   `light_change` – The amount to change the lightness by,<br>
        in range `-1.0` (darken by 100%) and `1.0` (lighten by 100%)."""

    if not (-1.0 <= light_change <= 1.0):
        raise ValueError(f"The 'light_change' parameter must be in range [-1.0, 1.0] inclusive, got {light_change!r}")

    was_hexa = is_valid_hexa(color)
    hsla_color = to_hsla(color)

    hue, sat, light, alpha = (
        int(hsla_color[0]),
        int(hsla_color[1]),
        int(hsla_color[2]),
        hsla_color[3] if hsla_color.has_alpha() else None,
    )
    light = int(max(0, min(100, light + light_change * 100)))

    return (
        hsla(hue, sat, light, alpha, _validate=False).to_hexa()
        if was_hexa
        else hsla(hue, sat, light, alpha, _validate=False).to_rgba()
    )


@overload
def adjust_saturation(color: rgba, sat_change: float, /) -> rgba: ...
@overload
def adjust_saturation(color: hexa, sat_change: float, /) -> hexa: ...
@overload
def adjust_saturation(color: Rgba | Hexa, sat_change: float, /) -> rgba | hexa: ...


def adjust_saturation(color: Rgba | Hexa, sat_change: float, /) -> rgba | hexa:
    """In- or decrease the saturation of the input color.\n
    ----------------------------------------------------------------------------------------------------
    *   `color` – The color to adjust (can be in RGBA or HEXA format).
    *   `sat_change` – The amount to change the saturation by,<br>
        in range `-1.0` (saturate by 100%) and `1.0` (desaturate by 100%)."""

    if not (-1.0 <= sat_change <= 1.0):
        raise ValueError(f"The 'sat_change' parameter must be in range [-1.0, 1.0] inclusive, got {sat_change!r}")

    was_hexa = is_valid_hexa(color)
    hsla_color = to_hsla(color)

    hue, sat, light, alpha = (
        int(hsla_color[0]),
        int(hsla_color[1]),
        int(hsla_color[2]),
        hsla_color[3] if hsla_color.has_alpha() else None,
    )
    sat = int(max(0, min(100, sat + sat_change * 100)))

    return (
        hsla(hue, sat, light, alpha, _validate=False).to_hexa()
        if was_hexa
        else hsla(hue, sat, light, alpha, _validate=False).to_rgba()
    )


def _parse_rgba(color: Rgba, /) -> rgba:
    """Internal method to parse a color to an RGBA object."""

    if isinstance(color, rgba):
        return color

    elif isinstance(color, (list, tuple)):
        array_color = cast("list[Any] | tuple[Any, ...]", color)
        if len(array_color) == 4:
            return rgba(int(array_color[0]), int(array_color[1]), int(array_color[2]), float(array_color[3]), _validate=False)
        elif len(array_color) == 3:
            return rgba(int(array_color[0]), int(array_color[1]), int(array_color[2]), None, _validate=False)
        raise ValueError(f"Could not parse RGBA color: {color!r}")

    elif isinstance(color, dict):
        dict_color = cast("dict[str, Any]", color)
        try:
            return rgba(
                int(dict_color["red"]),
                int(dict_color["green"]),
                int(dict_color["blue"]),
                dict_color.get("alpha"),
                _validate=False,
            )
        except (KeyError, ValueError):
            raise ValueError(f"Could not parse RGBA color: {color!r}") from None

    elif isinstance(color, str) and (parsed := str_to_rgba(color, only_first=True)):
        return parsed

    raise ValueError(f"Could not parse RGBA color: {color!r}")


def _parse_hsla(color: Hsla, /) -> hsla:
    """Internal method to parse a color to an HSLA object."""

    if isinstance(color, hsla):
        return color

    elif isinstance(color, (list, tuple)):
        array_color = cast("list[Any] | tuple[Any, ...]", color)
        if len(color) == 4:
            return hsla(int(array_color[0]), int(array_color[1]), int(array_color[2]), float(array_color[3]), _validate=False)
        elif len(color) == 3:
            return hsla(int(array_color[0]), int(array_color[1]), int(array_color[2]), None, _validate=False)
        raise ValueError(f"Could not parse HSLA color: {color!r}")

    elif isinstance(color, dict):
        dict_color = cast("dict[str, Any]", color)
        try:
            return hsla(
                int(dict_color["hue"]),
                int(dict_color["sat"]),
                int(dict_color["light"]),
                dict_color.get("alpha"),
                _validate=False,
            )
        except (KeyError, ValueError):
            raise ValueError(f"Could not parse HSLA color: {color!r}") from None

    elif isinstance(color, str) and (parsed := str_to_hsla(color, only_first=True)):
        return parsed

    raise ValueError(f"Could not parse HSLA color: {color!r}")
