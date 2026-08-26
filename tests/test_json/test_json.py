import json
import math
from pathlib import Path
from typing import Any, cast
from unittest.mock import patch
import xulbux.json as _json_module
from xulbux.base.exceptions import SameContentFileExistsError
import pytest


def test_read_simple_json_file(tmp_path: Path) -> None:
    file_path = tmp_path / "sample.json"
    file_path.write_text('{"name": "test", "value": 123}')

    data = _json_module.read(str(file_path))
    assert data == {"name": "test", "value": 123}


def test_read_without_json_extension(tmp_path: Path) -> None:
    file_path = tmp_path / "data_without_ext"
    file_path.with_suffix(".json").write_text('{"key": "value"}')

    assert _json_module.read(file_path) == {"key": "value"}


def test_read_with_comments_and_return_original(tmp_path: Path) -> None:
    raw_json = """{
      "key1": "value with no comments",
      "key2": "value >>inline comment<<",
      "list": [1, ">>item is a comment", 2, "item >>inline comment<<"],
      "object": {">>": "whole key & value is a comment"},
      ">>": "whole key & value is a comment"
    }"""
    file_path = tmp_path / "comments.json"
    file_path.write_text(raw_json)

    processed = _json_module.read(str(file_path))
    assert processed == {
        "key1": "value with no comments",
        "key2": "value",
        "list": [1, 2, "item"],
        "object": {},
    }

    processed_data, original_data = _json_module.read(str(file_path), return_original=True)
    assert processed_data == processed
    assert "key2" in original_data


def test_read_error_cases(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        _json_module.read("non_existent_json_file.json")

    invalid_file = tmp_path / "invalid.json"
    invalid_file.write_text("{invalid json format")
    with pytest.raises(ValueError, match="Error parsing JSON"):
        _json_module.read(str(invalid_file))

    empty_file = tmp_path / "empty.json"
    empty_file.write_text("{}")
    with pytest.raises(ValueError, match="contains no data"):
        _json_module.read(str(empty_file))

    comment_only_file = tmp_path / "comment_only.json"
    comment_only_file.write_text('{\n">>": "only comment"\n}')
    with pytest.raises(ValueError, match="contains no data"):
        _json_module.read(str(comment_only_file))


def test_create_simple_and_formatted(tmp_path: Path) -> None:
    file_path = tmp_path / "created.json"
    created = _json_module.create(file_path, {"a": 1, "b": [2, 3]})

    assert isinstance(created, Path)
    assert created.exists()
    assert json.loads(created.read_text()) == {"a": 1, "b": [2, 3]}

    formatted_path = tmp_path / "formatted"
    created_formatted = _json_module.create(formatted_path, {"name": "test"}, indent=4, compactness=0)
    assert created_formatted.with_suffix(".json").exists()


def test_create_file_exists_errors(tmp_path: Path) -> None:
    file_path = tmp_path / "existing.json"
    _json_module.create(file_path, {"initial": 1})

    with pytest.raises(FileExistsError):
        _json_module.create(file_path, {"changed": 2}, force=False)

    with pytest.raises(SameContentFileExistsError):
        _json_module.create(file_path, {"initial": 1}, force=False)


def test_create_force_overwrite(tmp_path: Path) -> None:
    file_path = tmp_path / "overwrite.json"
    _json_module.create(file_path, {"version": 1})
    _json_module.create(file_path, {"version": 2}, force=True)

    assert json.loads(file_path.read_text()) == {"version": 2}


def test_update_existing_and_nested_values(tmp_path: Path) -> None:
    file_path = tmp_path / "update_target.json"
    _json_module.create(
        file_path,
        {"config": {"version": 1.0, "features": ["a", "b"]}, "user": "Test User"},
    )

    _json_module.update(
        file_path,
        {
            "config->version": 2.0,
            "config->features->1": "c",
            "new_section->nested->key": "value",
        },
    )

    result = json.loads(file_path.read_text())
    assert math.isclose(result["config"]["version"], 2.0)
    assert result["config"]["features"] == ["a", "c"]
    assert result["new_section"]["nested"]["key"] == "value"


def test_update_with_custom_separator(tmp_path: Path) -> None:
    file_path = tmp_path / "update_sep.json"
    _json_module.create(file_path, {"a": {"b": 1}})

    _json_module.update(file_path, {"a/b": 2}, path_sep="/")
    assert json.loads(file_path.read_text()) == {"a": {"b": 2}}


def test_update_with_comments_preservation(tmp_path: Path) -> None:
    file_path = tmp_path / "update_comments.json"
    file_path.write_text("""{
      "config": {
        "version >>ADJUSTED AUTOMATICALLY<<": 1.0,
        "features": ["a", "b"],
        ">>": "Features must be adjusted manually"
      },
      "user": "Test User >>DON'T TOUCH<<"
    }""")

    _json_module.update(
        file_path,
        {"config->version": 2.0, "config->features->0": "c", "user": "Cool User"},
    )

    updated: dict[str, Any] = _json_module.read(str(file_path))
    assert math.isclose(cast("float", updated["config"]["version"]), 2.0)
    assert updated["config"]["features"] == ["c", "b"]
    assert updated["user"] == "Cool User"


def test_update_when_path_id_returns_none(tmp_path: Path) -> None:
    file_path = tmp_path / "fallback.json"
    _json_module.create(file_path, {"a": 1})

    with patch("xulbux.data.get_path_id", return_value=None):
        _json_module.update(file_path, {"b": 2})

    assert json.loads(file_path.read_text()) == {"a": 1, "b": 2}


def test_create_nested_path_list_expansion_and_errors() -> None:
    empty_list_target: list[Any] = []
    res = _json_module._create_nested_path(cast("dict[str, Any]", empty_list_target), ["2"], "item")
    assert res == [None, None, "item"]

    empty_list_nested: list[Any] = []
    res_nested = _json_module._create_nested_path(cast("dict[str, Any]", empty_list_nested), ["2", "key"], "val")
    assert res_nested == [None, None, {"key": "val"}]

    existing_list_nested: list[Any] = [{"existing": "val"}]
    res_existing = _json_module._create_nested_path(cast("dict[str, Any]", existing_list_nested), ["0", "new_key"], "new_val")
    assert res_existing == [{"existing": "val", "new_key": "new_val"}]

    with pytest.raises(TypeError, match="Cannot set key"):
        _json_module._create_nested_path({"a": 1}, ["a", "b"], 2)

    with pytest.raises(TypeError, match="Cannot navigate through"):
        _json_module._create_nested_path({"a": 1}, ["a", "b", "c"], 2)
