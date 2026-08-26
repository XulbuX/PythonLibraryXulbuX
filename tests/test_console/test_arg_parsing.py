import sys
from xulbux.ansi import S, StyledText
from xulbux.console import ArgumentParser, ParsedArgData, ParsedArgs
import pytest


def test_parsed_arg_data():
    # Test `val()` and `vals()`:
    data = ParsedArgData(exists=True, values=("10", "20", "invalid"), is_arg=False, opt="-f")
    assert bool(data) is True
    assert str(data) == "10 20 invalid"
    assert data.val() == "10"
    assert data.val(int) == 10
    assert data.val(default="fallback") == "10"
    assert data.val(cast_type=int, default=0) == 10
    assert data.is_arg is False
    assert data.is_opt is True
    assert data.opt == "-f"

    valid_data = ParsedArgData(exists=True, values=("10", "20", "30"), is_arg=True)
    assert valid_data.vals() == ("10", "20", "30")
    assert valid_data.vals(int) == (10, 20, 30)
    assert valid_data.vals(default=()) == ("10", "20", "30")
    assert valid_data.vals(cast_type=int, default=()) == (10, 20, 30)
    assert valid_data.is_arg is True
    assert valid_data.is_opt is False

    # Test fallback default when casting fails:
    with pytest.raises(ValueError, match="Failed to cast value 'invalid' to"):
        data.vals(int, default=-1)

    # Test fallback default when not existing:
    empty_data = ParsedArgData(exists=False)
    assert empty_data.val() is None
    assert empty_data.val(default="") == ""
    assert empty_data.val(int) is None
    assert empty_data.val(int, default=42) == 42
    assert empty_data.val(cast_type=int, default=42) == 42
    assert empty_data.is_opt is False

    assert empty_data.vals() == ()
    assert empty_data.vals(default=None) is None
    assert empty_data.vals(default=()) == ()
    assert empty_data.vals(int) == ()
    assert empty_data.vals(int, default=None) is None
    assert empty_data.vals(int, default=42) == 42
    assert empty_data.vals(cast_type=int, default=()) == ()

    # Test existing option with no values:
    opt_only_data = ParsedArgData(exists=True, values=(), is_arg=False, opt="-v")
    assert opt_only_data.val() is None
    assert opt_only_data.val(default="") == ""
    assert opt_only_data.val(default="fallback") == "fallback"
    assert opt_only_data.vals() == ()
    assert opt_only_data.vals(default=None) is None
    assert opt_only_data.vals(default=()) == ()
    assert opt_only_data.is_opt is True


def test_parsed_args_attribute_access():
    args = ParsedArgs()
    args._add_arg("test1", ParsedArgData(exists=True))
    args._add_arg("test2", ParsedArgData(exists=False))
    args._add_arg("title", ParsedArgData(exists=True, values=("My App",)))

    assert args.test1.exists is True
    assert args.test2.exists is False
    assert args.title.val() == "My App"

    # Accessing an undefined argument raises informative AttributeError listing available args:
    with pytest.raises(
        AttributeError,
        match=r"Argument 'unknown' is not defined on 'ParsedArgs'\nAvailable arguments: 'test1', 'test2', 'title'",
    ):
        _ = args.unknown


def test_argument_parser_alias_validation(monkeypatch: pytest.MonkeyPatch):
    parser = ArgumentParser()

    # Aliases starting with underscore are rejected:
    with pytest.raises(ValueError, match="The 'alias' parameter cannot start with an underscore"):
        parser.add_opt({"-p"}, "_private")

    with pytest.raises(ValueError, match="The argument name cannot start with an underscore"):
        parser.add_arg("_private_pos")

    # Common names like title, controls, parse are fully allowed and work without collisions:
    parser.add_opt({"-t", "--title"}, expects_value="TITLE")
    parser.add_opt({"-c", "--controls"}, expects_value="CTRL")
    parser.add_opt({"-p", "--parse"}, expects_value=False)

    with pytest.raises(ValueError, match="overlap with existing argument"):
        parser.add_opt({"-t"}, "other_title")

    with pytest.raises(ValueError, match="is already defined on this 'ArgumentParser'"):
        parser.add_opt({"-t2", "--title2"}, "title")

    monkeypatch.setattr(sys, "argv", ["script.py", "-t=AppTitle", "-c=CtrlKey", "-p"])
    parsed = parser.parse()
    assert isinstance(parsed, ParsedArgs)
    assert parsed.title.val() == "AppTitle"
    assert parsed.controls.val() == "CtrlKey"
    assert parsed.parse.exists is True


def test_argument_parser_basic(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(sys, "argv", ["script.py", "-f=token", "-d"])
    parser = ArgumentParser()
    parser.add_opt({"-f", "--file"}, expects_value="VAL")
    parser.add_opt({"-d"}, expects_value=False)

    args = parser.parse()
    assert args.file.exists is True
    assert args.file.val() == "token"
    assert args.file.opt == "-f"

    assert args.d.exists is True
    assert args.d.values == ()
    assert args.d.opt == "-d"


def test_argument_parser_alias_deduction():
    parser = ArgumentParser()
    parser.add_opt({"-f", "--file"}, expects_value="VAL")
    parser.add_opt({"-o", "--to-file"}, expects_value="PATH")
    parser.add_opt({"-v", "--verbose"})
    parser.add_opt({"-a", "-b", "--custom-flag"}, "my_custom_alias")

    assert "file" in parser._arg_configs
    assert "to_file" in parser._arg_configs
    assert "verbose" in parser._arg_configs
    assert "my_custom_alias" in parser._arg_configs


def test_argument_parser_opt_pattern_validation():
    parser = ArgumentParser()
    with pytest.raises(ValueError, match="contains invalid option 'not a flag'"):
        parser.add_opt({"not a flag"})

    with pytest.raises(ValueError, match="The 'opts' parameter cannot be empty"):
        parser.add_opt(set())

    # Positional argument cannot start with prefix chars:
    with pytest.raises(ValueError, match="cannot start with prefix char"):
        parser.add_arg("-invalid_pos")


def test_argument_parser_custom_prefix_chars(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(sys, "argv", ["script.py", "/q", "+O=2", "/debug", "input.txt"])
    parser = ArgumentParser(prefix_chars="-/+")
    parser.add_opt({"/q", "/quiet"})
    parser.add_opt({"+O"}, "opt", expects_value="VAL")
    parser.add_opt({"/debug"})
    parser.add_arg("target_file")

    args = parser.parse()
    assert args.quiet.exists is True
    assert args.opt.val() == "2"
    assert args.debug.exists is True
    assert args.target_file.val() == "input.txt"


def test_argument_parser_positionals(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(sys, "argv", ["script.py", "pre1", "-f", "file.txt", "post1", "post2"])
    parser = ArgumentParser()
    parser.add_arg("before")
    parser.add_opt({"-f", "--file"}, expects_value="VAL")
    parser.add_arg("after", nargs="+")

    args = parser.parse()
    assert args.before.exists is True
    assert args.before.val() == "pre1"
    assert args.before.is_arg is True

    assert args.file.val() == "file.txt"

    assert args.after.exists is True
    assert args.after.vals() == ("post1", "post2")
    assert args.after.is_arg is True


def test_argument_parser_multi_positionals(monkeypatch: pytest.MonkeyPatch):
    # One or more with `nargs="+"`:
    monkeypatch.setattr(sys, "argv", ["script.py", "#ff0000", "#00ff00", "#0000ff", "-o", "gradient.png"])
    parser = ArgumentParser()
    parser.add_arg("color_points", nargs="+", help="Color stops")
    parser.add_opt({"-o", "--output"}, expects_value="PATH", help="Output file")

    args = parser.parse()
    assert args.color_points.exists is True
    assert args.color_points.vals() == ("#ff0000", "#00ff00", "#0000ff")
    assert args.color_points.is_arg is True
    assert args.output.val() == "gradient.png"


def test_argument_parser_positional_nargs_options(monkeypatch: pytest.MonkeyPatch):
    # Fixed count `nargs=2`, optional `nargs="?"`, zero-or-more `nargs="*"`:
    monkeypatch.setattr(sys, "argv", ["script.py", "10", "20", "extra1", "extra2"])
    parser = ArgumentParser()
    parser.add_arg("coords", nargs=2)
    parser.add_arg("extras", nargs="*")

    args = parser.parse()
    assert args.coords.vals() == ("10", "20")
    assert args.extras.vals() == ("extra1", "extra2")


def test_argument_parser_optional_fixed_nargs(monkeypatch: pytest.MonkeyPatch):
    parser = ArgumentParser()
    parser.add_arg("coords", nargs=2, required=False)
    parser.add_arg("extras", nargs="*")

    # 0 tokens provided:
    monkeypatch.setattr(sys, "argv", ["script.py"])
    args_empty = parser.parse()
    assert args_empty.coords.exists is False
    assert args_empty.coords.values == ()
    assert args_empty.extras.exists is False

    # 2 tokens provided:
    monkeypatch.setattr(sys, "argv", ["script.py", "10", "20", "extra1"])
    args_two = parser.parse()
    assert args_two.coords.exists is True
    assert args_two.coords.vals() == ("10", "20")
    assert args_two.extras.vals() == ("extra1",)

    # 1 token provided (incomplete):
    monkeypatch.setattr(sys, "argv", ["script.py", "10"])
    with pytest.raises(SystemExit):
        parser.parse()

    # Optional fixed nargs with subsequent required positional argument:
    parser2 = ArgumentParser()
    parser2.add_arg("coords", nargs=2, required=False)
    parser2.add_arg("file")

    monkeypatch.setattr(sys, "argv", ["script.py", "main.py"])
    args_sub1 = parser2.parse()
    assert args_sub1.coords.exists is False
    assert args_sub1.file.val() == "main.py"

    monkeypatch.setattr(sys, "argv", ["script.py", "10", "20", "main.py"])
    args_sub2 = parser2.parse()
    assert args_sub2.coords.vals() == ("10", "20")
    assert args_sub2.file.val() == "main.py"


def test_argument_parser_required_missing(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]):
    monkeypatch.setattr(sys, "argv", ["script.py"])
    parser = ArgumentParser()
    parser.add_opt({"-r", "--req"}, required=True)

    with pytest.raises(SystemExit) as exc:
        parser.parse()
    assert exc.value.code == 1

    clean_out = StyledText(capsys.readouterr().out).raw
    assert "script ERROR" in clean_out
    assert "Missing required option 'req' (-r, --req)" in clean_out
    assert "Run with --help for usage and available options." in clean_out
    assert "Options:" not in clean_out


def test_argument_parser_required_positional_missing(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]):
    monkeypatch.setattr(sys, "argv", ["script.py"])
    parser = ArgumentParser()
    parser.add_arg("input_file")

    with pytest.raises(SystemExit) as exc:
        parser.parse()
    assert exc.value.code == 1

    clean_out = StyledText(capsys.readouterr().out).raw
    assert "script ERROR" in clean_out
    assert "Missing required argument 'input_file'" in clean_out


def test_argument_parser_invalid_choice(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]):
    monkeypatch.setattr(sys, "argv", ["script.py", "-m=invalid"])
    parser = ArgumentParser()
    parser.add_opt({"-m", "--mode"}, expects_value="VAL", choices=["test", "prod"])

    with pytest.raises(SystemExit) as exc:
        parser.parse()
    assert exc.value.code == 1

    clean_out = StyledText(capsys.readouterr().out).raw
    assert "script ERROR" in clean_out
    assert "Invalid choice 'invalid' for 'mode' (-m, --mode)" in clean_out
    assert "Allowed: test, prod" in clean_out
    assert "Run with --help for usage and available options." in clean_out
    assert "Options:" not in clean_out


def test_argument_parser_help_flag(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]):
    monkeypatch.setattr(sys, "argv", ["script.py", "--help"])
    parser = ArgumentParser(title="MyCLI", epilog="Footer text")
    parser.add_opt({"-m", "--mode"}, expects_value="MODE", help="The mode to run")

    with pytest.raises(SystemExit) as exc:
        parser.parse()
    assert exc.value.code == 0

    captured = capsys.readouterr()
    assert "MyCLI" in captured.out
    assert "Footer text" in captured.out
    assert "The mode to run" in captured.out


def test_argument_parser_unknown_flags(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]):
    monkeypatch.setattr(sys, "argv", ["script.py", "--known", "--unknown1"])
    parser = ArgumentParser()
    parser.add_opt({"--known"}, expects_value=False)

    with pytest.raises(SystemExit) as exc:
        parser.parse()
    assert exc.value.code == 1

    clean_out = StyledText(capsys.readouterr().out).raw
    assert "script ERROR" in clean_out
    assert "Unrecognized option: '--unknown1'" in clean_out
    assert "Run with --help for usage and available options." in clean_out


def test_argument_parser_unexpected_positional(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]):
    monkeypatch.setattr(sys, "argv", ["script.py", "extra_arg"])
    parser = ArgumentParser()

    with pytest.raises(SystemExit) as exc:
        parser.parse()
    assert exc.value.code == 1

    clean_out = StyledText(capsys.readouterr().out).raw
    assert "script ERROR" in clean_out
    assert "Unrecognized argument: 'extra_arg'" in clean_out
    assert "Run with --help for usage and available options." in clean_out


def test_argument_parser_flag_missing_value(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]):
    monkeypatch.setattr(sys, "argv", ["script.py", "-f"])
    parser = ArgumentParser()
    parser.add_opt({"-f"}, "file", expects_value="VAL")

    with pytest.raises(SystemExit) as exc:
        parser.parse()
    assert exc.value.code == 1

    clean_out = StyledText(capsys.readouterr().out).raw
    assert "script ERROR" in clean_out
    assert "Option '-f' requires a value (expected <VAL>)" in clean_out
    assert "Run with --help for usage and available options." in clean_out


def test_argument_parser_custom_sep(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]):
    monkeypatch.setattr(sys, "argv", ["script.py", "--msg::hello"])
    parser = ArgumentParser()
    parser.add_opt({"--msg"}, "msg", expects_value="VAL")

    args = parser.parse(opt_value_sep="::")
    assert args.msg.val() == "hello"

    # Custom sep configured on `ArgumentParser`:
    parser2 = ArgumentParser(opt_value_sep="::")
    parser2.add_opt({"--msg"}, "msg", expects_value="VAL", help="Message option")
    parser2.print_help()

    out2 = capsys.readouterr().out
    clean2 = StyledText(out2).raw
    assert "--msg::VAL" in clean2

    args2 = parser2.parse()
    assert args2.msg.val() == "hello"

    # None sep configured on `ArgumentParser` (space-separated only):
    parser3 = ArgumentParser(opt_value_sep=None)
    parser3.add_opt({"--msg"}, "msg", expects_value="VAL", help="Message option")
    parser3.print_help()

    out3 = capsys.readouterr().out
    clean3 = StyledText(out3).raw
    assert "--msg VAL" in clean3


def test_argument_parser_allow_space_value(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(sys, "argv", ["script.py", "-m", "hello"])
    parser = ArgumentParser()
    parser.add_opt({"-m"}, "msg", expects_value="VAL")

    # By default `allow_space_value` is true:
    args1 = parser.parse()
    assert args1.msg.val() == "hello"

    # With `allow_space_value=False`, `-m` lacks a value:
    with pytest.raises(SystemExit):
        parser.parse(allow_space_value=False)


def test_argument_parser_flag_value_starting_with_dash(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(sys, "argv", ["script.py", "-o", "-my-output.txt", "-c", "-5"])
    parser = ArgumentParser()
    parser.add_opt({"-o"}, "output", expects_value="VAL")
    parser.add_opt({"-c"}, "count", expects_value="VAL")

    args = parser.parse()
    assert args.output.val() == "-my-output.txt"
    assert args.count.val() == "-5"


def test_argument_parser_negative_numbers_as_positionals(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(sys, "argv", ["script.py", "-10", "-d", "-3.14"])
    parser = ArgumentParser()
    parser.add_arg("pre")
    parser.add_opt({"-d"}, "debug", expects_value=False)
    parser.add_arg("post")

    args = parser.parse()
    assert args.pre.val() == "-10"
    assert args.debug.exists is True
    assert args.post.val() == "-3.14"


def test_argument_parser_bare_double_dash_delimiter(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(sys, "argv", ["script.py", "--known", "--", "-not-a-flag", "--also-pos"])
    parser = ArgumentParser()
    parser.add_opt({"--known"}, "known", expects_value=False)
    parser.add_arg("files", nargs="*")

    args = parser.parse()
    assert args.known.exists is True
    assert args.files.vals() == ("-not-a-flag", "--also-pos")


def test_argument_parser_interspersed_unknown_flag(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]):
    monkeypatch.setattr(sys, "argv", ["script.py", "--bool", "--unknown", "--known"])
    parser = ArgumentParser()
    parser.add_opt({"--bool"}, "bool", expects_value=False)
    parser.add_opt({"--known"}, "known", expects_value=False)
    parser.add_arg("files", nargs="*")

    with pytest.raises(SystemExit) as exc:
        parser.parse()
    assert exc.value.code == 1

    clean_out = StyledText(capsys.readouterr().out).raw
    assert "script ERROR" in clean_out
    assert "Unrecognized option: '--unknown'" in clean_out


def test_argument_parser_optional_value_flag(monkeypatch: pytest.MonkeyPatch):
    # Attached value:
    monkeypatch.setattr(sys, "argv", ["script.py", "-f=custom.log"])
    parser1 = ArgumentParser()
    parser1.add_opt({"-f", "--to-file"}, expects_value="PATH?")
    args1 = parser1.parse()
    assert args1.to_file.exists is True
    assert args1.to_file.val() == "custom.log"

    # Space-separated value:
    monkeypatch.setattr(sys, "argv", ["script.py", "--to-file", "other.log"])
    parser2 = ArgumentParser()
    parser2.add_opt({"-f", "--to-file"}, expects_value="PATH?")
    args2 = parser2.parse()
    assert args2.to_file.exists is True
    assert args2.to_file.val() == "other.log"

    # Bare flag at end (no value):
    monkeypatch.setattr(sys, "argv", ["script.py", "-f"])
    parser3 = ArgumentParser()
    parser3.add_opt({"-f", "--to-file"}, expects_value="PATH?")
    args3 = parser3.parse()
    assert args3.to_file.exists is True
    assert args3.to_file.val() is None
    assert args3.to_file.values == ()
    assert bool(args3.to_file) is True

    # Bare flag followed by another flag:
    monkeypatch.setattr(sys, "argv", ["script.py", "-f", "-v"])
    parser4 = ArgumentParser()
    parser4.add_opt({"-f", "--to-file"}, expects_value="PATH?")
    parser4.add_opt({"-v", "--verbose"}, expects_value=False)
    args4 = parser4.parse()
    assert args4.to_file.exists is True
    assert args4.to_file.val() is None
    assert args4.verbose.exists is True


def test_argument_parser_optional_value_help_print(capsys: pytest.CaptureFixture[str]):
    parser = ArgumentParser()
    parser.add_opt({"-f", "--to-file"}, expects_value="PATH?", help="Write to file")
    parser.print_help()

    captured = capsys.readouterr()
    clean_out = StyledText(captured.out).raw
    assert "-f, --to-file=PATH?" in clean_out

    # Check ANSI formatting of `?`:
    bold_blue_question = StyledText((S.BOLD | S.BLUE)("?")).ansi
    assert bold_blue_question in captured.out


def test_argument_parser_args_help_formatting(capsys: pytest.CaptureFixture[str]):
    parser = ArgumentParser()
    parser.add_arg("req_single", help="Required single")
    parser.add_arg("opt_single", required=False, help="Optional single")
    parser.add_arg("req_multi", nargs=3, help="Required 3")
    parser.add_arg("opt_multi", nargs=2, required=False, help="Optional 2")
    parser.add_arg("req_plus", nargs="+", help="Required 1+")
    parser.add_arg("opt_plus", nargs="+", required=False, help="Optional 1+")
    parser.add_arg("opt_star", nargs="*", help="Optional 0+")
    parser.add_arg("opt_q", nargs="?", help="Optional 0 or 1")
    parser.add_arg("req_q", nargs="?", required=True, help="Required 0 or 1")

    parser.print_help()

    captured = capsys.readouterr()
    clean_out = StyledText(captured.out).raw

    assert "<req_single>" in clean_out
    assert "[opt_single]" in clean_out
    assert "<req_multi [3]>" in clean_out
    assert "[opt_multi [2]]" in clean_out
    assert "<req_plus...>" in clean_out
    assert "[opt_plus...]" in clean_out
    assert "[opt_star...]" in clean_out
    assert "[opt_q]" in clean_out
    assert "<req_q>" in clean_out


def test_argument_parser_invalid_expects_value():
    parser = ArgumentParser()
    with pytest.raises(ValueError, match="The 'expects_value' parameter must be False or a string"):
        # `True` is not allowed, must be a string placeholder or `False`:
        parser.add_opt({"-f"}, expects_value=True)  # pyright:ignore[reportArgumentType]

    with pytest.raises(ValueError, match="The 'expects_value' parameter must be False or a string"):
        parser.add_opt({"-f"}, expects_value="Hi!")

    with pytest.raises(ValueError, match="The 'expects_value' parameter must be False or a string"):
        parser.add_opt({"-f"}, expects_value="")


def test_argument_parser_overlapping_flags():
    parser = ArgumentParser(help_opts={"-h"})
    with pytest.raises(ValueError, match="overlap with help options"):
        parser.add_opt({"-h"})

    parser.add_opt({"-t", "--test"})
    with pytest.raises(ValueError, match="overlap with existing argument"):
        parser.add_opt({"-t"})


def test_argument_parser_help_cross_section_alignment(capsys: pytest.CaptureFixture[str]):
    parser = ArgumentParser(
        title="Tree Generator",
        subtitle="Quickly generate directory trees",
        controls=[("Ctrl+C", "Cancel and exit")],
    )
    parser.add_arg("base_dir", help="Base directory to generate tree from")
    parser.add_opt({"-I", "--interactive"}, help="Prompt for interactive tree settings")
    parser.add_opt({"-i", "--ignore"}, expects_value="S", help="Directories to ignore")

    parser.print_help()

    captured = capsys.readouterr()
    lines = [StyledText(line).raw for line in captured.out.splitlines()]

    arg_line = next(line for line in lines if "Base directory to generate tree from" in line)
    opt_line = next(line for line in lines if "Prompt for interactive tree settings" in line)
    ctrl_line = next(line for line in lines if "Cancel and exit" in line)

    arg_col = arg_line.index("Base directory to generate tree from")
    opt_col = opt_line.index("Prompt for interactive tree settings")
    ctrl_col = ctrl_line.index("Cancel and exit")

    assert arg_col == opt_col == ctrl_col


def test_argument_parser_controls_multiple_keybinds(capsys: pytest.CaptureFixture[str]):
    parser = ArgumentParser(
        title="Game",
        controls=[
            (("WASD", "⏶⏴⏷⏵"), "Move the player"),
            (["Ctrl+C", "Ctrl+D"], "Exit the game"),
            ("Enter", "Start game"),
        ],
    )
    parser.print_help()

    captured = capsys.readouterr()
    raw_lines = [StyledText(line).raw for line in captured.out.splitlines()]
    ansi_lines = captured.out.splitlines()

    assert any("WASD, ⏶⏴⏷⏵" in line for line in raw_lines)
    assert any("Ctrl+C, Ctrl+D" in line for line in raw_lines)

    move_line = next(line for line in ansi_lines if "Move the player" in line)
    exit_line = next(line for line in ansi_lines if "Exit the game" in line)

    red_seq = StyledText(S.BR.RED).ansi
    dim_seq = StyledText(S.DIM).ansi

    assert f"{red_seq}WASD" in move_line
    assert f"{red_seq}⏶⏴⏷⏵" in move_line
    assert ", " in move_line

    assert f"{red_seq}Ctrl" in exit_line
    assert f"{dim_seq}+" in exit_line
    assert "C" in exit_line
    assert "D" in exit_line
    assert ", " in exit_line


def test_argument_parser_examples_syntax_highlighting_and_alignment(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr("xulbux.console.get_width", lambda: 120)

    parser = ArgumentParser(
        title="App",
        examples=[
            ("{cmd} -I", "Short example"),
            ('{cmd} -i "/path/with spaces | dir" --auto-ignore=1', "Long example with flag value"),
            ('{cmd} --recurse "/some/pos/path"', "Boolean flag followed by positional argument"),
        ],
    )
    parser.add_opt({"-i", "--ignore"}, expects_value="S", help="Directories to ignore")
    parser.add_opt({"-a", "--auto-ignore"}, expects_value="N", help="Auto-ignore mode")
    parser.add_opt({"-r", "--recurse"}, expects_value=False, help="Recurse subdirectories")
    parser.add_opt({"-I", "--interactive"}, expects_value=False, help="Interactive mode")

    parser.print_help()

    captured = capsys.readouterr()
    raw_lines = [StyledText(line).raw for line in captured.out.splitlines()]

    example_line1 = next(line for line in raw_lines if "Short example" in line)
    example_line2 = next(line for line in raw_lines if "Long example with flag value" in line)
    example_line3 = next(line for line in raw_lines if "Boolean flag followed by positional argument" in line)

    col1 = example_line1.index("# Short example")
    col2 = example_line2.index("# Long example with flag value")
    col3 = example_line3.index("# Boolean flag followed by positional argument")

    assert col1 == col2 == col3

    ansi_lines = captured.out.splitlines()
    ansi_line2 = next(line for line in ansi_lines if "Long example with flag value" in line)
    ansi_line3 = next(line for line in ansi_lines if "Boolean flag followed by positional argument" in line)

    cyan_seq = StyledText(S.BR.CYAN).ansi
    assert cyan_seq in ansi_line3
    blue_seq = StyledText(S.BR.BLUE).ansi
    assert blue_seq in ansi_line2
    assert blue_seq in ansi_line3
    green_seq = StyledText(S.BR.GREEN).ansi
    assert green_seq in ansi_line2
    assert green_seq in ansi_line3

    expected_flag_st = StyledText(S.BR.BLUE("--auto-ignore", S.DIM("="), "1")).ansi
    assert expected_flag_st in ansi_line2


def test_argument_parser_reactive_narrow_width_layout(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("xulbux.console.get_width", lambda: 60)

    parser = ArgumentParser(
        title="Tree Generator",
        subtitle="Quickly generate advanced and good looking directory trees",
        examples=[
            ("{cmd} -I", "Prompt for interactive settings"),
            ('{cmd} -i "/abs/to/dir1 | rel/to/dir2 | dir3"', "Ignore specified directories"),
        ],
    )
    parser.add_arg(
        "base_dir",
        help=("Base directory to generate tree from ", S.DIM("(default: CWD)")),
    )
    parser.add_opt(
        {"-i", "--ignore"},
        expects_value="S",
        help=("Directories to ignore ", S.DIM("(directory paths/names, separated by |)")),
    )

    parser.print_help()

    captured = capsys.readouterr()
    raw_lines = [StyledText(line).raw for line in captured.out.splitlines()]
    ansi_lines = captured.out.splitlines()

    # [1] Title box should be full width (60 chars):
    box_top = next(line for line in raw_lines if line.startswith("▄"))
    assert len(box_top) == 60

    # [2] Subtitle should be on its own line in the box (not following `—`):
    assert any("Quickly generate" in line for line in raw_lines)
    assert not any("Tree Generator — Quickly generate" in line for line in raw_lines)

    # [3] Examples should switch to stacked layout (comment line on top of command line):
    comment_idx = next(i for i, line in enumerate(raw_lines) if "# Prompt for interactive settings" in line)
    cmd_idx = next(i for i, line in enumerate(raw_lines) if "-I" in line and "#" not in line)
    assert comment_idx < cmd_idx

    # [4] Long descriptions in Options should wrap and continuation lines should be indented:
    continuation_line = next(line for line in raw_lines if "paths/names, separated by |)" in line)
    assert continuation_line.startswith(" ")

    # [5] Styling (e.g., dim sequence) in wrapped descriptions should be preserved:
    dim_seq = StyledText(S.DIM).ansi
    ansi_continuation = next(line for line in ansi_lines if "paths/names, separated by |)" in line)
    assert dim_seq in ansi_continuation


def test_argument_parser_notice(capsys: pytest.CaptureFixture[str]):
    parser = ArgumentParser(
        title="MyTool",
        notice=(S.BOLD | S.BR.YELLOW)("Warning: This is a test notice."),
    )
    parser.add_arg("cmd")
    parser.print_help()

    captured = capsys.readouterr()
    raw_lines = [StyledText(line).raw for line in captured.out.splitlines()]

    assert any("Warning: This is a test notice." in line for line in raw_lines)
    notice_idx = next(i for i, line in enumerate(raw_lines) if "Warning: This is a test notice." in line)
    usage_idx = next(i for i, line in enumerate(raw_lines) if "Usage:" in line)
    assert notice_idx < usage_idx


def test_argument_parser_non_intermixed(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(sys, "argv", ["xc.py", "--no-meta", "ls", "-la", "--sort=time"])
    parser = ArgumentParser(intermixed=False)
    parser.add_arg("command", nargs="+")
    parser.add_opt({"-nm", "--no-meta"})
    parser.add_opt({"-a", "--ansi"})

    args = parser.parse()
    assert args.no_meta.exists is True
    assert args.ansi.exists is False
    assert args.command.vals() == ("ls", "-la", "--sort=time")


def test_argument_parser_non_intermixed_unrecognized_option_before_pos(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    monkeypatch.setattr(sys, "argv", ["script.py", "--invalid-flag", "command"])
    parser = ArgumentParser(intermixed=False)
    parser.add_arg("command")

    with pytest.raises(SystemExit) as exc:
        parser.parse()
    assert exc.value.code == 1

    clean_out = StyledText(capsys.readouterr().out).raw
    assert "script ERROR" in clean_out
    assert "Unrecognized option: '--invalid-flag'" in clean_out


def test_argument_parser_error_box_formatting(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]):
    monkeypatch.setattr(sys, "argv", ["my_tool.py"])
    parser = ArgumentParser(title="MyTool")
    parser.add_opt({"-f", "--file"}, required=True)

    with pytest.raises(SystemExit) as exc:
        parser.parse()
    assert exc.value.code == 1

    captured = capsys.readouterr()
    clean_out = StyledText(captured.out).raw

    assert "▄" in clean_out
    assert "▀" in clean_out
    assert "MyTool ERROR" in clean_out
    assert "Missing required option 'file' (-f, --file)" in clean_out
    assert "Run with --help for usage and available options." in clean_out

    red_seq = StyledText(S.BR.RED).ansi
    assert red_seq in captured.out


def test_argument_parser_parse_intermixed_override(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(sys, "argv", ["script.py", "pos1", "-v", "pos2"])
    parser = ArgumentParser(intermixed=True)
    parser.add_arg("args", nargs="+")
    parser.add_opt({"-v", "--verbose"})

    # With default `intermixed=True`:
    args_intermixed = parser.parse()
    assert args_intermixed.verbose.exists is True
    assert args_intermixed.args.vals() == ("pos1", "pos2")

    # Overridden with intermixed=False in `parse()`:
    args_non_intermixed = parser.parse(intermixed=False)
    assert args_non_intermixed.verbose.exists is False
    assert args_non_intermixed.args.vals() == ("pos1", "-v", "pos2")


def test_argument_parser_subcommand_help_flag_non_intermixed(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(sys, "argv", ["xc.py", "pytest", "-h"])
    parser = ArgumentParser(intermixed=False)
    parser.add_arg("command", nargs="+")
    parser.add_opt({"-nc", "--no-command"})

    args = parser.parse()
    assert args.command.vals() == ("pytest", "-h")


def test_argument_parser_non_intermixed_examples_highlighting(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr("xulbux.console.get_width", lambda: 120)

    parser = ArgumentParser(
        title="XC",
        examples=[
            ("{cmd} --only ls -la", "Run and copy ls -la output only"),
        ],
        intermixed=False,
    )
    parser.add_arg("command", nargs="+")
    parser.add_opt({"-o", "--only"})
    parser.add_opt({"-a", "--ansi"})

    parser.print_help()

    captured = capsys.readouterr()
    ansi_line = next(line for line in captured.out.splitlines() if "ls -la" in line)

    blue_seq = StyledText(S.BR.BLUE).ansi
    cyan_seq = StyledText(S.BR.CYAN).ansi

    # `--only` should be blue, but `ls` and `-la` must be cyan (parsed as positional arguments):
    assert f"{blue_seq}--only" in ansi_line
    assert f"{cyan_seq}ls" in ansi_line
    assert f"{cyan_seq}-la" in ansi_line
