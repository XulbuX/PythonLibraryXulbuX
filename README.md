# **xulbux**

[![](https://img.shields.io/pypi/v/xulbux?labelColor=404560&color=7075FF)](https://pypi.org/project/xulbux) [![](https://img.shields.io/pepy/dt/xulbux?labelColor=404560&color=7075FF)](https://clickpy.clickhouse.com/dashboard/xulbux) [![](https://img.shields.io/github/license/XulbuX/PythonLibraryXulbuX?labelColor=405555&color=70FFEE)](https://github.com/XulbuX/PythonLibraryXulbuX/blob/main/LICENSE) [![](https://img.shields.io/github/last-commit/XulbuX/PythonLibraryXulbuX?labelColor=554045&color=FF6065)](https://github.com/XulbuX/PythonLibraryXulbuX/commits) [![](https://img.shields.io/github/issues/XulbuX/PythonLibraryXulbuX?labelColor=554045&color=FF6065)](https://github.com/XulbuX/PythonLibraryXulbuX/issues)

**`xulbux`** is a library that contains many useful classes, types, and functions,
ranging from console logging and working with colors to file management and system operations.
The library is designed to simplify common programming tasks and improve code readability through its collection of tools.

For precise information about the library, see the library's [**documentation**](https://github.com/XulbuX/PythonLibraryXulbuX/wiki).<br>
For the libraries latest changes and updates, see the [**change log**](https://github.com/XulbuX/PythonLibraryXulbuX/blob/main/CHANGELOG.md).

### The best modules, you have to check out:

[![format_codes](https://img.shields.io/badge/format__codes-FF7E58?style=for-the-badge)](https://github.com/XulbuX/PythonLibraryXulbuX/wiki/format_codes) [![console](https://img.shields.io/badge/console-FF7E58?style=for-the-badge)](https://github.com/XulbuX/PythonLibraryXulbuX/wiki/console) [![color](https://img.shields.io/badge/color-FF7E58?style=for-the-badge)](https://github.com/XulbuX/PythonLibraryXulbuX/wiki/color)

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

## CLI Commands

When the library is installed, the following commands are available in the console:
| Command       | Description                              |
| :------------ | :--------------------------------------- |
| `xulbux-help` | shows some information about the library |

<br>

## Usage

Import the full library under the alias `xx`, so its constants, classes, methods, and types are accessible with `xx.CONSTANT.value`, `xx.Class.method()`, `xx.type()`:
```python
import xulbux as xx
```
So you don't have to import the full library under an alias, you can also import only certain parts of the library's contents:
```python
# LIBRARY CONSTANTS
from xulbux.base.consts import COLOR, CHARS, ANSI
# Main Classes
from xulbux import Code, Color, Console, ...
# module specific imports
from xulbux.color import rgba, hsla, hexa
```

<br>

## Modules

| Module                                                                                                                                                    | Short Description                                                                           |
| :-------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------ |
| [![base](https://img.shields.io/badge/base-FF7E58?style=for-the-badge)](https://github.com/XulbuX/PythonLibraryXulbuX/wiki/base)                          | includes more modules like library constants                                                |
| [![code](https://img.shields.io/badge/code-FF7E58?style=for-the-badge)](https://github.com/XulbuX/PythonLibraryXulbuX/wiki/code)                          | advanced code-string operations (*changing the indent, finding function calls, ...*)        |
| [![color](https://img.shields.io/badge/color-FF7E58?style=for-the-badge)](https://github.com/XulbuX/PythonLibraryXulbuX/wiki/color)                       | everything around colors (*converting, blending, searching colors in strings, ...*)         |
| [![console](https://img.shields.io/badge/console-FF7E58?style=for-the-badge)](https://github.com/XulbuX/PythonLibraryXulbuX/wiki/console)                 | advanced actions related to the console (*pretty logging, advanced inputs, ...*)            |
| [![data](https://img.shields.io/badge/data-FF7E58?style=for-the-badge)](https://github.com/XulbuX/PythonLibraryXulbuX/wiki/data)                          | advanced operations with data structures (*compare, generate path IDs, pretty print, ...*)  |
| [![env_path](https://img.shields.io/badge/env__path-FF7E58?style=for-the-badge)](https://github.com/XulbuX/PythonLibraryXulbuX/wiki/env_path)             | getting and editing the PATH variable (*get paths, check for paths, add paths, ...*)        |
| [![file](https://img.shields.io/badge/file-FF7E58?style=for-the-badge)](https://github.com/XulbuX/PythonLibraryXulbuX/wiki/file)                          | advanced working with files (*create files, rename file-extensions, ...*)                   |
| [![format_codes](https://img.shields.io/badge/format__codes-FF7E58?style=for-the-badge)](https://github.com/XulbuX/PythonLibraryXulbuX/wiki/format_codes) | easy pretty printing using custom format codes (*print, inputs, format codes to ANSI, ...*) |
| [![json](https://img.shields.io/badge/json-FF7E58?style=for-the-badge)](https://github.com/XulbuX/PythonLibraryXulbuX/wiki/json)                          | advanced working with json files (*read, create, update, ...*)                              |
| [![path](https://img.shields.io/badge/path-FF7E58?style=for-the-badge)](https://github.com/XulbuX/PythonLibraryXulbuX/wiki/path)                          | advanced path operations (*get paths, smart-extend relative paths, delete paths, ...*)      |
| [![regex](https://img.shields.io/badge/regex-FF7E58?style=for-the-badge)](https://github.com/XulbuX/PythonLibraryXulbuX/wiki/regex)                       | generated regex pattern-templates (*match bracket- and quote pairs, match colors, ...*)     |
| [![string](https://img.shields.io/badge/string-FF7E58?style=for-the-badge)](https://github.com/XulbuX/PythonLibraryXulbuX/wiki/string)                    | helpful actions when working with strings. (*normalize, escape, decompose, ...*)            |
| [![system](https://img.shields.io/badge/system-FF7E58?style=for-the-badge)](https://github.com/XulbuX/PythonLibraryXulbuX/wiki/system)                    | advanced system actions (*restart with message, check installed Python libs, ...*)          |

<br>

## Example Usage

This is what it could look like using this library for a simple but ultra good-looking color converter:
```python
from xulbux.base.consts import COLOR, CHARS
from xulbux.color import hexa
from xulbux import Console


def main() -> None:

    # LET THE USER ENTER A HEXA COLOR IN ANY HEXA FORMAT
    input_clr = Console.input(
        "[b](Enter a HEXA color in any format) > ",
        start="\n",
        placeholder="#7075FF",
        max_len=7,
        allowed_chars=CHARS.HEX_DIGITS,
    )

    # ANNOUNCE INDEXING THE INPUT COLOR
    Console.log(
        "INDEX",
        "Indexing the input HEXA color...",
        start="\n",
        title_bg_color=COLOR.BLUE,
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
        title_bg_color=COLOR.TANGERINE,
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
[View this library on **PyPI**](https://pypi.org/project/xulbux)
