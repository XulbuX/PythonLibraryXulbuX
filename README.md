<div align="center">
<br><br>
<h1>
<a href="https://xulbux.github.io/python-lib-xulbux"><img height="64" src="https://github.com/xulbux/python-lib-xulbux/blob/main/assets/icon.svg?raw=true"></a>
<br>
Python library <code>xulbux</code>
<br><br>
<a href="https://pypi.org/project/xulbux"><img src="https://img.shields.io/pypi/v/xulbux?style=flat&labelColor=404560&color=7075FF"/></a> <a href="https://clickpy.clickhouse.com/dashboard/xulbux"><img src="https://img.shields.io/pepy/dt/xulbux?style=flat&labelColor=404560&color=7075FF"/></a> <a href="https://github.com/xulbux/python-lib-xulbux/blob/main/LICENSE"><img src="https://img.shields.io/github/license/xulbux/python-lib-xulbux?style=flat&labelColor=405055&color=70E0FF"/></a> <a href="https://github.com/xulbux/python-lib-xulbux/commits"><img src="https://img.shields.io/github/last-commit/xulbux/python-lib-xulbux?style=flat&labelColor=55404A&color=FF608A"/></a> <a href="https://github.com/xulbux/python-lib-xulbux/issues"><img src="https://img.shields.io/github/issues/xulbux/python-lib-xulbux?style=flat&labelColor=55404A&color=FF608A"/></a> <a href="https://github.com/xulbux/python-lib-xulbux/stargazers"><img src="https://img.shields.io/github/stars/xulbux/python-lib-xulbux?label=★&style=flat&labelColor=604055&color=FF9ECA"/></a>
</h1>
<h3>A Python library to simplify common programming tasks.</h3>
<br><br>
</div>

**`xulbux`** is a library that contains many useful classes, types, and functions,
ranging from terminal logging and working with colors to file management and system operations.
The library is designed to simplify common programming tasks and improve code readability through its collection of tools.

For precise information about the library, see the library's [**documentation**](https://xulbux.github.io/python-lib-xulbux/docs).<br>
For the library's latest changes and updates, see the [**change log**](https://github.com/xulbux/python-lib-xulbux/blob/main/CHANGELOG.md).

### The best modules, you have to check out:

<a href="https://xulbux.github.io/python-lib-xulbux/docs/ansi"><img src="https://img.shields.io/badge/ansi-9670FF?style=for-the-badge" alt="ansi"></a> <a href="https://xulbux.github.io/python-lib-xulbux/docs/console"><img src="https://img.shields.io/badge/console-9670FF?style=for-the-badge" alt="console"></a> <a href="https://xulbux.github.io/python-lib-xulbux/docs/color"><img src="https://img.shields.io/badge/color-9670FF?style=for-the-badge" alt="color"></a>

<br>

## Installation

It is recommended to install the library within a [virtual environment](https://docs.python.org/3/tutorial/venv.html) to align with modern Python standards and prevent `externally-managed-environment` errors on newer operating systems.

To install the library, run:

```bash
pip install xulbux
```

To upgrade to the latest available version:

```bash
pip install --upgrade xulbux
```

<br>

## CLI Commands

When the library is installed, the following commands are available in the terminal:

| Command                | Description                                       |
| :--------------------- | :------------------------------------------------ |
| `xulbux-lib`           | Show some information about the library.          |
| `xulbux-lib ansi`      | Preview all possible ANSI styles in the terminal. |
| `xulbux-lib color256`  | Show a map of all 256 colors in the terminal.     |
| `xulbux-lib truecolor` | Show a true-color gradient map in the terminal.   |

<br>

## Usage

The library's modules can be accessed by importing the `xulbux` package. It is highly recommended to alias the package (e.g., as `xx`) to prevent naming conflicts with common variable names like `data` or `file`:

```python
import xulbux as xx

xx.console.log("Hello, World!")
xx.data.render({"key": "value"})
```

The library's classes can be imported directly from the `xulbux` package:

```python
from xulbux import ArgumentParser, S
```

Certain things aren't exposed under the `xulbux` package directly.<br>
They can be imported from their respective submodules, for example:

```python
from xulbux.base.consts import COLOR
from xulbux.base.types import PathsList
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
      <td align="center"><b><code><a href="https://xulbux.github.io/python-lib-xulbux/docs/base">base</a></code></b></td>
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
              <td align="center"><b><code><a href="https://xulbux.github.io/python-lib-xulbux/docs/base#consts">consts</a></code></b></td>
              <td>Constant values used throughout the library.</td>
            </tr>
            <tr>
              <td align="center"><b><code><a href="https://xulbux.github.io/python-lib-xulbux/docs/base#decorators">decorators</a></code></b></td>
              <td>Utility decorators used throughout the library.</td>
            </tr>
            <tr>
              <td align="center"><b><code><a href="https://xulbux.github.io/python-lib-xulbux/docs/base#exceptions">exceptions</a></code></b></td>
              <td>Custom exception classes used throughout the library.</td>
            </tr>
            <tr>
              <td align="center"><b><code><a href="https://xulbux.github.io/python-lib-xulbux/docs/base#types">types</a></code></b></td>
              <td>Custom type definitions used throughout the library.</td>
            </tr>
          </tbody>
        </table>
      </td>
    </tr>
    <tr>
      <td align="center"><b><code><a href="https://xulbux.github.io/python-lib-xulbux/docs/ansi">ansi</a></code></b></td>
      <td><code>S</code> <code>Term</code> classes for building richly formatted terminal output via a typed,<br>
        operator-based syntax and for emitting common cursor- and screen-control sequences.</td>
    </tr>
    <tr>
      <td align="center"><b><code><a href="https://xulbux.github.io/python-lib-xulbux/docs/code">code</a></code></b></td>
      <td><code>code</code> module, which provides methods to work with code strings.</td>
    </tr>
    <tr>
      <td align="center"><b><code><a href="https://xulbux.github.io/python-lib-xulbux/docs/color">color</a></code></b></td>
      <td><code>rgba</code> <code>hsla</code> <code>hexa</code> <code>color</code> modules, which provide methods to work with<br>
        colors in various formats.</td>
    </tr>
    <tr>
      <td align="center"><b><code><a href="https://xulbux.github.io/python-lib-xulbux/docs/console">console</a></code></b></td>
      <td><code>console</code> module, which provides methods to work with the terminal console and logging.</td>
    </tr>
    <tr>
      <td align="center"><b><code><a href="https://xulbux.github.io/python-lib-xulbux/docs/data">data</a></code></b></td>
      <td><code>data</code> module, which provides methods to work with nested data structures.</td>
    </tr>
    <tr>
      <td align="center"><b><code><a href="https://xulbux.github.io/python-lib-xulbux/docs/env_path">env_path</a></code></b></td>
      <td><code>env_path</code> module, which provides methods to work with the PATH environment variable.</td>
    </tr>
    <tr>
      <td align="center"><b><code><a href="https://xulbux.github.io/python-lib-xulbux/docs/file_sys">file_sys</a></code></b></td>
      <td><code>file_sys</code> module, which provides methods to work with the file system and directories.</td>
    </tr>
    <tr>
      <td align="center"><b><code><a href="https://xulbux.github.io/python-lib-xulbux/docs/file">file</a></code></b></td>
      <td><code>file</code> module, which provides methods to work with files and file paths.</td>
    </tr>
    <tr>
      <td align="center"><b><code><a href="https://xulbux.github.io/python-lib-xulbux/docs/json">json</a></code></b></td>
      <td><code>json</code> module, which provides methods to read, create and update JSON files,<br>
        with support for comments inside the JSON data.</td>
    </tr>
    <tr>
      <td align="center"><b><code><a href="https://xulbux.github.io/python-lib-xulbux/docs/regex">regex</a></code></b></td>
      <td><code>regex</code> module, which provides methods to dynamically generate complex regex patterns<br>
        for common use cases.</td>
    </tr>
    <tr>
      <td align="center"><b><code><a href="https://xulbux.github.io/python-lib-xulbux/docs/string">string</a></code></b></td>
      <td><code>string</code> module, which provides various utility methods for string manipulation and conversion.</td>
    </tr>
    <tr>
      <td align="center"><b><code><a href="https://xulbux.github.io/python-lib-xulbux/docs/system">system</a></code></b></td>
      <td><code>system</code> module, which provides methods to interact with the underlying operating system.</td>
    </tr>
  </tbody>
</table>

<br>

## Example Usage

This is what it could look like using this library for a simple but ultra good-looking color converter:

```python
import xulbux as xx
from xulbux import S, hexa
from xulbux.base.consts import CHARS
from xulbux.color import fg_for_on_bg


def main() -> None:

    # Let the user enter a hexa color in any hexa format.
    input_clr = xx.console.input(
        (S.BOLD("Enter a HEXA color in any format"), " > "),
        start="\n",
        placeholder="#7075FF",
        max_len=7,
        allowed_chars=CHARS.HEX_DIGITS,
    )

    # Announce indexing the input color.
    xx.console.log("INDEX", "Indexing the input HEXA color...", start="\n", title_bg_color=S.BG.BR.BLUE)

    try:
        # Try to initialize the input string as a `hexa()` object.
        hexa_color = hexa(input_clr)

    except ValueError:
        # Announce the invalid input color and exit the program.
        xx.console.fail("The input HEXA color is invalid.", end="\n\n", exit=True)

    # Announce starting the conversion.
    xx.console.log("CONVERT", "Converting the HEXA color into different types...", title_bg_color=S.BG.BR.MAGENTA)

    # Convert the hexa color into the two other color styles.
    rgba_color = hexa_color.to_rgba()
    hsla_color = hexa_color.to_hsla()

    # Announce the successful conversion.
    xx.console.done("Successfully converted color into different types.", end="\n\n")

    # Pretty print the color in different formats.
    xx.console.log_box_bordered(
        (S.BOLD("HEXA: "), (S.ITALIC | S.BR.WHITE)(str(hexa_color))),
        (S.BOLD("RGBA: "), (S.ITALIC | S.BR.WHITE)(str(rgba_color))),
        (S.BOLD("HSLA: "), (S.ITALIC | S.BR.WHITE)(str(hsla_color))),
        "{hr}",
        (S.hex(fg_for_on_bg(hexa_color)) | S.BG.hex(hexa_color))(" ... .... . -. .- -. .. --. .- -. ... "),
        border_style=S.DIM,
        end="\n\n",
    )


if __name__ == "__main__":
    main()
```

<br>
<br>

-----------------------------------------------------------------
[View this library on **PyPI**](https://pypi.org/project/xulbux)
