from xulbux.console import log_box_bordered, log_box_filled
import pytest


def test_log_box_filled_errors():
    with pytest.raises(ValueError, match="w_padding"):
        log_box_filled("msg", w_padding=-1)
    with pytest.raises(ValueError, match="indent"):
        log_box_filled("msg", indent=-1)


def test_log_box_bordered_errors():
    with pytest.raises(ValueError, match="w_padding"):
        log_box_bordered("msg", w_padding=-1)
    with pytest.raises(ValueError, match="indent"):
        log_box_bordered("msg", indent=-1)

    with pytest.raises(ValueError, match="contain exactly 11"):
        log_box_bordered("msg", border_chars=("a",))

    with pytest.raises(ValueError, match="single-char"):
        log_box_bordered("msg", border_chars=("a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "aa"))


def test_log_box_bordered_hr():
    # Will trigger lines 1784-1785
    log_box_bordered("line1", "{hr}", "line2")
