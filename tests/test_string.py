import math
import xulbux.string as _string_module
import pytest

# ******************************************************* MODULE TESTS ********************************************************


def test_to_type():
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
    assert _string_module.to_type("  {'key': [1, 'val']}  ") == {"key": [1, "val"]}
    assert _string_module.to_type("invalid { structure") == "invalid { structure"


def test_normalize_spaces():
    assert _string_module.normalize_spaces("Hello\tWorld") == "Hello    World"
    assert _string_module.normalize_spaces("Hello\tWorld", tab_spaces=2) == "Hello  World"
    assert _string_module.normalize_spaces("Spaces:\u2000\u2001\u2002\u2003!") == "Spaces:    !"
    assert _string_module.normalize_spaces("Mix:\t\u2004 and normal") == "Mix:      and normal"
    assert _string_module.normalize_spaces("No special spaces") == "No special spaces"


def test_escape():
    assert _string_module.escape("Line 1\nLine 2\tTabbed") == r"Line 1\nLine 2\tTabbed"
    assert _string_module.escape("Path: C:\\Users\\Name") == r"Path: C:\\Users\\Name"
    # Default: no escaping quotes:
    assert _string_module.escape('String with "double quotes"') == 'String with "double quotes"'
    assert _string_module.escape("String with 'single quotes'") == "String with 'single quotes'"
    assert (
        _string_module.escape("Mix: \n \"quotes\" and 'single' \t tabs \\ backslash")
        == r"""Mix: \n "quotes" and 'single' \t tabs \\ backslash"""
    )
    # Escape double quotes:
    assert _string_module.escape('String with "double quotes"', str_quotes='"') == r"String with \"double quotes\""
    assert _string_module.escape("String with 'single quotes'", str_quotes='"') == r"String with 'single quotes'"
    assert (
        _string_module.escape("Mix: \n \"quotes\" and 'single' \t tabs \\ backslash", str_quotes='"')
        == r"Mix: \n \"quotes\" and 'single' \t tabs \\ backslash"
    )
    # Escape single quotes:
    assert _string_module.escape('String with "double quotes"', str_quotes="'") == r'String with "double quotes"'
    assert _string_module.escape("String with 'single quotes'", str_quotes="'") == r"String with \'single quotes\'"
    assert (
        _string_module.escape("Mix: \n \"quotes\" and 'single' \t tabs \\ backslash", str_quotes="'")
        == r'Mix: \n "quotes" and \'single\' \t tabs \\ backslash'
    )


def test_is_empty():
    assert _string_module.is_empty(None) is True
    assert _string_module.is_empty("") is True
    assert _string_module.is_empty("   ") is False
    assert _string_module.is_empty("   ", spaces_are_empty=True) is True
    assert _string_module.is_empty("Not Empty") is False
    assert _string_module.is_empty(" Not Empty ", spaces_are_empty=True) is False


def test_single_char_repeats():
    assert _string_module.single_char_repeats("-----", "-") == 5
    assert _string_module.single_char_repeats("", "a") == 0
    assert _string_module.single_char_repeats("a", "a") == 1
    assert _string_module.single_char_repeats("aaaaa", "a") == 5
    assert _string_module.single_char_repeats("aaaba", "a") == 0
    assert _string_module.single_char_repeats("abcde", "a") == 0
    assert _string_module.single_char_repeats("bbbbb", "a") == 0


def test_decompose():
    assert _string_module.decompose("camelCaseString") == ["camel", "case", "string"]
    assert _string_module.decompose("PascalCaseString") == ["pascal", "case", "string"]
    assert _string_module.decompose("snake_case_string") == ["snake", "case", "string"]
    assert _string_module.decompose("kebab-case-string") == ["kebab", "case", "string"]
    assert _string_module.decompose("SCREAMING_SNAKE_CASE") == ["screaming", "snake", "case"]
    assert _string_module.decompose("mixed_Case-StringExample") == ["mixed", "case", "string", "example"]
    assert _string_module.decompose("string") == ["string"]
    assert _string_module.decompose("stringWith1Number") == ["string", "with1number"]
    assert _string_module.decompose("version2_0", seps="_.") == ["version2", "0"]
    assert _string_module.decompose("PascalCase", lower_all=False) == ["Pascal", "Case"]
    assert _string_module.decompose("snake_case", lower_all=False) == ["snake", "case"]
    assert _string_module.decompose("mixed_Case", lower_all=False) == ["mixed", "Case"]


def test_to_camel_case():
    assert _string_module.to_camel_case("snake_case_string") == "SnakeCaseString"
    assert _string_module.to_camel_case("kebab-case-string") == "KebabCaseString"
    assert _string_module.to_camel_case("PascalCaseString") == "PascalCaseString"
    assert _string_module.to_camel_case("camelCaseString") == "CamelCaseString"
    assert _string_module.to_camel_case("SCREAMING_SNAKE_CASE") == "ScreamingSnakeCase"
    assert _string_module.to_camel_case("mixed_Case-StringExample") == "MixedCaseStringExample"
    assert _string_module.to_camel_case("string") == "String"

    assert _string_module.to_camel_case("snake_case_string", upper=False) == "snakeCaseString"
    assert _string_module.to_camel_case("kebab-case-string", upper=False) == "kebabCaseString"
    assert _string_module.to_camel_case("PascalCaseString", upper=False) == "pascalCaseString"
    assert _string_module.to_camel_case("camelCaseString", upper=False) == "camelCaseString"
    assert _string_module.to_camel_case("SCREAMING_SNAKE_CASE", upper=False) == "screamingSnakeCase"
    assert _string_module.to_camel_case("mixed_Case-StringExample", upper=False) == "mixedCaseStringExample"
    assert _string_module.to_camel_case("string", upper=False) == "string"


def test_to_delimited_case():
    assert _string_module.to_delimited_case("camelCaseString") == "camel_case_string"
    assert _string_module.to_delimited_case("PascalCaseString") == "pascal_case_string"
    assert _string_module.to_delimited_case("snake_case_string") == "snake_case_string"
    assert _string_module.to_delimited_case("kebab-case-string") == "kebab_case_string"
    assert _string_module.to_delimited_case("SCREAMING_SNAKE_CASE") == "screaming_snake_case"
    assert _string_module.to_delimited_case("mixed_Case-StringExample") == "mixed_case_string_example"
    assert _string_module.to_delimited_case("string") == "string"

    assert _string_module.to_delimited_case("camelCaseString", delimiter="-") == "camel-case-string"
    assert _string_module.to_delimited_case("PascalCaseString", delimiter="-") == "pascal-case-string"

    assert _string_module.to_delimited_case("camelCaseString", screaming=True) == "CAMEL_CASE_STRING"
    assert _string_module.to_delimited_case("PascalCaseString", screaming=True) == "PASCAL_CASE_STRING"
    assert _string_module.to_delimited_case("snake_case_string", screaming=True) == "SNAKE_CASE_STRING"

    assert _string_module.to_delimited_case("camelCaseString", delimiter="-", screaming=True) == "CAMEL-CASE-STRING"


def test_get_lines():
    assert _string_module.get_lines("Line 1\nLine 2\nLine 3") == ["Line 1", "Line 2", "Line 3"]
    assert _string_module.get_lines("Line 1\r\nLine 2\rLine 3") == ["Line 1", "Line 2", "Line 3"]
    assert _string_module.get_lines("Line 1\n\nLine 3") == ["Line 1", "", "Line 3"]
    assert _string_module.get_lines("Line 1\n \nLine 3") == ["Line 1", " ", "Line 3"]
    assert _string_module.get_lines("") == []
    assert _string_module.get_lines("\n") == [""]

    assert _string_module.get_lines("Line 1\n\nLine 3", remove_empty_lines=True) == ["Line 1", "Line 3"]
    assert _string_module.get_lines("Line 1\n \nLine 3", remove_empty_lines=True) == ["Line 1", "Line 3"]
    assert _string_module.get_lines("\nLine 1\n  \nLine 3\n", remove_empty_lines=True) == ["Line 1", "Line 3"]
    assert _string_module.get_lines("\n\n\n", remove_empty_lines=True) == []
    assert _string_module.get_lines("Only text") == ["Only text"]
    assert _string_module.get_lines("Only text", remove_empty_lines=True) == ["Only text"]


def test_remove_consecutive_empty_lines():
    assert _string_module.remove_consecutive_empty_lines("Line 1\n\n\nLine 2") == "Line 1\nLine 2"
    assert _string_module.remove_consecutive_empty_lines("Line 1\n\nLine 2\n\n\n\nLine 3") == "Line 1\nLine 2\nLine 3"
    assert _string_module.remove_consecutive_empty_lines("\n\nStart\n\n\nEnd\n\n") == "\nStart\nEnd\n"
    assert _string_module.remove_consecutive_empty_lines("Line 1\nLine 2") == "Line 1\nLine 2"
    assert _string_module.remove_consecutive_empty_lines("") == ""
    assert _string_module.remove_consecutive_empty_lines("\n\n\n") == "\n"

    assert _string_module.remove_consecutive_empty_lines("Line 1\n\n\nLine 2", max_consecutive=1) == "Line 1\n\nLine 2"
    assert (
        _string_module.remove_consecutive_empty_lines("Line 1\n\nLine 2\n\n\n\nLine 3", max_consecutive=1)
        == "Line 1\n\nLine 2\n\nLine 3"
    )
    assert _string_module.remove_consecutive_empty_lines("Line 1\n\n\n\nLine 2", max_consecutive=2) == "Line 1\n\n\nLine 2"
    assert _string_module.remove_consecutive_empty_lines("\n\n\n\n", max_consecutive=1) == "\n\n"
    assert _string_module.remove_consecutive_empty_lines("\n\n\n\n", max_consecutive=0) == "\n"


def test_split_count():
    assert _string_module.split_count("abcdefghi", 3) == ["abc", "def", "ghi"]
    assert _string_module.split_count("abcdefgh", 3) == ["abc", "def", "gh"]
    assert _string_module.split_count("abc", 3) == ["abc"]
    assert _string_module.split_count("abc", 5) == ["abc"]
    assert _string_module.split_count("", 3) == []
    with pytest.raises(ValueError):
        _string_module.split_count("abc", 0)
    assert _string_module.split_count("abcdef", 1) == ["a", "b", "c", "d", "e", "f"]
