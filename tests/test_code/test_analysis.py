import xulbux.code as _code_module


def test_get_func_calls_simple_and_nested():
    sample = "foo()\nbar(1, 2)\nbaz('test')"
    result = _code_module.get_func_calls(sample)
    assert len(result) == 3
    assert ("foo", "") in result
    assert ("bar", "1, 2") in result
    assert ("baz", "'test'") in result

    nested_sample = "outer(inner1(), inner2(param))"
    nested_result = _code_module.get_func_calls(nested_sample)
    func_names = [call[0] for call in nested_result]
    assert "outer" in func_names
    assert "inner1" in func_names
    assert "inner2" in func_names


def test_get_func_calls_methods_and_empty():
    assert _code_module.get_func_calls("no function calls here") == []

    method_sample = "obj.method()\nobj.other_method(123)"
    method_result = _code_module.get_func_calls(method_sample)
    assert len(method_result) == 2
    assert ("method", "") in method_result
    assert ("other_method", "123") in method_result


def test_is_js_short_strings():
    assert _code_module.is_js("") is False
    assert _code_module.is_js("ab") is False


def test_is_js_direct_patterns():
    assert _code_module.is_js('$("#element").hide();') is True
    assert _code_module.is_js("$.ajax();") is True
    assert _code_module.is_js("(function() { console.log('ok'); })();") is True
    assert _code_module.is_js("document.getElementById('id');") is True
    assert _code_module.is_js("window.location.reload();") is True
    assert _code_module.is_js("console.log('hi');") is True


def test_is_js_arrow_function_patterns():
    assert _code_module.is_js("f = (x) => x + 1;") is True
    assert _code_module.is_js("const f = x => x * 2;") is True
    assert _code_module.is_js("(a, b) => a + b") is True
    assert _code_module.is_js("x => x") is True


def test_is_js_custom_and_default_functions():
    assert _code_module.is_js("__('translation_key')") is True
    assert _code_module.is_js("$t('key')") is True
    assert _code_module.is_js("$lang('key')") is True
    assert _code_module.is_js("customFunc()", funcs={"customFunc"}) is True
    assert _code_module.is_js("var x = 1; customFunc();", funcs={"customFunc"}) is True
    assert _code_module.is_js("customFunc()") is False


def test_is_js_multi_line_heuristics():
    js_sample = """
    function calculateTotal(items) {
        let total = 0;
        for (let i = 0; i < items.length; i++) {
            total += items[i].price;
        }
        return total;
    }
    """
    assert _code_module.is_js(js_sample) is True
    assert _code_module.is_js("let x = 1; if (x === 1) { }", funcs=set()) is True
    assert _code_module.is_js("plain text without javascript characteristics") is False
