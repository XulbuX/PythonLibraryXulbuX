import math
import xulbux.string as _string_module
import pytest


def test_to_type_conversions() -> None:
    assert _string_module.to_type("123") == 123
    assert math.isclose(_string_module.to_type("123.45"), 123.45)
    assert _string_module.to_type("True") is True
    assert _string_module.to_type("False") is False
    assert _string_module.to_type("None") is None
    assert _string_module.to_type("'hello'") == "hello"
    assert _string_module.to_type('"world"') == "world"
    assert _string_module.to_type("[1, 2, 3]") == [1, 2, 3]
    assert _string_module.to_type("{'a': 1, 'b': 2}") == {"a": 1, "b": 2}
    assert _string_module.to_type('{"c": [3, 4], "d": null}') == {"c": [3, 4], "d": None}
    assert _string_module.to_type("(1, 'two', 3.0)") == (1, "two", 3.0)
    assert _string_module.to_type("just a string") == "just a string"
    assert _string_module.to_type("invalid { structure") == "invalid { structure"


def test_normalize_spaces() -> None:
    assert _string_module.normalize_spaces("Hello\tWorld") == "Hello    World"
    assert _string_module.normalize_spaces("Hello\tWorld", tab_spaces=2) == "Hello  World"
    assert _string_module.normalize_spaces("Spaces:\u2000\u2001\u2002\u2003!") == "Spaces:    !"
    assert _string_module.normalize_spaces("No special spaces") == "No special spaces"

    with pytest.raises(ValueError, match="must be non-negative"):
        _string_module.normalize_spaces("text", -1)


def test_escape() -> None:
    assert _string_module.escape("Line 1\nLine 2\tTabbed") == r"Line 1\nLine 2\tTabbed"
    assert _string_module.escape("Path: C:\\Users\\Name") == r"Path: C:\\Users\\Name"

    assert _string_module.escape('String with "double quotes"') == 'String with "double quotes"'
    assert _string_module.escape('String with "double quotes"', str_quotes='"') == r"String with \"double quotes\""
    assert _string_module.escape("String with 'single quotes'", str_quotes="'") == r"String with \'single quotes\'"
    assert _string_module.escape("String without quotes", str_quotes=None) == "String without quotes"


def test_is_empty() -> None:
    assert _string_module.is_empty(None) is True
    assert _string_module.is_empty("") is True
    assert _string_module.is_empty("   ") is False
    assert _string_module.is_empty("   ", spaces_are_empty=True) is True
    assert _string_module.is_empty("Not Empty") is False
    assert _string_module.is_empty(" Not Empty ", spaces_are_empty=True) is False


def test_count_char_repeats() -> None:
    assert _string_module.count_char_repeats("-----", "-") == 5
    assert _string_module.count_char_repeats("", "a") == 0
    assert _string_module.count_char_repeats("a", "a") == 1
    assert _string_module.count_char_repeats("aaaaa", "a") == 5
    assert _string_module.count_char_repeats("aaaba", "a") == 0

    with pytest.raises(ValueError, match="must be a single character"):
        _string_module.count_char_repeats("test", "ab")

    with pytest.raises(ValueError, match="must be a single character"):
        _string_module.count_char_repeats("test", "")


def test_get_lines() -> None:
    assert _string_module.get_lines("Line 1\nLine 2\nLine 3") == ["Line 1", "Line 2", "Line 3"]
    assert _string_module.get_lines("Line 1\r\nLine 2\rLine 3") == ["Line 1", "Line 2", "Line 3"]
    assert _string_module.get_lines("Line 1\n\nLine 3") == ["Line 1", "", "Line 3"]
    assert _string_module.get_lines("") == []

    assert _string_module.get_lines("Line 1\n\nLine 3", remove_empty_lines=True) == ["Line 1", "Line 3"]
    assert _string_module.get_lines("\n\n\n", remove_empty_lines=True) == []
    assert _string_module.get_lines("Only text", remove_empty_lines=True) == ["Only text"]


def test_remove_consecutive_empty_lines() -> None:
    assert _string_module.remove_consecutive_empty_lines("Line 1\n\n\nLine 2") == "Line 1\nLine 2"
    assert _string_module.remove_consecutive_empty_lines("Line 1\n\n\nLine 2", max_consecutive=1) == "Line 1\n\nLine 2"
    assert _string_module.remove_consecutive_empty_lines("") == ""

    with pytest.raises(ValueError, match="must be non-negative"):
        _string_module.remove_consecutive_empty_lines("test", -1)


def test_chunk() -> None:
    assert _string_module.chunk("abcdefghi", 3) == ["abc", "def", "ghi"]
    assert _string_module.chunk("abcdefgh", 3) == ["abc", "def", "gh"]
    assert _string_module.chunk("abc", 3) == ["abc"]
    assert _string_module.chunk("", 3) == []

    with pytest.raises(ValueError, match="must be a positive integer"):
        _string_module.chunk("abc", 0)

    with pytest.raises(ValueError, match="must be a positive integer"):
        _string_module.chunk("abc", -1)
