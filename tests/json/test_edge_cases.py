from unittest.mock import patch
from xulbux import json as xjson
import pytest


def test_json_read_no_suffix(tmp_path):
    file = tmp_path / "test"
    with open(file.with_suffix(".json"), "w") as f:
        f.write('{"a": 1}')
    res = xjson.read(file)
    assert res == {"a": 1}


def test_json_create_no_suffix(tmp_path):
    file = tmp_path / "test"
    xjson.create(file, {"a": 1})
    assert file.with_suffix(".json").exists()


def test_json_update_create_nested(tmp_path):
    file = tmp_path / "test.json"
    xjson.create(file, {"a": [1, {"b": 2}]})

    xjson.update(
        file,
        {
            "a->0": 10,
            "a->2->c": 3,
            "d->e": 4,
        },
    )

    res = xjson.read(file)
    assert res["a"][0] == 10
    assert res["a"][1] == {"b": 2}
    assert res["a"][2] == {"c": 3}
    assert res["d"] == {"e": 4}


def test_json_update_dead_code(tmp_path):
    file = tmp_path / "test2.json"
    xjson.create(file, {"a": 1})
    with patch("xulbux.data.get_path_id", return_value=None):
        xjson.update(file, {"b": 2})
    res = xjson.read(file)
    assert res["b"] == 2


def test_json_update_type_error(tmp_path):
    with pytest.raises(TypeError):
        xjson._create_nested_path({"a": 1}, ["a", "b"], 2)

    with pytest.raises(TypeError):
        xjson._create_nested_path({"a": 1}, ["a", "b", "c"], 2)


def test_create_nested_list_expand():
    # 173-175: while len <= idx: append(None) (for last_idx)
    # 190-192: while len <= idx: append(None) (for NOT last_idx)
    res = xjson._create_nested_path([], ["2"], 1)
    assert res == [None, None, 1]

    res = xjson._create_nested_path([], ["2", "a"], 1)
    assert res == [None, None, {"a": 1}]


def test_create_nested_list_existing():
    res = xjson._create_nested_path([{"a": 1}], ["0", "b"], 2)
    assert res == [{"a": 1, "b": 2}]
