import xulbux.code as _code_module
import pytest


def test_add_indent_with_valid_spaces() -> None:
    sample = "def hello():\n    return 'Hello, World!'"
    expected = "    def hello():\n        return 'Hello, World!'"
    assert _code_module.add_indent(sample, 4) == expected
    assert _code_module.add_indent("", 4) == ""


def test_add_indent_with_negative_spaces_raises_value_error() -> None:
    with pytest.raises(ValueError, match="must be non-negative"):
        _code_module.add_indent("code", -1)


def test_get_tab_spaces_detection() -> None:
    sample_four = "def test():\n    print('test')\n    if True:\n        print('nested')"
    assert _code_module.get_tab_spaces(sample_four) == 4

    sample_two = "def test():\n  print('test')\n  if True:\n    print('nested')"
    assert _code_module.get_tab_spaces(sample_two) == 2

    assert _code_module.get_tab_spaces("") == 0
    assert _code_module.get_tab_spaces("no_indent_here\nstill_none") == 0


def test_change_tab_size_rescaling() -> None:
    sample = "def test():\n  print('test')\n  if True:\n    print('nested')"
    expected = "def test():\n    print('test')\n    if True:\n        print('nested')"
    assert _code_module.change_tab_size(sample, 4) == expected


def test_change_tab_size_when_tab_size_matches_or_zero() -> None:
    sample_same = "def test():\n    print('test')"
    assert _code_module.change_tab_size(sample_same, 4) == sample_same

    sample_unindented = "def test():\nprint('test')"
    assert _code_module.change_tab_size(sample_unindented, 4) == sample_unindented


def test_change_tab_size_with_remove_empty_lines() -> None:
    sample = "def test():\n\n  print('test')"
    expected = "def test():\n    print('test')"
    assert _code_module.change_tab_size(sample, 4, remove_empty_lines=True) == expected

    sample_same = "def test():\n\n    print('test')"
    expected_same = "def test():\n    print('test')"
    assert _code_module.change_tab_size(sample_same, 4, remove_empty_lines=True) == expected_same


def test_change_tab_size_with_negative_size_raises_value_error() -> None:
    with pytest.raises(ValueError, match="must be non-negative"):
        _code_module.change_tab_size("code", -1)
