from typing import Any, Literal, cast
import xulbux.data as _data_module
from xulbux.ansi import StyledText
from xulbux.base.types import DataObj, IndexIterable, is_data_obj, is_index_iterable
import pytest

# Don't change this data!
d_comments: dict[str, Any] = {
    "key1": [
        ">> Comment in the beginning of the string. <<  value1",
        "value2  >> Comment in the end of the string.",
        "val>> Comment in the middle of the string. <<ue3",
        ">> Full value is a comment:  value4",
    ],
    ">> Full key & all its values are a comment:  key2": ["value", "value", "value"],
    "key3": ">> All the keys values are comments:  value",
}

d1_equal: dict[str, Any] = {
    "key1": ["value1", "value2", "value3", ["value1", "value2", "value3"]],
    "key2": ["value1", "value2", "value3", ["value1", "value2", "value3"]],
    "key3": "value",
}
d2_equal: dict[str, Any] = {
    "key1": ["value1", "value2", "value3", ["value1", "value2", "value3"]],
    "key2": ["value1", "value2", "value3", ["value1", "value2", "value3"]],
    "key3": "CHANGED value",
}

d1_path_id = {"healthy": {"fruit": ["apples", "bananas", "oranges"], "vegetables": ["carrots", "broccoli", "celery"]}}
d2_path_id = {"school": {"material": ["pencil", "paper", "rubber"], "subjects": ["math", "science", "history"]}}


# ******************************************************* MODULE TESTS ********************************************************


@pytest.mark.parametrize(
    "input_data, expected_count",
    [
        (["a", "bc", "def"], 6),
        (("a", "bc", "def"), 6),
        ({"a", "bc", "def"}, 6),
        ({"k1": "v1", "k2": "v2"}, 8),
        (["ab", ["c", "d"]], 4),
        ({"k": ["v1", "v2"]}, 5),
        ([], 0),
        ({}, 0),
    ],
)
def test_chars_count(input_data: DataObj, expected_count: int):
    assert _data_module.chars_count(input_data) == expected_count


@pytest.mark.parametrize(
    "input_data, expected_output",
    [
        (["  a  ", " b ", "c"], ["a", "b", "c"]),
        (("  a  ", " b ", "c"), ("a", "b", "c")),
        ({"  a  ": "  v1 ", " b ": "v2"}, {"a": "v1", "b": "v2"}),
        ([" a ", [" b ", " c"]], ["a", ["b", "c"]]),
    ],
)
def test_strip(input_data: DataObj, expected_output: DataObj):
    assert _data_module.strip(input_data) == expected_output


@pytest.mark.parametrize(
    "input_data, spaces_are_empty, expected_output",
    cast(
        "list[tuple[DataObj, bool, DataObj]]",
        [
            (["a", "", "b", None, "  "], False, ["a", "b", "  "]),
            (["a", "", "b", None, "  "], True, ["a", "b"]),
            (("a", "", "b", None, "  "), False, ("a", "b", "  ")),
            (("a", "", "b", None, "  "), True, ("a", "b")),
            ({"k1": "a", "k2": "", "k3": "b", "k4": None, "k5": "  "}, False, {"k1": "a", "k3": "b", "k5": "  "}),
            ({"k1": "a", "k2": "", "k3": "b", "k4": None, "k5": "  "}, True, {"k1": "a", "k3": "b"}),
            (["a", ["", "b"], "c"], False, ["a", ["b"], "c"]),
            (["a", ["", "b"], "c"], True, ["a", ["b"], "c"]),
            (["a", {"x": "", "y": "b"}, "c"], False, ["a", {"y": "b"}, "c"]),
            (["a", {"x": "", "y": "b"}, "c"], True, ["a", {"y": "b"}, "c"]),
            (["a", [], {}], False, ["a"]),
        ],
    ),
)
def test_remove_empty_items(input_data: DataObj, spaces_are_empty: bool, expected_output: DataObj):
    assert _data_module.remove_empty_items(input_data, spaces_are_empty=spaces_are_empty) == expected_output


@pytest.mark.parametrize(
    "input_data, expected_output",
    [
        (["a", "b", "a", "c", "b"], ["a", "b", "c"]),
        (("a", "b", "a", "c", "b"), ("a", "b", "c")),
        ({"a", "b", "c"}, {"a", "b", "c"}),
        ({"k1": "a", "k2": "b", "k3": "a"}, {"k1": "a", "k2": "b", "k3": "a"}),
        (["a", ["b", "b"], "c"], ["a", ["b"], "c"]),
        ({"k": ["v", "v"]}, {"k": ["v"]}),
    ],
)
def test_remove_duplicates(input_data: DataObj, expected_output: DataObj):
    assert _data_module.remove_duplicates(input_data) == expected_output


def test_remove_comments():
    assert _data_module.remove_comments(d_comments, comment_sep="__") == {
        "key1": ["value1", "value2", "val__ue3"],
        "key3": None,
    }


def test_is_equal():
    assert _data_module.is_equal(d1_equal, d2_equal) is False
    assert _data_module.is_equal(d1_equal, d2_equal, ignore_paths="key3") is True


def test_get_path_id():
    id1, id2 = _data_module.get_path_id(d1_path_id, ["healthy->fruit->bananas", "healthy->vegetables->2"])  # type: ignore[return-value]
    assert id1 == "1>001"
    assert id2 == "1>012"
    assert _data_module.get_value_by_path_id(d1_path_id, id1) == "bananas"
    assert _data_module.get_value_by_path_id(d1_path_id, id2) == "celery"
    assert _data_module.set_value_by_path_id(d2_path_id, {id1: "NEW1", id2: "NEW2"}) == {
        "school": {"material": ["pencil", "NEW1", "rubber"], "subjects": ["math", "science", "NEW2"]}
    }


def test_get_value_by_path_id() -> None:
    data: dict[str, Any] = {"a": [1, {"b": "c"}], "d": ("e", "f")}
    path_id_1 = str(_data_module.get_path_id(data, "a->1->b"))
    path_id_2 = str(_data_module.get_path_id(data, "d->1"))

    assert path_id_1 == "1>010"
    assert path_id_2 == "1>11"
    assert _data_module.get_value_by_path_id(data, path_id_1) == "c"
    assert _data_module.get_value_by_path_id(data, path_id_2) == "f"
    assert _data_module.get_value_by_path_id(data, path_id_1, get_key=True) == "b"
    assert _data_module.get_value_by_path_id(data, path_id_2, get_key=True) == "d"

    with pytest.raises(ValueError):
        _data_module.get_value_by_path_id(data, "invalid_id")
    with pytest.raises(IndexError):
        _data_module.get_value_by_path_id({"a": [1]}, "1>01")


def test_set_value_by_path_id() -> None:
    data: dict[str, Any] = {"a": [1, {"b": "c"}], "d": ("e", "f")}
    path_id_c = _data_module.get_path_id(data, "a->1->b")
    path_id_f = _data_module.get_path_id(data, "d->1")
    assert path_id_c is not None and path_id_f is not None

    updated_data = _data_module.set_value_by_path_id(data, {path_id_c: "NEW_C", path_id_f: "NEW_F"})  # type: ignore[assignment]
    expected_data: dict[str, Any] = {"a": [1, {"b": "NEW_C"}], "d": ("e", "NEW_F")}
    assert updated_data == expected_data

    updated_data_types = _data_module.set_value_by_path_id(data, {path_id_c: [1, 2], path_id_f: {"x": 1}})  # type: ignore[assignment]
    expected_data_types: dict[str, Any] = {"a": [1, {"b": [1, 2]}], "d": ("e", {"x": 1})}
    assert updated_data_types == expected_data_types

    with pytest.raises(ValueError):
        _data_module.set_value_by_path_id(data, {"invalid": "value"})

    with pytest.raises(ValueError):
        _data_module.set_value_by_path_id(data, {})


@pytest.mark.parametrize(
    "data, indent, compactness, max_width, sep, as_json, expected_str",
    [
        ([1, 2, 3], 4, 1, 80, ", ", False, "[1, 2, 3]"),
        ((), 4, 1, 80, ", ", False, "()"),
        ((1,), 4, 1, 80, ", ", False, "(1,)"),
        ((1, 2), 4, 1, 80, ", ", False, "(1, 2)"),
        (cast("set[Any]", set()), 4, 1, 80, ", ", False, "set()"),
        ({1}, 4, 1, 80, ", ", False, "{1}"),
        ({1, 2}, 4, 1, 80, ", ", False, "{1, 2}"),
        (cast("frozenset[Any]", frozenset()), 4, 1, 80, ", ", False, "frozenset()"),
        (frozenset({1, 2}), 4, 1, 80, ", ", False, "frozenset({1, 2})"),
        ({"a": 1, "b": 2}, 4, 1, 80, ", ", False, '{"a": 1, "b": 2}'),
        ({"a": [1, 2], "b": {"c": 3}}, 4, 1, 80, ", ", False, '{"a": [1, 2], "b": {"c": 3}}'),
        (
            {"a": [1, 2], "b": {"c": 3}},
            4,
            0,
            80,
            ", ",
            False,
            '{\n    "a": [\n        1,\n        2\n    ],\n    "b": {\n        "c": 3\n    }\n}',
        ),
        ({"a": [1, 2], "b": {"c": 3}}, 4, 2, 80, ", ", False, '{"a": [1, 2], "b": {"c": 3}}'),
        ([1, [2, 3]], 2, 1, 80, ", ", False, "[1, [2, 3]]"),
        ({"ultralongkeyname": [1, None, False]}, 4, 1, 20, ", ", False, '{"ultralongkeyname": [1, None, False]}'),
        ([1, 2, 3], 4, 1, 80, "; ", False, "[1; 2; 3]"),
        ({"a": True, "b": None, "c": [1, 2.5]}, 4, 2, 80, ", ", True, '{"a": true, "b": null, "c": [1, 2.5]}'),
        ({"data": b"hello"}, 2, 0, 80, ", ", True, '{\n  "data": "hello"\n}'),
        ({"data": b"hello"}, 4, 1, 80, ", ", False, '{"data": bytes("hello", "utf-8")}'),
        ([1 + 2j], 4, 1, 80, ", ", False, "[complex(1.0, 2.0)]"),
        ([1 + 2j], 4, 1, 80, ", ", True, '["1+2j"]'),
    ],
)
def test_render(
    data: DataObj, indent: int, compactness: Literal[0, 1, 2], max_width: int, sep: str, as_json: bool, expected_str: str
):
    result = _data_module.render(
        data, indent=indent, compactness=compactness, max_width=max_width, sep=sep, as_json=as_json, syntax_highlighting=False
    )
    assert isinstance(result, StyledText)
    normalized_result = "\n".join(line.rstrip() for line in result.raw.splitlines())
    normalized_expected = "\n".join(line.rstrip() for line in expected_str.splitlines())
    assert normalized_result == normalized_expected


def test_is_data_obj_and_is_index_iterable():
    # Test `is_data_obj`:
    assert is_data_obj([1, 2, 3]) is True
    assert is_data_obj((1, 2, 3)) is True
    assert is_data_obj({1, 2, 3}) is True
    assert is_data_obj(frozenset([1, 2, 3])) is True
    assert is_data_obj({"a": 1}) is True
    assert is_data_obj("string") is False
    assert is_data_obj(123) is False

    # Test `is_index_iterable`:
    assert is_index_iterable([1, 2, 3]) is True
    assert is_index_iterable((1, 2, 3)) is True
    assert is_index_iterable({1, 2, 3}) is True
    assert is_index_iterable(frozenset([1, 2, 3])) is True
    assert is_index_iterable({"a": 1}) is False
    assert is_index_iterable("string") is False

    # Test `is_index_iterable` with `item_type`:
    assert is_index_iterable([1, 2, 3], int) is True
    assert is_index_iterable([1, 2, "3"], int) is False
    assert is_index_iterable(["a", "b", "c"], str) is True
    assert is_index_iterable(["a", 1, "c"], str) is False
    assert is_index_iterable(["a", 1, 2.5], (str, int, float)) is True
    assert is_index_iterable(["a", 1, None], (str, int)) is False
    assert is_index_iterable([], int) is True
    assert is_index_iterable("string", str) is False

    # Parameterized typing usage:
    str_list: IndexIterable[str] = ["a", "b", "c"]
    int_tuple: IndexIterable[int] = (1, 2, 3)
    assert len(str_list) == 3
    assert len(int_tuple) == 3
