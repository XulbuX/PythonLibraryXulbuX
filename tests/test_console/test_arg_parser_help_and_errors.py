import io
from typing import TYPE_CHECKING, Any
from unittest.mock import patch
from xulbux.ansi import StyledText
from xulbux.console import ArgumentParser
import pytest

if TYPE_CHECKING:
    from xulbux.base.types import Renderable


def test_argument_parser_help_generation_full_options() -> None:
    parser = ArgumentParser(
        title="Sample App Title With Long Description Text That Wraps Beyond Normal Limits",
        subtitle="Sample subtitle for testing across multiple lines",
        notice="Beta software",
        usage="sample-app {args} {opts}",
        controls=[("Ctrl+C", "Quit"), ("F1", "Help guide")],
        examples=[
            ("{cmd} --count=2 -v 123 -- extra", "Run with count and extra"),
            ("{cmd} --count 1 -unknown", "Run with space count"),
            ("{cmd} --custom=val", "Custom opt val"),
            ("{cmd} -f", "Flag only"),
            ("{cmd}", "Bare command"),
        ],
        epilog="For more info, visit https://example.com",
    )
    parser.add_arg("input_file", nargs="+", help="Input file paths with detailed description that wraps lines")
    parser.add_arg("pair", nargs=2, help="Two items")
    parser.add_opt(["-v", "--verbose"], help="Verbose logging with description")
    parser.add_opt(["-c", "--count"], expects_value="N", choices=["1", "2", "3"], help="Count")
    parser.add_opt(["-o", "--output"], expects_value="FILE?", help="Optional file path")
    parser.add_opt(["-f", "--flag"], help="Flag")

    stream = io.StringIO()
    with patch("sys.stdout", stream):
        parser.print_help()
    help_text = stream.getvalue()
    raw_help = StyledText.remove_ansi(help_text)
    assert "Sample App Title" in raw_help
    assert "Sample subtitle" in raw_help
    assert "Beta software" in raw_help
    assert "<input_file...>" in raw_help
    assert "<pair [2]>" in raw_help
    assert "--verbose" in raw_help
    assert "--output=FILE?" in raw_help
    assert "Ctrl" in raw_help
    assert "Quit" in raw_help
    assert "https://example.com" in raw_help


def test_argument_parser_help_minimal_and_no_opts() -> None:
    parser = ArgumentParser(
        title="Short",
        subtitle="Sub",
        help_opts=(),
    )
    parser.add_arg("cmd", nargs="?", choices=["start", "stop"], help="Command")

    stream = io.StringIO()
    with patch("sys.stdout", stream):
        parser.print_help()
    help_text = stream.getvalue()
    assert "[cmd]" in help_text
    assert "Command" in help_text


def test_argument_parser_title_box_variants() -> None:
    # Title only, multiline:
    parser_title = ArgumentParser(title="Title Only", subtitle=None)
    output_title: list[Renderable] = []
    parser_title._add_title_box_to_output(output_title, 80, inline_subtitle=False)
    assert len(output_title) > 0

    # Subtitle only, multiline:
    parser_sub = ArgumentParser(title=None, subtitle="Subtitle Only")
    output_sub: list[Renderable] = []
    parser_sub._add_title_box_to_output(output_sub, 80, inline_subtitle=False)
    assert len(output_sub) > 0

    # Neither title nor subtitle:
    parser_empty = ArgumentParser(title=None, subtitle=None, help_opts=())
    output_empty: list[Renderable] = []
    parser_empty._add_title_box_to_output(output_empty, 80)
    assert len(output_empty) == 0

    # Default usage when no args and no opts:
    stream = io.StringIO()
    with patch("sys.stdout", stream):
        parser_empty.print_help()
    assert "Usage:" in stream.getvalue()


def test_argument_parser_usage_variants() -> None:
    parser_args_only = ArgumentParser(usage="{cmd} {args}", help_opts=())
    parser_args_only.add_arg("input")
    stream = io.StringIO()
    with patch("sys.stdout", stream):
        parser_args_only.print_help()
    assert "input" in stream.getvalue()

    parser_opts_only = ArgumentParser(usage="{cmd} {opts}")
    parser_opts_only.add_opt(["-f", "--flag"])
    stream_opts = io.StringIO()
    with patch("sys.stdout", stream_opts):
        parser_opts_only.print_help()
    assert "-f" in stream_opts.getvalue()


def test_argument_parser_examples_narrow_wrap() -> None:
    parser = ArgumentParser(
        title="App",
        examples=[
            (
                "{cmd} --very-long-option-name-that-does-not-fit-on-single-line",
                "Very long description comment that triggers multi line wrapping mode",
            )
        ],
    )
    stream = io.StringIO()
    with patch("sys.stdout", stream), patch("xulbux.console.get_width", return_value=40):
        parser.print_help()
    assert "Very long description" in stream.getvalue()


def test_argument_parser_examples_highlighting_non_intermixed() -> None:
    parser = ArgumentParser(
        title="App",
        intermixed=False,
        examples=[
            ("{cmd} pos_arg --opt=val", "Option after positional in non-intermixed"),
            ("{cmd} pos_arg -f -unknown", "Flag after positional in non-intermixed"),
            ("{cmd} pos_arg --unknown=val", "Unknown opt after positional"),
            ("{cmd} pos_arg extra_pos", "Second positional token"),
        ],
    )
    parser.add_arg("pos_arg")
    parser.add_opt(["-f", "--flag"])
    parser.add_opt(["-o", "--opt"], expects_value="VAL")

    stream = io.StringIO()
    with patch("sys.stdout", stream):
        parser.print_help()
    assert "pos_arg" in stream.getvalue()


def test_help_flag_triggers_exit() -> None:
    parser = ArgumentParser()
    parser.add_arg("cmd")

    with (
        patch("sys.argv", ["script.py", "--help"]),
        pytest.raises(SystemExit) as exc_info,
        patch("builtins.print"),
    ):
        parser.parse()
    assert exc_info.value.code == 0


def test_missing_required_arguments_and_options() -> None:
    parser = ArgumentParser()
    parser.add_arg("first")
    parser.add_arg("plus_items", nargs="+")
    parser.add_arg("last", nargs=1)
    parser.add_opt(["-c", "--config"], expects_value="PATH", required=True)

    # Missing positional argument:
    with patch("sys.argv", ["script.py", "--config=conf.json"]), pytest.raises(SystemExit):
        parser.parse()

    # Missing required option:
    with patch("sys.argv", ["script.py", "1", "2", "3"]), pytest.raises(SystemExit):
        parser.parse()

    # Missing positional argument with choices when nargs is int > 1:
    parser_multi = ArgumentParser()
    parser_multi.add_arg("items", nargs=2, choices=["x", "y"], required=True)
    with patch("sys.argv", ["script.py"]), pytest.raises(SystemExit):
        parser_multi.parse()

    # Missing positional argument with choices when nargs is "?":
    parser_question = ArgumentParser()
    parser_question.add_arg("opt_item", nargs="?", choices=["x", "y"], required=True)
    with patch("sys.argv", ["script.py"]), pytest.raises(SystemExit):
        parser_question.parse()

    # Missing positional argument without choices when nargs is "?":
    parser_q_no_choices = ArgumentParser()
    parser_q_no_choices.add_arg("plain_opt_item", nargs="?", required=True)
    with patch("sys.argv", ["script.py"]), pytest.raises(SystemExit):
        parser_q_no_choices.parse()


def test_validate_parsed_data_missing_argument_direct() -> None:
    parser = ArgumentParser()
    parser.add_arg("req_with_choices", choices=["a", "b"], required=True)
    parsed_data: dict[str, dict[str, Any]] = {"req_with_choices": {"exists": False, "values": []}}

    with pytest.raises(SystemExit):
        parser._validate_parsed_data(parsed_data)

    # Without choices:
    parser_no_choices = ArgumentParser()
    parser_no_choices.add_arg("req_no_choices", required=True)
    parsed_data_no_choices: dict[str, dict[str, Any]] = {"req_no_choices": {"exists": False, "values": []}}
    with pytest.raises(SystemExit):
        parser_no_choices._validate_parsed_data(parsed_data_no_choices)


def test_option_value_errors_and_choices() -> None:
    parser = ArgumentParser()
    parser.add_opt(["-f", "--flag"])  # Boolean flag (no value)
    parser.add_opt(["-c", "--choice"], expects_value="VAL", choices=["apple", "banana"])
    parser.add_opt(["-v", "--val"], expects_value="VALUE")

    # Option missing expected value:
    with patch("sys.argv", ["script.py", "--val"]), pytest.raises(SystemExit):
        parser.parse()

    # Option missing expected value with choices:
    with patch("sys.argv", ["script.py", "--choice"]), pytest.raises(SystemExit):
        parser.parse()

    # Disallowed choice value:
    with patch("sys.argv", ["script.py", "--choice=orange"]), pytest.raises(SystemExit):
        parser.parse()

    # Disallowed positional choice:
    parser_arg = ArgumentParser()
    parser_arg.add_arg("arg_choice", choices=["x", "y"])
    with patch("sys.argv", ["script.py", "z"]), pytest.raises(SystemExit):
        parser_arg.parse()


def test_unrecognized_arguments_and_options() -> None:
    parser = ArgumentParser()
    parser.add_arg("single_arg")

    # Extra unexpected positional argument:
    with patch("sys.argv", ["script.py", "arg1", "extra_arg"]), pytest.raises(SystemExit):
        parser.parse()

    # Unknown option:
    with patch("sys.argv", ["script.py", "arg1", "--unknown-opt"]), pytest.raises(SystemExit):
        parser.parse()

    # Unexpected argument when no positional arguments configured:
    empty_parser = ArgumentParser()
    with patch("sys.argv", ["script.py", "unexpected"]), pytest.raises(SystemExit):
        empty_parser.parse()
