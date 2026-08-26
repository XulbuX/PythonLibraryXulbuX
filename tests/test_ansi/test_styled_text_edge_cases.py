import io
from unittest.mock import patch
import xulbux.ansi
from xulbux.ansi import S, StyledText, _Link, is_any_style, is_base_style, is_render_segment, is_text_segment


def test_missing_5():
    # 661: `_ColorStyle.__matmul__`?
    c_st = S.hex("#F00")
    assert (c_st @ "a").text == "a"

    # 828-831: `_Link.__eq__`:
    l1 = _Link("url")
    l2 = _Link("url")
    l3 = _Link("url2")
    assert l1 == l2
    assert l1 != l3
    assert l1 != 1

    # `_StyledSequence` format methods 946-1048:
    sseq = S.BOLD("a")
    assert isinstance(sseq.join(["1", "2"]), StyledText)
    assert isinstance(sseq.ljust(5), StyledText)
    assert isinstance(sseq.rjust(5), StyledText)
    assert isinstance(sseq.center(5), StyledText)
    assert isinstance(sseq.wrap(5), list)

    file1 = io.StringIO()
    sseq.print(file=file1, flush=False)
    assert file1.getvalue() == "\x1b[1ma\x1b[22m\n"

    with patch("builtins.input", return_value="x"):
        assert sseq.input() == "x"

    # Type guards 1113, 1123, 1133, 1143:
    assert is_base_style(S.BOLD)
    assert is_any_style(S.BOLD)
    assert is_text_segment("a")
    assert is_render_segment("a")
    assert not is_base_style(1)
    assert not is_any_style(1)
    assert not is_text_segment(1)
    assert not is_render_segment(1)

    # 1785-1787, 1793, 1809: `StyledText.wrap`.
    # `wrap` behavior:
    st = StyledText("a b")
    wrapped1 = st.wrap(1)  # Force chunk wrapping.
    assert isinstance(wrapped1, list)

    # 1991->exit: `_process_code` SGR:
    g3 = S.BOLD | S.DIM
    _opens3, _closes3 = xulbux.ansi._build_open_close(g3)
