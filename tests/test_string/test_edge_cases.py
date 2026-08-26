from xulbux import string as xstring
import pytest


def test_normalize_spaces_negative():
    with pytest.raises(ValueError):
        xstring.normalize_spaces("test", -1)


def test_single_char_repeats_invalid():
    with pytest.raises(ValueError):
        xstring.single_char_repeats("test", "ab")

    with pytest.raises(ValueError):
        xstring.single_char_repeats("test", "")


def test_remove_consecutive_empty_lines_negative():
    with pytest.raises(ValueError):
        xstring.remove_consecutive_empty_lines("test", -1)
