from typing import Any, cast
import xulbux.data as _data_module
from xulbux.base.types import DataObj
import pytest


@pytest.mark.parametrize(
    "input_data, expected_count",
    [
        (["a", "bc", "def"], 6),
        (("a", "bc", "def"), 6),
        ({"a", "bc", "def"}, 6),
        ({"k1": "v1", "k2": "v2"}, 8),
        (["ab", ["c", "d"]], 4),
        ({"key": ["v1", "v2"]}, 7),
        ([], 0),
        ({}, 0),
    ],
)
def test_chars_count_data_structures(input_data: DataObj, expected_count: int):
    assert _data_module.chars_count(input_data) == expected_count


def test_strip_nested_collections():
    sample_list = ["  item1  ", " item2 ", "item3"]
    assert _data_module.strip(sample_list) == ["item1", "item2", "item3"]

    sample_tuple = ("  item1  ", " item2 ", "item3")
    assert _data_module.strip(sample_tuple) == ("item1", "item2", "item3")

    sample_dict = {"  key1  ": "  val1 ", " key2 ": "val2"}
    assert _data_module.strip(sample_dict) == {"key1": "val1", "key2": "val2"}

    nested_structure = [" a ", [" b ", " c"]]
    assert _data_module.strip(nested_structure) == ["a", ["b", "c"]]


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


def test_remove_duplicates_hashable_and_unhashable():
    sample_list = ["a", "b", "a", "c", "b"]
    assert _data_module.remove_duplicates(sample_list) == ["a", "b", "c"]

    sample_tuple = ("a", "b", "a", "c", "b")
    assert _data_module.remove_duplicates(sample_tuple) == ("a", "b", "c")

    sample_set = {"a", "b", "c"}
    assert _data_module.remove_duplicates(sample_set) == {"a", "b", "c"}

    sample_dict = {"k1": "a", "k2": "b", "k3": "a"}
    assert _data_module.remove_duplicates(sample_dict) == {"k1": "a", "k2": "b", "k3": "a"}

    nested_list = ["a", ["b", "b"], "c"]
    assert _data_module.remove_duplicates(nested_list) == ["a", ["b"], "c"]

    unhashable_items = [[1], [1], {"a": 1}, {"a": 1}]
    assert _data_module.remove_duplicates(unhashable_items) == [[1], {"a": 1}]


def test_remove_comments_basic_and_nested():
    commented_data: dict[str, Any] = {
        "key1": [
            ">> Comment at start << value1",
            "value2 >> Comment at end",
            "val>> Middle <<ue3",
            ">> Full comment value",
        ],
        ">> Full comment key": ["v1", "v2"],
        "key3": ">> Comment only",
    }

    cleaned = _data_module.remove_comments(commented_data, comment_sep="_")
    assert cleaned == {
        "key1": ["value1", "value2", "val_ue3"],
        "key3": None,
    }


def test_remove_comments_custom_delimiters():
    data_list = ["# comment", "val # comment", "val"]
    res = _data_module.remove_comments(data_list, comment_start="#", comment_end="")
    assert res == ["val # comment", "val"]


def test_remove_comments_empty_start_raises_value_error():
    with pytest.raises(ValueError, match="must be a non-empty string"):
        _data_module.remove_comments({"a": 1}, comment_start="")
