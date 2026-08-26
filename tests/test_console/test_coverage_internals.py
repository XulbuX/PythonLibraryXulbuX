from xulbux.console import _compile_format, _is_number


def test_compile_format_not_tuple_not_string():
    class Dummy:
        def __str__(self):
            return "dummy"

    # To hit line 100: "return [StyledText(fmt).ansi if not isinstance(fmt, str) else fmt]"
    assert _compile_format(Dummy()) == ["dummy"]


def test_is_number():
    assert _is_number("-5")
    assert _is_number("3.14")
    assert not _is_number("")
    assert not _is_number("-")
    assert _is_number("-.5")
    assert not _is_number("abc")
    assert not _is_number("-abc")
