# `rgba()`

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
The `rgba()` color object can be treated like a list/tuple with the items:<br>
`0` = red channel value<br>
`1` = green channel value<br>
`2` = blue channel value<br>
`3` = alpha channel value (*only if the color has an alpha channel*)

If the `rgba()` color object is treated like a string, it will be the color in the format:<br>
`(R, G, B)` if the color has no alpha channel<br>
`(R, G, B, A)` if the color has an alpha channel

<br>

### `.dict()`

This method will get the color components as a dictionary with keys `'r'`, `'g'`, `'b'` and optionally `'a'`.<br>
**Returns:** the color as a dictionary  `{'r': r, 'g': g, 'b': b}` if the color has no alpha channel, else `{'r': r, 'g': g, 'b': b, 'a': a}`

<br>

### `.values()`

This method will get the color components as separate values `r`, `g`, `b` and optionally `a`.<br>
**Returns:** the color as a tuple  `(r, g, b)` if the color has no alpha channel, else `(r, g, b, a)`

### `.to_hsla()`

This method will convert the current color to a HSLA color.<br>
**Returns:** the color as a `hsla()` color

<br>

### `.to_hexa()`

This method will convert the current color to a HEXA color.<br>
**Returns:** the color as a `hexa()` color

<br>

### `.has_alpha()`

This method will check if the current color has an alpha channel.<br>
**Returns:** `True` if the color has an alpha channel, `False` otherwise

<br>

### `.lighten()`

This method will create a lighter version of the current color.<br>
**Param:** <code>amount: *float*</code> the amount to lighten the color by (`0.0`-`1.0`)<br>
**Returns:** the lightened `rgba()` color

<br>

### `.darken()`

This method will create a darker version of the current color.<br>
**Param:** <code>amount: *float*</code> the amount to darken the color by (`0.0`-`1.0`)<br>
**Returns:** the darkened `rgba()` color

<br>

### `.saturate()`

This method will increase the saturation of the current color.<br>
**Param:** <code>amount: *float*</code> the amount to saturate the color by (`0.0`-`1.0`)<br>
**Returns:** the saturated `rgba()` color

<br>

### `.desaturate()`

This method will decrease the saturation of the current color.<br>
**Param:** <code>amount: *float*</code> the amount to desaturate the color by (`0.0`-`1.0`)<br>
**Returns:** the desaturated `rgba()` color

<br>

### `.rotate()`

This method will rotate the hue of the current color.<br>
**Param:** <code>degrees: *int*</code> the amount to rotate the hue by (`0`-`360`)<br>
**Returns:** the rotated `rgba()` color

<br>

### `.invert()`

This method will get the inverse color of the current color.<br>
**Returns:** the inverse `rgba()` color

<br>

### `.grayscale()`

This method will convert the current color to grayscale (*using the luminance formula*).<br>
**Returns:** the grayscale `rgba()` color

<br>

### `.blend()`

This method will blend (*additive*) the current color with another color.<br>
**Params:**
- <code>other: *rgba*</code> the color to blend with<br>
- <code>ratio: *float*</code> the weight of each color when blending (`0.0`-`1.0`)<br>
- <code>additive_alpha: *bool* = False</code> whether to blend the alpha channels additively as well or not

**Returns:** the blended `rgba()` color

**Ratio Example:**<br>
If `ratio` is `0.0` it means 100% of the current color and 0% of the `other` color (2:0 *mixture*)<br>
If `ratio` is `0.5` it means 50% of both colors (1:1 mixture)<br>
If `ratio` is `1.0` it means 0% of the current color and 100% of the `other` color (0:2 *mixture*)

<br>

### `.is_dark()`

This method will confirm if the current color is considered dark (*lightness < 50%*).<br>
**Returns:** `True` if the color is considered dark, `False` otherwise

<br>

### `.is_light()`

This method will confirm if the current color is considered light (*lightness >= 50%*).<br>
**Returns:** `True` if the color is considered light, `False` otherwise

<br>

### `.is_grayscale()`

This method will confirm if the current color is grayscale (`R` *=* `G` *=* `B`).<br>
**Returns:** `True` if the color is grayscale, `False` otherwise

<br>

### `.is_opaque()`

This method will confirm if the current color has no transparency (*alpha =* `1.0` *or no alpha channel*).<br>
**Returns:** `True` if the color is opaque, `False` otherwise

<br>

### `.with_alpha()`

This method will create a new color with different alpha.<br>
**Param:** <code>alpha: *float*</code> the new alpha value (`0.0`-`1.0`)<br>
**Returns:** the `rgba()` color with the new alpha channel value

<br>

### `.complementary()`

This method will get the complementary color of the current color (*180 degrees on the color wheel*).<br>
**Returns:** the complementary `rgba()` color

<br>

# `hsla()`

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
The `hsla()` color object can be treated like a list/tuple with the items:<br>
`0` = hue channel value<br>
`1` = saturation channel value<br>
`2` = lightness channel value<br>
`3` = alpha channel value (*only if the color has an alpha channel*)

If the `hsla()` color object is treated like a string, it will be the color in the format:<br>
`(H, S, L)` if the color has no alpha channel<br>
`(H, S, L, A)` if the color has an alpha channel

<br>

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

# `hexa()`

A HEX color: is a string representing a hexadecimal color code with optional alpha channel.
```python
hexa(
    color: str | int
)
```
The `hexa()` color object can be treated like a list/tuple with the items:<br>
`0` = red channel value<br>
`1` = green channel value<br>
`2` = blue channel value<br>
`3` = alpha channel value (*only if the color has an alpha channel*)

If the `hexa()` color object is treated like a string, it will be the color in the format:<br>
`#RRGGBB` if the color has no alpha channel<br>
`#RRGGBBAA` if the color has an alpha channel


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

<br>

# `Color`

This class includes all sorts of methods for working with colors in general.<br>

<br>

### 