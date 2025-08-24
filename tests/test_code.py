from xulbux.code import Code


def test_add_indent():
    sample = "def hello():\n    return 'Hello, World!'"
    result = Code.add_indent(sample, 4)
    expected = "    def hello():\n        return 'Hello, World!'"
    assert result == expected
    assert Code.add_indent("", 4) == ""
    sample = "line1\n\nline3"
    expected = "    line1\n    \n    line3"
    assert Code.add_indent(sample, 4) == expected


def test_get_tab_spaces():
    sample = "def test():\n    print('test')\n    if True:\n        print('nested')"
    assert Code.get_tab_spaces(sample) == 4
    sample = "def test():\n  print('test')\n  if True:\n    print('nested')"
    assert Code.get_tab_spaces(sample) == 2
    assert Code.get_tab_spaces("") == 0


def test_change_tab_size():
    sample = "def test():\n  print('test')\n  if True:\n    print('nested')"
    expected = "def test():\n    print('test')\n    if True:\n        print('nested')"
    assert Code.change_tab_size(sample, 4) == expected
    sample = "def test():\n    print('test')"
    assert Code.change_tab_size(sample, 4) == sample
    sample = "def test():\n  print('test')\n\n  if True:\n    print('nested')"
    expected = "def test():\n    print('test')\n    if True:\n        print('nested')"
    assert Code.change_tab_size(sample, 4, remove_empty_lines=True) == expected
    sample = "def test():\nprint('test')\nprint('no indent')"
    assert Code.change_tab_size(sample, 4) == sample


def test_get_func_calls():
    sample = "foo()\nbar(1, 2)\nbaz('test')"
    result = Code.get_func_calls(sample)
    assert len(result) == 3
    assert ('foo', '') in result
    assert ('bar', '1, 2') in result
    assert ('baz', "'test'") in result
    sample = "outer(inner1(), inner2(param))"
    result = Code.get_func_calls(sample)
    assert len(result) >= 3
    function_names = [match[0] for match in result]
    assert 'outer' in function_names
    assert 'inner1' in function_names
    assert 'inner2' in function_names
    assert not Code.get_func_calls("no function calls here")
    sample = "obj.method()\nobj.other_method(123)"
    result = Code.get_func_calls(sample)
    assert len(result) == 2
    assert ('method', '') in result
    assert ('other_method', '123') in result


def test_is_js():
    js_sample = """
function test() {
    const x = 5;
    if (x === 5) {
        return true;
    } else {
        return false;
    }
}
    """
    assert Code.is_js(js_sample) is True
    js_sample = "$('#element').hide();"
    assert Code.is_js(js_sample) is True
    js_sample = "__('translation_key')"
    assert Code.is_js(js_sample) is True
    js_sample = "const func = () => { return 42; }"
    assert Code.is_js(js_sample) is True
    js_sample = "customFunc()"
    assert Code.is_js(js_sample, funcs=["customFunc"]) is True
    assert Code.is_js(js_sample) is False
