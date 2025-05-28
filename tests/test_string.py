from xulbux import String

import pytest


def test_to_type():
    assert String.to_type("123") == 123
    assert String.to_type("123.45") == 123.45
    assert String.to_type("True") is True
    assert String.to_type("False") is False
    assert String.to_type("None") is None
    assert String.to_type("'hello'") == "hello"
    assert String.to_type('"world"') == "world"
    assert String.to_type("[1, 2, 3]") == [1, 2, 3]
    assert String.to_type("{'a': 1, 'b': 2}") == {"a": 1, "b": 2}
    assert String.to_type('{"c": [3, 4], "d": null}') == {"c": [3, 4], "d": None}
    assert String.to_type("(1, 'two', 3.0)") == (1, "two", 3.0)
    assert String.to_type("just a string") == "just a string"
    assert String.to_type("  {'key': [1, 'val']}  ") == {'key': [1, 'val']}
    assert String.to_type("invalid { structure") == "invalid { structure"


def test_normalize_spaces():
    assert String.normalize_spaces("Hello\tWorld") == "Hello    World"
    assert String.normalize_spaces("Hello\tWorld", tab_spaces=2) == "Hello  World"
    assert String.normalize_spaces("Spaces:\u2000\u2001\u2002\u2003!") == "Spaces:    !"
    assert String.normalize_spaces("Mix:\t\u2004 and normal") == "Mix:      and normal"
    assert String.normalize_spaces("No special spaces") == "No special spaces"


def test_escape():
    assert String.escape("Line 1\nLine 2\tTabbed") == r"Line 1\nLine 2\tTabbed"
    assert String.escape('Path: C:\\Users\\Name') == r"Path: C:\\Users\\Name"
    assert String.escape('String with "double quotes"') == r'String with \"double quotes\"'
    assert String.escape("String with 'single quotes'") == r"String with 'single quotes'"
    assert String.escape('String with "double quotes"', str_quotes="'") == r'String with "double quotes"'
    assert String.escape("String with 'single quotes'", str_quotes="'") == r"String with \'single quotes\'"
    assert String.escape(
        "Mix: \n \"quotes\" and 'single' \t tabs \\ backslash"
    ) == r"Mix: \n \"quotes\" and 'single' \t tabs \\ backslash"
    assert String.escape(
        "Mix: \n \"quotes\" and 'single' \t tabs \\ backslash", str_quotes="'"
    ) == r'Mix: \n "quotes" and \'single\' \t tabs \\ backslash'


def test_is_empty():
    assert String.is_empty(None) is True  # type: ignore[assignment]
    assert String.is_empty("") is True
    assert String.is_empty("   ") is False
    assert String.is_empty("   ", spaces_are_empty=True) is True
    assert String.is_empty("Not Empty") is False
    assert String.is_empty(" Not Empty ", spaces_are_empty=True) is False
    assert String.is_empty(123) is False  # type: ignore[assignment]
    assert String.is_empty([]) is False  # type: ignore[assignment]


def test_single_char_repeats():
    assert String.single_char_repeats("aaaaa", "a") == 5
    assert String.single_char_repeats("-----", "-") == 5
    assert String.single_char_repeats("bbbbb", "a") is False
    assert String.single_char_repeats("abcde", "a") is False
    assert String.single_char_repeats("", "a") == 0
    assert String.single_char_repeats("a", "a") == 1
    assert String.single_char_repeats("aaaba", "a") is False


def test_decompose():
    assert String.decompose("camelCaseString") == ["camel", "case", "string"]
    assert String.decompose("PascalCaseString") == ["pascal", "case", "string"]
    assert String.decompose("snake_case_string") == ["snake", "case", "string"]
    assert String.decompose("kebab-case-string") == ["kebab", "case", "string"]
    assert String.decompose("SCREAMING_SNAKE_CASE") == ["screaming", "snake", "case"]
    assert String.decompose("mixed_Case-StringExample") == ["mixed", "case", "string", "example"]
    assert String.decompose("string") == ["string"]
    assert String.decompose("stringWith1Number") == ["string", "with1number"]
    assert String.decompose("version2_0", seps="_.") == ["version2", "0"]
    assert String.decompose("PascalCase", lower_all=False) == ["Pascal", "Case"]
    assert String.decompose("snake_case", lower_all=False) == ["snake", "case"]
    assert String.decompose("mixed_Case", lower_all=False) == ["mixed", "Case"]


def test_to_camel_case():
    assert String.to_camel_case("snake_case_string") == "SnakeCaseString"
    assert String.to_camel_case("kebab-case-string") == "KebabCaseString"
    assert String.to_camel_case("PascalCaseString") == "PascalCaseString"
    assert String.to_camel_case("camelCaseString") == "CamelCaseString"
    assert String.to_camel_case("SCREAMING_SNAKE_CASE") == "ScreamingSnakeCase"
    assert String.to_camel_case("mixed_Case-StringExample") == "MixedCaseStringExample"
    assert String.to_camel_case("string") == "String"

    assert String.to_camel_case("snake_case_string", upper=False) == "snakeCaseString"
    assert String.to_camel_case("kebab-case-string", upper=False) == "kebabCaseString"
    assert String.to_camel_case("PascalCaseString", upper=False) == "pascalCaseString"
    assert String.to_camel_case("camelCaseString", upper=False) == "camelCaseString"
    assert String.to_camel_case("SCREAMING_SNAKE_CASE", upper=False) == "screamingSnakeCase"
    assert String.to_camel_case("mixed_Case-StringExample", upper=False) == "mixedCaseStringExample"
    assert String.to_camel_case("string", upper=False) == "string"


def test_to_delimited_case():
    assert String.to_delimited_case("camelCaseString") == "camel_case_string"
    assert String.to_delimited_case("PascalCaseString") == "pascal_case_string"
    assert String.to_delimited_case("snake_case_string") == "snake_case_string"
    assert String.to_delimited_case("kebab-case-string") == "kebab_case_string"
    assert String.to_delimited_case("SCREAMING_SNAKE_CASE") == "screaming_snake_case"
    assert String.to_delimited_case("mixed_Case-StringExample") == "mixed_case_string_example"
    assert String.to_delimited_case("string") == "string"

    assert String.to_delimited_case("camelCaseString", delimiter="-") == "camel-case-string"
    assert String.to_delimited_case("PascalCaseString", delimiter="-") == "pascal-case-string"

    assert String.to_delimited_case("camelCaseString", screaming=True) == "CAMEL_CASE_STRING"
    assert String.to_delimited_case("PascalCaseString", screaming=True) == "PASCAL_CASE_STRING"
    assert String.to_delimited_case("snake_case_string", screaming=True) == "SNAKE_CASE_STRING"

    assert String.to_delimited_case("camelCaseString", delimiter="-", screaming=True) == "CAMEL-CASE-STRING"


def test_get_lines():
    assert String.get_lines("Line 1\nLine 2\nLine 3") == ["Line 1", "Line 2", "Line 3"]
    assert String.get_lines("Line 1\r\nLine 2\rLine 3") == ["Line 1", "Line 2", "Line 3"]
    assert String.get_lines("Line 1\n\nLine 3") == ["Line 1", "", "Line 3"]
    assert String.get_lines("Line 1\n \nLine 3") == ["Line 1", " ", "Line 3"]
    assert String.get_lines("") == []
    assert String.get_lines("\n") == [""]

    assert String.get_lines("Line 1\n\nLine 3", remove_empty_lines=True) == ["Line 1", "Line 3"]
    assert String.get_lines("Line 1\n \nLine 3", remove_empty_lines=True) == ["Line 1", "Line 3"]
    assert String.get_lines("\nLine 1\n  \nLine 3\n", remove_empty_lines=True) == ["Line 1", "Line 3"]
    assert String.get_lines("\n\n\n", remove_empty_lines=True) == []
    assert String.get_lines("Only text") == ["Only text"]
    assert String.get_lines("Only text", remove_empty_lines=True) == ["Only text"]


def test_remove_consecutive_empty_lines():
    assert String.remove_consecutive_empty_lines("Line 1\n\n\nLine 2") == "Line 1\nLine 2"
    assert String.remove_consecutive_empty_lines("Line 1\n\nLine 2\n\n\n\nLine 3") == "Line 1\nLine 2\nLine 3"
    assert String.remove_consecutive_empty_lines("\n\nStart\n\n\nEnd\n\n") == "\nStart\nEnd\n"
    assert String.remove_consecutive_empty_lines("Line 1\nLine 2") == "Line 1\nLine 2"
    assert String.remove_consecutive_empty_lines("") == ""
    assert String.remove_consecutive_empty_lines("\n\n\n") == "\n"

    assert String.remove_consecutive_empty_lines("Line 1\n\n\nLine 2", max_consecutive=1) == "Line 1\n\nLine 2"
    assert String.remove_consecutive_empty_lines(
        "Line 1\n\nLine 2\n\n\n\nLine 3", max_consecutive=1
    ) == "Line 1\n\nLine 2\n\nLine 3"
    assert String.remove_consecutive_empty_lines("Line 1\n\n\n\nLine 2", max_consecutive=2) == "Line 1\n\n\nLine 2"
    assert String.remove_consecutive_empty_lines("\n\n\n\n", max_consecutive=1) == "\n\n"
    assert String.remove_consecutive_empty_lines("\n\n\n\n", max_consecutive=0) == "\n"


def test_split_count():
    assert String.split_count("abcdefghi", 3) == ["abc", "def", "ghi"]
    assert String.split_count("abcdefgh", 3) == ["abc", "def", "gh"]
    assert String.split_count("abc", 3) == ["abc"]
    assert String.split_count("abc", 5) == ["abc"]
    assert String.split_count("", 3) == []
    with pytest.raises(ValueError):
        String.split_count("abc", 0)
    assert String.split_count("abcdef", 1) == ["a", "b", "c", "d", "e", "f"]
