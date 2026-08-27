import io
from xulbux.ansi import S


def test_s_construction_and_properties() -> None:
    text = S("Plain text")
    assert text.raw == "Plain text"
    assert text.ansi == "Plain text"
    assert len(text) == 10
    assert bool(text) is True
    assert bool(S("")) is False

    multi_line = S("Line 1", "Line 2", sep="\n")
    assert multi_line.raw == "Line 1\nLine 2"

    multi_part_line = S(("Part 1 ", S.BOLD("Part 2"), " Part 3"))
    assert multi_part_line.raw == "Part 1 Part 2 Part 3"
    assert "\x1b[1mPart 2\x1b[22m" in multi_part_line.ansi


def test_s_slicing_and_containment() -> None:
    styled = S.RED("Hello World")
    assert isinstance(styled, S)
    assert styled[0:5].raw == "Hello"
    assert styled[6:11].raw == "World"
    assert "World" in styled.raw
    assert "World" in styled.ansi
    assert "World" in styled
    assert "lo Wo" in S(S.RED("Hello "), S.BLUE("World"))
    assert "xyz" not in styled


def test_s_concatenation_and_repetition() -> None:
    text1 = S.RED("Hello")
    text2 = S.BLUE(" World")

    combined = text1 + text2
    assert isinstance(combined, S)
    assert combined.raw == "Hello World"
    assert "\x1b[31mHello\x1b[39m\x1b[34m World\x1b[39m" in combined.ansi

    str_combined = text1 + " Plain"
    assert str_combined.raw == "Hello Plain"

    radd_combined = "Plain " + text2
    assert radd_combined.raw == "Plain  World"

    iadd_text = S("Base")
    iadd_text += " Extra"
    assert iadd_text.raw == "Base Extra"
    iadd_text += S(" More")
    assert iadd_text.raw == "Base Extra More"

    repeated = text1 * 3
    assert repeated.raw == "HelloHelloHello"
    assert (3 * text1).raw == "HelloHelloHello"


def test_s_matmul_operator() -> None:
    base_text = "Important Notification"

    applied_left = (S.BOLD | S.RED) @ base_text
    assert isinstance(applied_left, S)
    assert applied_left.raw == "Important Notification"
    assert applied_left.ansi == "\x1b[1;31mImportant Notification\x1b[22;39m"

    single_matmul = S.UNDERLINE @ "Underlined"
    assert isinstance(single_matmul, S)
    assert single_matmul.ansi == "\x1b[4mUnderlined\x1b[24m"

    group_matmul_styled = (S.BOLD | S.BLUE) @ S("Nested")
    assert isinstance(group_matmul_styled, S)
    assert group_matmul_styled.raw == "Nested"


def test_s_equality() -> None:
    text1 = S.RED("Hello")
    text2 = S.RED("Hello")
    text3 = S.BLUE("Hello")

    assert text1 == text2
    assert text1 != text3
    assert text1 == "\x1b[31mHello\x1b[39m"
    assert text1 != 123
    assert str(text1) == text1.ansi
    assert "S(" in repr(text1)


def test_s_print() -> None:
    stream = io.StringIO()
    text = S.GREEN("Success")

    text.print(file=stream)
    assert stream.getvalue() == "\x1b[32mSuccess\x1b[39m\n"


def test_s_render_dispatch_and_fallbacks() -> None:
    class CustomRenderable:
        def __str__(self) -> str:
            return "CustomStr"

    rendered = S(
        "Str",
        S("Nested"),
        S.BOLD("Sequence"),
        ("Tuple1", "Tuple2"),
        S.BOLD,  # Bare _Style
        S.hex("#FF0000"),  # Bare _ColorStyle
        S.link("https://example.com"),  # Bare _Link
        S.BOLD | S.RED,  # Bare _StyleGroup
        CustomRenderable(),  # type:ignore[arg-type]
    )
    assert "CustomStr" in rendered.raw
    assert "Sequence" in rendered.raw

    parts: list[str] = []
    S._render("direct_render", parts)
    assert parts == ["direct_render"]
