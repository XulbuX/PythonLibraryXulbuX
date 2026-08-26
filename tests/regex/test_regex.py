from typing import cast
import regex as rx
import xulbux.regex as _regex_module
from xulbux.regex import LazyRegex
import pytest

# ******************************************************* MODULE TESTS ********************************************************


def test_regex_quotes_pattern():
    """Test quotes method returns correct pattern"""

    pattern = _regex_module.quotes()
    assert isinstance(pattern, str)
    assert "quote" in pattern
    assert "string" in pattern


def test_regex_quotes_single_quotes():
    """Test quotes pattern with single quotes"""

    text = "He said 'Hello world' and 'Goodbye'"
    pattern = _regex_module.quotes()
    matches = rx.findall(pattern, text)
    assert matches == [("'", "Hello world"), ("'", "Goodbye")]


def test_regex_quotes_double_quotes():
    """Test quotes pattern with double quotes"""

    text = 'She said "Hello world" and "Goodbye"'
    pattern = _regex_module.quotes()
    matches = rx.findall(pattern, text)
    assert matches == [('"', "Hello world"), ('"', "Goodbye")]


def test_regex_quotes_mixed_quotes():
    """Test quotes pattern with mixed quote types"""

    text = """He said 'Hello' and she said "World" and 'Another' string"""
    pattern = _regex_module.quotes()
    matches = rx.findall(pattern, text)
    assert matches == [("'", "Hello"), ('"', "World"), ("'", "Another")]


def test_regex_quotes_no_quotes():
    """Test quotes pattern with no quotes"""

    text = "No quotes in this string"
    pattern = _regex_module.quotes()
    matches = rx.findall(pattern, text)
    assert matches == []


def test_regex_quotes_empty_string():
    """Test quotes pattern with empty string"""

    pattern = _regex_module.quotes()
    matches = rx.findall(pattern, "")
    assert matches == []


def test_regex_quotes_escaped_quotes():
    """Test quotes pattern with escaped quotes"""

    text = r"He said \"Hello\" and 'World'"
    pattern = _regex_module.quotes()
    matches = rx.findall(pattern, text)
    assert len(matches) == 2
    assert ("'", "World") in matches


def test_regex_quotes_nested_quotes():
    """Test quotes pattern with nested quotes of different types"""

    text = """He said "She said 'Hello' to me" yesterday"""
    pattern = _regex_module.quotes()
    matches = rx.findall(pattern, text)
    assert matches == [('"', "She said 'Hello' to me")]


def test_regex_quotes_unclosed_quotes():
    """Test quotes pattern with unclosed quotes"""

    text = "He said 'Hello and never closed it"
    pattern = _regex_module.quotes()
    matches = rx.findall(pattern, text)
    assert matches == []


def test_regex_brackets_default():
    """Test brackets method with default parameters"""

    pattern = _regex_module.brackets()
    assert isinstance(pattern, str)


def test_regex_brackets_round_brackets():
    """Test brackets pattern with round brackets"""

    text = "Function call (parameter1, parameter2) and (another_call)"
    pattern = _regex_module.brackets()
    matches = rx.findall(pattern, text)
    assert matches == ["(parameter1, parameter2)", "(another_call)"]


def test_regex_brackets_square_brackets():
    """Test brackets pattern with square brackets"""

    text = "Array access [index] and [another_idx]"
    pattern = _regex_module.brackets("[", "]")
    matches = rx.findall(pattern, text)
    assert matches == ["[index]", "[another_idx]"]


def test_regex_brackets_curly_brackets():
    """Test brackets pattern with curly brackets"""

    text = "Dictionary {key: value} and {another: dict}"
    pattern = _regex_module.brackets("{", "}")
    matches = rx.findall(pattern, text)
    assert matches == ["{key: value}", "{another: dict}"]


def test_regex_brackets_nested_brackets():
    """Test brackets pattern with nested brackets"""

    text = "Nested [outer [inner] content] and (function(call))"
    pattern = _regex_module.brackets("[", "]")
    matches = rx.findall(pattern, text)
    assert matches == ["[outer [inner] content]"]

    matches_overlapped = rx.findall(pattern, text, overlapped=True)
    assert matches_overlapped == ["[outer [inner] content]", "[inner]"]

    pattern = _regex_module.brackets()
    matches = rx.findall(pattern, text)
    assert matches == ["(function(call))"]

    matches_overlapped = rx.findall(pattern, text, overlapped=True)
    assert matches_overlapped == ["(function(call))", "(call)"]


def test_regex_brackets_no_brackets():
    """Test brackets pattern with no brackets"""

    text = "No brackets in this string"
    pattern = _regex_module.brackets()
    matches = rx.findall(pattern, text)
    assert matches == []


def test_regex_brackets_empty_string():
    """Test brackets pattern with empty string"""

    pattern = _regex_module.brackets()
    matches = rx.findall(pattern, "")
    assert matches == []


def test_regex_brackets_empty_brackets():
    """Test brackets pattern with empty brackets"""

    text = "Empty () and [] and {} brackets"
    pattern = _regex_module.brackets()
    matches = rx.findall(pattern, text)
    assert matches == ["()"]
    pattern = _regex_module.brackets("[", "]")
    matches = rx.findall(pattern, text)
    assert matches == ["[]"]


def test_regex_brackets_with_strip_spaces():
    """Test brackets pattern with strip_spaces option"""

    text = "Function ( spaced content ) and (normal)"
    pattern = _regex_module.brackets(strip_spaces=True, is_group=True)
    matches = rx.findall(pattern, text)
    assert len(matches) == 2
    assert any("spaced content" in m for m in matches)
    assert "normal" in matches


def test_regex_brackets_as_group():
    """Test brackets pattern with is_group option"""

    text = "Function (content) here"
    pattern = _regex_module.brackets(is_group=True)
    match = rx.search(pattern, text)
    assert match is not None
    assert match.group(1) == "content"


def test_regex_brackets_ignore_in_strings():
    """Test brackets pattern with ignore_in_strings option"""

    text = 'fn(param = "f(x)")'
    pattern = _regex_module.brackets(ignore_in_strings=True)
    matches = rx.findall(pattern, text)
    assert len(matches) == 1
    assert 'param = "f(x)"' in matches[0]

    # Test that it correctly handles brackets inside strings:
    text2 = 'outer("inner(test)")'
    matches2 = rx.findall(pattern, text2)
    assert len(matches2) == 1
    assert "inner(test)" in matches2[0]


def test_regex_outside_strings_pattern():
    """Test outside_strings method returns correct pattern"""

    pattern = _regex_module.outside_strings()
    assert isinstance(pattern, str)
    assert ".*" in pattern


def test_regex_outside_strings_custom_pattern():
    """Test outside_strings with custom pattern"""

    pattern = _regex_module.outside_strings(r"\d+")
    text = 'Number 123 and "string 456" and 789'
    matches = rx.findall(pattern, text)
    assert "123" in matches
    assert "456" not in matches
    assert "789" in matches


def test_regex_outside_strings_with_special_chars():
    """Test outside_strings with special characters"""

    pattern = _regex_module.outside_strings(r"\$")
    text = 'Price $100 and "cost $50" and $200'
    matches = rx.findall(pattern, text)
    assert len(matches) >= 2


def test_regex_outside_strings_complex_pattern():
    """Test outside_strings with complex pattern"""

    pattern = _regex_module.outside_strings(r"[a-z]+")
    text = "word1 \"word2\" word3 'word4' word5"
    matches = rx.findall(pattern, text)
    assert len(matches) >= 3
    assert any("word" in match for match in matches)


def test_regex_all_except_pattern():
    """Test all_except method returns correct pattern"""

    pattern = _regex_module.all_except(">")
    assert isinstance(pattern, str)


def test_regex_all_except_basic():
    """Test all_except with basic pattern"""

    pattern = _regex_module.all_except(">")
    text = "Hello > World"
    match = rx.match(pattern, text)
    assert match is not None
    assert "Hello" in match.group(0)
    assert ">" not in match.group(0)


def test_regex_all_except_with_ignore():
    """Test all_except with ignore pattern"""

    pattern = _regex_module.all_except(">", "->")
    text = "Arrow -> here"
    match = rx.match(pattern, text)
    assert match is not None
    assert len(match.group(0)) > 0


def test_regex_all_except_as_group():
    """Test all_except with is_group option"""

    pattern = _regex_module.all_except(">", is_group=True)
    text = "Content > more"
    match = rx.match(pattern, text)
    assert match is not None
    assert match.group(1) is not None


def test_regex_func_call_pattern():
    """Test func_call method returns correct pattern"""

    pattern = _regex_module.func_call()
    assert isinstance(pattern, str)


def test_regex_func_call_any_function():
    """Test func_call pattern with any function"""

    text = "Call function1(arg1, arg2) and function2(arg3)"
    pattern = _regex_module.func_call()
    matches = rx.findall(pattern, text)
    assert matches == [("function1", "arg1, arg2"), ("function2", "arg3")]


def test_regex_func_call_specific_function():
    """Test func_call pattern with specific function name"""

    text = "Call print(hello) and input(prompt) and print(world)"
    pattern = _regex_module.func_call("print")
    matches = rx.findall(pattern, text)
    assert matches == [("print", "hello"), ("print", "world")]


def test_regex_rgba_str_pattern():
    """Test rgba_str method returns correct pattern"""

    pattern = _regex_module.rgba_str()
    assert isinstance(pattern, str)


def test_regex_rgba_str_default_separator():
    """Test rgba_str pattern with default comma separator"""

    text = "Color rgba(255, 128, 0) and (100, 200, 50, 0.5)"
    pattern = _regex_module.rgba_str()
    matches = rx.findall(pattern, text)
    assert len(matches) > 0
    assert len(matches) >= 2


def test_regex_rgba_str_valid_values():
    """Test rgba_str pattern validates correct ranges"""

    pattern = _regex_module.rgba_str()
    # Valid RGB values in a string:
    text = "Colors: rgba(255, 255, 255, 1.0) and rgb(0, 0, 0) and (128, 128, 128) and plain 255, 128, 0"
    matches = rx.findall(pattern, text)
    assert len(matches) >= 4, f"Should match all valid colors, got: {matches}"

    # Invalid RGB values (out of range) should not match or match partially:
    text_invalid = "Invalid: rgba(256, 128, 0) and rgb(300, 0, 0)"
    matches_invalid = rx.findall(pattern, text_invalid)

    # Should either not match or not include the invalid values:
    for match in matches_invalid:
        match_str = str(match)
        assert "256" not in match_str
        assert "300" not in match_str


def test_regex_rgba_str_no_alpha():
    """Test rgba_str pattern with alpha disabled"""

    pattern = _regex_module.rgba_str(allow_alpha=False)
    assert isinstance(pattern, str)


def test_regex_rgba_str_custom_separator():
    """Test rgba_str pattern with custom separator"""

    pattern = _regex_module.rgba_str(fix_sep="|")
    assert isinstance(pattern, str)
    assert "|" in pattern or "\\|" in pattern


def test_regex_hsla_str_pattern():
    """Test hsla_str method returns correct pattern"""

    pattern = _regex_module.hsla_str()
    assert isinstance(pattern, str)


def test_regex_hsla_str_default_separator():
    """Test hsla_str pattern with default comma separator"""

    text = "Color hsla(240, 100%, 50%) and (120, 80%, 60%, 0.8)"
    pattern = _regex_module.hsla_str()
    matches = rx.findall(pattern, text)
    assert len(matches) > 0


def test_regex_hsla_str_valid_values():
    """Test hsla_str pattern validates correct ranges"""

    pattern = _regex_module.hsla_str()
    # Valid HSL values in a string:
    text = (
        "Colors: hsla(360°, 100%, 50%, 1.0) and hsl(0, 0%, 0%) and (180, 50%, 50%) "
        "and plain 240, 100%, 50% and with degree 120°, 80%, 60%"
    )
    matches = rx.findall(pattern, text)
    assert len(matches) >= 5, f"Should match all valid colors, got: {matches}"

    # Verify that `%` and `°` symbols are not in the captured groups:
    for match in matches:
        groups = cast("tuple[str]", match if isinstance(match, tuple) else (match,))
        for group in groups:
            if group:  # Skip empty groups.
                assert "%" not in group, f"Percent sign should not be in captured group: {group}"
                assert "°" not in group, f"Degree sign should not be in captured group: {group}"

    # Invalid HSL values (out of range):
    text_invalid = "Invalid: hsla(361, 100%, 50%) and hsl(240, 101%, 50%)"
    matches_invalid = rx.findall(pattern, text_invalid)
    # Should either not match or not include the invalid values:
    for match in matches_invalid:
        match_str = str(match)
        assert "361" not in match_str
        assert "101" not in match_str


def test_regex_hsla_str_no_alpha():
    """Test hsla_str pattern with alpha disabled"""

    pattern = _regex_module.hsla_str(allow_alpha=False)
    assert isinstance(pattern, str)


def test_regex_hsla_str_custom_separator():
    """Test hsla_str pattern with custom separator"""

    pattern = _regex_module.hsla_str(fix_sep="|")
    assert isinstance(pattern, str)


def test_regex_hexa_str_pattern():
    """Test hexa_str method returns correct pattern"""

    pattern = _regex_module.hexa_str()
    assert isinstance(pattern, str)


def test_regex_hexa_str_with_alpha():
    """Test hexa_str pattern with alpha channel"""

    pattern = _regex_module.hexa_str(allow_alpha=True)
    text = "Colors: FF0000 and FF0000FF and F00 and F00F and #ABCDEF and 0xF0F in text"
    matches = rx.findall(pattern, text)
    assert len(matches) == 6, f"Should match all 6 colors, got: {matches}"
    # Verify all expected colors are captured (group 1 contains the hex value):
    expected = ["FF0000", "FF0000FF", "F00", "F00F", "ABCDEF", "F0F"]
    for exp in expected:
        assert any(exp.upper() == match.upper() for match in matches), f"Should match {exp}"


def test_regex_hexa_str_no_alpha():
    """Test hexa_str pattern without alpha channel"""

    pattern = _regex_module.hexa_str(allow_alpha=False)

    # Test valid colors (3 and 6 digit formats):
    text = "Valid colors: FF0000 and F00 and #ABCDEF and 0xABC in the text"
    matches = rx.findall(pattern, text)
    assert len(matches) == 4, f"Should match all 4 valid colors, got: {matches}"
    # The captured groups should not include prefix:
    for hex_value in matches:
        assert "#" not in hex_value
        assert "0x" not in hex_value.lower()

    # Test that 4-digit and 8-digit formats only partially match (first 3 or 6 chars):
    text_with_alpha = "With alpha: FF0000FF and F00F should only match the non-alpha part"
    matches_alpha = rx.findall(pattern, text_with_alpha)
    # Should match `FF0000` and `F00` (without the alpha channel):
    assert len(matches_alpha) == 2
    for hex_value in matches_alpha:
        assert len(hex_value) in [3, 6], f"Should only match 3 or 6 digit formats, got: {hex_value}"


def test_regex_hexa_str_with_prefix():
    """Test hexa_str pattern with optional prefixes"""

    pattern = _regex_module.hexa_str(allow_alpha=True)
    text = "Mixed: #FF0000 and 0xABCDEF and F00 and #F00F in text"
    matches = rx.findall(pattern, text)
    assert len(matches) == 4, f"Should match all 4 colors, got: {matches}"

    # Verify the captured hex values (without prefix):
    expected = ["FF0000", "ABCDEF", "F00", "F00F"]
    for exp in expected:
        assert any(exp.upper() == match.upper() for match in matches), f"Should capture {exp}"


def test_regex_func_call_nested():
    """Test func_call pattern with nested function calls"""

    text = "outer(inner(arg1, arg2), arg3)"
    pattern = _regex_module.func_call()
    matches = rx.findall(pattern, text)
    assert len(matches) >= 1
    func_names = [m[0] for m in matches]
    assert "outer" in func_names


def test_regex_quotes_with_escapes():
    """Test quotes pattern handles escaped characters properly"""

    text = r'He said "She said \"Hello\" to me"'
    pattern = _regex_module.quotes()
    matches = rx.findall(pattern, text)
    assert len(matches) >= 1


def test_regex_rgba_str_without_prefix():
    """Test rgba_str matches plain number format"""

    pattern = _regex_module.rgba_str()
    text = "255, 128, 0"
    match = rx.search(pattern, text)
    assert match is not None


def test_regex_hsla_str_without_prefix():
    """Test hsla_str matches plain number format"""

    pattern = _regex_module.hsla_str()
    text = "240, 100%, 50%"
    match = rx.search(pattern, text)
    assert match is not None


def test_regex_brackets_deeply_nested():
    """Test brackets pattern with deeply nested brackets"""

    text = "Level1(Level2(Level3(deepest)))"
    pattern = _regex_module.brackets()
    matches = rx.findall(pattern, text)
    assert len(matches) >= 1
    assert "deepest" in matches[0]
    assert "Level2" in matches[0]


# ****************************************************** LazyRegex TESTS ******************************************************


def test_lazy_regex_init():
    patterns = LazyRegex(test=r"\d+")
    assert patterns._patterns == {"test": r"\d+"}


def test_lazy_regex_getattr_valid():
    patterns = LazyRegex(test=r"\d+")
    regex = patterns.test
    assert regex.pattern == r"\d+"
    assert "test" in patterns.__dict__  # Check caching.


def test_lazy_regex_getattr_invalid():
    patterns = LazyRegex(test=r"\d+")
    with pytest.raises(AttributeError):
        _ = patterns.invalid


def test_lazy_regex_caching():
    patterns = LazyRegex(test=r"\d+")
    regex1 = patterns.test
    regex2 = patterns.test
    assert regex1 is regex2
