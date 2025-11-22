<div id="top" style="width:45px; height:45px; right:10px; top:10px; position:absolute">
  <a href="#release" title="scroll to bottom">
    <div style="
      font-size: 2em;
      font-weight: bold;
      background: #88889845;
      border-radius: 0.2em;
      text-align: center;
      justify-content: center;
    "><span style="display:none">scroll to bottom </span>🠫</div>
  </a>
</div>


# <br><b>Changelog</b><br>


<span id="v1-9-1" />

## 21.11.2025 `v1.9.1`
* Unified the module and class docstring styles throughout the whole library.
* Moved the Protocol `ProgressUpdater` from the `console` module to the `types` module.


<span id="v1-9-0" />

## 21.11.2025 `v1.9.0` Big Update 🚀
* Standardized the docstrings for all public methods in the whole library to use the same style and structure.
* Replaced left over single quotes with double quotes for consistency.
* Fixed a bug inside `Data.remove_empty_items()`, where types other than strings where passed to `String.is_empty()`, which caused an exception.
* Refactored/reformatted the code of the whole library, to introduce more clear code structure with more room to breathe.
* Made the really complex regex patterns in the `Regex` class all multi-line for better readability.
* Added a new internal method `Regex._clean()`, which is used to clean up the regex patterns, defined as multi-line strings.
* Moved custom exception classes to their own file `base/exceptions.py`, so the user can easily import them all from the same place.
* Moved custom types to their own file `base/types.py`, so the user can easily import them all from the same place.
* Removed unnecessary duplicate code in several methods throughout the library.
* Introduced some minor performance improvements in a few methods, that might be called very often in a short time span.
* Added a small description to the docstrings of all modules and their main classes.

**BREAKING CHANGES:**
* The `find_args` param from the method `Console.get_args()` now only accepts sets for the flags instead of lists/tuples, since the order of flags doesn't matter and sets have better performance for lookups.
* Added missing type checking to all public methods in the whole library, so now they will all throw errors if the params aren't of the expected type.
* Removed the second definitions of constants in with lowercase names in the `ANSI` class inside the `consts` module, so now you can only access them with their uppercase names (*e.g.* `ANSI.CHAR` instead of `ANSI.char`).


<span id="v1-8-5" />

## 14.11.2025 `v1.8.5`

* Made the help command `xulbux-help` new primarily use console default colors so it fits the user's console theme.
* Changed the default `box_bg_color` in `Console.log_box_filled()` from `green` to `br:green`.
* Fixed a bug in all methods of `FormatCodes`, where as soon as you used more than a single modifier format code (*e.g.* `[ll]` *or* `[++]`), it was treated as invalid and ignored.
* Added a new method `FormatCodes.escape()` which will escape all valid formatting codes in a string.
* Again refactored the whole `CHANGELOG.md` to use actual sentences and add a `BREAKING CHANGES` section to more clearly highlight breaking changes.

**BREAKING CHANGES:**
* Removed the `*c` and `*color` formatting codes, since the user should just use the code `default` to achieve the exact same instead.
* Renamed the method `FormatCodes.remove_formatting()` to `FormatCodes.remove()`.


<span id="v1-8-4" />

## 11.11.2025 `v1.8.4` 𝓢𝓲𝓷𝓰𝓵𝓮𝓼 𝓓𝓪𝔂 🥇😉

* Adjusted `Regex.hsla_str()` to not include optional degree (`°`) and percent (`%`) symbols in the captured groups.
* Fixed that `Regex.hexa_str()` couldn't match HEXA colors anywhere inside a string, but only if the whole string was just the HEXA color.
* Added `_ArgResultRegular` and `_ArgResultPositional` TypedDict classes for better type hints in `Args.dict()` and `Args.items()` methods.

**BREAKING CHANGES:**
* The method `Console.get_args()` no longer tries to convert found arg values to their respective types, since that caused too many unwanted, wrong type conversions.
* `ArgResult` now has separate properties for different argument types to improve type safety and eliminate the need for type casting when accessing argument values:
  - <code>value: Optional[*str*]</code> for regular flagged arguments
  - <code>values: list[*str*]</code> for positional `"before"`/`"after"` arguments


<span id="v1-8-3" />

## 08.10.2025 `v1.8.3`

* Adjusted the look of the prompts and inputs of the `System.check_libs()` method.
* Added a new param to `System.check_libs()`:<br>
  <code>missing_libs_msgs: tuple[str, str] = (…)</code> two messages: The first one is displayed when missing libraries are found. The second one is the confirmation message before installing missing libraries.
* Adjusted error messages throughout the whole library to all be structured about the same.
* Fixed a small bug in `FormatCodes.__config_console()`, where it would cause an exception, because it tried to configure Windows specific console settings on non-Windows systems.
* The `Console.get_args()` method will now treat everything as values (*even if it starts with* `-` *or* `--`) unless it's specified in the `find_args` param.
* Added two new params to all the `Console.log()` presets:<br>
  - <code>exit_code: *int* = 0</code> the exit code to use if `exit` is true
  - <code>reset_ansi: *bool* = True</code> whether to reset all ANSI formatting after pausing/exiting or not
* Made the type hints and value checks for `Console.get_args()` more strict.
* You can now insert horizontal rules inside a `Console.log_box_bordered()` by putting `{hr}` in the text.
* Made it possible to also update the title within a `ProgressBar.progress_context()` using the returned callable with the new kwarg `label`.

**BREAKING CHANGES:**
* Reordered the params of `Console.pause_exit()` to be more logical.


<span id="v1-8-2" />

## 11.09.2025 `v1.8.2`

* The client command `xulbux-help` now tells you that there's a newer version of the library available, if you're not using the latest version.
* Added two new params to `Console.input()`:
  - <code>default_val: Optional[T] = None</code> the default value to return if the input is empty
  - <code>output_type: type[T] = *str*</code> the type (*class*) to convert the input to before returning it
* Added a new class to `ProgressBar` to the `console` module.
* Made small performance improvement in `FormatCodes.to_ansi()`.
* Added missing docstrings to several public class variables.
* Added the missing tests for methods in the `console` module.
* Added test for the last two modules that didn't have test until now: `regex` and `system`.

**BREAKING CHANGES:**
* Spaces between a format code and the auto-reset-brackets are no longer allowed, so `[red]␣(text)` will not be automatically reset and output as `␣(text)`.


<span id="v1-8-1" />

## 20.08.2025 `v1.8.1`

* **<u>HOTFIX:</u> Fixed a critical bug which caused the package to not install properly and make the whole library not work.**
* Fixed several small bugs regarding the tabs and text wrapping inside `Console.log()`.
* Added two new params to `Console.log()`:
  - <code>title_px: *int* = 1</code> the horizontal padding (*in chars*) to the title (*if* `title_bg_color` *is set*)
  - <code>title_mx: *int* = 2</code> the horizontal margin (*in chars*) to the title

**BREAKING CHANGES:**
* Renamed the param `_console_tabsize` form the method `Console.log()` to `tab_size`, and it will now just set the size for the log directly instead of specifying, what the console's tab size is.


<span id="v1-8-0" />

## 28.08.2025 `v1.8.0` **⚠️This release is broken!**

* New options for the param `find_args` from the method `Console.get_args()`:<br>
  Previously you could only input a dictionary with items like `"alias_name": ["-f", "--flag"]` that specify an arg's alias and the flags that correspond to it.<br>
  New, instead of flags, you can also once use the literal `"before"` and once `"after"`, which corresponds to all non-flagged values before or after all flagged values.
* Changed the default `default_color` for all `Console` class input methods to `None`.
* Now `prompt` from `Console.pause_exit()` also supports custom formatting codes and the method new pauses per default (*without exiting*).

**BREAKING CHANGES:**
* The method `Console.restricted_input()` now returns an empty string instead of `None` if the user didn't input anything.
* Completely rewrote `Console.restricted_input()`, so now it's actually usable, and renamed it to just `Console.input()`.
* Removed method `Console.pwd_input()`, since you can now simply use `Console.input(mask_char="*")` instead, which does the exact same thing.
* Removed the CLI command `xx-help`, since it was redundant because there's already the CLI command `xulbux-help`.
* Renamed the previously internal module `_consts_` to `consts` and made it accessible via `from xulbux.base.consts import …`, since you should be able to use library constants without them being «internal».
* Removed the `xx_` from all the library modules since it's redundant, and without it the imports look more professional and cleaner.
* The constants form inside the `consts` module are now all uppercase (*except the class methods*), to make clear that they're constants.
* Removed the wildcard imports from the `__init__.py` file, so now you can only access the main classes directly with `from xulbux import …` and for the rest you have to import the specific module first.


<span id="v1-7-3" />

## 29.07.2025 `v1.7.3`

* Added a new param to the methods `Console.log_box_filled()` and `Console.log_box_bordered()`:<br>
  <code>indent: *int* = 0</code> the indentation of the box (in chars)
* Fixed a bug in `Console.log_box_filled()` where the box background color would sometimes not stop at the box's edge, but would continue to the end of the console line.

**BREAKING CHANGES:**
* Removed the param `title_bg_color` from the `Console.log()` preset methods, since that is part of the preset and doesn't need to be changed by the user.


<span id="v1-7-2" />

## 17.06.2025 `v1.7.2`

* The `Console.w`, `Console.h` and `Console.wh` class properties now return a default size if there is no console, instead of throwing an error.
* It wasn't actually possible to use default console-colors (*e.g.* `"red"`, `"green"`, ...) for the color params in `Console.log()` so that option was completely removed again.
* Upgraded the speed of `FormatCodes.to_ansi()` by adding the internal ability to skip the `default_color` validation.
* Fixed type hints for the whole library.
* Fixed a small bug in `Console.pause_exit()`, where the key, pressed to unpause wasn't suppressed, so it was written into the next console input after unpausing.


<span id="v1-7-1" />

## 11.06.2025 `v1.7.1`

* Fixed an issue with the `Color.is_valid_…()` and `Color.is_valid()` methods, where you were not able to input any color without a type mismatch.
* Added a new method `Console.log_box_bordered()`, which does the same as `Console.log_box_filled()`, but with a border instead of a background color.
* The module `xx_format_codes` now treats the `[*]` to-default-color-reset as a normal full-reset, when no `default_color` is set, instead of just counting it as an invalid format code.
* Fixed bug where entering a color as HEX integer in the color params of the methods `Console.log()`, `Console.log_box_filled()` and `Console.log_box_bordered()` would not work, because it was not properly converted to a format code.
* You can now use default console colors (*e.g.* `"red"`, `"green"`, ...) for the color params in `Console.log()`.
* The methods `Console.log_box_filled()` and `Console.log_box_bordered()` no longer right-strip spaces, so you can make multiple log boxes the same width, by adding spaces to the end of the text.

**BREAKING CHANGES:**
* Renamed the method `Console.log_box()` to `Console.log_box_filled()`.


<span id="v1-7-0" />

## 28.05.2025 `v1.7.0`

* Fixed a small bug in `Console.log()` where empty linebreaks where removed.
* Corrected and added missing type hints for the whole library.
* Fixed possibly unbound variables for the whole library.
* Updated the client command `xulbux-help`.


<span id="v1-6-9" />

## 30.04.2025 `v1.6.9`

* Added a new param to the methods `FormatCodes.remove_ansi()` and `FormatCodes.remove_formatting()`:<br>
  <code>_ignore_linebreaks: *bool* = False</code> whether to include linebreaks in the removal positions or not
* Added a new param to method `Color.luminance()` and to the `.grayscale()` method of all color types:
  <code>method: *str* = "wcag2"</code> the luminance calculation method to use
* Added a new param to the method `File.rename_extension()`:
  <code>full_extension: *bool* = False</code> whether to treat everything behind the first `.` as the extension or everything behind the last `.`
* Fixed a small bug in `Console.log_box()` where the leading spaces where removed from the box content.
* You can now assign default values to args in `Console.get_args()`.

**BREAKING CHANGES:**
* Changed the params in `Json.create()`:
  - <code>new_file: *str* = "config"</code> is now the first param and <code>content: *dict*</code> the second one
  - <code>new_file: *str* = "config"</code> is now called <code>json_file: *str*</code> with no default value
* The methods `Json.update()` and `Data.set_value_by_path_id()` now intake a dictionary as `update_values` param, instead of a list of strings.
* Renamed param `correct_path` in `Path.extend()` and param `correct_paths` in `File.extend_or_make_path()` to `use_closest_match`, since this name describes its functionality better.
* Moved the method `extend_or_make_path()` from the `xx_file` module to the `xx_path` module and renamed it to `extend_or_make()`.


<span id="v1-6-8" />

## 18.03.2025 `v1.6.8`

* Made it possible to escape formatting codes by putting a slash (`/` *or* `\\`) at the beginning inside the brackets (*e.g.* `[/red]`).
* New methods for `Args` (*the returned object from* `Console.get_args()`):
  - The `len()` function can now be used on `Args` (*the returned object from* `Console.get_args()`).
  - The `Args` object now also has the dict like methods `.keys()`, `.values()` and `.items()`.
  - You can also get the args as a dict with the `.dict()` method.
  - You can now use the `in` operator on `Args`.
* New methods for `ArgResult` (*a single arg-object from inside `Args`):
  - You can now use the `bool()` function on `ArgResult` to directly see if the arg exists.
* The methods `FormatCodes.remove_ansi()` and `FormatCodes.remove_formatting()` now have a second param <code>get_removals: *bool* = False</code>:<br>
  If this param is true additionally to the cleaned string, a list of tuples will be returned, where tuple contains the position of the removed formatting/ansi code and the removed code.
* Fixed a bug in the line wrapping in all logging methods from the `xx_console` module.
* Added a new param to the method `Console.get_args()`:<br>
  <code>allow_spaces: *bool* = False</code> whether to take spaces as separator of arg values or as part of an arg value


<span id="v1-6-7" />

## 26.02.2025 `v1.6.7`

* Made the staticmethod `System.is_elevated()` into a class property, which now can be accessed as `System.is_elevated`.
* The method `File.create()` now throws a custom `SameContentFileExistsError` exception if a file with the same name and content already exists.
* Added a bunch more docstrings to class properties and library constants.

**BREAKING CHANGES:**
* Restructured the object returned from `Console.get_args()`:<br>
  Before, you accessed an arg's result with `args["<arg_alias>"]["value"]` and `args["<arg_alias>"]["exists"]`.<br>
  Now, you can directly access the result with `args.<arg_alias>.value` and `args.<arg_alias>.exists`.
* Made the method <code>Path.get(*cwd*=True)</code> or <code>Path.get(*base_dir*=True)</code> into two class properties, which now can be accessed as `Path.cwd` and `Path.script_dir`.


<span id="v1-6-6" />

## 17.02.2025 `v1.6.6`

* Added a new method `Console.multiline_input()`.
* Added two new params to the method `Console.log_box()`:<br>
  - <code>w_padding: *int* = 2</code> the horizontal padding (*in chars*) to the box content<br>
  - <code>w_full: *bool* = False</code> whether to make the box be the full console width or not
* Fixed a small bug in `Data.print()` where two params passed to `Data.to_str()` where swapped, which caused an error.
* The method `Data.print()` now per default syntax highlights the console output:<br>
  The syntax highlighting colors and styles can now be customized via the new param <code>syntax_highlighting: dict[*str*, *str*] = {…}</code>.
* Added two new methods `Data.serialize_bytes()` and `Data.deserialize_bytes()`.
* Made the method `String.to_type()` be able to also interpret and convert large complex structures.
* Added the new parameter <code>strip_spaces: *bool* = True</code> to the method `Regex.brackets()` which makes it possible to not ignore spaces around the content inside the brackets.
* Adjusted the `Console.log_box()` method, so the box background can't be reset to nothing any more.
* Added a new param to `Console.log()` (*and therefore also to every* `Console.log()` *preset*):<br>
  <code>format_linebreaks: *bool* = True</code> when true, indents the text after every linebreak to the level of the previous text

**BREAKING CHANGES:**
* Restructured the `_consts_` library constants to use `@dataclass` classes (*and simpler structured classes*) as much as possible.
* Renamed the `DEFAULT` class from the `_consts_` to `COLOR`, whose colors are now directly accessible as variables (*e.g.* `COLOR.red`) and not through dictionary keys.
* Changed the methods `Console.w()`, `Console.h()`, `Console.wh()` and `Console.user()` to modern class properties instead:<br>
  `Console.w` current console columns (*in text characters*)<br>
  `Console.h` current console lines<br>
  `Console.wh` a tuple with the console size as (columns, lines)<br>
  `Console.usr` the current username


<span id="v1-6-5" />

## 29.01.2025 `v1.6.5`

* Now the method `FormatCodes.to_ansi()` automatically converts the param `string` to a *`str`* if it isn't one already.
* Added a new method `FormatCodes.remove_codes()`.
* Added a new method `FormatCodes.remove_ansi()`.
* Added a new method `Console.log_box()`.
* Changed the default values of two params in the `Console.log()` method and every log preset:<br>
  - <code>start: *str* = "\n"</code> changed to <code>start: *str* = ""</code><br>
  - <code>end: *str* = "\n\n"</code> changed to <code>end: *str* = "\n"</code>
* Added the params <code>start: *str* = ""</code>, <code>end: *str* = "\n"</code> and <code>default_color: *rgba* | *hexa* = DEFAULT.color["cyan"]</code> to `Console.restricted_input()` and `Console.pwd_input()`.


<span id="v1-6-4" />

## 22.01.2025 `v1.6.4`

* **<u>HOTFIX:</u> Fixed a heavy bug, where the library could not be imported after the last update, because of a bug in `xx_format_codes`.**


<span id="v1-6-3" />

## 22.01.2025 `v1.6.3` **⚠️This release is broken!**

* Fixed a small bug in `xx_format_codes`:<br>
  Inside print-strings, if there was a `'` or `"` inside an auto-reset-formatting (*e.g.* `[u](there's a quote)`), that caused it to not be recognized as valid, and therefore not be automatically reset.<br>
  Now this is fixed and auto-reset-formatting works as expected.
* Added a new param <code>ignore_in_strings: *bool* = True</code> to `Regex.brackets()`:<br>
  If this param is true and a bracket is inside a string (e.g. `'…'` or `"…"`), it will not be counted as the matching closing bracket.
* Removed `lru_cache` from the `xx_format_codes` module's internal methods, since it was unnecessary.
* Adjusted `FormatCodes.__config_console()` so it can only be called once per process.


<span id="v1-6-2" />

## 20.01.2025 `v1.6.2`

* Added a new method `elevate()` to `xx_system`, which is used to request elevated privileges.
* Fixed a bug in `rgba()`, `hsla()` and `hexa()`:<br>
  Previously, when initializing a color with the alpha channel set to `0.0` (*100% transparent*), it was saved correctly, but when converted to a different color type or when returned, the alpha channel got ignored, just like if it was `None` or `1.0` (*opaque*).<br>
  Now when initializing a color with the alpha channel set to `0.0`, this doesn't happen and when converted or returned, the alpha channel is still `0.0`.
* Huge speed and efficiency improvements in `xx_color`, due to newly added option to initialize a color without validation, which saves time when initializing colors, when we know, that the values are valid.
* Added a new param <code>reset_ansi: *bool* = False</code> to `FormatCodes.input()`:<br>
  If this param is true, all formatting will be reset after the user confirmed the input and the program continues.

**BREAKING CHANGES:**
* Moved the method `is_admin()` from `xx_console` to `xx_system`.
* Method `hex_int_to_rgba()` from `xx_color` now returns an `rgba()` object instead of the separate values `r`, `g`, `b` and `a`.


<span id="v1-6-1" />

## 15.01.2025 `v1.6.1`

* Changed the params in `File.make_path()`:<br>
  Previously there were the params <code>filename: *str*</code> and <code>filetype: *str* = ""</code> where `filename` didn't have to have the file extension included, as long as the `filetype` was set.<br>
  Now these params have become one param <code>file: *str*</code> which is the file with file extension.
* Removed all line breaks and other Markdown formatting from docstrings, since not all IDEs support them.

**BREAKING CHANGES:**
* Changed the order the params in `File.create()`:<br>
  Until now the param <code>content: *str* = ""</code> was the first param and <code>file: *str* = ""</code>.<br>
  New the param <code>file: *str* = ""</code> is the first param and <code>content: *str* = ""</code> is the second.
* Renamed `File.make_path()` to a more descriptive name `File.extend_or_make_path()` and adjusted the usages of `File.create()` and `File.make_path()` inside `xx_json` accordingly.


<span id="v1-6-0" />

## 07.01.2025 `v1.6.0`

* Fixed a small bug in `to_camel_case()` in the `xx_string` module:<br>
  Previously, it would return only the first part of the decomposed string.<br>
  Now it correctly returns all decomposed string parts, joined in CamelCase.


<span id="v1-5-9" />

## 21.12.2024 `v1.5.9`

* Fixed bugs in method `to_ansi()` in module `xx_format_codes`:<br>
  1. The method always returned an empty string, because the color validation was broken, and it would identify all colors as invalid.<br>
    Now the validation `Color.is_valid_rgba()` and `Color.is_valid_hexa()` are fixed and now, if a color is identified as invalid, the method returns the original string instead of an empty string.
  2. Previously the method `to_ansi()` couldn't handle formats inside `[]` because everything inside the brackets was recognized as an invalid format.<br>
    Now you are able to use formats inside `[]` (*e.g.* `"[[red](Red text [b](inside) square brackets!)]"`).
* Introduced a new test for the `xx_format_codes` module.
* Fixed a small bug in the help client-command:<br>
  Added back the default text color.


<span id="v1-5-8" />

## 21.11.2024 `v1.5.8`

* Added method `String.is_empty()` to check if the string is empty.
* Added method `String.escape()` to escape special characters in a string.
* Introduced a new test for `xx_data` (*all methods*).
* Added doc-strings to all the methods in `xx_data`.
* Made all the methods from `xx_data` work wih all the types of data structures (*`list`, `tuple`, `set`, `frozenset`, `dict`*).
* Added method `EnvPath.remove_path()`.
* Introduced a new test for `xx_env_vars` (*all methods*).
* Added a `hexa_str()` preset to the `xx_regex` module.
* Introduced a new test for the methods from the `Color` class in `xx_color`.

**BREAKING CHANGES:**
* Renamed the library from `XulbuX` to `xulbux` for better naming conventions.
* Renamed the module `xx_cmd`, and it's class `Cmd` to `xx_console` and `Console`.
* Renamed the module `xx_env_vars`, and it's class `EnvVars` to `xx_env_path` and `EnvPath`.


<span id="v1-5-7" />

## 15.11.2024 `v1.5.7`

* Change the testing modules to be able to run together with the library `pytest`.
* Added formatting checks, using `black`, `isort` and `flake8`.
* Added the script (*command*) `xx-help` or `xulbux-help`.
* Structured `Cmd.restricted_input()` a bit nicer, so it appears less complex.
* Corrected code after `Lint with flake8` formatting suggestions.
* Added additional tests for the custom color types.
* Updated the whole `xx_format_codes` module for more efficiency and speed.

**BREAKING CHANGES:**
* Moved the `help()` function to the file `_cli_.py`, because that's where all the scripts are located (*It also was renamed to* `help_command()`).
* Moved the method `normalize_spaces()` to `xx_string`.


<span id="v1-5-6" />

## 11.11.2024 `v1.5.6`

* Moved the whole library to its own repository: **[PythonLibraryXulbuX](https://github.com/XulbuX/PythonLibraryXulbuX)**
* Updated all connections and links correspondingly.


<span id="v1-5-5" />

## 11.11.2024 `v1.5.5`

* Added methods to get the width and height of the console (*in characters and lines*):<br>
  - <code>Cmd.w() -> *int*</code> how many text characters the console is wide<br>
  - <code>Cmd.h() -> *int*</code> how many lines the console is high<br>
  - <code>Cmd.wh() -> tuple[*int*, *int*]</code> a tuple with width and height
* Added the method <code>split_count(*string*, *count*) -> list[*str*]</code> to `xx_string`.
* Added doc-strings to every method in `xx_string`.
* Updated the `Cmd.restricted_input()` method to be able to:
  - paste text from the clipboard,
  - select all text to delete everything at once,
  - write and backspace over multiple lines and
  - added support for custom formatting codes in the prompt.
* Added required non-standard libraries to the project file.
* Added more metadata to the project file.


<span id="v1-5-4" />

## 06.11.2024 `v1.5.4`

* Added a new method <code>normalize_spaces(*code*) -> *str*</code> to `Code`.
* Added new doc-strings to `xx_code` and `xx_cmd`.
* Added a custom `input()` method to `Cmd`, which lets you specify the allowed text characters the user can type, as well as the minimum and maximum length of the input.
* Added the method `pwd_input()` to `Cmd`, which works just like the `Cmd.restricted_input()` but masks the input characters with `*`.
* Restructured the whole library's imports, so the custom types won't get displayed as `Any` when hovering over a method/function.
* Fixed bug when trying to get the base directory from a compiled script (*EXE*):<br>
  Would previously get the path to the temporary extracted directory, which is created when running the EXE file.<br>
  Now it gets the actual base directory of the currently running file.

**BREAKING CHANGES:**
* Made the `blend()` method from all the color types modify the *`self`* object as well as returning the result.


<span id="v1-5-3" />

## 30.10.2024 `v1.5.3`

* Added the default text color to the `_consts_.py` so it's easier to change it (*and used it in the library*).
* Added a bunch of other default colors to the `_consts_.py` (*and used them in the library*).
* Refactored the whole library's code after the **[PEPs](https://peps.python.org)** and **[The Zen of Python](https://peps.python.org/pep-0020/#the-zen-of-python)** 🫡:
  - Changed the indent to 4 spaces.
  - No more inline control statements.
* Added new methods to `Color`:<br>
  - <code>rgba_to_hex(*r*, *g*, *b*, *a*) -> *int*</code><br>
  - <code>hex_to_rgba(*hex_int*) -> *tuple*</code><br>
  - <code>luminance(*r*, *g*, *b*, *precision*, *round_to*) -> *float*|*int*</code>
* Fixed the `grayscale()` method of `rgba()`, `hsla()` and `hexa()`:<br>
  The method would previously just return the color, fully desaturated (*not grayscale*).<br>
  Now this is fixed, and the method uses the luminance formula, to get the actual grayscale value.
* All the methods in the `xx_color` module now support HEX integers (*e.g.* `0x8085FF` *instead of only strings:* `"#8085FF"` `"0x8085FF"`).

**BREAKING CHANGES:**
* Restructured the values in `_consts_.py`.


<span id="v1-5-2" />

## 28.10.2024 `v1.5.2`

* New parameter <code>correct_path:*bool*</code> in `Path.extend()`:
  This makes sure, that typos in the path will only be corrected if this parameter is true.
* Fixed bug in `Path.extend()`, where an empty string was taken as a valid path for the current directory `./`.
* Fixed color validation bug:<br>
  `Color.is_valid_rgba()` and `Color.is_valid_hsla()` would not accept an alpha channel of `None`.<br>
  `Color.is_valid_rgba()` was still checking for an alpha channel from `0` to `255` instead of `0` to `1`.
* Fixed bug for `Color.has_alpha()`:<br>
  Previously, it would return `True` if the alpha channel was `None`.<br>
  Now in such cases it will return `False`.


<span id="v1-5-1" />

## 28.10.2024 `v1.5.1`

* Now all methods in `xx_color` support both HEX prefixes (`#` *and* `0x`).
* Added the default HEX prefix to `_consts_.py`.
* Fixed bug when initializing a `hexa()` object:<br>
  Would throw an error, even if the color was valid.

**BREAKING CHANGES:**
* Renamed all library files for a better naming convention.


<span id="v1-5-0" />

## 27.10.2024 `v1.5.0`

* Added a `__help__.py` file, which will show some information about the library and how to use it, when it's run as a script or when the `help()` function is called.
* Added a lot more metadata to the library:<br>
  `__version__` (*was already added in update [v1.4.2](#v1-4-2)*)<br>
  `__author__`<br>
  `__email__`<br>
  `__license__`<br>
  `__copyright__`<br>
  `__url__`<br>
  `__description__`<br>
  `__all__`

**BREAKING CHANGES:**
* Split all classes into separate files, so users can download only parts of the library more easily.


<span id="v1-4-2" /><span id="v1-4-3" />

## 27.10.2024 `v1.4.2` `v1.4.3`

* <code>Path.extend(*rel_path*) -> *abs_path*</code> now also extends system variables like `%USERPROFILE%` and `%APPDATA%`.
* Removed unnecessary parts when checking for missing required libraries.
* You can now get the libraries current version by accessing the attribute `XulbuX.__version__`.


<span id="v1-4-1" />

## 26.10.2024 `v1.4.1`

* Added methods to each color type:<br>
  - <code>is_grayscale() -> *self*</code><br>
  - <code>is_opaque() -> *self*</code>
* Added additional error checking to the color types.
* Made error messages for the color types clearer.
* Updated the <code>blend(*other*, *ratio*)</code> method of all color types to use additive blending except for the alpha-channel.
* Fixed problem with method-chaining for all color types.


<span id="v1-4-0" />

## 25.10.2024 `v1.4.0`

* Huge update to the custom color types:
  - Now all type-methods support chaining.
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


<span id="v1-3-1" />

## 23.10.2024 `v1.3.1`

* Now the alpha channel will be rounded to maximal 2 decimals, if converting from `hexa()` to `rgba()` or `hsla()`.


<span id="v1-3-0" />

## 21.10.2024 `v1.3.0`

* Fixed the custom types `rgba()`, `hsla()` and `hexa()`:<br>
  - `rgba()`:<br>
    Fixed `to_hsla()` and `to_hexa()`.
  - `hsla()`:<br>
    Fixed `to_rgba()` and `to_hexa()`.
  - `hexa()`:<br>
    Fixed `to_rgba()` and `to_hsla()`.
* Fixed methods from the `Color` class:<br>
  `Color.has_alpha()`<br>
  `Color.to_rgba()`<br>
  `Color.to_hsla()`<br>
  `Color.to_hexa()`
* Set default value for param <code>allow_alpha: *bool*</code> to `True` for methods:<br>
  `Color.is_valid_rgba()`<br>
  `Color.is_valid_hsla()`<br>
  `Color.is_valid_hexa()`<br>
  `Color.is_valid()`


<span id="v1-2-4" /><span id="v1-2-5" />

## 18.10.2024 `v1.2.4` `v1.2.5`

* Added more info to the `README.md` as well as additional links.
* Adjusted the structure inside `CHANGELOG.md` for a better overview and readability.

**BREAKING CHANGES:**
* Renamed the class `rgb()` to `rgba()` to communicate, more clearly, that it supports an alpha channel.
* Renamed the class `hsl()` to `hsla()` to communicate, more clearly, that it supports an alpha channel.


<span id="v1-2-3" />

## 18.10.2024 `v1.2.3`

* Added project links to the Python-project-file.
* Made some `CHANGELOG.md` improvements.
* Improved `README.md`.


<span id="v1-2-1" /><span id="v1-2-2" />

## 18.10.2024 `v1.2.1` `v1.2.2`

* Fixed bug in method <code>Path.get(*base_dir*=True)</code>:<br>
  Previously, setting `base_dir` to `True` would not return the actual base directory or even cause an error.<br>
  Setting `base_dir` to `True` now will return the actual base directory of the current program (*except if not running from a file*).


<span id="v1-2-0" />

## 17.10.2024 `v1.2.0`

* New method in the `Path` class:<br>
  `Path.remove()`


<span id="v1-1-9" />

## 17.10.2024 `v1.1.9`

**BREAKING CHANGES:**
* Corrected the naming of classes to comply with Python naming standards.


<span id="v1-1-8" />

## 17.10.2024 `v1.1.8`

* Added support for all OSes to the OS-dependent methods.


<span id="v1-1-6" /><span id="v1-1-7" />

## 17.10.2024 `v1.1.6` `v1.1.7`

* Fixed the `Cmd.cls()` method:<br>
  There was a bug where only on Windows 10, the ANSI formats weren't cleared.


<span id="v1-1-4" /><span id="v1-1-5" />

## 17.10.2024 `v1.1.4` `v1.1.5`

* Added links to the `CHANGELOG.md` and `README.md` files.


<span id="v1-1-3" />

## 17.10.2024 `v1.1.3`

* Changed the default value of the param <code>compactness: *int*</code> in the method `Data.print()` to `1` instead of `0`.


<span id="v1-1-1" /><span id="v1-1-2" />

## 17.10.2024 `v1.1.1` `v1.1.2`

* Adjusted the library's description.


<span id="v1-1-0" />

## 16.10.2024 `v1.1.0`

* Made it possible to also auto-reset the color and not only the predefined formats, using the [auto-reset-format](#auto-reset-format) (`[format](Automatically resetting)`).


<span id="v1-0-9" />

## 16.10.2024 `v1.0.9`

* Added a library description, which gets shown if the library base-import is run directly.
* Made it possible to escape an <span id="auto-reset-format">auto-reset-format</span> (`[format](Automatically resetting)`) with a slash, so you can still have `()` brackets behind a `[format]`:
  ```python
  FormatCodes.print('[u](Automatically resetting) following text')
  ```
  prints: <code><u>Automatically resetting</u> following text</code>

  ```python
  FormatCodes.print('[u]/(Automatically resetting) following text')
  ```
  prints: <code><u>(Automatically resetting) following text</u></code>


<span id="v1-0-7" /><span id="v1-0-8" />

## 16.10.2024 `v1.0.7` `v1.0.8`

* Added `input()` method to the `FormatCodes` class, so you can make pretty looking input prompts.
* Added warning for no network connection when trying to [install missing libraries](#improved-lib-importing).


<span id="v1-0-6" />

## 15.10.2024 `v1.0.6`

* <span id="improved-lib-importing">Improved **$\color{#8085FF}\textsf{XulbuX}$** library importing:</span><br>
  Checks for missing required libraries and gives you the option to directly install them, if there are any.
* Fixed issue where configuration file wasn't created and loaded correctly.

**BREAKING CHANGES:**
* Moved constant variables into a separate file.


<span id="v1-0-1" /><span id="v1-0-2" /><span id="v1-0-3" /><span id="v1-0-4" /><span id="v1-0-5" />

## 15.10.2024 `v1.0.1` `v1.0.2` `v1.0.3` `v1.0.4` `v1.0.5`

* Fixed `f-string` issues for Python 3.10:
  1. Not making use of same quotes inside f-strings any more.
  2. No backslash escaping in f-strings.


<span id="release" /><span id="v1-0-0" />

## 14.10.2024 `v1.0.0`

$\color{#F90}\Huge\textsf{INITIAL RELEASE!\ 🤩🎉}$<br>
**At initial release**, the library **$\color{#8085FF}\textsf{XulbuX}$** looks like this:
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

<br>

<div id="bottom" style="width:45px; height:45px; right:10px; position:absolute">
  <a href="#top" title="scroll to top">
    <div style="
      font-size: 2em;
      font-weight: bold;
      background: #88889845;
      border-radius: 0.2em;
      text-align: center;
      justify-content: center;
    "><span style="display:none">scroll to top </span>🠩</div>
  </a>
</div>
