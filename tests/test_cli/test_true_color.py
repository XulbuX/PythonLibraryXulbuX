from xulbux.cli.true_color import _parse_color_arg, show_true_color
import pytest


def test_parse_color_arg_hex() -> None:
    result = _parse_color_arg("#FF0000")
    assert result is not None
    assert result.hue == 0
    assert result.sat == 100

    result = _parse_color_arg("00FF00")
    assert result is not None
    assert result.hue == 120

    result = _parse_color_arg("#00F")
    assert result is not None
    assert result.hue == 240

    result = _parse_color_arg("0xFF00FF")
    assert result is not None
    assert result.hue == 300


def test_parse_color_arg_rgb() -> None:
    result = _parse_color_arg("rgb(255, 0, 0)")
    assert result is not None
    assert result.hue == 0

    result = _parse_color_arg("0, 255, 0")
    assert result is not None
    assert result.hue == 120

    result = _parse_color_arg("0 0 255")
    assert result is not None
    assert result.hue == 240

    assert _parse_color_arg("rgb(300, 0, 0)") is None


def test_parse_color_arg_hue() -> None:
    result = _parse_color_arg("180")
    assert result is not None
    assert result.hue == 180

    result = _parse_color_arg("240deg")
    assert result is not None
    assert result.hue == 240


def test_parse_color_arg_invalid() -> None:
    assert _parse_color_arg("not_a_valid_color") is None
    assert _parse_color_arg("") is None
    assert _parse_color_arg("0xINVALID") is None


def test_show_true_color_full_spectrum(capsys: pytest.CaptureFixture[str]) -> None:
    show_true_color()
    captured = capsys.readouterr()
    assert "▄" in captured.out


def test_show_true_color_with_color(capsys: pytest.CaptureFixture[str]) -> None:
    show_true_color("#1E90FF")
    captured = capsys.readouterr()
    assert "▄" in captured.out


def test_show_true_color_with_invalid_color_fallback(capsys: pytest.CaptureFixture[str]) -> None:
    show_true_color("invalid_color")
    captured = capsys.readouterr()
    assert "▄" in captured.out
