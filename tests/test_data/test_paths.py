from typing import Any
import xulbux.data as _data_module
from xulbux.data import _set_nested_val
import pytest


def test_is_equal_identical_and_differing_structures():
    dict1 = {"k1": [1, 2], "k2": "value"}
    dict2 = {"k1": [1, 2], "k2": "value"}
    dict3 = {"k1": [1, 3], "k2": "value"}

    assert _data_module.is_equal(dict1, dict2) is True
    assert _data_module.is_equal(dict1, dict3) is False
    assert _data_module.is_equal({"a": 1}, ["a", 1]) is False
    assert _data_module.is_equal({"a": 1}, {"a": 2, "b": 3}) is False
    assert _data_module.is_equal({"a": 1}, {"b": 1}) is False
    assert _data_module.is_equal([1, 2], [1]) is False
    assert _data_module.is_equal([1, 2], [1, 3]) is False
    assert _data_module.is_equal({1}, {2}) is False
    assert _data_module.is_equal(frozenset([1]), frozenset([2])) is False


def test_is_equal_with_ignore_paths():
    dict_source = {"k1": [1, 2], "k2": "value_original"}
    dict_target = {"k1": [1, 2], "k2": "value_modified"}

    assert _data_module.is_equal(dict_source, dict_target, ignore_paths="k2") is True
    assert _data_module.is_equal(dict_source, dict_target, ignore_paths=["k2"]) is True
    assert _data_module.is_equal({"a": {"b": 1}}, {"a": {"b": 2}}, ignore_paths=["c->d"]) is False


def test_is_equal_empty_path_sep_raises_value_error():
    with pytest.raises(ValueError, match="must be a non-empty string"):
        _data_module.is_equal({"a": 1}, {"a": 1}, path_sep="")


def test_get_path_id_single_and_multiple():
    sample_data = {
        "healthy": {
            "fruit": ["apples", "bananas", "oranges"],
            "vegetables": ["carrots", "broccoli", "celery"],
        }
    }

    assert _data_module.get_path_id(sample_data, "healthy->fruit->0") == "1>000"
    assert _data_module.get_path_id(sample_data, "healthy->fruit->apples") == "1>000"
    assert _data_module.get_path_id(sample_data, "healthy->vegetables->1") == "1>011"

    multiple_results = _data_module.get_path_id(sample_data, ["healthy->fruit->0", "healthy->vegetables->1"])
    assert multiple_results == ["1>000", "1>011"]

    single_in_list = _data_module.get_path_id(sample_data, ["healthy->fruit->0"])
    assert single_in_list == "1>000"
    assert _data_module.get_path_id(sample_data, []) is None


def test_get_path_id_errors_and_ignore_not_found():
    with pytest.raises(ValueError, match="must be a non-empty string"):
        _data_module.get_path_id({"a": 1}, "a", path_sep="")

    assert _data_module.get_path_id({"a": 1}, "b", ignore_not_found=True) is None
    assert _data_module.get_path_id([1, 2], "3", ignore_not_found=True) is None
    assert _data_module.get_path_id([1, 2], "missing", ignore_not_found=True) is None
    assert _data_module.get_path_id({"a": 1}, "1", ignore_not_found=True) is None

    with pytest.raises(TypeError):
        _data_module.get_path_id({"a": 1}, "1")

    with pytest.raises(KeyError):
        _data_module.get_path_id({"a": 1}, "b")

    with pytest.raises(ValueError):
        _data_module.get_path_id([1, 2], "missing")

    with pytest.raises(IndexError):
        _data_module.get_path_id([1, 2], "3")

    assert str(_data_module.get_path_id({"a": 1}, "a->b", ignore_not_found=True)) == "1>0"


def test_get_value_by_path_id():
    sample_data = {
        "healthy": {
            "fruit": ["apples", "bananas", "oranges"],
        }
    }
    path_id = _data_module.get_path_id(sample_data, "healthy->fruit->1")
    assert path_id is not None
    assert _data_module.get_value_by_path_id(sample_data, path_id) == "bananas"
    assert _data_module.get_value_by_path_id(sample_data, path_id, get_key=True) == "fruit"

    dict_path_id = _data_module.get_path_id(sample_data, "healthy->fruit")
    assert dict_path_id is not None
    assert _data_module.get_value_by_path_id(sample_data, dict_path_id, get_key=True) == "fruit"

    multi_key_dict = {"other": [10], "healthy": {"a": 1, "fruit": ["apples", "bananas"]}}
    multi_path_id = _data_module.get_path_id(multi_key_dict, "healthy->fruit->0")
    assert multi_path_id is not None
    assert _data_module.get_value_by_path_id(multi_key_dict, multi_path_id, get_key=True) == "fruit"


def test_get_value_by_path_id_errors():
    path_id = _data_module.get_path_id([[1]], "0->0")
    assert path_id is not None
    with pytest.raises(ValueError, match="Cannot get key from a non-dict parent"):
        _data_module.get_value_by_path_id([[1]], path_id, get_key=True)

    with pytest.raises(TypeError, match="Unsupported type"):
        _data_module.get_value_by_path_id({"a": 1}, "1>02")

    class IncompleteDict(dict[str, Any]):
        def items(self) -> Any:  # type:ignore[override] # pyright:ignore[reportIncompatibleMethodOverride]
            return []

    data = IncompleteDict({"a": [1]})
    dict_path_id = _data_module.get_path_id({"a": [1]}, "a->0")
    assert dict_path_id is not None
    with pytest.raises(StopIteration):
        _data_module.get_value_by_path_id(data, dict_path_id, get_key=True)


def test_set_value_by_path_id():
    sample_data = {"healthy": {"fruit": ["apples", "bananas"]}}
    path_id = _data_module.get_path_id(sample_data, "healthy->fruit->0")
    assert path_id is not None

    updated = _data_module.set_value_by_path_id(sample_data, {path_id: "strawberries"})
    assert updated["healthy"]["fruit"][0] == "strawberries"

    nested_list = [[1, 2], [3, 4]]
    list_path_id = _data_module.get_path_id(nested_list, "0->1")
    assert list_path_id is not None
    updated_list = _data_module.set_value_by_path_id(nested_list, {list_path_id: 99})
    assert updated_list[0][1] == 99

    single_dict = {"a": 1}
    assert _data_module.set_value_by_path_id(single_dict, {"1>0": 2}) == {"a": 2}

    single_list = [10, 20]
    assert _data_module.set_value_by_path_id(single_list, {"1>0": 99}) == [99, 20]

    single_tuple = (10, 20)
    assert _data_module.set_value_by_path_id(single_tuple, {"1>0": 99}) == (99, 20)

    res = _set_nested_val(1, [0, 0], 2)  # pyright:ignore[reportArgumentType]
    assert res == 1

    res_single = _set_nested_val(1, [0], 2)  # pyright:ignore[reportArgumentType]
    assert res_single == 1


def test_set_value_by_path_id_invalid_formats():
    with pytest.raises(ValueError, match="No valid 'update_values'"):
        _data_module.set_value_by_path_id({"a": 1}, {})

    with pytest.raises(ValueError, match="is an invalid format"):
        _data_module.set_value_by_path_id({"a": 1}, {"invalid": 1})

    with pytest.raises(ValueError, match="is an invalid format"):
        _data_module.set_value_by_path_id({"a": 1}, {"1>a": 1})

    with pytest.raises(ValueError, match="is an invalid format"):
        _data_module.set_value_by_path_id({"a": 1}, {"2>0": 1})
