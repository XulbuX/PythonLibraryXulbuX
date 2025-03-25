# **$\color{#8085FF}\Huge\textsf{XulbuX}$**

**$\color{#8085FF}\textsf{XulbuX}$** is library that contains many useful classes, types, and functions,
ranging from console logging and working with colors to file management and system operations.
The library is designed to simplify common programming tasks and improve code readability through its collection of tools.

For precise information about the library, see the library's [wiki page](https://github.com/XulbuX/PythonLibraryXulbuX/wiki).<br>
For the libraries latest changes and updates, see the [change log](https://github.com/XulbuX/PythonLibraryXulbuX/blob/main/CHANGELOG.md).

<br>

## Installation

Run the following commands in a console with administrator privileges, so the actions take effect for all users.

Install the library and all its dependencies with the command:
```console
pip install xulbux
```

Upgrade the library and all its dependencies to their latest available version with the command:
```console
pip install --upgrade xulbux
```

<br>

## Usage

Import the full library under the alias `xx`, so its constants, classes, methods and types are accessible with `xx.CONSTANT.value`, `xx.Class.method()`, `xx.type()`:
```python
import xulbux as xx
```
So you don't have to import the full library under an alias, you can also import only certain parts of the library's contents:
```python
# CONSTANTS
from xulbux import COLOR, CHARS, ANSI
# Classes
from xulbux import Code, Color, Console, ...
# types
from xulbux import rgba, hsla, hexa
```

<br>

## Modules

| Module                                                                                           | Short Description                                                                                  |
| :----------------------------------------------------------------------------------------------: | :------------------------------------------------------------------------------------------------- |
| <h3>[`xx_code`](https://github.com/XulbuX/PythonLibraryXulbuX/wiki/xx_code)</h3>                 | advanced code-string operations (*changing the indent, finding function calls, ...*)               |
| <h3>[`xx_color`](https://github.com/XulbuX/PythonLibraryXulbuX/wiki/xx_color)</h3>               | everything around colors (*converting, blending, searching colors in strings, ...*)                |
| <h3>[`xx_console`](https://github.com/XulbuX/PythonLibraryXulbuX/wiki/xx_console)</h3>           | advanced actions related to the console (*pretty logging, advanced inputs, ...*)                   |
| <h3>[`xx_data`](https://github.com/XulbuX/PythonLibraryXulbuX/wiki/xx_data)</h3>                 | advanced operations with data structures (*compare, generate path ID's, pretty print/format, ...*) |
| <h3>[`xx_env_path`](https://github.com/XulbuX/PythonLibraryXulbuX/wiki/xx_env_path)</h3>         | getting and editing the PATH variable (*get paths, check for paths, add paths, ...*)               |
| <h3>[`xx_file`](https://github.com/XulbuX/PythonLibraryXulbuX/wiki/xx_file)</h3>                 | advanced working with files (*create files, rename file-extensions, ...*)                          |
| <h3>[`xx_format_codes`](https://github.com/XulbuX/PythonLibraryXulbuX/wiki/xx_format_codes)</h3> | easy pretty printing with custom format codes (*print, inputs, custom format codes to ANSI, ...*)  |
| <h3>[`xx_json`](https://github.com/XulbuX/PythonLibraryXulbuX/wiki/xx_json)</h3>                 | advanced working with json files (*read, create, update, ...*)                                     |
| <h3>`xx_path`</h3>                                                                               | advanced path operations (*get paths, smart-extend relative paths, delete paths, ...*)             |
| <h3>`xx_regex`</h3>                                                                              | generated regex pattern-templates (*match bracket- and quote pairs, match colors, ...*)            |
| <h3>[`xx_string`](https://github.com/XulbuX/PythonLibraryXulbuX/wiki/xx_string)</h3>             | helpful actions when working with strings. (*normalize, escape, decompose, ...*)                   |
| <h3>`xx_system`</h3>                                                                             | advanced system actions (*restart with message, check installed Python libs, ...*)                 |

<br>

## Example Usage

This is what it could look like using this library for a simple but very nice looking color converter:
```python
from xulbux import COLOR                 # CONSTANTS
from xulbux import FormatCodes, Console  # Classes
from xulbux import hexa                  # types


def main() -> None:

    # LET THE USER ENTER A HEXA COLOR IN ANY HEXA FORMAT
    input_clr = FormatCodes.input(
      "\n[b](Enter a HEXA color in any format) [dim](>) "
    )

    # ANNOUNCE INDEXING THE INPUT COLOR
    Console.log(
      "INDEX",
      "Indexing the input HEXA color...",
      start="\n",
      title_bg_color=COLOR.blue,
    )

    try:
        # TRY TO CONVERT THE INPUT COLOR INTO A hexa() COLOR
        hexa_color = hexa(input_clr)

    except ValueError:
        # ANNOUNCE THE ERROR AND EXIT THE PROGRAM
        Console.fail(
          "The input HEXA color is invalid.",
          end="\n\n",
          exit=True,
        )

    # ANNOUNCE STARTING THE CONVERSION
    Console.log(
      "CONVERT",
      "Converting the HEXA color into different types...",
      title_bg_color=COLOR.tangerine,
    )

    # CONVERT THE HEXA COLOR INTO THE TWO OTHER COLOR TYPES
    rgba_color = hexa_color.to_rgba()
    hsla_color = hexa_color.to_hsla()

    # ANNOUNCE THE SUCCESSFUL CONVERSION
    Console.done(
      "Successfully converted color into different types.",
      end="\n\n",
    )

    # PRETTY PRINT THE COLOR IN DIFFERENT TYPES
    FormatCodes.print(f"[b](HEXA:) [i|white]({hexa_color})")
    FormatCodes.print(f"[b](RGBA:) [i|white]({rgba_color})")
    FormatCodes.print(f"[b](HSLA:) [i|white]({hsla_color})\n")


if __name__ == "__main__":
    main()
```

<br>
<br>

--------------------------------------------------------------
[View this library on PyPI](https://pypi.org/project/XulbuX/)
