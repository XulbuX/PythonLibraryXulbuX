from ..ansi import S, TextRenderable


def _render_pair(code: int, /) -> TextRenderable:
    """Internal helper to format a 256-color BG block and FG label pair."""

    bg, label = S.BG.color256(code), f"{code:03d}"
    return ((bg.contrast_fg() | bg)(f" {label} "), " ", S.color256(code)(label))


def show_color256() -> None:
    """CLI command function for `xulbux-lib c256` command,<br>
    which displays the full 256-color ANSI terminal palette."""

    lines: list[TextRenderable] = [S.RESET.ansi]

    # [1] System Colors (0-15):
    lines.extend([
        S(" ").join([_render_pair(col) for col in range(8)]),
        S(" ").join([_render_pair(col) for col in range(8, 16)]),
        "",
    ])

    # [2] 6x6x6 Color Cube (16-231):
    for red in range(6):
        for green in range(6):
            lines.append(S(" ").join([_render_pair(16 + (36 * red) + (6 * green) + blue) for blue in range(6)]))
        lines.append("")

    # [3] Grayscale Ramp (232-255):
    for row in range(4):
        lines.append(S(" ").join([_render_pair(232 + (row * 6) + col_idx) for col_idx in range(6)]))

    S(*lines, "", sep="\n").print()
