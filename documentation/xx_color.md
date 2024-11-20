# `rgba()`

**An RGBA color:** is a tuple of 3 integers, representing the red (`0`-`255`), green (`0`-`255`), and blue (`0`-`255`).<br>
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
**Returns:** the color as a dictionary:
```python
{
    'r': red,
    'g': green,
    'b': blue,
    'a': alpha,  # ONLY IF THE COLOR HAS AN ALPHA CHANNEL
}
```

<br>

### `.values()`

This method will get the color components as separate values `R`, `G`, `B` and optionally `A`.<br>
**Returns:** the color as a tuple `(R, G, B,)` if the color has no alpha channel, else `(R, G, B, A,)`

<br>

### `.to_hsla()`

This method will convert the current color to a HSLA color.<br>
**Returns:** the converted color as a `hsla()` color object

<br>

### `.to_hexa()`

This method will convert the current color to a HEXA color.<br>
**Returns:** the converted color as a `hexa()` color object

<br>

### `.has_alpha()`

This method will check if the current color has an alpha channel.<br>
**Returns:** `True` if the color has an alpha channel, `False` otherwise

<br>

### `.lighten()`

This method will create a lighter version of the current color.<br>
**Param:** <code>amount: *float*</code> the amount to lighten the color by (`0.0`-`1.0`)<br>
**Returns:** the lightened `rgba()` color object

<br>

### `.darken()`

This method will create a darker version of the current color.<br>
**Param:** <code>amount: *float*</code> the amount to darken the color by (`0.0`-`1.0`)<br>
**Returns:** the darkened `rgba()` color object

<br>

### `.saturate()`

This method will increase the saturation of the current color.<br>
**Param:** <code>amount: *float*</code> the amount to saturate the color by (`0.0`-`1.0`)<br>
**Returns:** the saturated `rgba()` color object

<br>

### `.desaturate()`

This method will decrease the saturation of the current color.<br>
**Param:** <code>amount: *float*</code> the amount to desaturate the color by (`0.0`-`1.0`)<br>
**Returns:** the desaturated `rgba()` color object

<br>

### `.rotate()`

This method will rotate the hue of the current color.<br>
**Param:** <code>degrees: *int*</code> the amount to rotate the hue by (`0`-`360`)<br>
**Returns:** the rotated `rgba()` color object

<br>

### `.invert()`

This method will get the inverse color of the current color.<br>
**Returns:** the inverse `rgba()` color object

<br>

### `.grayscale()`

This method will convert the current color to grayscale (*using the luminance formula*).<br>
**Returns:** the grayscale `rgba()` color object

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
**Returns:** the `rgba()` color object with the new alpha channel value

<br>

### `.complementary()`

This method will get the complementary color of the current color (*180 degrees on the color wheel*).<br>
**Returns:** the complementary `rgba()` color object

<br>
<br>

# `hsla()`

**A HSLA color:** is a tuple of 3 integers, representing hue (`0`-`360`), saturation (`0`-`100`), and lightness (`0`-`100`).<br>
It also includes an optional 4th param, which is a float, that represents the alpha channel (`0.0`-`1.0`).
```python
hsla(
    h: int,
    s: int,
    l: int,
    a: float = None
)
```
A `hsla()` color object can be initialized with the three or four values mentioned above:
`

The `hsla()` color object can be treated like a list/tuple with the items:<br>
`0` = hue channel value<br>
`1` = saturation channel value<br>
`2` = lightness channel value<br>
`3` = alpha channel value (*only if the color has an alpha channel*)

If the `hsla()` color object is treated like a string, it will be the color in the format:<br>
`(H, S, L)` if the color has no alpha channel<br>
`(H, S, L, A)` if the color has an alpha channel

<br>

### `.dict()`

This method will get the color components as a dictionary with keys `'h'`, `'s'`, `'l'` and optionally `'a'`.<br>
**Returns:** the color as a dictionary:
```python
{
    'h': hue,
    's': saturation,
    'l': lightness,
    'a': alpha,  # ONLY IF THE COLOR HAS AN ALPHA CHANNEL
}
```

<br>

### `.values()`

This method will get the color components as separate values `H`, `S`, `L` and optionally `A`.<br>
**Returns:** the color as a tuple `(H, S, L,)` if the color has no alpha channel, else `(H, S, L, A,)`

<br>

### `.to_rgba()`

This method will convert the current color to a RGBA color.<br>
**Returns:** the converted color as a `rgba()` color object

<br>

### `.to_hexa()`

This method will convert the current color to a HEXA color.<br>
**Returns:** the converted color as a `hexa()` color object

<br>

### `.has_alpha()`

This method will check if the current color has an alpha channel.<br>
**Returns:** `True` if the color has an alpha channel, `False` otherwise

<br>

### `.lighten()`

This method will create a lighter version of the current color.<br>
**Param:** <code>amount: *float*</code> the amount to lighten the color by (`0.0`-`1.0`)<br>
**Returns:** the lightened `hsla()` color object

<br>

### `.darken()`

This method will create a darker version of the current color.<br>
**Param:** <code>amount: *float*</code> the amount to darken the color by (`0.0`-`1.0`)<br>
**Returns:** the darkened `hsla()` color object

<br>

### `.saturate()`

This method will increase the saturation of the current color.<br>
**Param:** <code>amount: *float*</code> the amount to saturate the color by (`0.0`-`1.0`)<br>
**Returns:** the saturated `hsla()` color object

<br>

### `.desaturate()`

This method will decrease the saturation of the current color.<br>
**Param:** <code>amount: *float*</code> the amount to desaturate the color by (`0.0`-`1.0`)<br>
**Returns:** the desaturated `hsla()` color object

<br>

### `.rotate()`

This method will rotate the hue of the current color.<br>
**Param:** <code>degrees: *int*</code> the amount to rotate the hue by (`0`-`360`)<br>
**Returns:** the rotated `hsla()` color object

<br>

### `.invert()`

This method will get the inverse color of the current color.<br>
**Returns:** the inverse `hsla()` color object

<br>

### `.grayscale()`

This method will convert the current color to grayscale (*using the luminance formula*).<br>
**Returns:** the grayscale `hsla()` color object

<br>

### `.blend()`

This method will blend (*additive*) the current color with another color.<br>
**Params:**
- <code>other: *rgba*</code> the color to blend with<br>
- <code>ratio: *float*</code> the weight of each color when blending (`0.0`-`1.0`)<br>
- <code>additive_alpha: *bool* = False</code> whether to blend the alpha channels additively as well or not

**Returns:** the blended `hsla()` color

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
**Returns:** the `hsla()` color object with the new alpha channel value

<br>

### `.complementary()`

This method will get the complementary color of the current color (*180 degrees on the color wheel*).<br>
**Returns:** the complementary `hsla()` color object

<br>
<br>

# `hexa()`

**A HEXA color:** is a string representing a hexadecimal color code (`0`-`9`, `A`-`F`) with optional alpha channel.
```python
hexa(
    color: str | int
)
```
A `hexa()` color can be initialized with a string in the formats:<br>
`#RGB` short form with no alpha channel<br>
`#RGBA` short form with alpha channel<br>
`#RRGGBB` normal form with no alpha channel<br>
`#RRGGBBAA` normal form with alpha channel<br>
... or as an integer in the formats:<br>
`0xRRGGBB` with no alpha channel<br>
`0xRRGGBBAA` with alpha channel

The `hexa()` color object can be treated like a list/tuple with the items:<br>
`0` = red channel value<br>
`1` = green channel value<br>
`2` = blue channel value<br>
`3` = alpha channel value (*only if the color has an alpha channel*)

If the `hexa()` color object is treated like a string, it will be the color in the format:<br>
`#RRGGBB` if the color has no alpha channel<br>
`#RRGGBBAA` if the color has an alpha channel

<br>

### `.dict()`

This method will get the color components (*hexadecimal as strings*) as a dictionary with keys `'r'`, `'g'`, `'b'` and optionally `'a'`.<br>
**Returns:** the color as a dictionary:
```python
{
    'r': red_hexa,
    'g': green_hexa,
    'b': blue_hexa,
    'a': alpha,  # ONLY IF THE COLOR HAS AN ALPHA CHANNEL
}
```

<br>

### `.values()`

This method will get the color components as separate values `R`, `G`, `B` and optionally `A`.<br>
**Returns:** the color as a tuple `(R, G, B,)` if the color has no alpha channel, else `(R, G, B, A,)`

<br>

### `.to_rgba()`

This method will convert the current color to a RGBA color.<br>
**Returns:** the converted color as a `rgba()` color object

<br>

### `.to_hsla()`

This method will convert the current color to a HSLA color.<br>
**Returns:** the converted color as a `hsla()` color object

<br>

### `.has_alpha()`

This method will check if the current color has an alpha channel.<br>
**Returns:** `True` if the color has an alpha channel, `False` otherwise

<br>

### `.lighten()`

This method will create a lighter version of the current color.<br>
**Param:** <code>amount: *float*</code> the amount to lighten the color by (`0.0`-`1.0`)<br>
**Returns:** the lightened `hexa()` color object

<br>

### `.darken()`

This method will create a darker version of the current color.<br>
**Param:** <code>amount: *float*</code> the amount to darken the color by (`0.0`-`1.0`)<br>
**Returns:** the darkened `hexa()` color object

<br>

### `.saturate()`

This method will increase the saturation of the current color.<br>
**Param:** <code>amount: *float*</code> the amount to saturate the color by (`0.0`-`1.0`)<br>
**Returns:** the saturated `hexa()` color object

<br>

### `.desaturate()`

This method will decrease the saturation of the current color.<br>
**Param:** <code>amount: *float*</code> the amount to desaturate the color by (`0.0`-`1.0`)<br>
**Returns:** the desaturated `hexa()` color object

<br>

### `.rotate()`

This method will rotate the hue of the current color.<br>
**Param:** <code>degrees: *int*</code> the amount to rotate the hue by (`0`-`360`)<br>
**Returns:** the rotated `hexa()` color object

<br>

### `.invert()`

This method will get the inverse color of the current color.<br>
**Returns:** the inverse `hexa()` color object

<br>

### `.grayscale()`

This method will convert the current color to grayscale (*using the luminance formula*).<br>
**Returns:** the grayscale `hexa()` color object

<br>

### `.blend()`

This method will blend (*additive*) the current color with another color.<br>
**Params:**
- <code>other: *rgba*</code> the color to blend with<br>
- <code>ratio: *float*</code> the weight of each color when blending (`0.0`-`1.0`)<br>
- <code>additive_alpha: *bool* = False</code> whether to blend the alpha channels additively as well or not

**Returns:** the blended `hexa()` color

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
**Returns:** the `hexa()` color object with the new alpha channel value

<br>

### `.complementary()`

This method will get the complementary color of the current color (*180 degrees on the color wheel*).<br>
**Returns:** the complementary `hexa()` color object

<br>
<br>

# `Color`

This class includes all sorts of methods for working with colors in general (*RGBA, HSLA and HEXA*).<br>

<br>

### `Color.is_valid_rgba()`

This method will confirm if the given color is a valid RGBA color.<br>
**Params:**
- <code>color: *str* | *list* | *tuple* | *dict*</code> the color to check
- <code>allow_alpha: *bool* = True</code> whether to allow alpha channel or not

**Returns:** `True` if the color is valid, `False` otherwise

<br>

### `Color.is_valid_hsla()`

This method  will confirm if the given color is a valid HSLA color.<br>
**Params:**
- <code>color: *str* | *list* | *tuple* | *dict*</code> the color to check
- <code>allow_alpha: *bool* = True</code> whether to allow alpha channel or not

**Returns:** `True` if the color is valid, `False` otherwise

<br>

### `Color.is_valid_hexa()`

This method  will confirm if the given color is a valid HEXA color.<br>
**Params:**
- <code>color: *str* | *int*</code> the color to check
- <code>allow_alpha: *bool* = True</code> whether to allow alpha channel or not
- <code>get_prefix: *bool* = False</code> whether to additionally return the HEX prefix if the color is valid

**Returns:**<br>
If `get_prefix` is false: `True` if the color is valid, `False` otherwise<br>
If `get_prefix` is true: `(True, <prefix>)` if the color is valid, `(False, None)` otherwise

<br>

### `Color.has_alpha()`

This method will confirm if the given color has an alpha channel.<br>
**Param:** <code>color: *rgba* | *hsla* | *hexa*</code> the color to check<br>
**Returns:** `True` if the color has an alpha channel, `False` otherwise

<br>

### `Color.to_rgba()`

This method will convert the given color to a `rgba()` color object.<br>
**Param:** <code>color: *hsla* | *hexa*</code> the color to convert<br>
**Returns:** the converted color as a `rgba()` color object

<br>

### `Color.to_hsla()`

This method will convert the given color to a `hsla()` color object.<br>
**Param:** <code>color: *rgba* | *hexa*</code> the color to convert<br>
**Returns:** the converted color as a `hsla()` color object

<br>

### `Color.to_hexa()`

This method will convert the given color to a `hexa()` color object.<br>
**Param:** <code>color: *rgba* | *hsla*</code> the color to convert<br>
**Returns:** the converted color as a `hexa()` color object

<br>

### `Color.str_to_rgba()`

This method will try to find RGBA colors in the given string and convert them into a `rgba()` color object.<br>
**Params:**
- <code>string: *str*</code> the string to search in
- <code>only_first: *bool* = True</code> whether to return all found colors as a list or just one

**Returns:**<br>
If `only_first` is true: the first found color as a `rgba()` color object<br>
If `only_first` is false: all found colors as a list of `rgba()` color objects

<br>

### `Color.rgba_to_hex_int()`

This method will convert the given RGBA color to a HEX integer.<br>
**Params:**
- <code>r: *int*</code> the red channel
- <code>g: *int*</code> the green channel
- <code>b: *int*</code> the blue channel
- <code>a: *float* = None</code> an optional alpha channel
- <code>_preserve_original: *bool* = False</code> whether to preserve the exact original color ([*not recommended setting this to true*](#color-rgbatohexint-preserveoriginal))

**Returns:** the converted color as a HEX integer

<span id="color-rgbatohexint-preserveoriginal">**Preserve Original:**</span><br>
The problem with converting to an integer is that an integer will not preserve leading zeros.

Example:<br>
opaque blue (*no alpha*): `0x0000FF` ⇾ is `255` as number ⇾ back to hexadecimal representation, is `0xFF`<br>
opaque black (*with alpha*): `0x000000FF` ⇾ is `255` as number ⇾ back to hexadecimal representation, is `0xFF`

Since both colors are the same number as integers, it will lead to wrong results later on (*e.g. when converting back to a color*).

To fix this, if the converted HEXA color starts with zeros, the first zero will be changed to `1`, so there's no leading zeros any more. This will change the color slightly, but almost unnoticeably.<br>
If you don't want this behavior, set the `_preserve_original` param to `True`.
