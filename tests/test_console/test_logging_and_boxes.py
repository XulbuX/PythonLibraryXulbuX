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
        debug("Debug message", active=True, pause=False, exit_code=None)
        debug("Inactive debug", active=False, exit_code=10)
        info("Info message", pause=False, exit_code=None)
        done("Done message", pause=False, exit_code=None)
        warn("Warn message", pause=False, exit_code=None)
        fail("Fail message", pause=False)
        fail("Fail message none", pause=False, exit_code=None)

    output = stream.getvalue()
    assert "TITLE" in output
    assert "DEBUG" in output
    assert "INFO" in output
    assert "DONE" in output
    assert "WARN" in output
    assert "FAIL" in output
    assert "Inactive debug" not in output


def test_log_error_presets_fail_and_exit() -> None:
    # Fail with system exit (explicit code):
    with pytest.raises(SystemExit) as exc_info:
        fail("Fatal failure", pause=False, exit_code=3)
    assert exc_info.value.code == 3

    with pytest.raises(SystemExit) as exc_info_one:
        fail("Fatal failure code 1", pause=False, exit_code=1)
    assert exc_info_one.value.code == 1

    # Exit preset with system exit (defaulting code):
    with pytest.raises(SystemExit) as exc_info_default:
        exit("Exiting program", pause=False)
    assert exc_info_default.value.code == 0

    # Exit preset with system exit (explicit code):
    with pytest.raises(SystemExit) as exc_info:
        exit("Exiting program", pause=False, exit_code=5)
    assert exc_info.value.code == 5

    # Presets with system exit:
    with pytest.raises(SystemExit) as exc_info:
        debug("Debug exit", active=True, pause=False, exit_code=10)
    assert exc_info.value.code == 10

    with pytest.raises(SystemExit) as exc_info:
        info("Info exit", pause=False, exit_code=11)
    assert exc_info.value.code == 11

    with pytest.raises(SystemExit) as exc_info:
        done("Done exit", pause=False, exit_code=12)
    assert exc_info.value.code == 12

    with pytest.raises(SystemExit) as exc_info:
        warn("Warn exit", pause=False, exit_code=13)
    assert exc_info.value.code == 13


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
            width=None,
            indent=2,
        )

        # Inverted default background:
        box("Inverted box", bg=True, width="full")

        # Bordered box:
        box(
            "Section 1",
            "{hr}",
            "Section 2",
            border="rounded",
            border_style=S.CYAN,
            default_color=S.WHITE,
            width=None,
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

        # Fixed width bordered, filled, and plain boxes:
        box("Fixed width bordered", width=30)
        box("Fixed width filled", bg=S.BG.MAGENTA, width=30)
        box("Fixed width plain", border=None, bg=None, width=30)

        # Fixed width with text wrapping and HR:
        box(
            "This is a longer line of content that will definitely wrap across multiple lines inside the box.",
            "{hr}",
            "Second section with wrapped content as well.",
            width=30,
        )

        # Styled text wrapping:
        box(
            S.GREEN("Styled green text that should wrap cleanly into multiple lines without breaking styles."),
            width=25,
        )

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
    assert "Fixed width bordered" in output


def test_box_fixed_width_dimensions() -> None:
    # Bordered box with fixed width:
    res = box("Short text", width=40, print=False)
    for line in res.raw.split("\n"):
        assert len(line) == 40

    # Filled box with fixed width:
    res_filled = box("Short text", bg=S.BG.GREEN, width=40, print=False)
    for line in res_filled.raw.split("\n"):
        assert len(line) == 40

    # Plain box with fixed width:
    res_plain = box("Short text", border=None, bg=None, width=40, print=False)
    for line in res_plain.raw.split("\n"):
        assert len(line) == 40

    # Plain box without width has zero padding (no leading indentation):
    res_plain_zero_pad = box("No leading spaces", border=None, bg=None, print=False)
    assert res_plain_zero_pad.raw == "No leading spaces"

    # Auto width (width=None) caps at terminal width:
    with patch("xulbux.console.get_width", return_value=35):
        long_auto = "This line is very long and should automatically wrap at the terminal width without breaking the box."
        res_auto = box(long_auto, border="rounded", print=False)
        for line in res_auto.raw.split("\n"):
            assert len(line) <= 35

    # Multi-line wrapping with fixed width:
    long_text = "This is a long sentence that should be wrapped onto multiple lines cleanly."
    res_wrapped = box(long_text, width=30, print=False)
    lines = res_wrapped.raw.split("\n")
    assert len(lines) > 3
    for line in lines:
        assert len(line) == 30

    # Styled content wrapping:
    styled_long = S.RED("This is a styled sentence that will wrap onto multiple lines inside the box.")
    res_styled = box(styled_long, width=25, print=False)
    for line in res_styled.raw.split("\n"):
        assert len(line) == 25

    # Full width:
    res_full = box("Full width box", width="full", print=False)
    assert len(res_full.raw.split("\n")[0]) > 0


def test_box_return_s_object() -> None:
    res = box("Returned Box", "{hr}", "Line 2", border="rounded", print=False)
    assert isinstance(res, S)
    assert "Returned Box" in res.raw
    assert "Line 2" in res.raw

    res_filled = box("Filled Returned", bg=S.BG.GREEN, print=False)
    assert isinstance(res_filled, S)
    assert "Filled Returned" in res_filled.raw


def test_box_validation() -> None:
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
    with pytest.raises(ValueError, match="width"):
        box("Error", width=-1)
    with pytest.raises(ValueError, match="width"):
        box("Error", width=3)  # too small: min is 2 + 2*1 + 1 = 5
    with pytest.raises(ValueError, match="width"):
        box("Error", width="invalid")  # type:ignore[arg-type,call-overload]
    with pytest.raises(ValueError, match="width"):
        box("Error", width=True)  # type:ignore[arg-type,call-overload]
    with pytest.raises(ValueError, match="align"):
        box("Error", align="invalid")  # type:ignore[arg-type,call-overload]


def test_box_alignment() -> None:
    # Left, center, right alignment in bordered box:
    res_l = box("Hi", width=20, align="left", print=False)
    line_l = res_l.raw.split("\n")[1]
    assert line_l == "│ Hi               │"

    res_r = box("Hi", width=20, align="right", print=False)
    line_r = res_r.raw.split("\n")[1]
    assert line_r == "│               Hi │"

    res_c = box("Hi", width=20, align="center", print=False)
    line_c = res_c.raw.split("\n")[1]
    assert line_c == "│        Hi        │"

    # Trailing whitespace stripped on right and center alignment:
    res_r_spaces = box("Hi   ", width=20, align="right", print=False)
    assert res_r_spaces.raw.split("\n")[1] == "│               Hi │"

    res_c_spaces = box("Hi   ", width=20, align="center", print=False)
    assert res_c_spaces.raw.split("\n")[1] == "│        Hi        │"

    # Styled trailing whitespace stripped on right alignment:
    res_r_styled = box(S.RED("Hi   "), width=20, align="right", print=False)
    assert res_r_styled.raw.split("\n")[1] == "│               Hi │"

    # Wrapped lines strip trailing whitespace on right alignment:
    long_txt = "This is a sentence that wraps nicely across lines."
    res_wrap_r = box(long_txt, width=25, align="right", print=False)
    for line in res_wrap_r.raw.split("\n")[1:-1]:
        assert line.endswith(" │")
        assert not line.endswith("  │")

    # Alignment in filled box:
    res_filled_c = box("Hi", bg=S.BG.GREEN, width=20, align="center", print=False)
    line_fc = res_filled_c.raw.split("\n")[1]
    assert line_fc == "         Hi         "

    res_filled_r = box("Hi", bg=S.BG.GREEN, width=20, align="right", print=False)
    line_fr = res_filled_r.raw.split("\n")[1]
    assert line_fr == "                Hi  "

    # Alignment in plain box:
    res_plain_c = box("Hi", border=None, bg=None, width=20, align="center", print=False)
    assert res_plain_c.raw == "         Hi         "

    res_plain_r = box("Hi", border=None, bg=None, width=20, align="right", print=False)
    assert res_plain_r.raw == "                  Hi"


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

    # _prepare_log_box with wrap_width:
    ansi_w, plain_w, max_len_w = _prepare_log_box(
        [S.RED("Styled line that is very long"), "A plain string that is very long", "{hr}"],
        has_rules=True,
        wrap_width=10,
    )
    assert len(ansi_w) > 3
    assert len(plain_w) == len(ansi_w)
    assert max_len_w <= 10
