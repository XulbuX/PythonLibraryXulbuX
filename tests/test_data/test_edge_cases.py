from xulbux.ansi import StyledText
from xulbux.data import (
    _DataRenderHelper,
    _set_nested_val,
    get_path_id,
    get_value_by_path_id,
    is_equal,
    remove_comments,
    remove_duplicates,
    render,
    set_value_by_path_id,
)
import pytest


def test_remove_duplicates_unhashable():
    data = [[1], [1], {"a": 1}, {"a": 1}]
    res = remove_duplicates(data)
    assert res == [[1], {"a": 1}]


def test_remove_comments_value_error():
    with pytest.raises(ValueError):
        remove_comments({"a": 1}, comment_start="")


def test_remove_comments_custom():
    data = ["# comment", "val # comment", "val"]
    res = remove_comments(data, comment_start="#", comment_end="")
    # It returns `None` for `# comment`, and keeps `val # comment` intact because there's no `comment_end`:
    assert res == ["val # comment", "val"]


def test_is_equal_exceptions():
    with pytest.raises(ValueError):
        is_equal({"a": 1}, {"a": 1}, path_sep="")


def test_is_equal_list_ignore():
    assert is_equal({"a": 1}, {"a": 2}, ignore_paths=["a"])


def test_is_equal_type_mismatch():
    assert is_equal({"a": 1}, ["a", 1]) is False
    assert is_equal({"a": 1}, {"a": 2, "b": 3}) is False
    assert is_equal({"a": 1}, {"b": 1}) is False
    assert is_equal({"a": 1}, {"a": 2}) is False
    assert is_equal([1, 2], [1]) is False
    assert is_equal([1, 2], [1, 3]) is False
    assert is_equal({1}, {2}) is False
    assert not is_equal(frozenset([1]), frozenset([2]))
    assert is_equal({"a": {"b": 1}}, {"a": {"b": 2}}, ignore_paths=["c->d"]) is False


def test_get_path_id_exceptions():
    with pytest.raises(ValueError):
        get_path_id({"a": 1}, "a", path_sep="")

    assert get_path_id({"a": 1}, "b", ignore_not_found=True) is None
    assert get_path_id([1, 2], "3", ignore_not_found=True) is None
    assert get_path_id([1, 2], "val", ignore_not_found=True) is None

    with pytest.raises(TypeError):
        get_path_id({"a": 1}, "1")
    assert get_path_id({"a": 1}, "1", ignore_not_found=True) is None

    with pytest.raises(KeyError):
        get_path_id({"a": 1}, "b")

    with pytest.raises(ValueError):
        get_path_id([1, 2], "val")

    # To hit `IndexError`, just pass out of bounds when not `ignore_not_found`:
    with pytest.raises(IndexError):
        get_path_id([1, 2], "3")


def test_get_value_by_path_id_exceptions():
    path_id = get_path_id([[1]], "0->0")
    with pytest.raises(ValueError):
        get_value_by_path_id([[1]], path_id, get_key=True)  # pyright:ignore[reportArgumentType]

    with pytest.raises(TypeError):
        get_value_by_path_id({"a": 1}, "1>02")


def test_set_nested_val():
    data = {"a": 1}
    res = set_value_by_path_id(data, {"1>00": 2})
    assert res == {"a": 1}


def test_render_exceptions():
    with pytest.raises(ValueError):
        render({}, indent=-1)
    with pytest.raises(ValueError):
        render({}, max_width=0)
    with pytest.raises(TypeError):
        render({}, syntax_highlighting="invalid")  # pyright:ignore[reportArgumentType]


def test_render_syntax_highlighting_dict():
    # Pass a valid lambda that returns `StyledText`:
    res = render({"a": 1}, syntax_highlighting={"number": lambda x: StyledText(x)})  # pyright:ignore[reportArgumentType,reportUnknownArgumentType,reportUnknownLambdaType]
    assert res is not None


def test_render_format_value():
    assert render(b"\xff", as_json=False).ansi != ""  # pyright:ignore[reportArgumentType]
    assert render(b"\xff", as_json=True).ansi != ""  # pyright:ignore[reportArgumentType]
    assert render(1 + 2j, as_json=False).ansi != ""  # pyright:ignore[reportArgumentType]
    assert render(1 + 2j, as_json=True).ansi != ""  # pyright:ignore[reportArgumentType]
    assert render(frozenset([1, 2])).ansi != ""


def test_sep_path_id_invalid():
    with pytest.raises(ValueError):
        set_value_by_path_id({"a": 1}, {"invalid": 1})
    with pytest.raises(ValueError):
        set_value_by_path_id({"a": 1}, {"1>a": 1})
    with pytest.raises(ValueError):
        set_value_by_path_id({"a": 1}, {"2>0": 1})


def test_data_get_value_stop_iteration():

    class BadDict(dict):  # pyright:ignore[reportMissingTypeArgument]
        def items(self):  # pyright:ignore[reportIncompatibleMethodOverride,reportUnknownParameterType]
            return []  # pyright:ignore[reportUnknownVariableType]

    data = BadDict({"a": [1]})
    path_id = get_path_id({"a": [1]}, "a->0")
    with pytest.raises(StopIteration):
        get_value_by_path_id(data, path_id, get_key=True)  # pyright:ignore[reportArgumentType]


def test_render_more_coverage():

    # Line 701: `syntax_highlighting` is `True`:
    render({"a": 1}, syntax_highlighting=True)

    # Line 737: `__dict__` formatting:
    class Dummy:
        def __init__(self):
            self.a = 1

    render({"dummy": Dummy()})

    # Line 746-748: bytearray fallback:
    render({"b": b"\xff\xfe"}, as_json=True)

    # Line 797-805: `get_complexity` on tuple, set, frozenset:
    render({"tuple": (1, (2,)), "set": {1, frozenset([2])}}, compactness=1)

    # Line 815: compactness=2:
    render([1, 2], compactness=2)


def test_should_expand_compactness_2():

    helper = _DataRenderHelper([1], indent=0, compactness=2, max_width=10, sep=",", as_json=False, syntax_highlighting=False)
    assert helper.should_expand([1]) is False


def test_set_nested_val_primitive():

    res = _set_nested_val(1, ["0", "0"], 2)  # pyright:ignore[reportArgumentType]
    assert res == 1


def test_path_id_resolver_else():

    assert str(get_path_id({"a": 1}, "a->b", ignore_not_found=True)) == "1>0"
