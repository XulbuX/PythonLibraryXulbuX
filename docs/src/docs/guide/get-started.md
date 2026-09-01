# Getting Started

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

## Example Usage

This is what it could look like using this library for a simple but ultra good-looking color converter:

```python
import xulbux as xx
from xulbux import S, hexa
from xulbux.base.consts import CHARS
from xulbux.color import fg_for_on_bg


def main() -> None:

    # Let the user enter a hexa color in any format:
    input_clr = xx.console.input(
        (S.BOLD("Enter a HEXA color in any format"), " > "),
        start="\n",
        placeholder="#7075FF",
        max_len=7,
        allowed_chars=CHARS.HEX_DIGITS,
    )

    # Announce indexing the input color:
    xx.console.log("INDEX", "Indexing the input HEXA color...", start="\n", title_bg_color=S.BG.BR.BLUE)

    try:
        # Try to initialize the input string as a `hexa()` object:
        hexa_color = hexa(input_clr)

    except ValueError:
        # Announce the invalid input color and exit the program:
        xx.console.fail("The input HEXA color is invalid.", end="\n\n", exit=True)

    # Announce starting the conversion:
    xx.console.log("CONVERT", "Converting the HEXA color into different types...", title_bg_color=S.BG.BR.MAGENTA)

    # Convert the hexa color into the two other color styles:
    rgba_color = hexa_color.as_rgba()
    hsla_color = hexa_color.as_hsla()

    # Announce the successful conversion:
    xx.console.done("Successfully converted color into different types.", end="\n\n")

    # Pretty print the color in different formats:
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
