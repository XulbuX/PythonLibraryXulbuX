import json
from pathlib import Path
from typing import Any
import xulbux.json as _json_module
from xulbux.base.exceptions import SameContentFileExistsError
import pytest


def create_test_json(tmp_path: Path, filename: str, data: Any) -> Path:
    file_path = tmp_path / filename
    with open(file_path, "w") as file:
        json.dump(data, file, indent=2)
    return file_path


def create_test_json_string(tmp_path: Path, filename: str, content: str) -> Path:
    file_path = tmp_path / filename
    with open(file_path, "w") as file:
        file.write(content)
    return file_path


SIMPLE_DATA: dict[str, Any] = {"name": "test", "value": 123}
SIMPLE_DATA_STR = '{"name": "test", "value": 123}'

COMMENT_DATA: dict[str, Any] = {
    "key1": "value with no comments",
    "key2": "value >>inline comment<<",
    "list": [1, ">>item is a comment", 2, "item >>inline comment<<"],
    "object": {">>": "whole key & value is a comment"},
    ">>": "whole key & value is a comment",
}
COMMENT_DATA_STR = """{
  "key1": "value with no comments",
  "key2": "value >>inline comment<<",
  "list": [1, ">>item is a comment", 2, "item >>inline comment<<"],
  "object": {">>": "whole key & value is a comment"},
  ">>": "whole key & value is a comment"
}"""
COMMENT_DATA_PROCESSED: dict[str, Any] = {
    "key1": "value with no comments",
    "key2": "value",
    "list": [1, 2, "item"],
    "object": {},
}

COMMENT_DATA_START = """{
  "config": {
    "version >>ADJUSTED AUTOMATICALLY<<": 1.0,
    "features": ["a", "b"],
    ">>": "Features ^ must be adjusted manually"
  },
  "user": "Test User >>DON'T TOUCH<<"
}"""
COMMENT_UPDATE_VALUES: dict[str, Any] = {"config->version": 2.0, "config->features->0": "c", "user": "Cool Test User"}
COMMENT_DATA_END = """{
  "config": {
    "version >>ADJUSTED AUTOMATICALLY<<": 2.0,
    "features": ["c", "b"],
    ">>": "Features ↑ must be adjusted manually"
  },
  "user": "Cool Test User >>DON'T TOUCH<<"
}"""

UPDATE_DATA_START: dict[str, Any] = {"config": {"version": 1.0, "features": ["a", "b"]}, "user": "Test User"}
UPDATE_VALUES: dict[str, Any] = {
    "config->version": 2.0,
    "config->features->1": "c",
    "user": {"name": "Test User", "admin": True},
}
UPDATE_DATA_END: dict[str, Any] = {
    "config": {"version": 2.0, "features": ["a", "c"]},
    "user": {"name": "Test User", "admin": True},
}

#
####################################################### Json TESTS #######################################################


def test_read_simple(tmp_path: Path):
    file_path = create_test_json(tmp_path, "simple.json", SIMPLE_DATA)
    data = _json_module.read(str(file_path))
    assert data == SIMPLE_DATA


def test_read_with_comments(tmp_path: Path):
    file_path = create_test_json_string(tmp_path, "comments.json", COMMENT_DATA_STR)
    data = _json_module.read(str(file_path))
    assert data == COMMENT_DATA_PROCESSED


def test_read_with_comments_return_original(tmp_path: Path):
    file_path = create_test_json_string(tmp_path, "comments_orig.json", COMMENT_DATA_STR)
    processed, original = _json_module.read(str(file_path), return_original=True)
    assert processed == COMMENT_DATA_PROCESSED
    expected_original = json.loads(COMMENT_DATA_STR.replace('">>": "This list item is a comment",', ""))
    assert original == expected_original


def test_read_non_existent_file():
    with pytest.raises(FileNotFoundError):
        _json_module.read("non_existent_file.json")


def test_read_invalid_json(tmp_path: Path):
    file_path = create_test_json_string(tmp_path, "invalid.json", "{invalid json")
    with pytest.raises(ValueError, match=r"Error parsing JSON"):
        _json_module.read(str(file_path))


def test_read_empty_json(tmp_path: Path):
    file_path = create_test_json_string(tmp_path, "empty.json", "{}")
    try:
        data = _json_module.read(str(file_path))
        assert data == {}
    except ValueError as e:
        assert "contains no data" in str(e)


def test_read_comment_only_json(tmp_path: Path):
    file_path = create_test_json_string(tmp_path, "comment_only.json", '{\n">>": "comment"\n}')
    with pytest.raises(ValueError, match=r"contains no data"):
        _json_module.read(str(file_path))


def test_create_simple(tmp_path: Path):
    file_path_str = str(tmp_path / "created.json")
    created_path = _json_module.create(file_path_str, SIMPLE_DATA)
    assert isinstance(created_path, Path)
    assert created_path.exists()
    with open(created_path) as file:
        data = json.load(file)
    assert data == SIMPLE_DATA


def test_create_with_indent_compactness(tmp_path: Path):
    file_path_str = str(tmp_path / "formatted.json")
    _json_module.create(file_path_str, SIMPLE_DATA, indent=4, compactness=0)
    with open(file_path_str) as file:
        content = file.read()
        assert '\n    "name":' in content


def test_create_force_false_exists(tmp_path: Path):
    file_path = create_test_json(tmp_path, "existing.json", {"a": 1})
    with pytest.raises(FileExistsError):
        _json_module.create(str(file_path), {"b": 2}, force=False)


def test_create_force_false_same_content(tmp_path: Path):
    from pathlib import Path

    file_path = _json_module.create(f"{tmp_path}/existing_same.json", SIMPLE_DATA, force=False)
    assert isinstance(file_path, Path)
    with pytest.raises(SameContentFileExistsError):
        _json_module.create(file_path, SIMPLE_DATA, force=False)


def test_create_force_true_exists(tmp_path: Path):
    file_path = create_test_json(tmp_path, "overwrite.json", {"a": 1})
    _json_module.create(str(file_path), {"b": 2}, force=True)
    with open(file_path) as file:
        data = json.load(file)
    assert data == {"b": 2}


def test_update_existing_values(tmp_path: Path):
    file_path = create_test_json(tmp_path, "update_test.json", UPDATE_DATA_START)
    _json_module.update(str(file_path), UPDATE_VALUES)
    with open(file_path) as file:
        data = json.load(file)
    assert data == UPDATE_DATA_END


def test_update_with_comments(tmp_path: Path):
    file_path = create_test_json_string(tmp_path, "update_comments.json", COMMENT_DATA_START)
    _json_module.update(str(file_path), COMMENT_UPDATE_VALUES)

    try:
        final_data: dict = _json_module.read(str(file_path))  # type: ignore[assignment]
        assert final_data["config"]["version"] == 2.0
        assert final_data["config"]["features"] == ["c", "b"]
        assert final_data["user"] == "Cool Test User"
    except json.JSONDecodeError:
        pytest.fail("JSON became invalid after update with comments")


def test_update_different_path_sep(tmp_path: Path):
    file_path = create_test_json(tmp_path, "update_sep.json", {"a": {"b": 1}})
    _json_module.update(str(file_path), {"a/b": 2}, path_sep="/")
    with open(file_path) as file:
        data = json.load(file)
    assert data == {"a": {"b": 2}}


def test_update_create_non_existent_path(tmp_path: Path):
    file_path = create_test_json(tmp_path, "update_create.json", {"existing": 1})
    _json_module.update(str(file_path), {"new->nested->value": "created"})
    with open(file_path) as file:
        data = json.load(file)
    assert data == {"existing": 1, "new": {"nested": {"value": "created"}}}
