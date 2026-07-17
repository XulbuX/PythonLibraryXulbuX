<div align="center">
<br><br>
<h1>
<a href="https://github.com/xulbux/python-lib-xulbux"><img height="64" src="https://github.com/xulbux/python-lib-xulbux/blob/main/assets/icon.svg?raw=true"></a>
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

For precise information about the library, see the library's [**documentation**](https://github.com/xulbux/python-lib-xulbux/wiki).<br>
For the library's latest changes and updates, see the [**change log**](https://github.com/xulbux/python-lib-xulbux/blob/main/CHANGELOG.md).

### The best modules, you have to check out:

<a href="https://github.com/xulbux/python-lib-xulbux/wiki/ansi"><img src="https://img.shields.io/badge/ansi-9670FF?style=for-the-badge" alt="ansi"></a> <a href="https://github.com/xulbux/python-lib-xulbux/wiki/console"><img src="https://img.shields.io/badge/console-9670FF?style=for-the-badge" alt="console"></a> <a href="https://github.com/xulbux/python-lib-xulbux/wiki/color"><img src="https://img.shields.io/badge/color-9670FF?style=for-the-badge" alt="color"></a>

<br>

## Installation

It is recommended to install the library within a [virtual environment](https://docs.python.org/3/tutorial/venv.html) to align with modern Python standards and prevent `externally-managed-environment` errors on newer operating systems.

To install the library, run:

```shell
pip install xulbux
```

To upgrade to the latest available version:

```shell
pip install --upgrade xulbux
```

<br>

## CLI Commands

When the library is installed, the following commands are available in the terminal:

| Command      | Description                              |
| :----------- | :--------------------------------------- |
| `xulbux-lib` | Show some information about the library. |

<br>

## Usage

The library's main classes can be imported directly from the `xulbux` package:

```python
from xulbux import Console, StyledText, S
```

Certain things aren't exposed under the `xulbux` package directly.<br>
They can be imported from their respective submodules, for example:

```python
from xulbux.base.consts import COLOR
from xulbux.color import rgba, hexa
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
      <td align="center"><b><code><a href="https://github.com/xulbux/python-lib-xulbux/wiki/base">base</a></code></b></td>
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
              <td align="center"><b><code><a href="https://github.com/xulbux/python-lib-xulbux/wiki/base#consts">consts</a></code></b></td>
              <td>Constant values used throughout the library.</td>
            </tr>
            <tr>
              <td align="center"><b><code><a href="https://github.com/xulbux/python-lib-xulbux/wiki/base#exceptions">exceptions</a></code></b></td>
              <td>Custom exception classes used throughout the library.</td>
            </tr>
            <tr>
              <td align="center"><b><code><a href="https://github.com/xulbux/python-lib-xulbux/wiki/base#types">types</a></code></b></td>
              <td>Custom type definitions used throughout the library.</td>
            </tr>
          </tbody>
        </table>
      </td>
    </tr>
    <tr>
      <td align="center"><b><code><a href="https://github.com/xulbux/python-lib-xulbux/wiki/code">code</a></code></b></td>
      <td><code>Code</code> class, which includes methods to work with code strings.</td>
    </tr>
    <tr>
      <td align="center"><b><code><a href="https://github.com/xulbux/python-lib-xulbux/wiki/color">color</a></code></b></td>
      <td><code>rgba</code> <code>hsla</code> <code>hexa</code> <code>Color</code> classes, which include methods to work with<br>
        colors in various formats.</td>
    </tr>
    <tr>
      <td align="center"><b><code><a href="https://github.com/xulbux/python-lib-xulbux/wiki/console">console</a></code></b></td>
      <td><code>Console</code> <code>ProgressBar</code> classes, which include methods for logging<br>
        and other actions within the console.</td>
    </tr>
    <tr>
      <td align="center"><b><code><a href="https://github.com/xulbux/python-lib-xulbux/wiki/data">data</a></code></b></td>
      <td><code>Data</code> class, which includes methods to work with nested data structures.</td>
    </tr>
    <tr>
      <td align="center"><b><code><a href="https://github.com/xulbux/python-lib-xulbux/wiki/env_path">env_path</a></code></b></td>
      <td><code>EnvPath</code> class, which includes methods to work with the PATH environment variable.</td>
    </tr>
    <tr>
      <td align="center"><b><code><a href="https://github.com/xulbux/python-lib-xulbux/wiki/path">path</a></code></b></td>
      <td><code>FileSys</code> class, which includes methods to work with the file system and directories.</td>
    </tr>
    <tr>
      <td align="center"><b><code><a href="https://github.com/xulbux/python-lib-xulbux/wiki/file">file</a></code></b></td>
      <td><code>File</code> class, which includes methods to work with files and file paths.</td>
    </tr>
    <tr>
      <td align="center"><b><code><a href="https://github.com/xulbux/python-lib-xulbux/wiki/ansi">ansi</a></code></b></td>
      <td><code>S</code> <code>StyledText</code> <code>Term</code> classes for building richly formatted terminal output via a typed,<br>
        operator-based syntax and for emitting common cursor- and screen-control sequences.</td>
    </tr>
    <tr>
      <td align="center"><b><code><a href="https://github.com/xulbux/python-lib-xulbux/wiki/json">json</a></code></b></td>
      <td><code>Json</code> class, which includes methods to read, create and update JSON files,<br>
        with support for comments inside the JSON data.</td>
    </tr>
    <tr>
      <td align="center"><b><code><a href="https://github.com/xulbux/python-lib-xulbux/wiki/regex">regex</a></code></b></td>
      <td><code>Regex</code> class, which includes methods to dynamically generate complex regex patterns<br>
        for common use cases.</td>
    </tr>
    <tr>
      <td align="center"><b><code><a href="https://github.com/xulbux/python-lib-xulbux/wiki/string">string</a></code></b></td>
      <td><code>String</code> class, which includes various utility methods for string manipulation and conversion.</td>
    </tr>
    <tr>
      <td align="center"><b><code><a href="https://github.com/xulbux/python-lib-xulbux/wiki/system">system</a></code></b></td>
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

    # Let the user enter a hexa color in any hexa format.
    input_clr = Console.input(
        "[b](Enter a HEXA color in any format) > ",
        start="\n",
        placeholder="#7075FF",
        max_len=7,
        allowed_chars=CHARS.HEX_DIGITS,
    )

    # Announce indexing the input color.
    Console.log(
        "INDEX",
        "Indexing the input HEXA color...",
        start="\n",
        title_bg_color=COLOR.BLUE,
    )

    try:
        # Try to convert the input string into a `hexa()` object.
        hexa_color = hexa(input_clr)

    except ValueError:
        # Announce the invalid input color and exit the program.
        Console.fail(
            "The input HEXA color is invalid.",
            end="\n\n",
            exit=True,
        )

    # Announce starting the conversion.
    Console.log(
        "CONVERT",
        "Converting the HEXA color into different types...",
        title_bg_color=COLOR.TANGERINE,
    )

    # Convert the hexa color into the two other color styles.
    rgba_color = hexa_color.to_rgba()
    hsla_color = hexa_color.to_hsla()

    # Announce the successful conversion.
    Console.done(
        "Successfully converted color into different types.",
        end="\n\n",
    )

    # Pretty print the color in different formats.
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
