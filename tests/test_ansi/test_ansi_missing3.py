from xulbux.ansi import S, StyledText, Term, _ColorStyle, _StyleGroup


def test_to_bg_fg():
    g_st = S.RED | S.BG.BLUE | S.BOLD
    g_bg_st = g_st.to_bg()
    g_fg_st = g_bg_st.to_fg()
    assert isinstance(g_bg_st, _StyleGroup)
    assert isinstance(g_fg_st, _StyleGroup)

    S.RED.to_bg().to_fg()
    S.BG.RED.to_fg().to_bg()

    c_st = S.hex("#F00")
    c_bg_st = c_st.to_bg()
    assert isinstance(c_bg_st, _ColorStyle)
    assert isinstance(c_bg_st.to_fg(), _ColorStyle)


def test_term_methods():
    assert isinstance(Term.up(), str)
    assert isinstance(Term.up(2), str)
    assert isinstance(Term.down(), str)
    assert isinstance(Term.down(2), str)
    assert isinstance(Term.right(), str)
    assert isinstance(Term.right(2), str)
    assert isinstance(Term.left(), str)
    assert isinstance(Term.left(2), str)
    assert isinstance(Term.move(1, 2), str)
    assert isinstance(Term.title("hi"), str)

    assert isinstance(Term.save(), str)
    assert isinstance(Term.alt_screen, str) if hasattr(Term, "alt_screen") else True  # pyright:ignore[reportAttributeAccessIssue, reportUnknownMemberType]
    assert isinstance(Term.hide_cursor, str) if hasattr(Term, "hide_cursor") else True  # pyright:ignore[reportAttributeAccessIssue, reportUnknownMemberType]


def test_styledtext_cache_reset():
    st = StyledText("a")
    _ = st.ansi  # cache it
    # nothing to do for property caching check directly, just call it multiple times


def test_colorstyle_from_hex():
    c1_st = _ColorStyle.from_hex("0xFF0000")
    assert c1_st._red == 255
    c2_st = _ColorStyle.from_hex("0x00FF00", bg=True)
    assert c2_st._bg


def test_more_styledtext():
    # StyledText.__eq__ other is not str or StyledText
    st = StyledText("a")
    assert st != 1

    # StyledText.__len__
    assert len(st) == 1

    # StyledText.__bool__
    assert bool(st) is True
    assert bool(StyledText("")) is False

    st.rjust(5)
    st.wrap(10)
    StyledText(S.BOLD("a")).rjust(5)
