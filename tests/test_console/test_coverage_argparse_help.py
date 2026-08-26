import contextlib
import io
from xulbux.console import ArgumentParser
import pytest


def test_argparser_help_styles(monkeypatch: pytest.MonkeyPatch):

    # We need to capture stdout
    parser1 = ArgumentParser(
        title="Test Title",
        subtitle="Subtitle\nNew line",  # trigger not inline_subtitle
        notice="Notice text",
        usage="Custom usage {cmd} {args} {opts}",
        controls=[("W", "up"), ({"A", "D"}, "left/right")],
        examples=[
            ("cmd {cmd} -- --foo -x=1 42 -f=1 -z", "example 1"),  # test state[2]=True, _is_number, intermixed
            ("cmd " + "a" * 100, "long example " + "b" * 100),  # trigger wrap in examples
        ],
        epilog="Epilog text",
        intermixed=False,
    )
    parser1.add_arg("arg1", help="Help for arg1")
    parser1.add_arg("arg2", nargs="*", help="Help for arg2")
    parser1.add_arg("arg3", nargs=2, help="Help for arg3")
    parser1.add_opt(["-x"], expects_value="X", help="Help for -x")
    parser1.add_opt(["-f"], expects_value="F?", help="Help for -f")
    parser1.add_opt(["--long"], help="long desc " * 10)  # trigger wrap in section

    file1 = io.StringIO()
    with contextlib.redirect_stdout(file1), contextlib.suppress(SystemExit):
        parser1.print_help()

    # Cover inline subtitle
    parser2 = ArgumentParser(title="Small", subtitle="sub")
    file2 = io.StringIO()
    with contextlib.redirect_stdout(file2), contextlib.suppress(SystemExit):
        parser2.print_help()
