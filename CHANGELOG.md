<div id="top" style="width:45px; height:45px; right:10px; top:10px; position:absolute">
  <a href="#release"><abbr title="go to bottom" style="text-decoration:none">
    <div style="
      font-size: 2em;
      font-weight: bold;
      background: #88889845;
      border-radius: 0.2em;
      text-align: center;
      justify-content: center;
    "><span style="display:none">go to bottom </span>🠫</div>
  </abbr></a>
</div>


# <br><b>Changelog</b><br>

## ... `v1.8.0`
* new options for the param `find_args` from the method `Console.get_args()`:
  previously you could only input a dictionary with items like `"alias_name": ["-f", "--flag"]` that specify an arg's alias and the flags that correspond to it
  new, instead of flags, you can also once use the literal `"before"` and once `"after"`, which corresponds to all non-flagged values before or after all flagged values
* changed the default `default_color` for all `Console` class input methods to `None`
* the method `Console.restricted_input()` now returns an empty string instead of `None` if the user didn't input anything
* fixed several small bugs for `Console.restricted_input()` regarding the ANSI formatting of the input prompt and the input text in the console
* completely rewrote `Console.restricted_input()`, so now it's actually usable, and renamed it to just `Console.input()`
* removed method `Console.pwd_input()`, since you can now simply use `Console.input(mask_char="*")` instead, which does the exact same thing
* removed the CLI command `xx-help`, since it was redundant because there's already the CLI command `xulbux-help`
* removed the `xx_` from all the library modules since it's redundant, and without it the imports look more professional and cleaner
* renamed the previously internal module `_consts_` to `consts` and made it accessible via `from xulbux.base.consts import …`, since you should be able to use library constants without them being "internal"
* removed the wildcard imports from the `__init__.py` file, so now you can only access the main classes directly with `from xulbux import …` and for the rest you have to import the specific module first

## 29.07.2025 `v1.7.3`
* removed the param `title_bg_color` from the `Console.log()` preset methods, since that is part of the preset and doesn't need to be changed by the user
* added a new param to the methods `Console.log_box_filled()` and `Console.log_box_bordered()`:<br>
  <code>indent: *int* = 0</code> the indentation of the box (in chars)
* fixed a bug in `Console.log_box_filled()` where the box background color would sometimes not stop at the box's edge, but would continue to the end of the console line

## 17.06.2025 `v1.7.2`
* the `Console.w`, `Console.h` and `Console.wh` class properties now return a default size if there is no console, instead of throwing an error
* it wasn't actually possible to use default console colors (*e.g.* `"red"`, `"green"`, ...) for the color params in `Console.log()` so that option was completely removed again
* upgraded the speed of `FormatCodes.to_ansi()` by adding the internal ability to skip the `default_color` validation
* fixed type hints for the whole library
* fixed a small bug in `Console.pause_exit()`, where the key, pressed to unpause wasn't suppressed, so it was written into the next console input after unpausing

## 11.06.2025 `v1.7.1`
* fixed an issue with the `Color.is_valid_...()` and `Color.is_valid()` methods, where you were not able to input any color without a type mismatch
* renamed the method `Console.log_box()` to `Console.log_box_filled()`
* added a new method `Console.log_box_bordered()`, which does the same as `Console.log_box_filled()`, but with a border instead of a background color
* the module `xx_format_codes` now treats the `[*]` to-default-color-reset as a normal full-reset, when no `default_color` is set, instead of just counting it as an invalid format code
* fixed bug where entering a color as HEX integer in the color params of the methods `Console.log()`, `Console.log_box_filled()` and `Console.log_box_bordered()` would not work, because it was not properly converted to a format code
* you can now use default console colors (*e.g.* `"red"`, `"green"`, ...) for the color params in `Console.log()`
* the methods `Console.log_box_filled()` and `Console.log_box_bordered()` no longer right-strip spaces, so you can make multiple log boxes the same width, by adding spaces to the end of the text

## 28.05.2025 `v1.7.0`
* fixed a small bug in `Console.log()` where empty linebreaks where removed
* corrected and added missing type hints for the whole library
* fixed possibly unbound variables for the whole library
* updated the client command `xx-help`

## 30.04.2025 `v1.6.9`
* changed the params in `Json.create()`:
  - <code>new_file: *str* = "config"</code> is now the first param and <code>content: *dict*</code> the second one
  - <code>new_file: *str* = "config"</code> is now called <code>json_file: *str*</code> with no default value
* the methods `Json.update()` and `Data.set_value_by_path_id()` now intake a dictionary as `update_values` param, instead of a list of strings
* added a new param to the methods `FormatCodes.remove_ansi()` and `FormatCodes.remove_formatting()`:<br>
  <code>_ignore_linebreaks: *bool* = False</code> whether to include linebreaks in the removal positions or not
* renamed param `correct_path` in `Path.extend()` and param `correct_paths` in `File.extend_or_make_path()` to `use_closest_match`, since this name describes its functionality better
* moved the method `extend_or_make_path()` from the `xx_file` module to the `xx_path` module and renamed it to `extend_or_make()`
* added a new param to method `Color.luminance()` and to the `.grayscale()` method of all color types:
  - <code>method: *str* = "wcag2"</code> the luminance calculation method to use
* added a new param to the method `File.rename_extension()`:
  - <code>full_extension: *bool* = False</code> whether to treat everything behind the first `.` as the extension or everything behind the last `.`
* fixed a small bug in `Console.log_box()` where the leading spaces where removed from the box content
* you can now assign default values to args in `Console.get_args()`

## 18.03.2025 `v1.6.8`
* made it possible to escape formatting codes by putting a slash (`/` *or* `\\`) at the beginning inside the brackets (*e.g.* `[/red]`)
* new methods for `Args` (*the returned object from* `Console.get_args()`):
  - the `len()` function can now be used on `Args` (*the returned object from* `Console.get_args()`)
  - the `Args` object now also has the dict like methods `.keys()`, `.values()` and `.items()`
  - you can also get the args as a dict with the `.dict()` method
  - you can now use the `in` operator on `Args`
* new methods for `ArgResult` (*a single arg-object from inside `Args`):
  - you can now use the `bool()` function on `ArgResult` to directly see if the arg exists
* the methods `FormatCodes.remove_ansi()` and `FormatCodes.remove_formatting()` now have a second param <code>get_removals: *bool* = False</code><br>
  if this param is `True` additionally to the cleaned string, a list of tuples will be returned, where tuple contains the position of the removed formatting/ansi code and the removed code
* fixed a bug in the line wrapping in all logging methods from the `xx_console` module
* added a new param to the method `Console.get_args()`:<br>
  <code>allow_spaces: *bool* = False</code> whether to take spaces as separator of arg values or as part of an arg value

## 26.02.2025 `v1.6.7`
* restructured the object returned from `Console.get_args()`:<br>
  before, you accessed an arg's result with `args["<arg_alias>"]["value"]` and `args["<arg_alias>"]["exists"]`<br>
  now, you can directly access the result with `args.<arg_alias>.value` and `args.<arg_alias>.exists`
* made the staticmethod `System.is_elevated()` into a class property, which now can be accessed as `System.is_elevated`
* made the method <code>Path.get(*cwd*=True)</code> or <code>Path.get(*base_dir*=True)</code> into two class properties, which now can be accessed as `Path.cwd` and `Path.script_dir`
* the method `File.create()` now throws a custom `SameContentFileExistsError` exception if a file with the same name and content already exists
* added a bunch more docstrings to class properties and library constants

## 17.02.2025 `v1.6.6`
* added a new method `Console.multiline_input()`
* added two new params to the method `Console.log_box()`:<br>
  <code>w_padding: *int* = 2</code> the horizontal padding (*in chars*) to the box content<br>
  <code>w_full: *bool* = False</code> whether to make the box be the full console width or not
* fixed a small bug in `Data.print()` where two params passed to `Data.to_str()` where swapped, which caused an error
* the method `Data.print()` now per default syntax highlights the console output:<br>
  the syntax highlighting colors and styles can be customized via the new param <code>syntax_highlighting: dict[*str*, *str*] = {...}</code>
* added two new methods `Data.serialize_bytes()` and `Data.deserialize_bytes()`
* made the method `String.to_type()` be able to also interpret and convert large complex structures
* added the new parameter <code>strip_spaces: *bool* = True</code> to the method `Regex.brackets()` which makes it possible to not ignore spaces around the content inside the brackets
* restructured the `_consts_` library constants to use `@dataclass` classes (*and simpler structured classes*) as much as possible
* adjusted the `Console.log_box()` method, so the box background can't be reset to nothing anymore
* renamed the `DEFAULT` class from the `_consts_` to `COLOR`, whose colors are now directly accessible as variables (*e.g.* `COLOR.red`) and not through dictionary keys
* changed the methods `Console.w()`, `Console.h()`, `Console.wh()` and `Console.user()` to modern class properties instead:<br>
  `Console.w` current console columns (*in text characters*)<br>
  `Console.h` current console lines<br>
  `Console.wh` a tuple with the console size as (columns, lines)<br>
  `Console.usr` the current username
* added a new param to `Console.log()` (*and therefore also to every* `Console.log()` *preset*):<br>
  <code>format_linebreaks: *bool* = True</code> indents the text after every linebreak to the level of the previous text, whe set to `True`

## 29.01.2025 `v1.6.5`
* now the method `FormatCodes.to_ansi()` automatically converts the param `string` to a *`str`* if it isn't one already
* added a new method `FormatCodes.remove_codes()`
* added a new method `FormatCodes.remove_ansi()`
* added a new method `Console.log_box()`
* changed the default values of two params in the `Console.log()` method and every log preset:<br>
  <code>start: *str* = "\n"</code> has been changed to <code>start: *str* = ""</code><br>
  <code>end: *str* = "\n\n"</code> has been changed to <code>end: *str* = "\n"</code>
* added the params <code>start: *str* = ""</code>, <code>end: *str* = "\n"</code> and <code>default_color: *rgba* | *hexa* = DEFAULT.color["cyan"]</code> to `Console.restricted_input()` and `Console.pwd_input()`

## 22.01.2025 `v1.6.4`
* fixed a heavy bug, where the library could not be imported after the last update, because of a bug in `xx_format_codes`

## 22.01.2025 `v1.6.3`
* fixed a small bug in `xx_format_codes`:<br>
  inside print-strings, if there was a `'` or `"` inside an auto-reset-formatting (*e.g.* `[u](there's a quote)`), that caused it to not be recognized as valid, and therefore not be automatically reset
  now this is fixed and auto-reset-formatting works as expected
* added a new param <code>ignore_in_strings: *bool* = True</code> to `Regex.brackets()`:<br>
  if this param is true and a bracket is inside a string (e.g. `'...'` or `"..."`), it will not be counted as the matching closing bracket
* removed `lru_cache` from the `xx_format_codes` module's internal methods, since it was unnecessary
* adjusted `FormatCodes.__config_console()` so it can only be called once per process

## 20.01.2025 `v1.6.2`
* moved the method `is_admin()` from `xx_console` to `xx_system`
* added a new method `elevate()` to `xx_system`, which is used to request elevated privileges
* fixed a bug in `rgba()`, `hsla()` and `hexa()`:<br>
  previously, when initializing a color with the alpha channel set to `0.0` (*100% transparent*), it was saved correctly, but when converted to a different color type or when returned, the alpha channel got ignored, just like if it was `None` or `1.0` (*opaque*)
  now when initializing a color with the alpha channel set to `0.0`, this doesn't happen and when converted or returned, the alpha channel is still `0.0`
* huge speed and efficiency improvements in `xx_color`, due to newly added option to initialize a color without validation, which saves time when initializing colors, when we know, that the values are valid
* method `hex_int_to_rgba()` from `xx_color` now returns an `rgba()` object instead of the separate values `r`, `g`, `b` and `a`
* added a new param <code>reset_ansi: *bool* = False</code> to `FormatCodes.input()`:<br>
  if this param is true, all formatting will be reset after the user confirmed the input and the program continues

## 15.01.2025 `v1.6.1`
* changed the order the params in `File.create()`:<br>
  until now the param <code>content: *str* = ""</code> was the first param and <code>file: *str* = ""</code>
  new the param <code>file: *str* = ""</code> is the first param and <code>content: *str* = ""</code> is the second
* changed the params in `File.make_path()`:<br>
  previously there were the params <code>filename: *str*</code> and <code>filetype: *str* = ""</code> where `filename` didn't have to have the file extension included, as long as the `filetype` was set
  now these params have become one param <code>file: *str*</code> which is the file with file extension
* `File.make_path()` was renamed to a more descriptive name `File.extend_or_make_path()`
* adjusted the usages of `File.create()` and `File.make_path()` inside `xx_json` accordingly
* removed all line breaks and other Markdown formatting from docstrings, since not all IDEs support them

## 07.01.2025 `v1.6.0`
* fixed a small bug in `to_camel_case()` in the `xx_string` module:<br>
  previously, it would return only the first part of the decomposed string
  now it correctly returns all decomposed string parts, joined in CamelCase

## 21.12.2024 `v1.5.9`
* fixed bugs in method `to_ansi()` in module `xx_format_codes`:<br>
  1. the method always returned an empty string, because the color validation was broken, and it would identify all colors as invalid<br>
    now the validation `Color.is_valid_rgba()` and `Color.is_valid_hexa()` are fixed and now, if a color is identified as invalid, the method returns the original string instead of an empty string
  2. previously the method `to_ansi()` couldn't handle formats inside `[]` because everything inside the brackets was recognized as an invalid format
    now you are able to use formats inside `[]` (*e.g.* `"[[red](Red text [b](inside) square brackets!)]"`)
* adjusted the format codes test accordingly to the bug fixes
* introduced a new test for the `xx_format_codes` module
* a lot of updates in the Wiki and README
* fixed a small bug in the help client-command:<br>
  added back the default text color

## 21.11.2024 `v1.5.8`
* renamed the library from `XulbuX` to `xulbux` for better naming conventions
* added method `String.is_empty()` to check if the string is empty
* added method `String.escape()` to escape special characters in a string
* introduced a new test for `xx_data` (*all methods*)
* added doc-strings to all the methods in `xx_data`
* made all the methods from `xx_data` work wih all the types of data structures (*`list`, `tuple`, `set`, `frozenset`, `dict`*)
* renamed the module `xx_cmd`, and it's class `Cmd` to `xx_console` and `Console`
* renamed the module `xx_env_vars`, and it's class `EnvVars` to `xx_env_path` and `EnvPath`
* added method `EnvPath.remove_path()`
* introduced a new test for `xx_env_vars` (*all methods*)
* Added a `hexa_str()` preset to the `xx_regex` module
* introduced a new test for the methods from the `Color` class in `xx_color`

## 15.11.2024 `v1.5.7`
* change the testing modules to be able to run together with the library `pytest`
* added formatting checks, using `black`, `isort` and `flake8`
* added the script (*command*) `xx-help` or `xulbux-help`
* moved the `help()` function to the file `_cli_.py`, because that's where all the scripts are located (*It also was renamed to* `help_command()`)
* structured `Cmd.restricted_input()` a bit nicer, so it appears less complex
* corrected code after `Lint with flake8` formatting suggestions
* moved the method `normalize_spaces()` to `xx_string`
* added additional tests for the custom color types
* updated the whole `xx_format_codes` module for more efficiency and speed

## 11.11.2024 `v1.5.6`
* moved the whole library to its own repository: [PythonLibraryXulbuX](https://github.com/XulbuX/PythonLibraryXulbuX)
* updated all connections and links

## 11.11.2024 `v1.5.5`
* added methods to get the width and height of the console (*in characters and lines*):<br>
  <code>Cmd.w() -> *int*</code> how many text characters the console is wide<br>
  <code>Cmd.h() -> *int*</code> how many lines the console is high<br>
  <code>Cmd.wh() -> *tuple[int,int]*</code> a tuple with width and height
* added the method <code>split_count(*string*, *count*) -> list[*str*]</code> to `xx_string`
* added doc-strings to every method in `xx_string`
* updated the `Cmd.restricted_input()` method:
  - paste text from the clipboard
  - select all text to delete everything at once
  - write and backspace over multiple lines
  - not the prompt supports custom format codes
* added required non-standard libraries to the project file
* added more metadata to the project file

## 06.11.2024 `v1.5.4`
* made the `blend()` method from all the color types modify the *`self`* object as well as returning the result
* added a new method <code>normalize_spaces(*code*) -> *str*</code> to `Code`
* added new doc-strings to `xx_code` and `xx_cmd`
* added a custom `input()` method to `Cmd`, which lets you specify the allowed text characters the user can type, as well as the minimum and maximum length of the input
* added the method `pwd_input()` to `Cmd`, which works just like the `Cmd.restricted_input()` but masks the input characters with `*`
* restructured the whole library's imports, so you the custom types won't get displayed as `Any` when hovering over a method/function
* fixed bug when trying to get the base directory from a compiled script (*EXE*):<br>
  would get the path to the temporary extracted directory, which is created when running the EXE file<br>
  now it gets the actual base directory of the currently running file

## 30.10.2024 `v1.5.3`
* restructured the values in `_consts_.py`
* added the default text color to the `_consts_.py` so it's easier to change it (*and used it in the library*)
* added a bunch of other default colors to the `_consts_.py` (*and used them in the library*)
* refactored the whole library's code after the [`PEPs`](https://peps.python.org/) and [`The Zen of Python`](https://peps.python.org/pep-0020/#the-zen-of-python) 🫡:
  - changed the indent to 4 spaces
  - no more inline control statements (*except it's only a tiny statement and body*)
* added new methods to `Color`:<br>
  <code>rgba_to_hex(*r*, *g*, *b*, *a*) -> *int*</code><br>
  <code>hex_to_rgba(*hex_int*) -> *tuple*</code><br>
  <code>luminance(*r*, *g*, *b*, *precision*, *round_to*) -> *float*|*int*</code>
* fixed the `grayscale()` method of `rgba()`, `hsla()` and `hexa()`:<br>
  the method would previously just return the color, fully desaturated (*not grayscale*)<br>
  now this is fixed, and the method uses the luminance formula, to get the actual grayscale value
* all the methods in the `xx_color` module now support HEXA integers (*e.g.* `0x8085FF` *instead of only strings:* `"#8085FF"` `"0x8085FF"`)

## 28.10.2024 `v1.5.2`
* new parameter <code>correct_path:*bool*</code> in `Path.extend()`:
  this makes sure, that typos in the path will only be corrected if this parameter is set to `True`
* fFixed bug in `Path.extend()`, where an empty string was taken as a valid path for the current directory `./`
* fixed color validation bug:<br>
  `Color.is_valid_rgba()`and `Color.is_valid_hsla()` would not accept an alpha channel of `None`<br>
  `Color.is_valid_rgba()` was still checking for an alpha channel from `0` to `255` instead of `0` to `1`
* fixed bug for `Color.has_alpha()`:<br>
  previously, it would return `True` if the alpha channel was `None`<br>
  now in such cases it will return `False`

## 28.10.2024 `v1.5.1`
* renamed all library files for a better naming convention
* now all methods in `xx_color` support both HEX prefixes (`#` *and* `0x`)
* added the default HEX prefix to `_consts_.py`
* fixed bug when initializing a `hexa()` object:<br>
  would throw an error, even if the color was valid

## 27.10.2024 `v1.5.0`
* split all classes into separate files, so users can download only parts of the library more easily
* added a `__help__.py` file, which will show some information about the library and how to use it, when it's run as a script or when the `help()` function is called
* added a lot more metadata to the library:<br>
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
* removed unnecessary parts when checking for missing required libraries
* you can now get the libraries current version by accessing the attribute `XulbuX.__version__`

## 26.10.2024 `v1.4.1`
* added methods to each color type:<br>
  <code>is_grayscale() -> *self*</code><br>
  <code>is_opaque() -> *self*</code>
* added additional error checking to the color types
* made error messages for the color types clearer
* updated the <code>blend(*other*, *ratio*)</code> method of all color types to use additive blending except for the alpha-channel
* fixed problem with method-chaining for all color types

## 25.10.2024 `v1.4.0`
* huge update to the custom color types:
  - now all type-methods support chaining
  - added new methods to each type:<br>
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
* now rounds the alpha channel to maximal 2 decimals, if converting from `hexa()` to `rgba()` or `hsla()` 

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
* fixed methods from the `Color` class:<br>
  `Color.has_alpha()` works correctly now<br>
  `Color.to_rgba()` works correctly now<br>
  `Color.to_hsla()` works correctly now<br>
  `Color.to_hexa()` works correctly now
* set default value for param `allow_alpha:bool` to `True` for methods:<br>
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
* fixed bug in method <code>Path.get(*base_dir*=True)</code>:<br>
  Previously, setting `base_dir` to `True` would not return the actual base directory or even cause an error.<br>
  This was now fixed, and setting `base_dir` to `True` will return the actual base directory of the current program (*except if not running from a file*).

## 17.10.2024 `v1.2.0`
* new method in the `Path` class: `Path.remove()`

## 17.10.2024 `v1.1.9`
* corrected the naming of classes to comply with Python naming standards

## 17.10.2024 `v1.1.8`
* added support for all OSes to the OS-dependent methods

## 17.10.2024 `v1.1.6` `v1.1.7`
* fixed the `Cmd.cls()` method:<br>
  There was a bug where, on Windows 10, the ANSI formats weren't cleared.

## 17.10.2024 `v1.1.4` `v1.1.5`
* added link to `CHANGELOG.md` to the `README.md` file

## 17.10.2024 `v1.1.3`
* changed the default value of the param `compactness:int` in the method `Data.print()` to `1` instead of `0`

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
  prints: <code><u>Automatically resetting</u> following text</code>

  ```python
  FormatCodes.print('[u]/(Automatically resetting) following text')
  ```
  prints: <code><u>(Automatically resetting) following text</u></code>

## 16.10.2024 `v1.0.7` `v1.0.8`
* added `input()` method to the `FormatCodes` class, so you can make pretty looking input prompts
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
    "><span style="display:none">go to top </span>🠩</div>
  </abbr></a>
</div>
