import xulbux.regex as _regex_module
import regex as rx


def test_quotes_matching_single_and_double():
    pattern = _regex_module.quotes()
    text = """He said 'Hello' and "World" and 'Another' string"""
    matches = rx.findall(pattern, text)
    assert matches == [("'", "Hello"), ('"', "World"), ("'", "Another")]
    assert rx.findall(pattern, "No quotes here") == []
    assert rx.findall(pattern, "") == []


def test_quotes_nested_and_escaped():
    text = r'He said "She said \"Hello\" to me"'
    pattern = _regex_module.quotes()
    matches = rx.findall(pattern, text)
    assert len(matches) >= 1
    assert rx.findall(pattern, "Unclosed 'quote") == []


def test_brackets_standard_delimiters():
    pattern_round = _regex_module.brackets()
    text_round = "Call fn(param1, param2) and fn(other)"
    assert rx.findall(pattern_round, text_round) == ["(param1, param2)", "(other)"]

    pattern_square = _regex_module.brackets("[", "]")
    text_square = "Items [1, 2] and [3, 4]"
    assert rx.findall(pattern_square, text_square) == ["[1, 2]", "[3, 4]"]

    pattern_curly = _regex_module.brackets("{", "}")
    text_curly = "Dict {a: 1} and {b: 2}"
    assert rx.findall(pattern_curly, text_curly) == ["{a: 1}", "{b: 2}"]


def test_brackets_options_group_spaces_and_strings():
    pattern_group = _regex_module.brackets(is_group=True)
    match_group = rx.search(pattern_group, "fn(content)")
    assert match_group is not None
    assert match_group.group(1) == "content"

    pattern_spaced = _regex_module.brackets(strip_spaces=True, is_group=True)
    matches_spaced = rx.findall(pattern_spaced, "fn( spaced content )")
    assert len(matches_spaced) == 1

    pattern_strings_ignored = _regex_module.brackets(ignore_in_strings=True)
    assert len(rx.findall(pattern_strings_ignored, 'fn("param(x)")')) == 1

    pattern_strings_not_ignored = _regex_module.brackets(ignore_in_strings=False)
    assert len(rx.findall(pattern_strings_not_ignored, 'fn("param(x)")')) >= 1

    pattern_multichar_bracket = _regex_module.brackets("<<", ">>")
    assert rx.findall(pattern_multichar_bracket, "custom <<content>>") == ["<<content>>"]


def test_outside_strings():
    pattern = _regex_module.outside_strings(r"\d+")
    text = 'Number 123 and "string 456" and 789'
    matches = rx.findall(pattern, text)
    assert "123" in matches
    assert "456" not in matches
    assert "789" in matches

    default_pattern = _regex_module.outside_strings()
    assert isinstance(default_pattern, str)


def test_all_except_with_and_without_ignore():
    pattern = _regex_module.all_except(">")
    match = rx.match(pattern, "Hello > World")
    assert match is not None
    assert "Hello" in match.group(0)
    assert ">" not in match.group(0)

    pattern_with_ignore = _regex_module.all_except(">", "->", is_group=True)
    match_with_ignore = rx.match(pattern_with_ignore, "Content without greater sign")
    assert match_with_ignore is not None
    assert match_with_ignore.group(1) == "Content without greater sign"


def test_func_call_any_and_specific():
    pattern_any = _regex_module.func_call()
    matches_any = rx.findall(pattern_any, "call_one(1, 2) and call_two(3)")
    assert matches_any == [("call_one", "1, 2"), ("call_two", "3")]

    pattern_empty = _regex_module.func_call("")
    matches_empty = rx.findall(pattern_empty, "call(1)")
    assert matches_empty == [("call", "1")]

    pattern_specific = _regex_module.func_call("print")
    matches_specific = rx.findall(pattern_specific, "print(hello) and input(prompt) and print(world)")
    assert matches_specific == [("print", "hello"), ("print", "world")]


def test_rgba_str_formats_and_options():
    pattern_default = _regex_module.rgba_str()
    text = "rgba(255, 128, 0, 0.5) and rgb(100, 200, 50) and 255, 128, 0"
    matches_default = rx.findall(pattern_default, text)
    assert len(matches_default) == 3

    pattern_no_alpha = _regex_module.rgba_str(allow_alpha=False)
    matches_no_alpha = rx.findall(pattern_no_alpha, "rgb(255, 0, 0)")
    assert len(matches_no_alpha) == 1

    pattern_pipe_sep = _regex_module.rgba_str(fix_sep="|")
    assert len(rx.findall(pattern_pipe_sep, "255|128|0")) == 1

    pattern_any_sep = _regex_module.rgba_str(fix_sep=None)
    assert len(rx.findall(pattern_any_sep, "255 128 0")) == 1


def test_hsla_str_formats_and_options():
    pattern_default = _regex_module.hsla_str()
    text = "hsla(240, 100%, 50%, 0.8) and hsl(360, 100%, 50%) and 120, 80%, 60%"
    matches_default = rx.findall(pattern_default, text)
    assert len(matches_default) == 3

    pattern_no_alpha = _regex_module.hsla_str(allow_alpha=False)
    matches_no_alpha = rx.findall(pattern_no_alpha, "hsl(240, 100%, 50%)")
    assert len(matches_no_alpha) == 1

    pattern_space_sep = _regex_module.hsla_str(fix_sep=" ")
    assert len(rx.findall(pattern_space_sep, "240 100% 50%")) == 1

    pattern_any_sep = _regex_module.hsla_str(fix_sep=None)
    assert len(rx.findall(pattern_any_sep, "240-100%-50%")) == 1


def test_hexa_str_formats_and_options():
    pattern_with_alpha = _regex_module.hexa_str(allow_alpha=True)
    text = "Colors: #FF0000 and 0xABCDEF and F00 and #FF0000FF and 0xF00F"
    matches_with_alpha = rx.findall(pattern_with_alpha, text)
    assert len(matches_with_alpha) == 5

    pattern_no_alpha = _regex_module.hexa_str(allow_alpha=False)
    matches_no_alpha = rx.findall(pattern_no_alpha, "Colors: #FF0000 and F00")
    assert len(matches_no_alpha) == 2
