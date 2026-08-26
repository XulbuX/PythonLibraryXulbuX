from xulbux.ansi import S, StyledText, is_renderable


def test_missing_7():
    # `is_renderable`:
    assert not is_renderable(1)
    assert not is_renderable(("a", 1))
    assert is_renderable(("a", "b"))

    # `rgb` / `bg.rgb` with tuples:
    assert S.rgb((1, 2, 3))._red == 1  # pyright:ignore[reportArgumentType]
    assert S.BG.rgb((1, 2, 3))._red == 1  # pyright:ignore[reportArgumentType]
    pass

    # `__str__`:
    assert str(StyledText("a")) == "a"

    # `wrap`:
    st1 = StyledText("a" * 100)
    st1.wrap(5)

    st2 = StyledText("a\tb\n")
    st2.wrap(10)

    st3 = StyledText("a   b")
    st3.wrap(2)

    st4 = StyledText("   ")
    st4.wrap(1)
