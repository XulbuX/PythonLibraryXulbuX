from pathlib import Path
from typing import Any
from xulbux.base.types import AllTextChars, ProgressUpdater, is_data_obj, is_paths_list, is_seq_or_set


def test_is_paths_list_valid_sequences():
    assert is_paths_list([Path("."), "test"]) is True
    assert is_paths_list(["a", "b", "c"]) is True
    assert is_paths_list((Path("."), "test")) is True
    assert is_paths_list(("single",)) is True
    assert is_paths_list([]) is True


def test_is_paths_list_invalid_inputs():
    assert is_paths_list([Path("."), 123]) is False
    assert is_paths_list([123, 456]) is False
    assert is_paths_list("not_a_list") is False
    assert is_paths_list(123) is False


def test_is_data_obj_types():
    assert is_data_obj([1, 2, 3]) is True
    assert is_data_obj((1, 2, 3)) is True
    assert is_data_obj({1, 2, 3}) is True
    assert is_data_obj(frozenset([1, 2, 3])) is True
    assert is_data_obj({"key": "val"}) is True
    assert is_data_obj("not_a_data_obj") is False
    assert is_data_obj(42) is False


def test_is_seq_or_set_without_item_type():
    assert is_seq_or_set([1, 2]) is True
    assert is_seq_or_set((1, 2)) is True
    assert is_seq_or_set({1, 2}) is True
    assert is_seq_or_set(frozenset([1, 2])) is True
    assert is_seq_or_set({"dict": "value"}) is False
    assert is_seq_or_set("string") is False


def test_is_seq_or_set_with_item_type_matching():
    assert is_seq_or_set([1, 2, 3], int) is True
    assert is_seq_or_set(["a", "b"], str) is True
    assert is_seq_or_set([1, "a"], (int, str)) is True
    assert is_seq_or_set([1, "a"], int) is False
    assert is_seq_or_set([1, 2, 3.5], int) is False


def test_all_text_chars_instantiation():
    sentinel = AllTextChars()
    assert isinstance(sentinel, AllTextChars)


def test_progress_updater_protocol():
    class SampleProgressUpdater(ProgressUpdater):
        def __call__(self, current: Any = None, label: Any = None) -> None:  # pyright:ignore[reportIncompatibleMethodOverride]
            super().__call__(current=current, label=label)  # type:ignore[safe-super]

    updater = SampleProgressUpdater()
    updater(current=50, label="Loading")
