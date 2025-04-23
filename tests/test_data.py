from xulbux import Data
import pytest

# ! DON'T CHANGE THIS DATA !
d_comments = {
    "key1": [
        ">> COMMENT IN THE BEGINNING OF THE STRING <<  value1",
        "value2  >> COMMENT IN THE END OF THE STRING",
        "val>> COMMENT IN THE MIDDLE OF THE STRING <<ue3",
        ">> FULL VALUE IS A COMMENT  value4",
    ],
    ">> FULL KEY + ALL ITS VALUES ARE A COMMENT  key2": ["value", "value", "value"],
    "key3": ">> ALL THE KEYS VALUES ARE COMMENTS  value",
}

d1_equal = {
    "key1": ["value1", "value2", "value3", ["value1", "value2", "value3"]],
    "key2": ["value1", "value2", "value3", ["value1", "value2", "value3"]],
    "key3": "value",
}
d2_equal = {
    "key1": ["value1", "value2", "value3", ["value1", "value2", "value3"]],
    "key2": ["value1", "value2", "value3", ["value1", "value2", "value3"]],
    "key3": "CHANGED value",
}

d1_path_id = {"healthy": {"fruit": ["apples", "bananas", "oranges"], "vegetables": ["carrots", "broccoli", "celery"]}}
d2_path_id = {"school": {"material": ["pencil", "paper", "rubber"], "subjects": ["math", "science", "history"]}}


def test_serialize_bytes():
    utf8_bytes = b"Hello"
    utf8_bytearray = bytearray(b"World")
    non_utf8_bytes = b'\x80abc'

    assert Data.serialize_bytes(utf8_bytes) == {"bytes": "Hello", "encoding": "utf-8"}
    assert Data.serialize_bytes(utf8_bytearray) == {"bytearray": "World", "encoding": "utf-8"}
    serialized_non_utf8 = Data.serialize_bytes(non_utf8_bytes)
    assert serialized_non_utf8["encoding"] == "base64"
    import base64
    assert base64.b64decode(serialized_non_utf8["bytes"]).decode("latin-1") == non_utf8_bytes.decode("latin-1")

    with pytest.raises(TypeError):
        Data.serialize_bytes("not bytes")


def test_deserialize_bytes():
    utf8_serialized_bytes = {"bytes": "Hello", "encoding": "utf-8"}
    utf8_serialized_bytearray = {"bytearray": "World", "encoding": "utf-8"}
    import base64
    non_utf8_bytes = b'\x80abc'
    base64_encoded = base64.b64encode(non_utf8_bytes).decode("utf-8")
    base64_serialized_bytes = {"bytes": base64_encoded, "encoding": "base64"}

    assert Data.deserialize_bytes(utf8_serialized_bytes) == b"Hello"
    assert Data.deserialize_bytes(utf8_serialized_bytearray) == bytearray(b"World")
    assert Data.deserialize_bytes(base64_serialized_bytes) == non_utf8_bytes

    with pytest.raises(ValueError):
        Data.deserialize_bytes({"bytes": "abc", "encoding": "unknown"})
    with pytest.raises(ValueError):
        Data.deserialize_bytes({"wrong_key": "abc", "encoding": "utf-8"})


@pytest.mark.parametrize(
    "input_data, expected_count", [
        (["a", "bc", "def"], 6),
        (("a", "bc", "def"), 6),
        ({"a", "bc", "def"}, 6),
        ({"k1": "v1", "k2": "v2"}, 8),
        (["ab", ["c", "d"]], 4),
        ({"k": ["v1", "v2"]}, 5),
        ([], 0),
        ({}, 0),
    ]
)
def test_chars_count(input_data, expected_count):
    assert Data.chars_count(input_data) == expected_count


@pytest.mark.parametrize(
    "input_data, expected_output", [
        (["  a  ", " b ", "c"], ["a", "b", "c"]),
        (("  a  ", " b ", "c"), ("a", "b", "c")),
        ({"  a  ": "  v1 ", " b ": "v2"}, {"a": "v1", "b": "v2"}),
        ([" a ", [" b ", " c"]], ["a", ["b", "c"]]),
    ]
)
def test_strip(input_data, expected_output):
    assert Data.strip(input_data) == expected_output


@pytest.mark.parametrize(
    "input_data, spaces_are_empty, expected_output", [
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
    ]
)
def test_remove_empty_items(input_data, spaces_are_empty, expected_output):
    assert Data.remove_empty_items(input_data, spaces_are_empty) == expected_output


@pytest.mark.parametrize(
    "input_data, expected_output", [
        (["a", "b", "a", "c", "b"], ["a", "b", "c"]),
        (("a", "b", "a", "c", "b"), ("a", "b", "c")),
        ({"a", "b", "a", "c", "b"}, {"a", "b", "c"}),
        ({"k1": "a", "k2": "b", "k3": "a"}, {"k1": "a", "k2": "b", "k3": "a"}),
        (["a", ["b", "b"], "c"], ["a", ["b"], "c"]),
        ({"k": ["v", "v"]}, {"k": ["v"]}),
    ]
)
def test_remove_duplicates(input_data, expected_output):
    assert Data.remove_duplicates(input_data) == expected_output


def test_remove_comments():
    assert Data.remove_comments(
        d_comments, comment_sep="__"
    ) == {
        "key1": ["value1", "value2", "val__ue3"],
        "key3": None,
    }


def test_is_equal():
    assert Data.is_equal(d1_equal, d2_equal) is False
    assert Data.is_equal(d1_equal, d2_equal, ignore_paths="key3") is True


def test_get_path_id():
    id1, id2 = Data.get_path_id(d1_path_id, ["healthy->fruit->bananas", "healthy->vegetables->2"])
    assert id1 == "1>001"
    assert id2 == "1>012"
    assert Data.get_value_by_path_id(d1_path_id, id1) == "bananas"
    assert Data.get_value_by_path_id(d1_path_id, id2) == "celery"
    assert Data.set_value_by_path_id(d2_path_id, {id1: "NEW1", id2: "NEW2"}) == {
        "school": {"material": ["pencil", "NEW1", "rubber"], "subjects": ["math", "science", "NEW2"]}
    }


def test_get_value_by_path_id():
    data = {"a": [1, {"b": "c"}], "d": ("e", "f")}
    path_id_1 = Data.get_path_id(data, "a->1->b")
    path_id_2 = Data.get_path_id(data, "d->1")

    assert path_id_1 == "1>010"
    assert path_id_2 == "1>11"
    assert Data.get_value_by_path_id(data, path_id_1) == "c"
    assert Data.get_value_by_path_id(data, path_id_2) == "f"
    assert Data.get_value_by_path_id(data, path_id_1, get_key=True) == "b"
    assert Data.get_value_by_path_id(data, path_id_2, get_key=True) == "d"

    with pytest.raises(ValueError):
        Data.get_value_by_path_id(data, "invalid_id")
    with pytest.raises(IndexError):
        Data.get_value_by_path_id({"a": [1]}, "1>01")


def test_set_value_by_path_id():
    data = {"a": [1, {"b": "c"}], "d": ("e", "f")}
    path_id_c = Data.get_path_id(data, "a->1->b")
    path_id_f = Data.get_path_id(data, "d->1")

    updated_data = Data.set_value_by_path_id(data, {path_id_c: "NEW_C", path_id_f: "NEW_F"})
    expected_data = {"a": [1, {"b": "NEW_C"}], "d": ("e", "NEW_F")}
    assert updated_data == expected_data

    updated_data_types = Data.set_value_by_path_id(data, {path_id_c: [1, 2], path_id_f: {"x": 1}})
    expected_data_types = {"a": [1, {"b": [1, 2]}], "d": ("e", {"x": 1})}
    assert updated_data_types == expected_data_types

    with pytest.raises(ValueError):
        Data.set_value_by_path_id(data, {"invalid": "value"})

    with pytest.raises(ValueError):
        Data.set_value_by_path_id(data, {})


@pytest.mark.parametrize(
    "data, indent, compactness, max_width, sep, as_json, expected_str", [
        ([1, 2, 3], 4, 1, 80, ", ", False, "[1, 2, 3]"),
        ({"a": 1, "b": 2}, 4, 1, 80, ", ", False, "{'a': 1, 'b': 2}"),
        ({"a": [1, 2], "b": {"c": 3}}, 4, 1, 80, ", ", False, "{\n    'a': [1, 2],\n    'b': {'c': 3}\n}"),
        ({"a": [1, 2], "b": {"c": 3}
          }, 4, 0, 80, ", ", False, "{\n    'a': [\n        1,\n        2\n    ],\n    'b': {\n        'c': 3\n    }\n}"),
        ({"a": [1, 2], "b": {"c": 3}}, 4, 2, 80, ", ", False, "{'a': [1, 2], 'b': {'c': 3}}"),
        ([1, [2, 3]], 2, 1, 80, ", ", False, "[\n  1,\n  [2, 3]\n]"),
        ({"ultralongkeyname": [1, None, False]}, 4, 1, 20, ", ", False, "{'ultralongkeyname': [1, None, False]}"),
        ([1, 2, 3], 4, 1, 80, "; ", False, "[1; 2; 3]"),
        ({"a": True, "b": None, "c": [1, 2.5]}, 4, 2, 80, ", ", True, '{"a": true, "b": null, "c": [1, 2.5]}'),
        ({"data": b"hello"}, 2, 0, 80, ", ", True, '{\n  "data": {\n    "bytes": "hello",\n    "encoding": "utf-8"\n  }\n}'),
        ({"data": b"hello"}, 4, 1, 80, ", ", False, "{'data': bytes('hello', 'utf-8')}"),
    ]
)
def test_to_str(data, indent, compactness, max_width, sep, as_json, expected_str):
    result = Data.to_str(data, indent, compactness, max_width, sep, as_json, _syntax_highlighting=False)
    normalized_result = "\n".join(line.rstrip() for line in result.splitlines())
    normalized_expected = "\n".join(line.rstrip() for line in expected_str.splitlines())
    assert normalized_result == normalized_expected
