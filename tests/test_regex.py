from xulbux.regex import Regex

import regex as rx
import re


def test_regex_quotes_pattern():
    """Test quotes method returns correct pattern"""
    pattern = Regex.quotes()
    assert isinstance(pattern, str)
    assert "quote" in pattern
    assert "string" in pattern


def test_regex_quotes_single_quotes():
    """Test quotes pattern with single quotes"""
    text = "He said 'Hello world' and 'Goodbye'"
    pattern = Regex.quotes()
    matches = rx.findall(pattern, text)
    assert matches == [("'", "Hello world"), ("'", "Goodbye")]


def test_regex_quotes_double_quotes():
    """Test quotes pattern with double quotes"""
    text = 'She said "Hello world" and "Goodbye"'
    pattern = Regex.quotes()
    matches = rx.findall(pattern, text)
    assert matches == [('"', "Hello world"), ('"', "Goodbye")]


def test_regex_quotes_mixed_quotes():
    """Test quotes pattern with mixed quote types"""
    text = """He said 'Hello' and she said "World" and 'Another' string"""
    pattern = Regex.quotes()
    matches = rx.findall(pattern, text)
    assert matches == [("'", "Hello"), ('"', "World"), ("'", "Another")]


def test_regex_quotes_no_quotes():
    """Test quotes pattern with no quotes"""
    text = "No quotes in this string"
    pattern = Regex.quotes()
    matches = rx.findall(pattern, text)
    assert matches == []


def test_regex_quotes_empty_string():
    """Test quotes pattern with empty string"""
    pattern = Regex.quotes()
    matches = rx.findall(pattern, "")
    assert matches == []


def test_regex_quotes_escaped_quotes():
    """Test quotes pattern with escaped quotes"""
    text = r"He said \"Hello\" and 'World'"
    pattern = Regex.quotes()
    matches = rx.findall(pattern, text)
    assert len(matches) == 2
    assert ("'", "World") in matches


def test_regex_quotes_nested_quotes():
    """Test quotes pattern with nested quotes of different types"""
    text = '''He said "She said 'Hello' to me" yesterday'''
    pattern = Regex.quotes()
    matches = rx.findall(pattern, text)
    assert matches == [('"', "She said 'Hello' to me")]


def test_regex_quotes_unclosed_quotes():
    """Test quotes pattern with unclosed quotes"""
    text = "He said 'Hello and never closed it"
    pattern = Regex.quotes()
    matches = rx.findall(pattern, text)
    assert matches == []


def test_regex_brackets_default():
    """Test brackets method with default parameters"""
    pattern = Regex.brackets()
    assert isinstance(pattern, str)


def test_regex_brackets_round_brackets():
    """Test brackets pattern with round brackets"""
    text = "Function call (parameter1, parameter2) and (another_call)"
    pattern = Regex.brackets()
    matches = rx.findall(pattern, text)
    assert matches == ["(parameter1, parameter2)", "(another_call)"]


def test_regex_brackets_square_brackets():
    """Test brackets pattern with square brackets"""
    text = "Array access [index] and [another_index]"
    pattern = Regex.brackets("[", "]")
    matches = rx.findall(pattern, text)
    assert matches == ["[index]", "[another_index]"]


def test_regex_brackets_curly_brackets():
    """Test brackets pattern with curly brackets"""
    text = "Dictionary {key: value} and {another: dict}"
    pattern = Regex.brackets("{", "}")
    matches = rx.findall(pattern, text)
    assert matches == ["{key: value}", "{another: dict}"]


def test_regex_brackets_nested_brackets():
    """Test brackets pattern with nested brackets"""
    text = "Nested [outer [inner] content] and (function(call))"
    pattern = Regex.brackets("[", "]")
    matches = rx.findall(pattern, text)
    assert matches == ["[outer [inner] content]"]
    pattern = Regex.brackets()
    matches = rx.findall(pattern, text)
    assert matches == ["(function(call))"]


def test_regex_brackets_no_brackets():
    """Test brackets pattern with no brackets"""
    text = "No brackets in this string"
    pattern = Regex.brackets()
    matches = rx.findall(pattern, text)
    assert matches == []


def test_regex_brackets_empty_string():
    """Test brackets pattern with empty string"""
    pattern = Regex.brackets()
    matches = rx.findall(pattern, "")
    assert matches == []


def test_regex_brackets_empty_brackets():
    """Test brackets pattern with empty brackets"""
    text = "Empty () and [] and {} brackets"
    pattern = Regex.brackets()
    matches = rx.findall(pattern, text)
    assert matches == ["()"]
    pattern = Regex.brackets("[", "]")
    matches = rx.findall(pattern, text)
    assert matches == ["[]"]


def test_regex_brackets_with_strip_spaces():
    """Test brackets pattern with strip_spaces option"""
    text = "Function ( spaced content ) and (normal)"
    pattern = Regex.brackets(strip_spaces=True)
    matches = rx.findall(pattern, text)
    assert "( spaced content )" in matches
    assert "(normal)" in matches
    pattern = Regex.brackets(strip_spaces=False)
    matches = rx.findall(pattern, text)
    assert "( spaced content )" in matches
    assert "(normal)" in matches


def test_regex_brackets_as_group():
    """Test brackets pattern with is_group option"""
    text = "Function (content) here"
    pattern = Regex.brackets(is_group=True)
    match = rx.search(pattern, text)
    assert match is not None
    assert match.group(1) == "content"


def test_regex_outside_strings_pattern():
    """Test outside_strings method returns correct pattern"""
    pattern = Regex.outside_strings()
    assert isinstance(pattern, str)
    assert ".*" in pattern


def test_regex_outside_strings_custom_pattern():
    """Test outside_strings with custom pattern"""
    pattern = Regex.outside_strings(r"\d+")
    text = 'Number 123 and "string 456" and 789'
    matches = re.findall(pattern, text)
    assert "123" in matches
    assert "789" in matches
    assert "456" not in matches


def test_regex_all_except_pattern():
    """Test all_except method returns correct pattern"""
    pattern = Regex.all_except(">")
    assert isinstance(pattern, str)


def test_regex_all_except_with_ignore():
    """Test all_except with ignore pattern"""
    pattern = Regex.all_except(">", "->")
    assert isinstance(pattern, str)


def test_regex_all_except_as_group():
    """Test all_except with is_group option"""
    pattern = Regex.all_except(">", is_group=True)
    assert isinstance(pattern, str)


def test_regex_func_call_pattern():
    """Test func_call method returns correct pattern"""
    pattern = Regex.func_call()
    assert isinstance(pattern, str)


def test_regex_func_call_any_function():
    """Test func_call pattern with any function"""
    text = "Call function1(arg1, arg2) and function2(arg3)"
    pattern = Regex.func_call()
    matches = rx.findall(pattern, text)
    assert matches == [("function1", "arg1, arg2"), ("function2", "arg3")]


def test_regex_func_call_specific_function():
    """Test func_call pattern with specific function name"""
    text = "Call print(hello) and input(prompt) and print(world)"
    pattern = Regex.func_call("print")
    matches = rx.findall(pattern, text)
    assert matches == [("print", "hello"), ("print", "world")]


def test_regex_rgba_str_pattern():
    """Test rgba_str method returns correct pattern"""
    pattern = Regex.rgba_str()
    assert isinstance(pattern, str)


def test_regex_rgba_str_default_separator():
    """Test rgba_str pattern with default comma separator"""
    text = "Color rgba(255, 128, 0) and (100, 200, 50, 0.5)"
    pattern = Regex.rgba_str()
    matches = re.findall(pattern, text, re.IGNORECASE | re.VERBOSE)
    assert len(matches) > 0


def test_regex_rgba_str_no_alpha():
    """Test rgba_str pattern with alpha disabled"""
    pattern = Regex.rgba_str(allow_alpha=False)
    assert isinstance(pattern, str)


def test_regex_rgba_str_custom_separator():
    """Test rgba_str pattern with custom separator"""
    pattern = Regex.rgba_str(fix_sep="|")
    assert isinstance(pattern, str)
    assert "|" in pattern or "\\|" in pattern


def test_regex_hsla_str_pattern():
    """Test hsla_str method returns correct pattern"""
    pattern = Regex.hsla_str()
    assert isinstance(pattern, str)


def test_regex_hsla_str_default_separator():
    """Test hsla_str pattern with default comma separator"""
    text = "Color hsla(240, 100%, 50%) and (120, 80%, 60%, 0.8)"
    pattern = Regex.hsla_str()
    matches = re.findall(pattern, text, re.IGNORECASE | re.VERBOSE)
    assert len(matches) > 0


def test_regex_hsla_str_no_alpha():
    """Test hsla_str pattern with alpha disabled"""
    pattern = Regex.hsla_str(allow_alpha=False)
    assert isinstance(pattern, str)


def test_regex_hsla_str_custom_separator():
    """Test hsla_str pattern with custom separator"""
    pattern = Regex.hsla_str(fix_sep="|")
    assert isinstance(pattern, str)


def test_regex_hexa_str_pattern():
    """Test hexa_str method returns correct pattern"""
    pattern = Regex.hexa_str()
    assert isinstance(pattern, str)


def test_regex_hexa_str_with_alpha():
    """Test hexa_str pattern with alpha channel"""
    pattern = Regex.hexa_str(allow_alpha=True)
    test_colors = ["FF0000", "FF0000FF", "F00", "F00F"]
    for color in test_colors:
        assert re.match(pattern, color) is not None


def test_regex_hexa_str_no_alpha():
    """Test hexa_str pattern without alpha channel"""
    pattern = Regex.hexa_str(allow_alpha=False)
    valid_colors = ["FF0000", "F00"]
    invalid_colors = ["FF0000FF", "F00F"]

    for color in valid_colors:
        match = re.match(pattern, color)
        assert match is not None
        assert match.group() == color

    for color in invalid_colors:
        match = re.match(pattern, color)
        if match: assert match.group() != color
