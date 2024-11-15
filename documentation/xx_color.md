# xx_color

<br>

## `rgba()`

An RGB/RGBA color: is a tuple of 3 integers, representing the red (`0`-`255`), green (`0`-`255`), and blue (`0`-`255`).<br>
It also includes an optional 4th param, which is a float, that represents the alpha channel (`0.0`-`1.0`):
```python
rgba(
    r: int,
    g: int,
    b: int,
    a: float = None
)
```
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
- `complementary()` to get the complementary color

<br>

## `hsla()`

A HSL/HSLA color: is a tuple of 3 integers, representing hue (`0`-`360`), saturation (`0`-`100`), and lightness (`0`-`100`).<br>
It also includes an optional 4th param, which is a float, that represents the alpha channel (`0.0`-`1.0`).\n
```python
hsla(
    h: int,
    s: int,
    l: int,
    a: float = None
)
```
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
- `complementary()` to get the complementary color

<br>

## `hexa()`

A HEX color: is a string representing a hexadecimal color code with optional alpha channel.
```python
hexa(
    color: str | int
)
```
Supports formats: RGB, RGBA, RRGGBB, RRGGBBAA (*with or without prefix*)<br>
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
- `complementary()` to get the complementary color
