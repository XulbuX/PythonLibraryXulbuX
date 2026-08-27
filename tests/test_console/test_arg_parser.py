from pathlib import Path
from typing import Any
from unittest.mock import patch
from xulbux.console import ArgumentParser, ParsedArgData, ParsedArgs, _is_number
import pytest


def test_is_number_internal_helper() -> None:
    assert _is_number("123") is True
    assert _is_number("-123") is True
    assert _is_number("3.14") is True
    assert _is_number("-3.14") is True
    assert _is_number("-.5") is True
    assert _is_number("-") is False
    assert _is_number("") is False
    assert _is_number("abc") is False
    assert _is_number("-abc") is False
    assert _is_number("1.2.3") is False
    assert _is_number("-.a") is False


def test_argument_parser_init_and_config() -> None:
    parser = ArgumentParser(
        title="My CLI",
        subtitle="CLI tool for automation",
        notice="Use with caution",
        usage="{cmd} {args} {opts}",
        controls=[("Q", "Quit"), (("W", "A", "S", "D"), "Move")],
        examples=[("my-cli --verbose", "Run verbosely")],
        epilog="Footer documentation",
        prefix_chars="-",
        opt_value_sep="=",
        intermixed=True,
    )

    assert parser.title == "My CLI"
    assert parser.subtitle == "CLI tool for automation"
    assert parser.prefix_chars == "-"

    with pytest.raises(ValueError, match="prefix_chars"):
        _ = ArgumentParser(prefix_chars="")
    with pytest.raises(ValueError, match="help_opts"):
        _ = ArgumentParser(help_opts=["invalid_opt"])


def test_add_positional_arguments() -> None:
    parser = ArgumentParser()
    parser.add_arg("input_file", help="Input file path")
    parser.add_arg("output_file", nargs="?", help="Optional output file")
    parser.add_arg("fixed_three", nargs=3, help="Three items")
    parser.add_arg("plus_args", nargs="+", help="One or more items")

    with patch("sys.argv", ["script.py", "in.txt", "out.txt", "1", "2", "3", "p1", "p2"]):
        result = parser.parse()
        assert result.input_file.exists is True
        assert result.input_file.val() == "in.txt"
        assert result.output_file.val() == "out.txt"
        assert result.fixed_three.vals(int) == (1, 2, 3)
        assert result.plus_args.vals() == ("p1", "p2")

    # Accessing undefined argument raises AttributeError with suggestions:
    with pytest.raises(AttributeError, match="not defined"):
        _ = result.undefined_arg
    with pytest.raises(AttributeError):
        _ = result._private


def test_add_options_and_flags() -> None:
    parser = ArgumentParser()
    parser.add_opt(["-v", "--verbose"], help="Verbose flag")
    parser.add_opt(["-c", "--count"], expects_value="N", help="Count option")
    parser.add_opt(["-o", "--output"], expects_value="FILE?", help="Optional file path")
    parser.add_opt(["-p", "--path"], expects_value="PATH", help="Path option")

    # Parsing with equal separator and space separator:
    with patch("sys.argv", ["script.py", "-v", "--count=5", "--output", "-p", "docs/dir"]):
        result = parser.parse()
        assert result.verbose.exists is True
        assert result.verbose.is_opt is True
        assert bool(result.verbose) is True
        assert result.count.val(int) == 5
        assert result.output.exists is True
        assert result.output.val() is None
        assert result.path.val(Path) == Path("docs/dir")

    # Option with choices:
    parser_choices = ArgumentParser()
    parser_choices.add_opt(["-m", "--mode"], expects_value="MODE", choices=["fast", "slow"])
    with patch("sys.argv", ["script.py", "--mode", "fast"]):
        result_choice = parser_choices.parse()
        assert result_choice.mode.val() == "fast"


def test_argument_parser_validation_errors() -> None:
    parser = ArgumentParser()
    parser.add_arg("arg1")
    parser.add_opt(["-f", "--flag"], "flag_alias")

    with pytest.raises(ValueError, match="underscore"):
        parser.add_arg("_invalid")
    with pytest.raises(ValueError, match="prefix char"):
        parser.add_arg("-invalid")
    with pytest.raises(ValueError, match="already defined"):
        parser.add_arg("arg1")
    with pytest.raises(ValueError, match="nargs"):
        parser.add_arg("bad_nargs", nargs=0)
    with pytest.raises(ValueError, match="nargs"):
        parser.add_arg("bad_nargs_str", nargs="invalid")  # type:ignore[arg-type]

    with pytest.raises(ValueError, match=r"opts.*cannot be empty"):
        parser.add_opt([])
    with pytest.raises(ValueError, match="invalid option"):
        parser.add_opt(["bad_opt"])
    with pytest.raises(ValueError, match="overlap with help"):
        parser.add_opt(["-h"])
    with pytest.raises(ValueError, match="overlap with existing argument"):
        parser.add_opt(["-f"])
    with pytest.raises(ValueError, match=r"alias.*underscore"):
        parser.add_opt(["-a"], "_alias")
    with pytest.raises(ValueError, match=r"alias.*already defined"):
        parser.add_opt(["-a"], "flag_alias")
    with pytest.raises(ValueError, match="expects_value"):
        parser.add_opt(["-b"], expects_value="???")


def test_parsed_arg_data_representations_and_casts() -> None:
    data = ParsedArgData(exists=True, values=("10", "20"), is_arg=True, opt=None)
    assert bool(data) is True
    assert data.is_opt is False
    assert str(data) == "10 20"
    assert "ParsedArgData" in repr(data)
    assert data.val(int) == 10
    assert data.vals(int) == (10, 20)

    # Casting errors:
    with pytest.raises(ValueError, match="Failed to cast value"):
        data.val(lambda v: int("not_a_number"))
    with pytest.raises(ValueError, match="Failed to cast value"):
        data.vals(lambda v: int("not_a_number"))

    empty_data = ParsedArgData(exists=False, values=(), is_arg=False, opt="-f")
    assert bool(empty_data) is False
    assert empty_data.is_opt is False
    assert str(empty_data) == ""
    assert empty_data.val(default="fallback") == "fallback"
    assert empty_data.vals(default=("fallback",)) == ("fallback",)
    assert "ParsedArgs" in repr(ParsedArgs())


def test_parse_special_delimiters_and_intermixed() -> None:
    parser = ArgumentParser(intermixed=False)
    parser.add_arg("target")
    parser.add_arg("rest", nargs="*")
    parser.add_opt(["-f", "--flag"])

    # Double-dash delimiter:
    with patch("sys.argv", ["script.py", "-f", "--", "--not-a-flag", "value"]):
        result = parser.parse()
        assert result.flag.exists is True
        assert result.target.val() == "--not-a-flag"
        assert result.rest.vals() == ("value",)

    # Non-intermixed stops option parsing after first positional:
    with patch("sys.argv", ["script.py", "my_target", "-f", "other"]):
        result_non_inter = parser.parse()
        assert result_non_inter.target.val() == "my_target"
        assert result_non_inter.rest.vals() == ("-f", "other")
        assert result_non_inter.flag.exists is False


def test_parse_empty_positional_handling() -> None:
    parser = ArgumentParser()
    parser.add_arg("opt_pos", nargs="?", required=False)
    parser.add_arg("fixed_pos", nargs=2, required=False)

    with patch("sys.argv", ["script.py"]):
        result = parser.parse()
        assert result.opt_pos.exists is False
        assert result.opt_pos.val() is None
        assert result.fixed_pos.exists is False


def test_internal_consume_opt_and_calc_remaining_branches() -> None:
    parser = ArgumentParser()
    parser._args_order = ["first", "second"]
    parser._arg_configs["second"] = {
        "is_arg": True,
        "nargs": "*",
        "required": True,
        "opts": None,
        "expects_value": None,
        "optional_value": False,
        "choices": None,
        "help": None,
    }
    # `_calculate_remaining_min` with `nargs="*"` and `required=True`:
    assert parser._calculate_remaining_min(0) == 0

    # `_consume_opt` with empty `expects_value` and `optional_value=False`:
    parser._arg_configs["custom_opt"] = {
        "is_arg": False,
        "nargs": 1,
        "required": False,
        "opts": frozenset({"-x"}),
        "expects_value": "",
        "optional_value": False,
        "choices": None,
        "help": None,
    }
    parsed_data: dict[str, dict[str, Any]] = {"custom_opt": {"exists": False, "opt": None, "values": []}}
    with pytest.raises(SystemExit):
        parser._consume_opt([], 0, "-x", None, "custom_opt", {}, parsed_data, True)
