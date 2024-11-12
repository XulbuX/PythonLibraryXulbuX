<div id="top" style="width:45px; height:45px; right:10px; top:10px; position:absolute">
  <a href="#bottom"><abbr title="go to bottom" style="text-decoration:none">
    <div style="
      font-size: 2em;
      font-weight: bold;
      background: #88889845;
      border-radius: 0.2em;
      text-align: center;
      justify-content: center;
    ">🠫</div>
  </abbr></a>
</div>

<br>
<br>


**$\color{#8085FF}\Huge\textsf{XulbuX}$**

-------------------------------------------------------------

**$\color{#8085FF}\textsf{XulbuX}$** is a library which includes a lot of really helpful classes, types and functions.<br>
For the libraries latest changes, see the [change log](https://github.com/XulbuX-dev/Python/blob/main/Libraries/XulbuX/CHANGELOG.md).


# Installation


Open a console and run the command:
```css
pip install XulbuX
```
This should install the latest version of the library, along with some other required libraries.<br>
To upgrade the library (*if there is a new release*) run the following command in your console:
```css
pip install --upgrade XulbuX
```


# Usage


This imports the full library under the alias `xx`, so it"s classes, types and functions are accessible with `xx.Class.class_func()`, `xx.type()` and `xx.function()`:
```python
import XulbuX as xx
```
So you don"t have to write `xx` in front of the library"s types, you can import them directly (*e.g.* `rgba(255,0,0,.5)`):
```python
from XulbuX import rgba, hsla, hexa
```


# Modules


## xx_color

### `rgba()`
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

### `hsla()`
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

### `hexa()`
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
<br>


## xx_cmd

### `Cmd`

This class includes functions for logging and other actions within the console.
<br>

#### `Cmd.get_args()`
----------------------
This function is used to get the command arguments, for if the current file is run via the console as a command.<br>
**Params:**<br>
- <code>find_args: *dict*</code> a dictionary that specifies, which arguments you are looking for and under which alias they should be returned if found. This dictionary could look something like this:
  ```python
  {
      "filepath": ["-f", "--file", "-p", "--path", "-fp", "--filepath", "--file-path"],
      "help":     ["-h", "--help"],
      "debug":    ["-d", "--debug"]
  }
  ```
  For this example, the command line could look like this:
  ```bash
  python main.py -f /path/to/file -d
  ```
  To get one value, you can allow multiple arguments, just like for the filepath in the above example.

**Returns:**<br>
The function will return a dictionary, with the specified aliases and two values per alias:
1. `"exists"` is `True`  if one of the listed arguments is found and `False` otherwise
2. `"value"` is the value of the argument (`None` *if the argument has no value*)

So for the example command line from above, the function would return a dictionary:
```python
{
    "filepath": { "exists": True, "value": "/path/to/file" },
    "help":     { "exists": False, "value": None },
    "debug":    { "exists": True, "value": None }
}
```
<br>

#### `Cmd.user()`
------------------
**Returns:** the username of the user of the current console session
<br>

#### `Cmd.is_admin()`
----------------------
**Returns:** `True` if the current console session is run as administrator and `False` otherwise
<br>

#### `Cmd.pause_exit()`
------------------------
Will print a prompt and then pause and/or exit the program.<br>
**Params:**
- <code>pause: *bool*</code> whether to pause the program at the message or not
- <code>exit: *bool*</code> whether to exit the program after the message was printed (*and the program was unpaused if* `pause` *is true*) or not
- <code>prompt: *str*</code> the prompt to print before pausing and/or exiting the program
- <code>exit_code: *int*</code> the exit code to use if `exit` is true
- <code>reset_ansi: *bool*</code> whether to reset the ANSI codes after the message was printed
<br>

#### `Cmd.cls()`
-----------------
Will clear the console in addition to completely resetting the ANSI formats.
<br>

#### <span id="cmd-log">`Cmd.log()`</span>
-----------------
Will print a nicely formatted log message.<br>
**Params:**
- <code>title: *str*</code> the title of the log message
- <code>prompt: *object*</code> the prompt to print before the log message
- <code>start: *str*</code> the string to print before the log message
- <code>end: *str*</code> the string to print after the log message (*default* `\n`)
- <code>title_bg_color: *hexa*|*rgba*</code> the background color of the title
- <code>default_color: *hexa*|*rgba*</code> the default color of the log message
The log message supports special formatting codes. For more detailed information about formatting codes, see the [`xx_format_codes` documentation](#xx_format_codes).
<br>

#### `Cmd.debug()` `Cmd.info()` `Cmd.done()` `Cmd.warn()` `Cmd.fail()` `Cmd.exit()`
-----------------------------------------------------------------------------------------
These functions are all presets for the [`Cmd.log()`](#cmd-log) function, with the options to pause at the message and exit the program after the message was printed. That means, they have the same params as the `Cmd.log()` function, with the two additional ones.<br>
**Additional Params:**
- <code>pause: *bool*</code> whether to pause the program at the message or not (*different default depending on the log preset*)
- <code>exit: *bool*</code> whether to exit the program after the message was printed (*and the program was unpaused if* `pause` *is true*) or not (*different default depending on the log preset*)
<br>

#### `Cmd.confirm()`
---------------------
This function can be used to ask a yes/no question.<br>
Like in the [`Cmd.log()`](#cmd-log) function it is possible to use special formatting codes inside the `prompt`.<br>
**Params:**
- <code>prompt: *object*</code> the prompt to print before the question
- <code>start: *str*</code> the string to print before the question
- <code>end: *str*</code> the string to print after the question (*default* `\n`)
- <code>default_color: *hexa*|*rgba*</code> the default color of the question
- <code>default_is_yes: *bool*</code> whether the default answer is yes or no (*if the user continues without entering anything or an unrecognized answer*)

**Returns:**
- `True` if the user enters `Y` or `yes` and `False` otherwise
- If the user entered nothing:
  - `True` if `default_is_yes` is true
  - `False` if `default_is_yes` is false
<br>

#### <span id="cmd-restricted_input">`Cmd.restricted_input()`</span>
------------------------------
This function acts like a standard Python `input()` with the advantage, that you can specify:
- what text characters the user is allowed to type and
- the minimum and/or maximum length of the users input
- optional mask character (hide user input, e.g. for passwords)

Like in the [`Cmd.log()`](#cmd-log) function it is possible to use special formatting codes inside the `prompt`.<br>
**Params:**
- <code>prompt: *object*</code> the prompt to print before the input
- <code>allowed_chars: *str*</code> the allowed text characters the user can type (*default is all characters*)
- <code>min_length: *int*</code> the minimum length of the users input (*user can not confirm the input before this length is reached*)
- <code>max_length: *int*</code> the maximum length of the users input (*user cannot keep on writing if this length is reached*)
- <code>mask_char: *str*</code> the mask character to hide the users input

**Returns:** the user's entry as a string
<br>

#### `Cmd.pwd_input()`
This function almost works like the [`Cmd.restricted_input()`](#cmd-restricted_input) function, but it always hides the users input.<br>
It has no additional parameters.<br>


<div id="bottom" style="width:45px; height:45px; right:10px; position:absolute">
  <a href="#top"><abbr title="go to top" style="text-decoration:none">
    <div style="
      font-size: 2em;
      font-weight: bold;
      background: #88889845;
      border-radius: 0.2em;
      text-align: center;
      justify-content: center;
    ">🠩</div>
  </abbr></a>
</div>

<br>
<br>

--------------------------------------------------------------
[View this library on PyPI](https://pypi.org/project/XulbuX/)
