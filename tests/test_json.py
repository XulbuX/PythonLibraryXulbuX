from xulbux.file import SameContentFileExistsError
from xulbux.json import Json

import pytest
import json
import os


def create_test_json(tmp_path, filename, data):
    file_path = tmp_path / filename
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)
    return file_path


def create_test_json_string(tmp_path, filename, content):
    file_path = tmp_path / filename
    with open(file_path, "w") as f:
        f.write(content)
    return file_path


SIMPLE_DATA = {"name": "test", "value": 123}
SIMPLE_DATA_STR = '{"name": "test", "value": 123}'

COMMENT_DATA = {
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
COMMENT_DATA_PROCESSED = {
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
COMMENT_UPDATE_VALUES = {
    "config->version": 2.0,
    "config->features->0": "c",
    "user": "Cool Test User",
}
COMMENT_DATA_END = """{
  "config": {
    "version >>ADJUSTED AUTOMATICALLY<<": 2.0,
    "features": ["c", "b"],
    ">>": "Features ↑ must be adjusted manually"
  },
  "user": "Cool Test User >>DON'T TOUCH<<"
}"""

UPDATE_DATA_START = {
    "config": {"version": 1.0, "features": ["a", "b"]},
    "user": "Test User",
}
UPDATE_VALUES = {
    "config->version": 2.0,
    "config->features->1": "c",
    "user": {"name": "Test User", "admin": True},
}
UPDATE_DATA_END = {
    "config": {"version": 2.0, "features": ["a", "c"]},
    "user": {"name": "Test User", "admin": True},
}


def test_read_simple(tmp_path):
    file_path = create_test_json(tmp_path, "simple.json", SIMPLE_DATA)
    data = Json.read(str(file_path))
    assert data == SIMPLE_DATA


def test_read_with_comments(tmp_path):
    file_path = create_test_json_string(tmp_path, "comments.json", COMMENT_DATA_STR)
    data = Json.read(str(file_path))
    assert data == COMMENT_DATA_PROCESSED


def test_read_with_comments_return_original(tmp_path):
    file_path = create_test_json_string(tmp_path, "comments_orig.json", COMMENT_DATA_STR)
    processed, original = Json.read(str(file_path), return_original=True)
    assert processed == COMMENT_DATA_PROCESSED
    expected_original = json.loads(COMMENT_DATA_STR.replace('">>": "This list item is a comment",', ""))
    assert original == expected_original


def test_read_non_existent_file():
    with pytest.raises(FileNotFoundError):
        Json.read("non_existent_file.json")


def test_read_invalid_json(tmp_path):
    file_path = create_test_json_string(tmp_path, "invalid.json", "{invalid json")
    with pytest.raises(ValueError, match="Error parsing JSON"):
        Json.read(str(file_path))


def test_read_empty_json(tmp_path):
    file_path = create_test_json_string(tmp_path, "empty.json", "{}")
    try:
        data = Json.read(str(file_path))
        assert data == {}
    except ValueError as e:
        assert "empty or contains only comments" in str(e)


def test_read_comment_only_json(tmp_path):
    file_path = create_test_json_string(tmp_path, "comment_only.json", '{\n">>": "comment"\n}')
    with pytest.raises(ValueError, match="empty or contains only comments"):
        Json.read(str(file_path))


def test_create_simple(tmp_path):
    file_path_str = str(tmp_path / "created.json")
    created_path = Json.create(file_path_str, SIMPLE_DATA)
    assert os.path.exists(created_path)
    assert file_path_str == created_path
    with open(created_path, "r") as f:
        data = json.load(f)
    assert data == SIMPLE_DATA


def test_create_with_indent_compactness(tmp_path):
    file_path_str = str(tmp_path / "formatted.json")
    Json.create(file_path_str, SIMPLE_DATA, indent=4, compactness=0)
    with open(file_path_str, "r") as f:
        content = f.read()
        assert '\n    "name":' in content


def test_create_force_false_exists(tmp_path):
    file_path = create_test_json(tmp_path, "existing.json", {"a": 1})
    with pytest.raises(FileExistsError):
        Json.create(str(file_path), {"b": 2}, force=False)


def test_create_force_false_same_content(tmp_path):
    file_path = Json.create(f"{tmp_path}/existing_same.json", SIMPLE_DATA, force=False)
    with pytest.raises(SameContentFileExistsError):
        Json.create(file_path, SIMPLE_DATA, force=False)


def test_create_force_true_exists(tmp_path):
    file_path = create_test_json(tmp_path, "overwrite.json", {"a": 1})
    Json.create(str(file_path), {"b": 2}, force=True)
    with open(file_path, "r") as f:
        data = json.load(f)
    assert data == {"b": 2}


def test_update_existing_values(tmp_path):
    file_path = create_test_json(tmp_path, "update_test.json", UPDATE_DATA_START)
    Json.update(str(file_path), UPDATE_VALUES)
    with open(file_path, "r") as f:
        data = json.load(f)
    assert data == UPDATE_DATA_END


def test_update_with_comments(tmp_path):
    file_path = create_test_json_string(tmp_path, "update_comments.json", COMMENT_DATA_START)
    Json.update(str(file_path), COMMENT_UPDATE_VALUES)

    try:
        final_data: dict = Json.read(str(file_path))  # type: ignore[assignment]
        assert final_data["config"]["version"] == 2.0
        assert final_data["config"]["features"] == ["c", "b"]
        assert final_data["user"] == "Cool Test User"
    except json.JSONDecodeError:
        pytest.fail("JSON became invalid after update with comments")


def test_update_different_path_sep(tmp_path):
    file_path = create_test_json(tmp_path, "update_sep.json", {"a": {"b": 1}})
    Json.update(str(file_path), {"a/b": 2}, path_sep="/")
    with open(file_path, "r") as f:
        data = json.load(f)
    assert data == {"a": {"b": 2}}


def test_update_create_non_existent_path(tmp_path):
    file_path = create_test_json(tmp_path, "update_create.json", {"existing": 1})
    Json.update(str(file_path), {"new->nested->value": "created"})
    with open(file_path, "r") as f:
        data = json.load(f)
    assert data == {"existing": 1, "new": {"nested": {"value": "created"}}}
