<div id="top" style="width:45px; height:45px; right:10px; top:10px; position:absolute">
  <a href="#release"><abbr title="go to bottom" style="text-decoration:none">
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


# <br><b>Changelog</b><br>


## ... `v1.5.5`
* Added functions to get the width and height of the console (*in characters and lines*):<br>
  <code>Cmd.w() -> *int*</code> how many text characters the console is wide<br>
  <code>Cmd.h() -> *int*</code> how many lines the console is high<br>
  <code>Cmd.wh() -> *tuple[int,int]*</code> a tuple with width and height
* Added the function <code>split_every_chars(*string*, *split_every*) -> *list*[*str*]</code> to `xx_string`
* Added doc-strings to every function in `xx_string`
* Updated the `Cmd.restricted_input()` function:
  - paste text from the clipboard
  - select all text to delete everything at once
  - write and backspace over multiple lines
* Added required non-standard libraries to the project file
* Added more metadata to the project file

## 06.11.2024 `v1.5.4`
* Made the `blend()` method from all the color types modify the *`self`* object as well as returning the result
* Added a new function <code>normalize_spaces(*code*) -> *str*</code> to `Code`
* Added new doc-strings to `xx_code` and `xx_cmd`
* Added a custom `input()` function to `Cmd`, which lets you specify the allowed text characters the user can type, as well as the minimum and maximum length of the input
* Added the function `pwd_input()` to `Cmd`, which works just like the `Cmd.restricted_input()` but masks the input characters with `*`
* Restructured the whole library's imports, so you the custom types won't get displayed as `Any` when hovering over a function
* Fixed bug when trying to get the base directory from a compiled script (*EXE*):<br>
  Would get the path to the temporary extracted directory, which is created when running the EXE file<br>
  Now it gets the actual base directory of the currently running file

## 30.10.2024 `v1.5.3`
* Restructured the values in `_consts_.py`
* Added the default text color to the `_consts_.py` so it's easier to change it (*and used it in the library*)
* Added a bunch of other default colors to the `_consts_.py` (*and used them in the library*)
* Refactored the whole library's code after the [`PEPs`](https://peps.python.org/) and [`The Zen of Python`](https://peps.python.org/pep-0020/#the-zen-of-python) 🫡:
  - changed the indent to 4 spaces
  - no more inline control statements (*except its only a really small statement and body*)
* Added new methods to `Color`:<br>
  <code>rgba_to_hex(*r*, *g*, *b*, *a*) -> *int*</code><br>
  <code>hex_to_rgba(*hex_int*) -> *tuple*</code><br>
  <code>luminance(*r*, *g*, *b*, *precision*, *round_to*) -> *float*|*int*</code>
* Fixed the `grayscale()` method of `rgba()`, `hsla()` and `hexa()`:<br>
  The method would previously just return the color, fully desaturated (*not grayscale*)<br>
  Now this is fixed, and the method uses the luminance formula, to get the actual grayscale value
* All the methods in the `xx_color` module now support HEXA integers (*e.g.* `0x8085FF` *instead of only strings:* `"#8085FF"` `"0x8085FF"`)

## 28.10.2024 `v1.5.2`
* New parameter <code>correct_path:*bool*</code> in `Path.extend()`:
  This makes sure, that typos in the path will only be corrected if this parameter is set to `True`
* Fixed bug in `Path.extend()`, where an empty string was taken as a valid path for the current directory `./`
* Fixed color validation bug:
  `Color.is_valid_rgba()`and `Color.is_valid_hsla()` would not accept an alpha channel of `None`
  `Color.is_valid_rgba()` was still checking for an alpha channel from `0` to `255` instead of `0` to `1`
* Fixed bug for `Color.has_alpha()`:
  Previously, it would return `True` if the alpha channel was `None`. Now in such cases it will return `False`.

## 28.10.2024 `v1.5.1`
* Renamed all library files for a better naming convention
* Now all functions in `xx_color` support both HEX prefixes (`#` *and* `0x`)
* Added the default HEX prefix to `_consts_.py`
* Fixed bug when initializing a `hexa()` object:<br>
  Would throw an error, even if the color was valid

## 27.10.2024 `v1.5.0`
* Split all classes into separate files, so users can download only parts of the library more easily
* Added a `__help__.py` file, which will show some information about the library and how to use it, when it's run as a script or when the `help()` function is called
* Added a lot more metadata to the library:<br>
  `__version__` (*was already added in update [v1.4.2](#update-1-4-2)*)<br>
  `__author__`<br>
  `__email__`<br>
  `__license__`<br>
  `__copyright__`<br>
  `__url__`<br>
  `__description__`<br>
  `__all__`

## <span id="update-1-4-2">27.10.2024 `v1.4.2` `v1.4.3`</span>
* <code>Path.extend(*rel_path*) -> *abs_path*</code> now also extends system variables like `%USERPROFILE%` and `%APPDATA%`
* Removed unnecessary parts when checking for missing required libraries
* You can now get the libraries current version by accessing the attribute `XulbuX.__version__`

## 26.10.2024 `v1.4.1`
* Added methods to each color type:<br>
  <code>is_grayscale() -> *self*</code><br>
  <code>is_opaque() -> *self*</code>
* Added additional error checking to the color types
* Made error messages for the color types clearer
* Updated the <code>blend(*other*, *ratio*)</code> method of all color types to use additive blending except for the alpha-channel
* Fixed problem with method-chaining for all color types

## 25.10.2024 `v1.4.0`
* Huge update to the custom color types:
  - Now all type-methods support chaining
  - Added new methods to each type:<br>
    <code>lighten(*amount*) -> *self*</code><br>
    <code>darken(*amount*) -> *self*</code><br>
    <code>saturate(*amount*) -> *self*</code><br>
    <code>desaturate(*amount*) -> *self*</code><br>
    <code>rotate(*hue*) -> *self*</code><br>
    <code>invert() -> *self*</code><br>
    <code>grayscale() -> *self*</code><br>
    <code>blend(*other*, *ratio*) -> *self*</code><br>
    <code>is_dark() -> *bool*</code><br>
    <code>is_light() -> *bool*</code><br>
    <code>with_alpha(*alpha*) -> *self*</code><br>
    <code>complementary() -> *self*</code>

## 23.10.2024 `v1.3.1`
* Now rounds the alpha channel to maximal 2 decimals, if converting from `hexa()` to `rgba()` or `hsla()` 

## 21.10.2024 `v1.3.0`
* fixed the custom types `rgba()`, `hsla()` and `hexa()`:<br>
  - `rgba()`:<br>
    the method `to_hsla()` works correctly now<br>
    the method `to_hexa()` works correctly now
  - `hsla()`:<br>
    the method `to_rgba()` works correctly now<br>
    the method `to_hexa()` works correctly now
  - `hexa()`:<br>
    the method `to_rgba()` works correctly now<br>
    the method `to_hsla()` works correctly now
* fixed functions from the `Color` class:<br>
  `Color.has_alpha()` works correctly now<br>
  `Color.to_rgba()` works correctly now<br>
  `Color.to_hsla()` works correctly now<br>
  `Color.to_hexa()` works correctly now
* set default value for param `allow_alpha:bool` to `True` for functions:<br>
  `Color.is_valid_rgba()`, `Color.is_valid_hsla()`, `Color.is_valid_hexa()`, `Color.is_valid()`

## 18.10.2024 `v1.2.4` `v1.2.5`
* renamed the class `rgb()` to `rgba()` to communicate, more clearly, that it supports an alpha channel
* renamed the class `hsl()` to `hsla()` to communicate, more clearly, that it supports an alpha channel
* added more info to the `README.md` as well as additional links
* adjusted the structure inside `CHANGELOG.md` for a better overview and readability

## 18.10.2024 `v1.2.3`
* added project links to the Python-project-file
* `CHANGELOG.md` improvements
* `README.md` improvements

## 18.10.2024 `v1.2.1` `v1.2.2`
* fixed bug in function <code>Path.get(*base_dir*=True)</code>:<br>
  Previously, setting `base_dir` to `True` would not return the actual base directory or even cause an error.<br>
  This was now fixed, and setting `base_dir` to `True` will return the actual base directory of the current program (*except if not running from a file*).

## 17.10.2024 `v1.2.0`
* new function in the `Path` class: `Path.remove()`

## 17.10.2024 `v1.1.9`
* corrected the naming of classes to comply with Python naming standards

## 17.10.2024 `v1.1.8`
* added support for all OSes to the OS-dependent functions

## 17.10.2024 `v1.1.6` `v1.1.7`
* fixed the `Cmd.cls()` function:<br>
  There was a bug where, on Windows 10, the ANSI formats weren't cleared.

## 17.10.2024 `v1.1.4` `v1.1.5`
* added link to `CHANGELOG.md` to the `README.md` file

## 17.10.2024 `v1.1.3`
* changed the default value of the param `compactness:int` in the function `Data.print()` to `1` instead of `0`

## 17.10.2024 `v1.1.1` `v1.1.2`
* adjusted the library's description

## 16.10.2024 `v1.1.0`
* made it possible to also auto-reset the color and not only the predefined formats, using the [auto-reset-format](#auto-reset-format) (`[format](Automatically resetting)`)

## 16.10.2024 `v1.0.9`
* added a library description, which gets shown if it's ran directly
* made it possible to escape an <span id="auto-reset-format">auto-reset-format</span> (`[format](Automatically resetting)`) with a slash, so you can still have `()` brackets behind a `[format]`:
  ```python
  FormatCodes.print('[u](Automatically resetting) following text')
  ```
  prints:  <code><u>Automatically resetting</u> following text</code>

  ```python
  FormatCodes.print('[u]/(Automatically resetting) following text')
  ```
  prints:  <code><u>(Automatically resetting) following text</u></code>

## 16.10.2024 `v1.0.7` `v1.0.8`
* added `input()` function to the `FormatCodes` class, so you can make pretty looking input prompts
* added warning for no network connection when trying to [install missing libraries](#improved-lib-importing)

## 15.10.2024 `v1.0.6`
* <span id="improved-lib-importing">improved **$\color{#8085FF}\textsf{XulbuX}$** library importing:</span><br>
  checks for missing required libraries and gives you the option to directly install them, if there are any
* moved constant variables into a separate file
* fixed issue where configuration file wasn't created and loaded correctly

## 15.10.2024 `v1.0.1` `v1.0.2` `v1.0.3` `v1.0.4` `v1.0.5`
* fixed `f-string` issues for Python 3.10:<br>
  **1:** no use of same quotes inside f-strings<br>
  **2:** no backslash escaping in f-strings

## <span id="release">14.10.2024 `v1.0.0`</span>
$\color{#F90}\Huge\textsf{RELEASE!\ 🤩🎉}$<br>
**at release**, the library **$\color{#8085FF}\textsf{XulbuX}$** looks like this:
```python
# GENERAL LIBRARY
import XulbuX as xx
# CUSTOM TYPES
from XulbuX import rgb, hsl, hexa
```
<table>
  <thead>
    <tr>
      <th>Features</th>
      <th>class, type, function, ...</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Custom Types:</td>
      <td>
<code>rgb(<i>int</i>, <i>int</i>, <i>int</i>, <i>float</i>)</code><br>
<code>hsl(<i>int</i>, <i>int</i>, <i>int</i>, <i>float</i>)</code><br>
<code>hexa(<i>str</i>)</code>
      </td>
    </tr><tr>
      <td>Directory Operations</td>
      <td><code>xx.Dir</code></td>
    </tr><tr>
      <td>File Operations</td>
      <td><code>xx.File</code></td>
    </tr><tr>
      <td>JSON File Operations</td>
      <td><code>xx.Json</code></td>
    </tr><tr>
      <td>System Actions</td>
      <td><code>xx.System</code></td>
    </tr><tr>
      <td>Manage Environment Vars</td>
      <td><code>xx.EnvVars</code></td>
    </tr><tr>
      <td>CMD Log And Actions</td>
      <td><code>xx.Cmd</code></td>
    </tr><tr>
      <td>Pretty Printing</td>
      <td><code>xx.FormatCodes</code></td>
    </tr><tr>
      <td>Color Operations</td>
      <td><code>xx.Color</code></td>
    </tr><tr>
      <td>Data Operations</td>
      <td><code>xx.Data</code></td>
    </tr><tr>
      <td>String Operations</td>
      <td><code>xx.String</code></td>
    </tr><tr>
      <td>Code String Operations</td>
      <td><code>xx.Code</code></td>
    </tr><tr>
      <td>Regex Pattern Templates</td>
      <td><code>xx.Regex</code></td>
    </tr>
  </tbody>
</table>


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
