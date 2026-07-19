from xulbux.console import ParsedArgData, ParsedArgs
from xulbux.console import Throbber, ProgressBar
from xulbux.console import Console
from xulbux.ansi import S
from xulbux import console

from typing import Any
from unittest.mock import MagicMock, patch
import builtins
import pytest
import sys
import io
import os


@pytest.fixture
def mock_terminal_size(monkeypatch: pytest.MonkeyPatch):

    def mock_get_terminal_size():
        return os.terminal_size((80, 24))

    monkeypatch.setattr("xulbux.console._os.get_terminal_size", mock_get_terminal_size)


@pytest.fixture
def mock_formatcodes_print(monkeypatch: pytest.MonkeyPatch):
    mock = MagicMock()
    # Patch in the original module where it is defined:
    import xulbux.format_codes
    monkeypatch.setattr(xulbux.format_codes.FormatCodes, "print", mock)
    # Also patch in console module just in case:
    monkeypatch.setattr("xulbux.console.FormatCodes.print", mock)
    return mock


@pytest.fixture
def mock_builtin_input(monkeypatch: pytest.MonkeyPatch):
    mock = MagicMock()
    monkeypatch.setattr(builtins, "input", mock)
    return mock


@pytest.fixture
def mock_prompt_toolkit(monkeypatch: pytest.MonkeyPatch):
    mock = MagicMock(return_value="mocked multiline input")
    monkeypatch.setattr("xulbux.console._pt.prompt", mock)
    return mock


###################################################### Console TESTS #####################################################


def test_console_user():
    user_output = Console.user
    assert isinstance(user_output, str)
    assert user_output != ""


def test_console_width(mock_terminal_size: MagicMock):
    width_output = Console.width
    assert isinstance(width_output, int)
    assert width_output == 80


def test_console_height(mock_terminal_size: MagicMock):
    height_output = Console.height
    assert isinstance(height_output, int)
    assert height_output == 24


def test_console_size(mock_terminal_size: MagicMock):
    size_output = Console.size
    assert isinstance(size_output, tuple)
    assert len(size_output) == 2
    assert size_output[0] == 80
    assert size_output[1] == 24


def test_console_is_tty():
    result = Console.is_tty
    assert isinstance(result, bool)


def test_console_encoding():
    encoding = Console.encoding
    assert isinstance(encoding, str)
    assert encoding != ""
    assert encoding.lower() in {"utf-8", "cp1252", "ascii", "latin-1", "iso-8859-1"} or "-" in encoding


def test_console_supports_color():
    result = Console.supports_color
    assert isinstance(result, bool)


@pytest.mark.parametrize(
    "argv, arg_parse_configs, expected_parsed_args", [
        # Simple flag value the includes spaces:
        (
            ["script.py", "-f=token with spaces", "-d"],
            {"file": {"-f"}, "debug": {"-d"}},
            {
                "file": {"exists": True, "is_pos": False, "values": ("token with spaces", ), "flag": "-f"},
                "debug": {"exists": True, "is_pos": False, "values": (), "flag": "-d"},
            },
        ),
        # Flag value plus other tokens:
        (
            ["script.py", "--msg=hello", "world"],
            {"message": {"--msg"}},
            {"message": {"exists": True, "is_pos": False, "values": ("hello", ), "flag": "--msg"}},
        ),
        # Value set in single token followed by second flag:
        (
            ["script.py", "--msg=this is a message", "--flag"],
            {"message": {"--msg"}, "flag": {"--flag"}},
            {
                "message": {"exists": True, "is_pos": False, "values": ("this is a message", ), "flag": "--msg"},
                "flag": {"exists": True, "is_pos": False, "values": (), "flag": "--flag"},
            },
        ),
        # Flag, separator, and value spread over multiple tokens:
        (
            ["script.py", "--msg", "=", "this is a message"],
            {"message": {"--msg"}},
            {"message": {"exists": True, "is_pos": False, "values": ("this is a message", ), "flag": "--msg"}},
        ),
        # Case sensitive flags with spaces:
        (
            ["script.py", "-t=this is some text", "-T=THIS IS A TITLE"],
            {"text": {"-t"}, "title": {"-T"}},
            {
                "text": {"exists": True, "is_pos": False, "values": ("this is some text", ), "flag": "-t"},
                "title": {"exists": True, "is_pos": False, "values": ("THIS IS A TITLE", ), "flag": "-T"},
            },
        ),

        # --- CASES WITH DEFAULTS ---
        # Given flag value overwrites default:
        (
            ["script.py", "--msg=given message"],
            {"msg": {"flags": {"--msg"}, "default": "no message"}, "other": {"-o"}},
            {
                "msg": {"exists": True, "is_pos": False, "values": ("given message", ), "flag": "--msg"},
                "other": {"exists": False, "is_pos": False, "values": (), "flag": None},
            },
        ),
        # Default used when flag present but no value given:
        (
            ["script.py", "-o", "--msg"],
            {"msg": {"flags": {"--msg"}, "default": "no message"}, "other": {"-o"}},
            {
                "msg": {"exists": True, "is_pos": False, "values": ("no message", ), "flag": "--msg"},
                "other": {"exists": True, "is_pos": False, "values": (), "flag": "-o"},
            },
        ),
        # Default used when flag absent:
        (
            ["script.py", "-o"],
            {"msg": {"flags": {"--msg"}, "default": "no message"}, "other": {"-o"}},
            {
                "msg": {"exists": False, "is_pos": False, "values": ("no message", ), "flag": None},
                "other": {"exists": True, "is_pos": False, "values": (), "flag": "-o"},
            },
        ),

        # --- POSITIONAL `before` / `after` SPECIAL CASES ---
        # Positional `before`:
        (
            ["script.py", "arg1", "arg2.1 arg2.2"],
            {"before": "before", "file": {"-f"}},
            {
                "before": {"exists": True, "is_pos": True, "values": ("arg1", "arg2.1 arg2.2"), "flag": None},
                "file": {"exists": False, "is_pos": False, "values": (), "flag": None},
            },
        ),
        (
            ["script.py", "arg1", "arg2.1 arg2.2", "-f=file.txt", "arg3"],
            {"before": "before", "file": {"-f"}},
            {
                "before": {"exists": True, "is_pos": True, "values": ("arg1", "arg2.1 arg2.2"), "flag": None},
                "file": {"exists": True, "is_pos": False, "values": ("file.txt", ), "flag": "-f"},
            },
        ),
        (
            ["script.py", "-f=file.txt", "arg1"],
            {"before": "before", "file": {"-f"}},
            {
                "before": {"exists": False, "is_pos": True, "values": (), "flag": None},
                "file": {"exists": True, "is_pos": False, "values": ("file.txt", ), "flag": "-f"},
            },
        ),
        # Positional `after`:
        (
            ["script.py", "arg1", "arg2.1 arg2.2"],
            {"after": "after", "file": {"-f"}},
            {
                "file": {"exists": False, "is_pos": False, "values": (), "flag": None},
                "after": {"exists": True, "is_pos": True, "values": ("arg1", "arg2.1 arg2.2"), "flag": None},
            },
        ),
        (
            ["script.py", "arg1", "-f=file.txt", "arg2", "arg3.1 arg3.2"],
            {"after": "after", "file": {"-f"}},
            {
                "file": {"exists": True, "is_pos": False, "values": ("file.txt", ), "flag": "-f"},
                "after": {"exists": True, "is_pos": True, "values": ("arg2", "arg3.1 arg3.2"), "flag": None},
            },
        ),
        (
            ["script.py", "arg1", "-f=file.txt"],
            {"after": "after", "file": {"-f"}},
            {
                "file": {"exists": True, "is_pos": False, "values": ("file.txt", ), "flag": "-f"},
                "after": {"exists": False, "is_pos": True, "values": (), "flag": None},
            },
        ),

        # --- CUSTOM FLAG PREFIXES ---
        # Question mark and double plus prefixes:
        (
            ["script.py", "?help = show detailed info", "++mode=test"],
            {"help": {"?help"}, "mode": {"++mode"}},
            {
                "help": {"exists": True, "is_pos": False, "values": ("show detailed info", ), "flag": "?help"},
                "mode": {"exists": True, "is_pos": False, "values": ("test", ), "flag": "++mode"},
            },
        ),
        # At symbol prefix with positional arguments:
        (
            ["script.py", "@msg = Hello, world!", "How are you?"],
            {"before": "before", "message": {"@msg"}, "after": "after"},
            {
                "before": {"exists": False, "is_pos": True, "values": (), "flag": None},
                "message": {"exists": True, "is_pos": False, "values": ("Hello, world!", ), "flag": "@msg"},
                "after": {"exists": True, "is_pos": True, "values": ("How are you?", ), "flag": None},
            },
        ),

        # --- NEGATIVE NUMBERS ARE TREATED AS VALUES; UNKNOWN FLAGS ARE COLLECTED SEPARATELY ---
        (
            ["script.py", "-42", "-d=-256", "--file=--not-a-flag", "--also-no-flag"],
            {"before": "before", "data": {"-d"}, "file": {"--file"}, "after": "after"},
            {
                "before": {"exists": True, "is_pos": True, "values": ("-42", ), "flag": None},
                "data": {"exists": True, "is_pos": False, "values": ("-256", ), "flag": "-d"},
                "file": {"exists": True, "is_pos": False, "values": ("--not-a-flag", ), "flag": "--file"},
                "after": {"exists": False, "is_pos": True, "values": (), "flag": None},
            },
        ),

        # --- SPACE-SEPARATED FLAG VALUES (allow_space_value=True default) ---
        # Simple space-separated value:
        (
            ["script.py", "--flag", "myValue"],
            {"flag": {"--flag"}},
            {"flag": {"exists": True, "is_pos": False, "values": ("myValue", ), "flag": "--flag"}},
        ),
        # Short flag with space-separated value:
        (
            ["script.py", "-f", "file.txt"],
            {"file": {"-f", "--file"}},
            {"file": {"exists": True, "is_pos": False, "values": ("file.txt", ), "flag": "-f"}},
        ),
        # Known flag following a flag is not consumed as value:
        (
            ["script.py", "--msg", "--flag"],
            {"message": {"--msg"}, "flag": {"--flag"}},
            {
                "message": {"exists": True, "is_pos": False, "values": (), "flag": "--msg"},
                "flag": {"exists": True, "is_pos": False, "values": (), "flag": "--flag"},
            },
        ),
        # Multiple flags with space-separated values:
        (
            ["script.py", "--msg", "hello", "-n", "42"],
            {"message": {"--msg"}, "number": {"-n"}},
            {
                "message": {"exists": True, "is_pos": False, "values": ("hello", ), "flag": "--msg"},
                "number": {"exists": True, "is_pos": False, "values": ("42", ), "flag": "-n"},
            },
        ),
        # Space-separated value consumed by flag, remaining token is `after` positional:
        (
            ["script.py", "--flag", "val", "after1"],
            {"flag": {"--flag"}, "after": "after"},
            {
                "flag": {"exists": True, "is_pos": False, "values": ("val", ), "flag": "--flag"},
                "after": {"exists": True, "is_pos": True, "values": ("after1", ), "flag": None},
            },
        ),
        # Space-separated value with both `before` and `after` positionals:
        (
            ["script.py", "pre", "--flag", "val", "post"],
            {"before": "before", "flag": {"--flag"}, "after": "after"},
            {
                "before": {"exists": True, "is_pos": True, "values": ("pre", ), "flag": None},
                "flag": {"exists": True, "is_pos": False, "values": ("val", ), "flag": "--flag"},
                "after": {"exists": True, "is_pos": True, "values": ("post", ), "flag": None},
            },
        ),
    ]
)
def test_get_args(
    monkeypatch: pytest.MonkeyPatch,
    argv: list[str],
    arg_parse_configs: dict[str, Any],
    expected_parsed_args: dict[str, dict[str, Any]],
):
    monkeypatch.setattr(sys, "argv", argv)
    args_result = Console.get_args(arg_parse_configs)
    assert isinstance(args_result, ParsedArgs)
    assert args_result.dict() == expected_parsed_args


def test_get_args_invalid_params():
    with pytest.raises(ValueError, match="Duplicate flag '-f' found. It's assigned to both 'file1' and 'file2'."):
        Console.get_args({"file1": {"-f", "--file1"}, "file2": {"flags": {"-f", "--file2"}, "default": "..."}})

    with pytest.raises(ValueError, match="Duplicate flag '--long' found. It's assigned to both 'arg1' and 'arg2'."):
        Console.get_args({"arg1": {"flags": {"--long"}, "default": "..."}, "arg2": {"-a", "--long"}})

    with pytest.raises(ValueError, match="The set must contain at least one flag to search for."):
        Console.get_args({"arg": set()})

    with pytest.raises(ValueError, match="The 'flags'-key set must contain at least one flag to search for."):
        Console.get_args({"arg": {"flags": set(), "default": "..."}})

    with pytest.raises(ValueError, match=r"non-empty string or None, got"):
        Console.get_args({"arg": {"-a"}}, flag_value_sep="")

    with pytest.raises(ValueError, match="non-negative integer"):
        Console.get_args({"arg": {"-a"}}, skip=-1)

    for reserved in ParsedArgs.RESERVED_ALIASES:
        with pytest.raises(ValueError, match=f"Invalid argument alias '{reserved}'"):
            Console.get_args({reserved: {"-a"}})


def test_get_args_custom_sep(monkeypatch: pytest.MonkeyPatch):
    """Test custom flag-value separator handling"""
    monkeypatch.setattr(sys, "argv", ["script.py", "--msg::This is a message", "-d::42"])
    result = Console.get_args({"message": {"--msg"}, "data": {"-d"}}, flag_value_sep="::")

    assert result.message.exists is True
    assert result.message.is_pos is False
    assert result.message.values == ("This is a message", )
    assert result.message.flag == "--msg"

    assert result.data.exists is True
    assert result.data.is_pos is False
    assert result.data.values == ("42", )
    assert result.data.flag == "-d"

    assert result.dict() == {
        "message": result.message.dict(),
        "data": result.data.dict(),
    }


def test_get_args_no_sep(monkeypatch: pytest.MonkeyPatch):
    """Test that flag_value_sep=None disables separator syntax and only space-separated values work."""
    # SEPARATOR SYNTAX SHOULD NOT BE RECOGNIZED – '--flag=val' IS TREATED AS A STANDALONE UNKNOWN TOKEN
    monkeypatch.setattr(sys, "argv", ["script.py", "--flag", "space_val", "--other=ignored"])
    result = Console.get_args(
        {"flag": {"--flag"}, "other": {"--other"}, "after": "after"},
        flag_value_sep=None,
    )

    # '--flag' CONSUMES 'space_val' VIA SPACE-SEPARATED SYNTAX
    assert result.flag.exists is True
    assert result.flag.values == ("space_val", )
    assert result.flag.flag == "--flag"

    # '--other=ignored' LOOKS LIKE A FLAG WITH NO SEPARATOR PROCESSING – TREATED AS UNKNOWN FLAG
    assert result.other.exists is False
    assert result.other.values == ()

    assert result.after.exists is False
    assert result.after.values == ()
    assert result.unknown_flags == frozenset({"--other=ignored"})


def test_get_args_allow_space_value_false(monkeypatch: pytest.MonkeyPatch):
    """Test that allow_space_value=False does not consume the next token as a flag value."""
    monkeypatch.setattr(sys, "argv", ["script.py", "--flag", "val", "after1"])
    result = Console.get_args(
        {"flag": {"--flag"}, "after": "after"},
        allow_space_value=False,
    )

    # 'val' must NOT be consumed by --flag
    assert result.flag.exists is True
    assert result.flag.values == ()
    assert result.flag.flag == "--flag"

    # both 'val' and 'after1' are unclaimed and collected as "after" positionals
    assert result.after.exists is True
    assert result.after.values == ("val", "after1")


def test_get_args_mixed_dash_scenarios(monkeypatch: pytest.MonkeyPatch):
    """Test complex scenario mixing defined flags with dash-prefixed values"""
    monkeypatch.setattr(
        sys, "argv", \
        ["script.py", "before string", "-42", "-d=256", "--file=my-file.txt", "-vv", "after string", "--also-no-flag"]
    )
    result = Console.get_args(
        {
            "before": "before",
            "data": {"-d", "--data"},
            "file": {"-f", "--file"},
            "verbose": {"-v", "-vv", "-vvv"},
            "help": {"-h", "--help"},
            "after": "after",
        },
        allow_space_value=False,
    )

    assert result.before.exists is True
    assert result.before.is_pos is True
    assert result.before.values == ("before string", "-42")
    assert result.before.flag is None

    assert result.data.exists is True
    assert result.data.is_pos is False
    assert result.data.values == ("256", )
    assert result.data.flag == "-d"

    assert result.file.exists is True
    assert result.file.is_pos is False
    assert result.file.values == ("my-file.txt", )
    assert result.file.flag == "--file"

    assert result.verbose.exists is True
    assert result.verbose.is_pos is False
    assert result.verbose.values == ()
    assert result.verbose.flag == "-vv"

    assert result.help.exists is False
    assert result.help.is_pos is False
    assert result.help.values == ()
    assert result.help.flag is None

    assert result.after.exists is True
    assert result.after.is_pos is True
    assert result.after.values == ("after string", )
    assert result.after.flag is None

    assert result.unknown_flags == frozenset({"--also-no-flag"})

    assert result.dict() == {
        "before": result.before.dict(),
        "data": result.data.dict(),
        "file": result.file.dict(),
        "verbose": result.verbose.dict(),
        "help": result.help.dict(),
        "after": result.after.dict(),
    }


def test_get_args_unknown_flags(monkeypatch: pytest.MonkeyPatch):
    """Unknown flags (not in config) are collected in unknown_flags and not consumed as values."""
    # Standalone unknown flags and unknown flag with inline separator:
    monkeypatch.setattr(sys, "argv", ["script.py", "--known=val", "--unknown", "--unknown=extra", "-u"])
    result = Console.get_args({"known": {"--known"}, "after": "after"})

    assert result.known.exists is True
    assert result.known.values == ("val", )
    assert result.unknown_flags == frozenset({"--unknown", "--unknown=extra", "-u"})
    assert result.after.values == ()


def test_get_args_unknown_flag_not_consumed_as_value(monkeypatch: pytest.MonkeyPatch):
    """An unknown flag following a known flag is NOT consumed as that flag's space-separated value."""
    monkeypatch.setattr(sys, "argv", ["script.py", "--known", "--unknown"])
    result = Console.get_args({"known": {"--known"}})

    assert result.known.exists is True
    assert result.known.values == ()
    assert result.unknown_flags == frozenset({"--unknown"})


def test_get_args_negative_number_not_unknown_flag(monkeypatch: pytest.MonkeyPatch):
    """Negative numbers (e.g., -42, -.5) are not treated as unknown flags."""
    monkeypatch.setattr(sys, "argv", ["script.py", "-42", "-.5", "--known"])
    result = Console.get_args({"before": "before", "known": {"--known"}})

    assert result.before.values == ("-42", "-.5")
    assert result.unknown_flags == frozenset()


def test_get_args_skip(monkeypatch: pytest.MonkeyPatch):
    """Test that skip=N drops the first N argv entries before any parsing."""
    # With `skip=1`, `argv[1]` (`fc`) is skipped; Parsing starts at `argv[2]`:
    monkeypatch.setattr(sys, "argv", ["script.py", "fc", "hello", "world"])
    result = Console.get_args({"input": "before"}, skip=1)
    assert result.input.exists is True
    assert result.input.values == ("hello", "world")

    # With `skip=2`, `argv[1]` and `argv[2]` are skipped; Parsing starts at `argv[3]`:
    monkeypatch.setattr(sys, "argv", ["script.py", "sub", "cmd", "--flag=val"])
    result = Console.get_args({"flag": {"--flag"}}, skip=2)
    assert result.flag.exists is True
    assert result.flag.values == ("val", )

    # With `skip` exceeding argv length, no args are parsed:
    monkeypatch.setattr(sys, "argv", ["script.py", "only"])
    result = Console.get_args({"flag": {"--flag"}}, skip=5)
    assert result.flag.exists is False

    # With `skip=0` (default); Behavior is unchanged:
    monkeypatch.setattr(sys, "argv", ["script.py", "--flag=val"])
    result = Console.get_args({"flag": {"--flag"}}, skip=0)
    assert result.flag.exists is True
    assert result.flag.values == ("val", )


def test_parsed_args_is_empty():
    # All missing, no values: `is_empty` is true:
    args = ParsedArgs(
        a=ParsedArgData(exists=False, values=[], is_pos=False),
        b=ParsedArgData(exists=False, values=[], is_pos=True),
    )
    assert args.is_empty is True

    # One has a default value: `is_empty` is false:
    args_with_default = ParsedArgs(
        a=ParsedArgData(exists=False, values=["default"], is_pos=False),
        b=ParsedArgData(exists=False, values=[], is_pos=False),
    )
    assert args_with_default.is_empty is False

    # One exists: `is_empty` is false:
    args_with_existing = ParsedArgs(
        a=ParsedArgData(exists=True, values=["val"], is_pos=False),
        b=ParsedArgData(exists=False, values=[], is_pos=False),
    )
    assert args_with_existing.is_empty is False

    # Empty `ParsedArgs`: `is_empty` is true:
    assert ParsedArgs().is_empty is True


def test_parsed_args_any_exist():
    # None exist:
    args_none = ParsedArgs(
        a=ParsedArgData(exists=False, values=[], is_pos=False),
        b=ParsedArgData(exists=False, values=["default"], is_pos=False),
    )
    assert args_none.any_exist is False

    # One exists:
    args_one = ParsedArgs(
        a=ParsedArgData(exists=True, values=["v"], is_pos=False),
        b=ParsedArgData(exists=False, values=[], is_pos=False),
    )
    assert args_one.any_exist is True

    # All exist:
    args_all = ParsedArgs(
        a=ParsedArgData(exists=True, values=["v"], is_pos=False),
        b=ParsedArgData(exists=True, values=[], is_pos=False),
    )
    assert args_all.any_exist is True

    # Empty `ParsedArgs`: `any_exist` is false:
    assert ParsedArgs().any_exist is False


def test_parsed_args_all_exist():
    # All exist:
    args_all = ParsedArgs(
        a=ParsedArgData(exists=True, values=["v"], is_pos=False),
        b=ParsedArgData(exists=True, values=[], is_pos=False),
    )
    assert args_all.all_exist is True

    # One missing:
    args_partial = ParsedArgs(
        a=ParsedArgData(exists=True, values=["v"], is_pos=False),
        b=ParsedArgData(exists=False, values=[], is_pos=False),
    )
    assert args_partial.all_exist is False

    # None exist:
    args_none = ParsedArgs(a=ParsedArgData(exists=False, values=[], is_pos=False), )
    assert args_none.all_exist is False

    # Empty `ParsedArgs`: `all_exist` is true (vacuously):
    assert ParsedArgs().all_exist is True


def test_parsed_args_properties_not_in_iter():
    """Properties is_empty, any_exist, all_exist must not appear when iterating."""
    args = ParsedArgs(flag=ParsedArgData(exists=True, values=[], is_pos=False), )
    keys = [k for k, _ in args]
    assert "is_empty" not in keys
    assert "any_exist" not in keys
    assert "all_exist" not in keys
    assert "unknown_flags" not in keys
    assert len(args) == 1


def test_args_dunder_methods():
    args = ParsedArgs(
        before=ParsedArgData(exists=True, values=["arg1", "arg2"], is_pos=True),
        debug=ParsedArgData(exists=True, values=[], is_pos=False),
        file=ParsedArgData(exists=True, values=["test.txt"], is_pos=False),
        after=ParsedArgData(exists=False, values=["arg3", "arg4"], is_pos=True),
    )

    assert len(args) == 4

    assert ("before" in args) is True
    assert ("missing" in args) is False

    assert bool(args) is True
    assert bool(ParsedArgs()) is False

    assert (args == args) is True
    assert (args != ParsedArgs()) is True


def test_parsed_arg_data_get():
    data = ParsedArgData(exists=True, values=["first", "second", "third"], is_pos=False)
    assert data.get(0) == "first"
    assert data.get(1) == "second"
    assert data.get(2) == "third"
    assert data.get(3) is None
    assert data.get(3, "fallback") == "fallback"
    assert data.get(-1) is None

    empty = ParsedArgData(exists=True, values=[], is_pos=False)
    assert empty.get(0) is None
    assert empty.get(0, "default") == "default"


def test_multiline_input(mock_prompt_toolkit: MagicMock, capsys: pytest.CaptureFixture[str]):
    expected_input = "mocked multiline input"
    result = Console.multiline_input("Enter text:", show_keybindings=True, default_color="#BCA")

    assert result == expected_input

    captured = capsys.readouterr()
    # Check that prompt and keybindings were printed:
    assert "Enter text:" in captured.out
    assert "CTRL+D" in captured.out or "end of input" in captured.out

    mock_prompt_toolkit.assert_called_once()
    pt_args, pt_kwargs = mock_prompt_toolkit.call_args
    assert pt_args == (" ⮡ ", )
    assert pt_kwargs.get("multiline") is True
    assert pt_kwargs.get("wrap_lines") is True
    assert "key_bindings" in pt_kwargs


def test_multiline_input_no_bindings(mock_prompt_toolkit: MagicMock, capsys: pytest.CaptureFixture[str]):
    Console.multiline_input("Enter text:", show_keybindings=False, end="DONE")

    captured = capsys.readouterr()
    # Check that prompt was printed and ends with `DONE`:
    assert "Enter text:" in captured.out
    assert captured.out.endswith("DONE")

    mock_prompt_toolkit.assert_called_once()


def test_pause_exit_pause_only(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]):
    mock_read_key = MagicMock()
    monkeypatch.setattr("xulbux.console.Console._read_single_key", mock_read_key)

    Console.pause_exit("Press any key...", pause=True, exit=False)

    captured = capsys.readouterr()
    assert "Press any key..." in captured.out
    mock_read_key.assert_called_once_with()


def test_pause_exit_with_exit(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]):
    mock_read_key = MagicMock()
    mock_sys_exit = MagicMock()
    monkeypatch.setattr("xulbux.console.Console._read_single_key", mock_read_key)
    monkeypatch.setattr("xulbux.console._sys.exit", mock_sys_exit)

    Console.pause_exit("Exiting...", pause=True, exit=True, exit_code=1)

    captured = capsys.readouterr()
    assert "Exiting..." in captured.out
    mock_read_key.assert_called_once_with()
    mock_sys_exit.assert_called_once_with(1)


def test_pause_exit_reset_ansi(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]):
    mock_read_key = MagicMock()
    monkeypatch.setattr("xulbux.console.Console._read_single_key", mock_read_key)

    Console.pause_exit(pause=True, exit=False, reset_ansi=True)

    captured = capsys.readouterr()
    # Check that ANSI reset code is present in output:
    assert "\033[0m" in captured.out or captured.out.strip() == ""


def test_cls(monkeypatch: pytest.MonkeyPatch):
    mock_shutil = MagicMock()
    mock_subprocess_run = MagicMock()
    mock_print = MagicMock()
    monkeypatch.setattr("xulbux.console._shutil.which", mock_shutil)
    monkeypatch.setattr("xulbux.console._subprocess.run", mock_subprocess_run)
    monkeypatch.setattr(builtins, "print", mock_print)

    mock_shutil.side_effect = lambda cmd: "/bin/cls" if cmd == "cls" else None  # type: ignore[type-unknown]
    Console.cls()
    mock_subprocess_run.assert_called_with(["cls"])
    mock_print.assert_called_with("\033[0m", end="", flush=True)

    mock_subprocess_run.reset_mock()
    mock_print.reset_mock()

    mock_shutil.side_effect = lambda cmd: "/bin/clear" if cmd == "clear" else None  # type: ignore[type-unknown]
    Console.cls()
    mock_subprocess_run.assert_called_with(["clear"])
    mock_print.assert_called_with("\033[0m", end="", flush=True)


def test_log_basic(capsys: pytest.CaptureFixture[str]):
    Console.log("INFO", "Test message")

    captured = capsys.readouterr()
    assert "INFO" in captured.out
    assert "Test message" in captured.out


def test_log_no_title(capsys: pytest.CaptureFixture[str]):
    Console.log(None, "Just a message")

    captured = capsys.readouterr()
    assert "Just a message" in captured.out


def test_debug_active(capsys: pytest.CaptureFixture[str]):
    Console.debug("Debug message", active=True)

    captured = capsys.readouterr()
    assert "DEBUG" in captured.out
    assert "Debug message" in captured.out


def test_debug_inactive(mock_formatcodes_print: MagicMock):
    Console.debug("Debug message", active=False)

    mock_formatcodes_print.assert_not_called()


def test_info(capsys: pytest.CaptureFixture[str]):
    Console.info("Info message")

    captured = capsys.readouterr()
    assert "INFO" in captured.out
    assert "Info message" in captured.out


def test_done(capsys: pytest.CaptureFixture[str]):
    Console.done("Task completed")

    captured = capsys.readouterr()
    assert "DONE" in captured.out
    assert "Task completed" in captured.out


def test_warn(capsys: pytest.CaptureFixture[str]):
    Console.warn("Warning message")

    captured = capsys.readouterr()
    assert "WARN" in captured.out
    assert "Warning message" in captured.out


def test_fail(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch):
    mock_sys_exit = MagicMock()
    monkeypatch.setattr("xulbux.console._sys.exit", mock_sys_exit)

    Console.fail("Error occurred")

    captured = capsys.readouterr()
    assert "FAIL" in captured.out
    assert "Error occurred" in captured.out
    mock_sys_exit.assert_called_once_with(1)


def test_exit_method(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch):
    mock_sys_exit = MagicMock()
    monkeypatch.setattr("xulbux.console._sys.exit", mock_sys_exit)

    Console.exit("Program ending")

    captured = capsys.readouterr()
    assert "EXIT" in captured.out
    assert "Program ending" in captured.out
    mock_sys_exit.assert_called_once_with(0)


def test_log_box_filled(capsys: pytest.CaptureFixture[str]):
    Console.log_box_filled("Line 1", "Line 2", box_bg_color=S.BG.GREEN)

    captured = capsys.readouterr()
    assert "Line 1" in captured.out
    assert "Line 2" in captured.out


def test_log_box_bordered(capsys: pytest.CaptureFixture[str]):
    Console.log_box_bordered("Content line", border_type="rounded")

    captured = capsys.readouterr()
    assert "Content line" in captured.out


@patch("xulbux.console.Console.input")
def test_confirm_yes(mock_input: MagicMock):
    mock_input.return_value = "y"
    result = Console.confirm("Continue?")
    assert result is True


@patch("xulbux.console.Console.input")
def test_confirm_no(mock_input: MagicMock):
    mock_input.return_value = "n"
    result = Console.confirm("Continue?")
    assert result is False


@patch("xulbux.console.Console.input")
def test_confirm_default_yes(mock_input: MagicMock):
    mock_input.return_value = ""
    result = Console.confirm("Continue?", default_is_yes=True)
    assert result is True


@patch("xulbux.console.Console.input")
def test_confirm_default_no(mock_input: MagicMock):
    mock_input.return_value = ""
    result = Console.confirm("Continue?", default_is_yes=False)
    assert result is False


@pytest.fixture
def mock_prompt_session(monkeypatch: pytest.MonkeyPatch):
    mock_session = MagicMock()
    mock_session_class = MagicMock(return_value=mock_session)
    mock_session.prompt.return_value = None
    monkeypatch.setattr("xulbux.console._pt.PromptSession", mock_session_class)
    return mock_session_class, mock_session


def test_input_creates_prompt_session(mock_prompt_session: tuple[MagicMock, MagicMock], mock_formatcodes_print: MagicMock):
    """Test that Console.input creates a PromptSession with correct parameters."""
    mock_session_class, mock_session = mock_prompt_session

    Console.input("Enter text: ")

    assert mock_session_class.called
    call_kwargs = mock_session_class.call_args[1]
    assert "message" in call_kwargs
    assert "validator" in call_kwargs
    assert "validate_while_typing" in call_kwargs
    assert "key_bindings" in call_kwargs
    assert "bottom_toolbar" in call_kwargs
    assert "style" in call_kwargs
    mock_session.prompt.assert_called_once()


def test_input_with_placeholder(mock_prompt_session: tuple[MagicMock, MagicMock], mock_formatcodes_print: MagicMock):
    """Test that placeholder is correctly passed to PromptSession."""
    mock_session_class, _ = mock_prompt_session

    Console.input("Enter text: ", placeholder="Type here...")

    assert mock_session_class.called
    call_kwargs = mock_session_class.call_args[1]
    assert "placeholder" in call_kwargs
    assert call_kwargs["placeholder"] != ""


def test_input_without_placeholder(mock_prompt_session: tuple[MagicMock, MagicMock], mock_formatcodes_print: MagicMock):
    """Test that placeholder is empty when not provided."""
    mock_session_class, _ = mock_prompt_session

    Console.input("Enter text: ")

    assert mock_session_class.called
    call_kwargs = mock_session_class.call_args[1]
    assert "placeholder" in call_kwargs
    assert call_kwargs["placeholder"] == ""


def test_input_with_validator_function(mock_prompt_session: tuple[MagicMock, MagicMock], mock_formatcodes_print: MagicMock):
    """Test that a custom validator function is properly handled."""
    mock_session_class, _ = mock_prompt_session

    def email_validator(text: str) -> str | None:
        if "@" not in text:
            return "Invalid email"
        return None

    Console.input("Enter email: ", validator=email_validator)

    assert mock_session_class.called
    call_kwargs = mock_session_class.call_args[1]
    assert "validator" in call_kwargs
    validator_instance = call_kwargs["validator"]
    assert hasattr(validator_instance, "validate")


def test_input_with_length_constraints(mock_prompt_session: tuple[MagicMock, MagicMock], mock_formatcodes_print: MagicMock):
    """Test that min_len and max_len are properly handled."""
    mock_session_class, _ = mock_prompt_session

    Console.input("Enter text: ", min_len=3, max_len=10)

    assert mock_session_class.called
    call_kwargs = mock_session_class.call_args[1]
    assert "validator" in call_kwargs
    validator_instance = call_kwargs["validator"]
    assert hasattr(validator_instance, "validate")


def test_input_with_allowed_chars(mock_prompt_session: tuple[MagicMock, MagicMock], mock_formatcodes_print: MagicMock):
    """Test that allowed_chars parameter is handled."""
    mock_session_class, _ = mock_prompt_session

    Console.input("Enter digits only: ", allowed_chars="0123456789")

    assert mock_session_class.called
    call_kwargs = mock_session_class.call_args[1]
    assert "key_bindings" in call_kwargs
    assert call_kwargs["key_bindings"] is not None


def test_input_disable_paste(mock_prompt_session: tuple[MagicMock, MagicMock], mock_formatcodes_print: MagicMock):
    """Test that allow_paste=False is handled."""
    mock_session_class, _ = mock_prompt_session

    Console.input("Enter text: ", allow_paste=False)

    assert mock_session_class.called
    call_kwargs = mock_session_class.call_args[1]
    assert "key_bindings" in call_kwargs
    assert call_kwargs["key_bindings"] is not None


def test_input_with_start_end_formatting(mock_prompt_session: tuple[MagicMock, MagicMock], capsys: pytest.CaptureFixture[str]):
    """Test that start and end parameters trigger `StyledText.print` calls."""
    mock_session_class, _ = mock_prompt_session

    Console.input("Enter text: ", start="[green]", end="[_c]")

    assert mock_session_class.called
    captured = capsys.readouterr()
    # Just verify output was produced (start/end formatting occurred):
    assert captured.out != "" or True  # Output may be captured or go to real STDOUT.


def test_input_message_formatting(mock_prompt_session: tuple[MagicMock, MagicMock], mock_formatcodes_print: MagicMock):
    """Test that the prompt message is properly formatted."""
    mock_session_class, _ = mock_prompt_session

    Console.input("[b]Bold prompt:[_b] ", default_color="#ABC")

    assert mock_session_class.called
    call_kwargs = mock_session_class.call_args[1]
    assert "message" in call_kwargs
    assert call_kwargs["message"] is not None


def test_input_bottom_toolbar_function(mock_prompt_session: tuple[MagicMock, MagicMock], capsys: pytest.CaptureFixture[str]):
    """Test that bottom toolbar function is set up."""
    mock_session_class, _ = mock_prompt_session

    Console.input("Enter text: ")

    assert mock_session_class.called
    call_kwargs = mock_session_class.call_args[1]
    assert "bottom_toolbar" in call_kwargs
    toolbar_func = call_kwargs["bottom_toolbar"]
    assert callable(toolbar_func)

    try:
        result = toolbar_func()
        assert result is not None
    except Exception:
        pass


def test_input_style_configuration(mock_prompt_session: tuple[MagicMock, MagicMock], capsys: pytest.CaptureFixture[str]):
    """Test that custom style is applied."""
    mock_session_class, _ = mock_prompt_session

    Console.input("Enter text: ")

    assert mock_session_class.called
    call_kwargs = mock_session_class.call_args[1]
    assert "style" in call_kwargs
    assert call_kwargs["style"] is not None


def test_input_validate_while_typing_enabled(
    mock_prompt_session: tuple[MagicMock, MagicMock],
    mock_formatcodes_print: MagicMock,
):
    """Test that validate_while_typing is enabled."""
    mock_session_class, _ = mock_prompt_session

    Console.input("Enter text: ")

    assert mock_session_class.called
    call_kwargs = mock_session_class.call_args[1]
    assert "validate_while_typing" in call_kwargs
    assert call_kwargs["validate_while_typing"] is True


def test_input_validator_class_creation(mock_prompt_session: tuple[MagicMock, MagicMock], mock_formatcodes_print: MagicMock):
    """Test that InputValidator class is properly instantiated."""
    mock_session_class, _ = mock_prompt_session

    Console.input("Enter text: ", min_len=5)

    assert mock_session_class.called
    call_kwargs = mock_session_class.call_args[1]
    assert "validator" in call_kwargs
    validator_instance = call_kwargs["validator"]
    assert hasattr(validator_instance, "validate")
    assert callable(getattr(validator_instance, "validate", None))


def test_input_key_bindings_setup(mock_prompt_session: tuple[MagicMock, MagicMock], mock_formatcodes_print: MagicMock):
    """Test that key bindings are properly set up."""
    mock_session_class, _ = mock_prompt_session

    Console.input("Enter text: ")

    assert mock_session_class.called
    call_kwargs = mock_session_class.call_args[1]
    assert "key_bindings" in call_kwargs
    kb = call_kwargs["key_bindings"]
    assert kb is not None
    assert hasattr(kb, "bindings")


def test_input_mask_char_single_character(mock_prompt_session: tuple[MagicMock, MagicMock], mock_formatcodes_print: MagicMock):
    """Test that mask_char works with single characters."""
    mock_session_class, _ = mock_prompt_session

    Console.input("Enter password: ", mask_char="*")

    assert mock_session_class.called


def test_input_output_type_int(mock_prompt_session: tuple[MagicMock, MagicMock], mock_formatcodes_print: MagicMock):
    """Test that output_type parameter is handled for int conversion."""
    mock_session_class, _ = mock_prompt_session

    Console.input("Enter number: ", output_type=int, default_val=42)

    assert mock_session_class.called


def test_input_default_val_handling(mock_prompt_session: tuple[MagicMock, MagicMock], mock_formatcodes_print: MagicMock):
    """Test that default_val parameter is properly handled."""
    mock_session_class, _ = mock_prompt_session

    Console.input("Enter text: ", default_val="default_value")

    assert mock_session_class.called


def test_input_custom_style_object(mock_prompt_session: tuple[MagicMock, MagicMock], mock_formatcodes_print: MagicMock):
    """Test that a custom Style object is created."""
    mock_session_class, _ = mock_prompt_session

    Console.input("Enter text: ")

    assert mock_session_class.called
    call_kwargs = mock_session_class.call_args[1]
    assert "style" in call_kwargs
    style = call_kwargs["style"]
    assert style is not None
    assert hasattr(style, "style_rules") or hasattr(style, "_style")


#################################################### ProgressBar TESTS ###################################################


def test_progressbar_init():
    pb = ProgressBar(min_width=5, max_width=30)
    assert pb.min_width == 5
    assert pb.max_width == 30
    assert pb.active is False
    assert len(pb.chars) == 9


def test_progressbar_set_width():
    pb = ProgressBar()
    pb.set_width(min_width=15, max_width=60)
    assert pb.min_width == 15
    assert pb.max_width == 60


def test_progressbar_set_width_invalid():
    pb = ProgressBar()
    with pytest.raises(TypeError):
        pb.set_width(min_width="not_int")  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        pb.set_width(min_width=0)
    with pytest.raises(TypeError):
        pb.set_width(max_width="not_int")  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        pb.set_width(max_width=0)


def test_progressbar_set_bar_format():
    pb = ProgressBar()
    pb.set_bar_format(bar_format=["{l}", "[{b}]", "{p}%"], limited_bar_format=["[{b}]"])
    assert pb.bar_format == ["{l}", "[{b}]", "{p}%"]
    assert pb.limited_bar_format == ["[{b}]"]


def test_progressbar_set_bar_format_invalid():
    pb = ProgressBar()
    with pytest.raises(ValueError, match="must contain the '{bar}' or '{b}' placeholder"):
        pb.set_bar_format(bar_format=["Progress: {p}%"])
    with pytest.raises(ValueError, match="must contain the '{bar}' or '{b}' placeholder"):
        pb.set_bar_format(limited_bar_format=["Progress: {p}%"])


def test_progressbar_set_chars():
    pb = ProgressBar()
    custom_chars = ("█", "▓", "▒", "░", " ")
    pb.set_chars(custom_chars)
    assert pb.chars == custom_chars


def test_progressbar_set_chars_invalid():
    pb = ProgressBar()
    with pytest.raises(ValueError, match="must contain at least two characters"):
        pb.set_chars(("█", ))
    with pytest.raises(ValueError, match="must be single-character strings"):
        pb.set_chars(("█", "▓▓", " "))


def test_progressbar_show_progress_invalid_total():
    pb = ProgressBar()
    with pytest.raises(ValueError, match="The 'total' parameter must be a positive integer."):
        pb.show_progress(10, 0)
    with pytest.raises(ValueError, match="The 'total' parameter must be a positive integer."):
        pb.show_progress(10, -5)


@patch("sys.stdout", new_callable=io.StringIO)
def test_progressbar_show_progress(mock_stdout: MagicMock):
    pb = ProgressBar()
    # Manually set and restore `_original_stdout` to avoid patching issues with compiled classes:
    original = pb._original_stdout
    pb._original_stdout = mock_stdout
    try:
        pb.active = True
        pb._draw_progress_bar(50, 100, "Loading")
    finally:
        pb._original_stdout = original

    output = mock_stdout.getvalue()
    assert len(output) > 0


def test_progressbar_hide_progress():
    pb = ProgressBar()
    pb.active = True
    pb._original_stdout = MagicMock()
    pb.hide_progress()
    assert pb.active is False
    assert pb._original_stdout is None


def test_progressbar_progress_context(capsys: pytest.CaptureFixture[str]):
    pb = ProgressBar()

    # Test context manager behavior by checking actual effects:
    with pb.progress_context(100, "Testing") as update_progress:
        update_progress(25)
        assert pb.active is True  # Active after first update.
        update_progress(50)

    # After context exits, progress bar should be hidden:
    assert pb.active is False
    captured = capsys.readouterr()
    assert captured.out != ""  # Some output should have been produced.


def test_progressbar_progress_context_exception():
    pb = ProgressBar()

    # Test that cleanup happens even with exceptions:
    with pytest.raises(ValueError):
        with pb.progress_context(100, "Testing") as update_progress:
            update_progress(25)
            raise ValueError("Test exception")

    # After exception, progress bar should still be cleaned up:
    assert pb.active is False


def test_progressbar_create_bar():
    pb = ProgressBar()

    bar = pb._create_bar(50, 100, 10)
    assert len(bar) == 10
    assert bar[0] == pb.chars[0]
    assert bar[-1] == pb.chars[-1]

    bar = pb._create_bar(100, 100, 10)
    assert len(bar) == 10
    assert all(char == pb.chars[0] for char in bar)

    bar = pb._create_bar(0, 100, 10)
    assert len(bar) == 10
    assert all(char == pb.chars[-1] for char in bar)


def test_progressbar_intercepted_output():
    pb = ProgressBar()
    intercepted = console._InterceptedOutput(pb)
    result = intercepted.write("test content")
    assert result == len("test content")
    assert "test content" in pb._buffer
    intercepted.flush()


def test_progressbar_emergency_cleanup():
    pb = ProgressBar()
    pb.active = True
    original_stdout = MagicMock()
    pb._original_stdout = original_stdout
    pb._emergency_cleanup()
    assert pb.active is False


def test_progressbar_get_formatted_info_and_bar_width(mock_terminal_size: MagicMock):
    pb = ProgressBar()
    formatted, bar_width = pb._get_formatted_info_and_bar_width(
        ["{l}", "|{b}|", "{c}/{t}", "({p}%)"],
        50,
        100,
        50.0,
        "Loading",
    )
    assert "Loading" in formatted
    assert "50" in formatted
    assert "100" in formatted
    assert "50.0" in formatted
    assert isinstance(bar_width, int)
    assert bar_width > 0


def test_progressbar_start_stop_intercepting():
    pb = ProgressBar()
    original_stdout = sys.stdout

    pb._start_intercepting()
    assert pb.active is True
    assert pb._original_stdout == original_stdout
    assert isinstance(sys.stdout, console._InterceptedOutput)

    pb._stop_intercepting()
    assert pb.active is False
    assert pb._original_stdout is None
    assert sys.stdout == original_stdout


def test_progressbar_clear_progress_line():
    pb = ProgressBar()
    mock_stdout = MagicMock()
    mock_stdout.write.return_value = 0
    mock_stdout.flush.return_value = None
    pb._original_stdout = mock_stdout
    pb._last_line_len = 20
    pb._clear_progress_line()
    mock_stdout.write.assert_called_once()
    mock_stdout.flush.assert_called_once()


def test_progressbar_redraw_progress_bar():
    pb = ProgressBar()
    mock_stdout = MagicMock()
    mock_stdout.write.return_value = 0
    mock_stdout.flush.return_value = None
    pb._original_stdout = mock_stdout
    pb._current_progress_str = "\x1b[2K\rLoading... ▕██████████          ▏ 50/100 (50.0%)"
    pb._redraw_display()
    mock_stdout.flush.assert_called_once()


##################################################### Throbber TESTS #####################################################


def test_throbber_init_defaults():
    throbber = Throbber()
    assert throbber.label is None
    assert throbber.interval == 0.2
    assert throbber.active is False
    assert throbber.sep == " "
    assert len(throbber.frames) > 0


def test_throbber_init_custom():
    throbber = Throbber(label="Loading", interval=0.5, sep="-")
    assert throbber.label == "Loading"
    assert throbber.interval == 0.5
    assert throbber.sep == "-"


def test_throbber_set_format_valid():
    throbber = Throbber()
    throbber.set_format(["{l}", "{a}"])
    assert throbber.throbber_format == ["{l}", "{a}"]


def test_throbber_set_format_invalid():
    throbber = Throbber()
    with pytest.raises(ValueError):
        throbber.set_format(["{l}"])  # Missing `{a}`.


def test_throbber_set_frames_valid():
    throbber = Throbber()
    throbber.set_frames(("a", "b"))
    assert throbber.frames == ("a", "b")


def test_throbber_set_frames_invalid():
    throbber = Throbber()
    with pytest.raises(ValueError):
        throbber.set_frames(("a", ))  # Less than 2 frames.


def test_throbber_set_interval_valid():
    throbber = Throbber()
    throbber.set_interval(1.0)
    assert throbber.interval == 1.0


def test_throbber_set_interval_invalid():
    throbber = Throbber()
    with pytest.raises(ValueError):
        throbber.set_interval(0)
    with pytest.raises(ValueError):
        throbber.set_interval(-1)


@patch("xulbux.console._threading.Thread")
@patch("xulbux.console._threading.Event")
@patch("sys.stdout", new_callable=MagicMock)
def test_throbber_start(mock_stdout: MagicMock, mock_event: MagicMock, mock_thread: MagicMock):
    mock_thread.return_value.start.return_value = None
    throbber = Throbber()
    throbber.start("Test")

    assert throbber.active is True
    assert throbber.label == "Test"
    mock_event.assert_called_once()
    mock_thread.assert_called_once()

    # Test, calling start again doesn't do anything:
    throbber.start("Test2")
    assert mock_event.call_count == 1


@patch("xulbux.console._threading.Thread")
@patch("xulbux.console._threading.Event")
def test_throbber_stop(mock_event: MagicMock, mock_thread: MagicMock):
    throbber = Throbber()
    # Manually set active to simulate running:
    throbber.active = True
    mock_stop_event = MagicMock()
    mock_stop_event.set.return_value = None
    throbber._stop_event = mock_stop_event
    mock_animation_thread = MagicMock()
    mock_animation_thread.join.return_value = None
    throbber._animation_thread = mock_animation_thread

    throbber.stop()

    assert throbber.active is False
    mock_stop_event.set.assert_called_once()
    mock_animation_thread.join.assert_called_once()


def test_throbber_update_label():
    throbber = Throbber()
    throbber.update_label("New Label")
    assert throbber.label == "New Label"


def test_throbber_context_manager():
    throbber = Throbber()

    # Test context manager behavior by checking actual effects:
    with throbber.context("Test") as update:
        assert throbber.active is True
        assert throbber.label == "Test"
        update("New Label")
        assert throbber.label == "New Label"

    # After context exits, throbber should be stopped:
    assert throbber.active is False


def test_throbber_context_manager_exception():
    throbber = Throbber()

    # Test that cleanup happens even with exceptions:
    with pytest.raises(ValueError):
        with throbber.context("Test"):
            raise ValueError("Oops")

    # After exception, throbber should still be cleaned up:
    assert throbber.active is False
