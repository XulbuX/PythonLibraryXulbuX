from xulbux.regex import LazyRegex
import pytest


def test_lazy_regex_init():
    patterns = LazyRegex(test=r"\d+")
    assert patterns._patterns == {"test": r"\d+"}


def test_lazy_regex_getattr_valid():
    patterns = LazyRegex(test=r"\d+")
    regex = patterns.test
    assert regex.pattern == r"\d+"
    assert "test" in patterns.__dict__  # Check caching.


def test_lazy_regex_getattr_invalid():
    patterns = LazyRegex(test=r"\d+")
    with pytest.raises(AttributeError):
        _ = patterns.invalid


def test_lazy_regex_caching():
    patterns = LazyRegex(test=r"\d+")
    regex1 = patterns.test
    regex2 = patterns.test
    assert regex1 is regex2
