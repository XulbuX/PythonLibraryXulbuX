from ..ansi import Renderable, S
from ..base.consts import CHARS
from ..color import hexa, hsla, rgba
from ..console import get_width

import re
from contextlib import suppress


def _parse_color_arg(raw: str, /) -> hsla | None:
    """Internal helper to parse a color CLI argument as an `hsla` color.\n
    ----------------------------------------------------------------------------------------------------
    Supports HEX (`#1E90FF`, `ff0055`), RGB (`rgb(255, 0, 128)`, `255,0,128`), and<br>
    numeric hue values (`210`, `210deg`). Returns `None` if invalid."""

    clean_str = raw.strip()

    # [1] Try parsing as HEX if explicit prefix or 6/8-digit hex:
    is_hex = False
    if clean_str.startswith(("#", "0x", "0X")):
        is_hex = True
    elif len(clean_str) in {6, 8}:
        is_hex = True
        for char in clean_str:
            if char not in CHARS.HEX_DIGITS:
                is_hex = False
                break

    if is_hex:
        with suppress(ValueError, TypeError):
            return hexa(clean_str).to_hsla()

    # [2] Try parsing as RGB color:
    if rgb_match := re.search(r"^(?:rgb\s*\(\s*)?(\d{1,3})\s*[, ]\s*(\d{1,3})\s*[, ]\s*(\d{1,3})\s*\)?$", clean_str):
        red, green, blue = [int(channel) for channel in rgb_match.groups()]
        if 0 <= red <= 255 and 0 <= green <= 255 and 0 <= blue <= 255:
            return rgba(red, green, blue).to_hsla()

    # [3] Try parsing as numeric hue degrees:
    with suppress(ValueError):
        return hsla(round(float(clean_str.rstrip("degDEG").strip())) % 360, 100, 50)

    # [4] Fallback try parsing as shorthand 3-digit HEX:
    with suppress(ValueError, TypeError):
        return hexa(clean_str).to_hsla()

    return None


def show_true_color(color_arg: str | None = None, /) -> None:
    """CLI command function for `xulbux-lib truecolor` command,<br>
    which renders a smooth true-color gradient in the terminal."""

    parsed_hsla: hsla | None = _parse_color_arg(color_arg) if color_arg else None

    width = min(max(get_width() - 4, 30), 60)
    rows = (height := width) // 2

    lines: list[Renderable] = [S.RESET]

    # Pixel generator function:
    def get_pixel(pixel_x: int, pixel_y: int) -> tuple[int, int, int]:
        lightness = round((1.0 - (pixel_y / (height - 1))) * 100)

        if parsed_hsla is not None:
            # Single color mode: Sweep saturation across X, lightness across Y:
            saturation = round((pixel_x / (width - 1)) * 100)
            rgb_obj = hsla(parsed_hsla.hue, saturation, lightness).to_rgba()
        else:
            # Full spectrum mode: Sweep hue across X, lightness across Y:
            hue = round((360.0 - (pixel_x / width) * 360.0) % 360.0)
            rgb_obj = hsla(hue, 100, lightness).to_rgba()

        return (rgb_obj.red, rgb_obj.green, rgb_obj.blue)

    # Render rows using half-block 2-in-1 character cells:
    for row_idx in range(rows):
        bottom_y = (top_y := row_idx * 2) + 1
        lines.append((
            "  ",
            *[(S.BG.rgb(*get_pixel(col_idx, top_y)) | S.rgb(*get_pixel(col_idx, bottom_y)))("▄") for col_idx in range(width)],
        ))

    S(*lines, "", sep="\n").print()
