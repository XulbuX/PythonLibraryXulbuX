> [!IMPORTANT]
> This library is compatible with Python 3.14, but **certain dependencies might not yet support this version**.

# **xulbux**

[![](https://img.shields.io/pypi/v/xulbux?style=flat&labelColor=404560&color=7075FF)](https://pypi.org/project/xulbux) [![](https://img.shields.io/pepy/dt/xulbux?style=flat&labelColor=404560&color=7075FF)](https://clickpy.clickhouse.com/dashboard/xulbux) [![](https://img.shields.io/github/license/XulbuX/PythonLibraryXulbuX?style=flat&labelColor=405555&color=70FFEE)](https://github.com/XulbuX/PythonLibraryXulbuX/blob/main/LICENSE) [![](https://img.shields.io/github/last-commit/XulbuX/PythonLibraryXulbuX?style=flat&labelColor=554045&color=FF6065)](https://github.com/XulbuX/PythonLibraryXulbuX/commits) [![](https://img.shields.io/github/issues/XulbuX/PythonLibraryXulbuX?style=flat&labelColor=554045&color=FF6065)](https://github.com/XulbuX/PythonLibraryXulbuX/issues) [![](https://img.shields.io/github/stars/XulbuX/PythonLibraryXulbuX?label=★&style=flat&labelColor=604A40&color=FF9673)](https://github.com/XulbuX/PythonLibraryXulbuX/stargazers)

**`xulbux`** is a library that contains many useful classes, types, and functions,
ranging from console logging and working with colors to file management and system operations.
The library is designed to simplify common programming tasks and improve code readability through its collection of tools.

For precise information about the library, see the library's [**documentation**](https://github.com/XulbuX/PythonLibraryXulbuX/wiki).<br>
For the libraries latest changes and updates, see the [**change log**](https://github.com/XulbuX/PythonLibraryXulbuX/blob/main/CHANGELOG.md).

### The best modules, you have to check out:

[![format_codes](https://img.shields.io/badge/format__codes-B272FC?style=for-the-badge)](https://github.com/XulbuX/PythonLibraryXulbuX/wiki/format_codes) [![console](https://img.shields.io/badge/console-B272FC?style=for-the-badge)](https://github.com/XulbuX/PythonLibraryXulbuX/wiki/console) [![color](https://img.shields.io/badge/color-B272FC?style=for-the-badge)](https://github.com/XulbuX/PythonLibraryXulbuX/wiki/color)

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

Import the full library under the alias `xx`, so its modules and main classes are accessible with `xx.module.Class`, `xx.MainClass.method()`:
```python
import xulbux as xx
```

So you don't have to import the full library under an alias, you can also import only certain parts of the library's contents:
```python
# LIBRARY SUB MODULES
from xulbux.base.consts import COLOR, CHARS, ANSI
# MODULE MAIN CLASSES
from xulbux import Code, Color, Console, ...
# MODULE SPECIFIC IMPORTS
from xulbux.color import rgba, hsla, hexa
```

<br>

## Modules

<table>
  <thead>
    <tr>
      <th align="left">Main Module</th>
      <th align="left">Contents</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><a href="https://github.com/XulbuX/PythonLibraryXulbuX/wiki/base"><img src="https://img.shields.io/badge/base-B272FC?style=for-the-badge" alt="base"></a></td>
      <td>
        <table>
          <thead>
            <tr>
              <th align="left">Sub Module</th>
              <th align="left">Contents</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><a href="https://github.com/XulbuX/PythonLibraryXulbuX/wiki/base#consts"><img src="https://img.shields.io/badge/consts-B272FC?style=for-the-badge" alt="consts"></a></td>
              <td>Constant values used throughout the library.</td>
            </tr>
            <tr>
              <td><a href="https://github.com/XulbuX/PythonLibraryXulbuX/wiki/base#exceptions"><img src="https://img.shields.io/badge/exceptions-B272FC?style=for-the-badge" alt="exceptions"></a></td>
              <td>Custom exception classes used throughout the library.</td>
            </tr>
            <tr>
              <td><a href="https://github.com/XulbuX/PythonLibraryXulbuX/wiki/base#types"><img src="https://img.shields.io/badge/types-B272FC?style=for-the-badge" alt="types"></a></td>
              <td>Custom type definitions used throughout the library.</td>
            </tr>
          </tbody>
        </table>
      </td>
    </tr>
    <tr>
      <td><a href="https://github.com/XulbuX/PythonLibraryXulbuX/wiki/code"><img src="https://img.shields.io/badge/code-B272FC?style=for-the-badge" alt="code"></a></td>
      <td><code>Code</code> class, which includes methods to work with code strings.</td>
    </tr>
    <tr>
      <td><a href="https://github.com/XulbuX/PythonLibraryXulbuX/wiki/color"><img src="https://img.shields.io/badge/color-B272FC?style=for-the-badge" alt="color"></a></td>
      <td><code>rgba</code> <code>hsla</code> <code>hexa</code> <code>Color</code> classes, which include methods to work with<br>
        colors in various formats.</td>
    </tr>
    <tr>
      <td><a href="https://github.com/XulbuX/PythonLibraryXulbuX/wiki/console"><img src="https://img.shields.io/badge/console-B272FC?style=for-the-badge" alt="console"></a></td>
      <td><code>Console</code> <code>ProgressBar</code> classes, which include methods for logging<br>
        and other actions within the console.</td>
    </tr>
    <tr>
      <td><a href="https://github.com/XulbuX/PythonLibraryXulbuX/wiki/data"><img src="https://img.shields.io/badge/data-B272FC?style=for-the-badge" alt="data"></a></td>
      <td><code>Data</code> class, which includes methods to work with nested data structures.</td>
    </tr>
    <tr>
      <td><a href="https://github.com/XulbuX/PythonLibraryXulbuX/wiki/env_path"><img src="https://img.shields.io/badge/env__path-B272FC?style=for-the-badge" alt="env_path"></a></td>
      <td><code>EnvPath</code> class, which includes methods to work with the PATH environment variable.</td>
    </tr>
    <tr>
      <td><a href="https://github.com/XulbuX/PythonLibraryXulbuX/wiki/file"><img src="https://img.shields.io/badge/file-B272FC?style=for-the-badge" alt="file"></a></td>
      <td><code>File</code> class, which includes methods to work with files and file paths.</td>
    </tr>
    <tr>
      <td><a href="https://github.com/XulbuX/PythonLibraryXulbuX/wiki/format_codes"><img src="https://img.shields.io/badge/format__codes-B272FC?style=for-the-badge" alt="format_codes"></a></td>
      <td><code>FormatCodes</code> class, which includes methods to print and work with strings that contain<br>
        special formatting codes, which are then converted to ANSI codes for pretty console output.</td>
    </tr>
    <tr>
      <td><a href="https://github.com/XulbuX/PythonLibraryXulbuX/wiki/json"><img src="https://img.shields.io/badge/json-B272FC?style=for-the-badge" alt="json"></a></td>
      <td><code>Json</code> class, which includes methods to read, create and update JSON files,<br>
        with support for comments inside the JSON data.</td>
    </tr>
    <tr>
      <td><a href="https://github.com/XulbuX/PythonLibraryXulbuX/wiki/path"><img src="https://img.shields.io/badge/path-B272FC?style=for-the-badge" alt="path"></a></td>
      <td><code>Path</code> class, which includes methods to work with file and directory paths.</td>
    </tr>
    <tr>
      <td><a href="https://github.com/XulbuX/PythonLibraryXulbuX/wiki/regex"><img src="https://img.shields.io/badge/regex-B272FC?style=for-the-badge" alt="regex"></a></td>
      <td><code>Regex</code> class, which includes methods to dynamically generate complex regex patterns<br>
        for common use cases.</td>
    </tr>
    <tr>
      <td><a href="https://github.com/XulbuX/PythonLibraryXulbuX/wiki/string"><img src="https://img.shields.io/badge/string-B272FC?style=for-the-badge" alt="string"></a></td>
      <td><code>String</code> class, which includes various utility methods for string manipulation and conversion.</td>
    </tr>
    <tr>
      <td><a href="https://github.com/XulbuX/PythonLibraryXulbuX/wiki/system"><img src="https://img.shields.io/badge/system-B272FC?style=for-the-badge" alt="system"></a></td>
      <td><code>System</code> class, which includes methods to interact with the underlying operating system.</td>
    </tr>
  </tbody>
</table>

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
        # TRY TO CONVERT THE INPUT STRING INTO A hexa() OBJECT
        hexa_color = hexa(input_clr)

    except ValueError:
        # ANNOUNCE THE INVALID INPUT COLOR AND EXIT THE PROGRAM
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

    # CONVERT THE HEXA COLOR INTO THE TWO OTHER COLOR FORMATS
    rgba_color = hexa_color.to_rgba()
    hsla_color = hexa_color.to_hsla()

    # ANNOUNCE THE SUCCESSFUL CONVERSION
    Console.done(
        "Successfully converted color into different types.",
        end="\n\n",
    )

    # PRETTY PRINT THE COLOR IN DIFFERENT FORMATS
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

-----------------------------------------------------------------
[View this library on **PyPI**](https://pypi.org/project/xulbux)
