from xulbux.ansi import S, StyledText, _ColorStyle, _StyleGroup


def test_stylegroup_missing():
    # __or__, __ror__
    g1 = S.BOLD | S.RED
    g2 = S.ITALIC | S.BLUE
    assert isinstance(g1 | g2, _StyleGroup)
    assert len((g1 | g2)._codes) == 4

    # ror with BaseStyle
    assert isinstance(S.ITALIC | g1, _StyleGroup)

    # __matmul__
    assert (g1 @ "text").text == "text"

    # __eq__ False
    assert g1 != S.BOLD

    # format methods
    assert isinstance(g1.join(["a", "b"]), StyledText)
    assert isinstance(g1.ljust(4, "-"), StyledText)
    assert isinstance(g1.rjust(4, "-"), StyledText)
    assert isinstance(g1.center(4, "-"), StyledText)
    assert isinstance(g1.wrap(10), list)


def test_style_missing():
    # __eq__ false
    assert S.BOLD != "bold"

    # __hash__
    assert hash(S.BOLD) == hash(1)

    # __ror__
    assert isinstance(S.RED | S.BOLD, _StyleGroup)

    # __matmul__
    assert (S.BOLD @ "text").text == "text"

    # format methods
    assert isinstance(S.BOLD.join(["a", "b"]), StyledText)
    assert isinstance(S.BOLD.ljust(4, "-"), StyledText)
    assert isinstance(S.BOLD.rjust(4, "-"), StyledText)
    assert isinstance(S.BOLD.center(4, "-"), StyledText)
    assert isinstance(S.BOLD.wrap(10), list)


def test_colorstyle_missing():
    # from_hex
    c1_st = S.hex("#FF0000")
    c2_st = S.hex("F00")
    S.BG.hex("0xFF0000")
    assert c1_st._red == 255 and c1_st._green == 0 and c1_st._blue == 0
    assert c2_st._red == 255 and c2_st._green == 0 and c2_st._blue == 0

    # __or__, __ror__
    assert isinstance(c1_st | c2_st, _StyleGroup)
    assert isinstance(c1_st | S.BOLD, _StyleGroup)
    assert isinstance(S.BOLD | c1_st, _StyleGroup)

    # __eq__ false
    assert c1_st != "red"

    # format methods
    assert isinstance(c1_st.join(["a", "b"]), StyledText)
    assert isinstance(c1_st.ljust(4), StyledText)
    assert isinstance(c1_st.rjust(4), StyledText)
    assert isinstance(c1_st.center(4), StyledText)
    assert isinstance(c1_st.wrap(10), list)


def test_link_missing():
    link_st = S.link("https://example.com")

    # __or__
    assert isinstance(link_st | S.BOLD, _StyleGroup)
    assert isinstance(link_st | (S.BOLD | S.RED), _StyleGroup)

    # __call__
    assert link_st("text").text == "text"

    # __matmul__
    assert (link_st @ "text").text == "text"

    # format methods
    assert isinstance(link_st.join(["a", "b"]), StyledText)
    assert isinstance(link_st.ljust(4), StyledText)
    assert isinstance(link_st.rjust(4), StyledText)
    assert isinstance(link_st.center(4), StyledText)
    assert isinstance(link_st.wrap(10), list)


def test_s_missing():
    assert S.hex("#F00") == _ColorStyle.from_hex("#F00")
    assert S.rgb(255, 0, 0) == _ColorStyle(255, 0, 0)
    assert S.BG.hex("#F00") == _ColorStyle.from_hex("#F00", bg=True)
    assert S.BG.rgb(255, 0, 0) == _ColorStyle(255, 0, 0, bg=True)
    assert S.link("url")._url == "url"


def test_styledtext_missing():
    st1 = StyledText("a")
    st2 = StyledText("b")

    # __eq__
    assert st1 != st2
    assert st1 == "a"

    # __len__
    assert len(st1) == 1

    # __bool__
    assert bool(st1) is True
    assert bool(StyledText("")) is False

    # ansi caching
    assert st1.ansi == "a"
    assert st1.ansi == "a"  # cached

    # rjust, wrap
    assert st1.rjust(4, "-").ansi == "---a"
    assert isinstance(st1.wrap(10), list)
