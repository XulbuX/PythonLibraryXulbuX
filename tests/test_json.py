from xulbux.xx_file import SameContentFileExistsError
from xulbux import Json

import pytest
import json
import os


def create_test_json(tmp_path, filename, data):
    file_path = tmp_path / filename
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)
    return file_path


def create_test_json_string(tmp_path, filename, content):
    file_path = tmp_path / filename
    with open(file_path, 'w') as f:
        f.write(content)
    return file_path


SIMPLE_DATA = {"name": "test", "value": 123}
COMMENT_DATA_STR = '''
{
  ">>": "This whole object is a comment",
  "a": 1
}
{
  "key1": "value1",
  "key2": "value with >>inline comment<<",
  "list": [
    1,
    ">>": "This list item is a comment",
    2,
    "item with >>inline comment<<"
  ]
}
'''
COMMENT_DATA_PROCESSED = {"key1": "value1", "key2": "value with ", "list": [1, "item with "]}
COMMENT_DATA_ORIGINAL = {
    ">>": "This whole object is a comment", "a": 1, "key1": "value1", "key2": "value with >>inline comment<<",
    "list": [1, ">>", 2, "item with >>inline comment<<"]
}
UPDATE_DATA_START = {"config": {"version": 1, "features": ["a", "b"]}, "user": "test_user"}
UPDATE_VALUES = {"config->version": 2, "config->features->1": "c", "new_key": True, "config->new_feature": "d"}
UPDATE_DATA_END = {"config": {"version": 2, "features": ["a", "c"], "new_feature": "d"}, "user": "test_user", "new_key": True}


def test_read_simple(tmp_path):
    file_path = create_test_json(tmp_path, "simple.json", SIMPLE_DATA)
    data = Json.read(str(file_path))
    assert data == SIMPLE_DATA


# def test_read_with_comments(tmp_path):
#     file_path = create_test_json_string(tmp_path, "comments.json", COMMENT_DATA_STR)
#     data = Json.read(str(file_path))
#     assert data == COMMENT_DATA_PROCESSED

# def test_read_with_comments_return_original(tmp_path):
#     file_path = create_test_json_string(tmp_path, "comments_orig.json", COMMENT_DATA_STR)
#     processed, original = Json.read(str(file_path), return_original=True)
#     assert processed == COMMENT_DATA_PROCESSED
#     expected_original = json.loads(COMMENT_DATA_STR.replace('">>": "This list item is a comment",', ''))
#     assert original == expected_original


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
    with open(created_path, 'r') as f:
        data = json.load(f)
    assert data == SIMPLE_DATA


def test_create_with_indent_compactness(tmp_path):
    file_path_str = str(tmp_path / "formatted.json")
    Json.create(file_path_str, SIMPLE_DATA, indent=4, compactness=0)
    with open(file_path_str, 'r') as f:
        content = f.read()
        assert '\n    "name":' in content


def test_create_force_false_exists(tmp_path):
    file_path = create_test_json(tmp_path, "existing.json", {"a": 1})
    with pytest.raises(FileExistsError):
        Json.create(str(file_path), {"b": 2}, force=False)


# def test_create_force_false_same_content(tmp_path):
#     file_path = create_test_json(tmp_path, "existing_same.json", SIMPLE_DATA)
#     with pytest.raises(SameContentFileExistsError):
#         Json.create(str(file_path), SIMPLE_DATA, force=False)


def test_create_force_true_exists(tmp_path):
    file_path = create_test_json(tmp_path, "overwrite.json", {"a": 1})
    Json.create(str(file_path), {"b": 2}, force=True)
    with open(file_path, 'r') as f:
        data = json.load(f)
    assert data == {"b": 2}


# def test_update_existing_values(tmp_path):
#     file_path = create_test_json(tmp_path, "update_test.json", UPDATE_DATA_START)
#     Json.update(str(file_path), UPDATE_VALUES)
#     with open(file_path, 'r') as f:
#         data = json.load(f)
#     assert data == UPDATE_DATA_END

# def test_update_with_comments(tmp_path):
#     update_start_with_comments = '''
# {
#   "config": {
#     ">>": "Config version",
#     "version": 1,
#     "features": ["a", ">>inline<<b"]
#   },
#   "user": "test_user"
# }
# '''
#     file_path = create_test_json_string(tmp_path, "update_comments.json", update_start_with_comments)

#     update_vals = {"config->version": 2, "config->features->1": "c"}
#     Json.update(str(file_path), update_vals)

#     with open(file_path, 'r') as f:
#         content = f.read()

#     expected_data_after_update = {
#         "config": {">>": "Config version", "version": 2, "features": ["a", "c"]}, "user": "test_user"
#     }
#     try:
#         final_data = json.loads(content)
#         assert final_data['config']['version'] == 2
#         assert final_data['config']['features'] == ["a", "c"]
#         assert final_data['user'] == "test_user"
#     except json.JSONDecodeError:
#         pytest.fail("JSON became invalid after update with comments")


def test_update_different_path_sep(tmp_path):
    file_path = create_test_json(tmp_path, "update_sep.json", {"a": {"b": 1}})
    Json.update(str(file_path), {"a/b": 2}, path_sep="/")
    with open(file_path, 'r') as f:
        data = json.load(f)
    assert data == {"a": {"b": 2}}


# def test_update_create_non_existent_path(tmp_path):
#     file_path = create_test_json(tmp_path, "update_create.json", {"existing": 1})
#     Json.update(str(file_path), {"new->nested->value": "created"})
#     with open(file_path, 'r') as f:
#         data = json.load(f)
#     assert data == {"existing": 1, "new": {"nested": {"value": "created"}}}
