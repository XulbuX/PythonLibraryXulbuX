import io
from unittest.mock import patch
import xulbux.ansi
from xulbux.ansi import S, StyledText, _Link, is_any_style, is_base_style, is_render_segment, is_text_segment


def test_missing_5():
    # `_ColorStyle.__matmul__`:
    c_st = S.hex("#F00")
    assert (c_st @ "a").text == "a"

    # `_Link.__eq__`:
    link1_st = _Link("url")
    link2_st = _Link("url")
    link3_st = _Link("url2")
    assert link1_st == link2_st
    assert link1_st != link3_st
    assert link1_st != 1

    # `_StyledSequence` format methods:
    seq_st = S.BOLD("a")
    assert isinstance(seq_st.join(["1", "2"]), StyledText)
    assert isinstance(seq_st.ljust(5), StyledText)
    assert isinstance(seq_st.rjust(5), StyledText)
    assert isinstance(seq_st.center(5), StyledText)
    assert isinstance(seq_st.wrap(5), list)

    file1 = io.StringIO()
    seq_st.print(file=file1, flush=False)
    assert file1.getvalue() == "\x1b[1ma\x1b[22m\n"

    with patch("builtins.input", return_value="x"):
        assert seq_st.input() == "x"

    # Type guards:
    assert is_base_style(S.BOLD)
    assert is_any_style(S.BOLD)
    assert is_text_segment("a")
    assert is_render_segment("a")
    assert not is_base_style(1)
    assert not is_any_style(1)
    assert not is_text_segment(1)
    assert not is_render_segment(1)

    # `StyledText.wrap` behavior:
    st = StyledText("a b")
    wrapped_st = st.wrap(1)  # Force chunk wrapping.
    assert isinstance(wrapped_st, list)

    # `_process_code`:
    g_st = S.BOLD | S.DIM
    _opens, _closes = xulbux.ansi._build_open_close(g_st)
