import xulbux.code as _code_module
import pytest


def test_add_indent_negative():
    with pytest.raises(ValueError):
        _code_module.add_indent("code", -1)


def test_change_tab_size_negative():
    with pytest.raises(ValueError):
        _code_module.change_tab_size("code", -1)


def test_change_tab_size_remove_empty():
    sample = "def test():\n\n    print('test')"
    expected = "def test():\n    print('test')"
    # 4 spaces to 4 spaces, with `remove_empty_lines=True`:
    assert _code_module.change_tab_size(sample, 4, remove_empty_lines=True) == expected


def test_is_js_short():
    assert _code_module.is_js("ab") is False


def test_is_js_empty_funcs():
    # To hit the branch if funcs: is `False`:
    assert _code_module.is_js("let x = 1; if (x === 1) { }", funcs=set()) is True


def test_is_js_arrow_exact():
    # Direct match for arrow function patterns:
    assert _code_module.is_js("f = (x) => x + 1;") is True


def test_is_js_funcs_middle():
    # To hit funcs score increment:
    assert _code_module.is_js("var x = 1; customFunc();", funcs={"customFunc"}) is True
