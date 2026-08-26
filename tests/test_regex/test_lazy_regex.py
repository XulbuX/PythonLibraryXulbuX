from xulbux.regex import LazyRegex
import pytest


def test_lazy_regex_initialization():
    lazy = LazyRegex(digits=r"\d+", letters=r"[a-z]+")
    assert lazy._patterns == {"digits": r"\d+", "letters": r"[a-z]+"}


def test_lazy_regex_attribute_access_and_caching():
    lazy = LazyRegex(digits=r"\d+")

    pattern1 = lazy.digits
    assert pattern1.pattern == r"\d+"
    assert "digits" in lazy.__dict__

    pattern2 = lazy.digits
    assert pattern1 is pattern2


def test_lazy_regex_missing_attribute_raises_attribute_error():
    lazy = LazyRegex(digits=r"\d+")

    with pytest.raises(AttributeError, match="has no attribute 'unknown'"):
        _ = lazy.unknown
