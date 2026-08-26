from xulbux.ansi import S, StyledText, is_renderable


def test_missing_7():
    # 1182, 1185: is_renderable
    assert not is_renderable(1)
    assert not is_renderable(("a", 1))
    assert is_renderable(("a", "b"))

    # 1248, 1383: rgb / bg.rgb with tuples
    assert S.rgb((1, 2, 3))._red == 1
    assert S.BG.rgb((1, 2, 3))._red == 1
    pass

    # 1808: __str__
    assert str(StyledText("a")) == "a"

    # 1784-1786: wrap edge
    # paragraph without spaces that is too long -> textwrap might not wrap it, or returns empty?
    # Actually `textwrap.wrap("abcdef", 2)` returns `['ab', 'cd', 'ef']`
    # Let's see if we can trigger find() returning -1 or wrapped chunks being empty
    t = StyledText("a" * 100)
    t.wrap(5)

    # To trigger `chunk_start = para_offset` (1793):
    # textwrap.wrap replaces tabs with spaces, so find fails
    t2 = StyledText("a\tb\n")
    t2.wrap(10)

    t3 = StyledText("a   b")
    t3.wrap(2)

    t4 = StyledText("   ")
    t4.wrap(1)
