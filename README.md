# **XulbuX**

![](https://img.shields.io/pypi/v/xulbux?labelColor=404560&color=7075FF) ![](https://img.shields.io/pypi/dm/xulbux?labelColor=405555&color=70FFEE) ![](https://img.shields.io/github/license/XulbuX/PythonLibraryXulbuX?labelColor=405555&color=70FFEE) ![](https://img.shields.io/github/last-commit/XulbuX/PythonLibraryXulbuX?labelColor=554045&color=FF6065) ![](https://img.shields.io/github/issues/XulbuX/PythonLibraryXulbuX?labelColor=554045&color=FF6065)

**XulbuX** is library that contains many useful classes, types, and functions,
ranging from console logging and working with colors to file management and system operations.
The library is designed to simplify common programming tasks and improve code readability through its collection of tools.

For precise information about the library, see the library's [**documentation**](https://github.com/XulbuX/PythonLibraryXulbuX/wiki).<br>
For the libraries latest changes and updates, see the [**change log**](https://github.com/XulbuX/PythonLibraryXulbuX/blob/main/CHANGELOG.md).

### Highlights, you should definitely check out:

[![xx_format_codes](https://img.shields.io/badge/xx__format__codes-FF7E58?style=for-the-badge)](https://github.com/XulbuX/PythonLibraryXulbuX/wiki/xx_format_codes) [![xx_console](https://img.shields.io/badge/xx__console-FF7E58?style=for-the-badge)](https://github.com/XulbuX/PythonLibraryXulbuX/wiki/xx_console) [![xx_color](https://img.shields.io/badge/xx__color-FF7E58?style=for-the-badge)](https://github.com/XulbuX/PythonLibraryXulbuX/wiki/xx_color)

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

| Module                                                                                                                                                     | Short Description                                                                                  |
| :--------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------- |
| [![xx_code](https://img.shields.io/badge/xx__code-6065FF?style=flat)](https://github.com/XulbuX/PythonLibraryXulbuX/wiki/xx_code)                          | advanced code-string operations (*changing the indent, finding function calls, ...*)               |
| [![xx_color](https://img.shields.io/badge/xx__color-6065FF?style=flat)](https://github.com/XulbuX/PythonLibraryXulbuX/wiki/xx_color)                       | everything around colors (*converting, blending, searching colors in strings, ...*)                |
| [![xx_console](https://img.shields.io/badge/xx__console-6065FF?style=flat)](https://github.com/XulbuX/PythonLibraryXulbuX/wiki/xx_console)                 | advanced actions related to the console (*pretty logging, advanced inputs, ...*)                   |
| [![xx_data](https://img.shields.io/badge/xx__data-6065FF?style=flat)](https://github.com/XulbuX/PythonLibraryXulbuX/wiki/xx_data)                          | advanced operations with data structures (*compare, generate path ID's, pretty print/format, ...*) |
| [![xx_env_path](https://img.shields.io/badge/xx__env__path-6065FF?style=flat)](https://github.com/XulbuX/PythonLibraryXulbuX/wiki/xx_env_path)             | getting and editing the PATH variable (*get paths, check for paths, add paths, ...*)               |
| [![xx_file](https://img.shields.io/badge/xx__file-6065FF?style=flat)](https://github.com/XulbuX/PythonLibraryXulbuX/wiki/xx_file)                          | advanced working with files (*create files, rename file-extensions, ...*)                          |
| [![xx_format_codes](https://img.shields.io/badge/xx__format__codes-6065FF?style=flat)](https://github.com/XulbuX/PythonLibraryXulbuX/wiki/xx_format_codes) | easy pretty printing with custom format codes (*print, inputs, custom format codes to ANSI, ...*)  |
| [![xx_json](https://img.shields.io/badge/xx__json-6065FF?style=flat)](https://github.com/XulbuX/PythonLibraryXulbuX/wiki/xx_json)                          | advanced working with json files (*read, create, update, ...*)                                     |
| [![xx_path](https://img.shields.io/badge/xx__path-6065FF?style=flat)](https://github.com/XulbuX/PythonLibraryXulbuX/wiki/xx_path)                          | advanced path operations (*get paths, smart-extend relative paths, delete paths, ...*)             |
| ![xx_regex](https://img.shields.io/badge/xx__regex-6065FF?style=flat)                                                                                      | generated regex pattern-templates (*match bracket- and quote pairs, match colors, ...*)            |
| [![xx_string](https://img.shields.io/badge/xx__string-6065FF?style=flat)](https://github.com/XulbuX/PythonLibraryXulbuX/wiki/xx_string)                    | helpful actions when working with strings. (*normalize, escape, decompose, ...*)                   |
| ![xx_system](https://img.shields.io/badge/xx__system-6065FF?style=flat)                                                                                    | advanced system actions (*restart with message, check installed Python libs, ...*)                 |

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
    Console.log_box_bordered(
        f"[b](HEXA:) [i|white]({hexa_color})",
        f"[b](RGBA:) [i|white]({rgba_color})",
        f"[b](HSLA:) [i|white]({hsla_color})",
    )


if __name__ == "__main__":
    main()
```

<br>
<br>

--------------------------------------------------------------
[View this library on **PyPI**](https://pypi.org/project/XulbuX/)
