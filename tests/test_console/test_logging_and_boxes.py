import io
from unittest.mock import patch
from xulbux.ansi import S
from xulbux.console import (
    _LOG_TITLE_CACHE_MAX,
    _as_bg_color_style,
    _as_fg_color_style,
    _persist_style,
    _prepare_log_box,
    _render_log_title,
    _resolve_title_colors,
    _split_hr_parts,
    box,
    debug,
    done,
    exit,
    fail,
    info,
    log,
    warn,
)
import pytest


def test_log_functions_presets() -> None:
    stream = io.StringIO()
    with patch("sys.stdout", stream):
        # Basic log:
        log("TITLE", "Hello Log", title_bg_color=S.BG.RED, default_color=S.GREEN)

        # Presets:
        debug("Debug message", active=True, pause=False, exit=False)
        debug("Inactive debug", active=False)
        info("Info message", pause=False, exit=False)
        done("Done message", pause=False, exit=False)
        warn("Warn message", pause=False, exit=False)

    output = stream.getvalue()
    assert "TITLE" in output
    assert "DEBUG" in output
    assert "INFO" in output
    assert "DONE" in output
    assert "WARN" in output
    assert "Inactive debug" not in output


def test_log_error_presets_fail_and_exit() -> None:
    # Fail with system exit:
    with pytest.raises(SystemExit) as exc_info:
        fail("Fatal failure", pause=False, exit=True, exit_code=3)
    assert exc_info.value.code == 3

    # Exit preset with system exit:
    with pytest.raises(SystemExit) as exc_info_exit:
        exit("Exiting program", pause=False, exit=True, exit_code=0)
    assert exc_info_exit.value.code == 0


def test_log_empty_title_and_colors() -> None:
    stream = io.StringIO()
    with patch("sys.stdout", stream):
        log(None, "No title message", title_bg_color=None, default_color=None)
        log("HEX_BG", "Message", title_bg_color=S.BG.hex("#FF0000"), default_color=S.hex("#00FF00"))
        log("DARK_BG", "Message", title_bg_color=S.BG.hex("#000000"), default_color=S.hex("#00FF00"))

    output = stream.getvalue()
    assert "No title message" in output
    assert "HEX_BG" in output
    assert "DARK_BG" in output


def test_log_invalid_arguments() -> None:
    with pytest.raises(ValueError, match="tab_size"):
        log("TITLE", "Msg", tab_size=-1)
    with pytest.raises(ValueError, match="title_px"):
        log("TITLE", "Msg", title_px=-1)
    with pytest.raises(ValueError, match="title_mx"):
        log("TITLE", "Msg", title_mx=-1)


def test_box_filled_and_bordered() -> None:
    stream = io.StringIO()
    with patch("sys.stdout", stream):
        # Filled box without border:
        box(
            "Line 1",
            "Line 2",
            bg=S.BG.BLUE,
            default_color=S.WHITE,
            w_padding=2,
            w_full=False,
            indent=2,
        )

        # Inverted default background:
        box("Inverted box", bg=True, w_full=True)

        # Bordered box:
        box(
            "Section 1",
            "{hr}",
            "Section 2",
            border="rounded",
            border_style=S.CYAN,
            default_color=S.WHITE,
            w_padding=1,
            w_full=False,
        )

        # Standard, strong, and double borders:
        box("Standard", border="standard")
        box("Strong", border="strong")
        box("Double", border="double")

        # Custom 11-character border:
        custom_borders = "+-+|+-+|+-+"
        box("Custom border", border_chars=custom_borders)

        # Border with None style:
        box("Border without style", border="rounded", border_style=None)

        # Borderless with background:
        box("Top BG Custom", "{hr}", "Bottom BG Custom", bg=S.BG.BLUE)

        # Borderless without background:
        box("Top", "{hr}", "Bottom", border=None, bg=None)

    output = stream.getvalue()
    assert "Line 1" in output
    assert "Line 2" in output
    assert "Inverted box" in output
    assert "Section 1" in output
    assert "Section 2" in output
    assert "Standard" in output
    assert "Strong" in output
    assert "Double" in output
    assert "Custom border" in output
    assert "Top BG Custom" in output
    assert "Top" in output


def test_box_return_s_object() -> None:
    res = box("Returned Box", "{hr}", "Line 2", border="rounded", print=False)
    assert isinstance(res, S)
    assert "Returned Box" in res.raw
    assert "Line 2" in res.raw

    res_filled = box("Filled Returned", bg=S.BG.GREEN, print=False)
    assert isinstance(res_filled, S)
    assert "Filled Returned" in res_filled.raw


def test_box_validation() -> None:
    with pytest.raises(ValueError, match="w_padding"):
        box("Error", w_padding=-1)
    with pytest.raises(ValueError, match="indent"):
        box("Error", indent=-1)
    with pytest.raises(ValueError, match="exactly 11 characters"):
        box("Error", border_chars="+-")
    with pytest.raises(ValueError, match="border_style"):
        box("Error", border_style=S.BG.RED)
    with pytest.raises(ValueError, match="border_style"):
        box("Error", border_style=object())  # type:ignore[arg-type,call-overload]
    with pytest.raises(ValueError, match="border"):
        box("Error", border="invalid")  # type:ignore[arg-type,call-overload]
    with pytest.raises(ValueError, match="bg"):
        box("Error", bg="invalid")  # type:ignore[arg-type,call-overload]


def test_style_resolution_and_persistence_helpers() -> None:
    # _resolve_title_colors:
    bg_style, fg_style = _resolve_title_colors(S.BG.RED)
    assert bg_style == S.BG.RED and fg_style == S.BLACK

    bg_color_dark, fg_color_dark = _resolve_title_colors(S.BG.hex("#000000"))
    assert bg_color_dark is not None and fg_color_dark == S.hex(0xFFFFFF)

    bg_color_light, fg_color_light = _resolve_title_colors(S.BG.hex("#FFFFFF"))
    assert bg_color_light is not None and fg_color_light == S.hex(0x000000)

    # 256-color testing (base, cube dark/light, grayscale dark/light, and cache hit):
    assert _resolve_title_colors(S.BG.color256(1))[1] == S.BLACK
    assert _resolve_title_colors(S.BG.color256(16))[1] == S.hex(0xFFFFFF)
    assert _resolve_title_colors(S.BG.color256(16))[1] == S.hex(0xFFFFFF)  # Cache hit
    assert _resolve_title_colors(S.BG.color256(231))[1] == S.hex(0x000000)
    assert _resolve_title_colors(S.BG.color256(232))[1] == S.hex(0xFFFFFF)
    assert _resolve_title_colors(S.BG.color256(255))[1] == S.hex(0x000000)

    with pytest.raises(ValueError, match="title_bg_color"):
        _resolve_title_colors("invalid_color")
    with pytest.raises(ValueError, match="title_bg_color"):
        _resolve_title_colors(S.RED)

    # _as_bg_color_style:
    assert _as_bg_color_style(S.BG.BLUE) == S.BG.BLUE
    assert _as_bg_color_style(S.BG.rgb(10, 20, 30)) is not None
    with pytest.raises(ValueError, match="box_bg_color"):
        _as_bg_color_style(S.BLUE)
    with pytest.raises(ValueError, match="box_bg_color"):
        _as_bg_color_style(object())

    # _as_fg_color_style:
    assert _as_fg_color_style(S.GREEN) == S.GREEN
    assert _as_fg_color_style(S.hex("#ff00ff")) is not None
    with pytest.raises(ValueError, match="color"):
        _as_fg_color_style(S.BG.GREEN)
    with pytest.raises(ValueError, match="color"):
        _as_fg_color_style(object())

    # _persist_style:
    assert _persist_style("plain text", "\x1b[31m") == "plain text"
    assert _persist_style("plain text", "") == "plain text"
    persisted = _persist_style("hello \x1b[32mworld\x1b[0m", "\x1b[41m")
    assert "\x1b[41m" in persisted

    # _render_log_title caching and cached hit:
    res1 = _render_log_title("HIT_TEST", S.BG.GREEN)
    res2 = _render_log_title("HIT_TEST", S.BG.GREEN)
    assert res1 == res2

    # _render_log_title cache limit fill:
    for idx in range(_LOG_TITLE_CACHE_MAX + 10):
        _ = _render_log_title(f"CACHE_TEST_{idx}", S.BG.RED)
    # Extra call with full cache and new key:
    res_overflow = _render_log_title("OVERFLOW_TITLE", S.BG.YELLOW)
    assert res_overflow is not None


def test_split_hr_parts_and_prepare_log_box() -> None:
    # _split_hr_parts edge cases:
    parts_1 = _split_hr_parts("pre{hr}post")
    assert len(parts_1) == 3
    parts_2 = _split_hr_parts("{hr}start")
    assert len(parts_2) == 2
    parts_3 = _split_hr_parts("end{hr}")
    assert len(parts_3) == 2
    parts_4 = _split_hr_parts("alone\n{hr}\nalone")
    assert len(parts_4) >= 1
    parts_5 = _split_hr_parts("{hr}")
    assert len(parts_5) == 1
    parts_6 = _split_hr_parts("")
    assert len(parts_6) == 1
    parts_7 = _split_hr_parts("pre{hr}{hr}post")
    assert len(parts_7) == 4

    # _prepare_log_box with S and tuple items:
    ansi_lines, _, max_w = _prepare_log_box(
        [S.RED("Styled line 1\nStyled line 2"), ("Tuple line 1",), "Plain line"],
        has_rules=True,
    )
    assert len(ansi_lines) == 4
    assert max_w > 0
