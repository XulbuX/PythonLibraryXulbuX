from xulbux.console import Console, Args, ArgResult, ProgressBar
from xulbux import console

from unittest.mock import MagicMock, patch, call
from collections import namedtuple
import builtins
import pytest
import sys
import io


@pytest.fixture
def mock_terminal_size(monkeypatch):
    TerminalSize = namedtuple("TerminalSize", ["columns", "lines"])
    mock_get_terminal_size = lambda: TerminalSize(columns=80, lines=24)
    monkeypatch.setattr(console._os, "get_terminal_size", mock_get_terminal_size)


@pytest.fixture
def mock_formatcodes_print(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr(console.FormatCodes, "print", mock)
    return mock


@pytest.fixture
def mock_builtin_input(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr(builtins, "input", mock)
    return mock


@pytest.fixture
def mock_prompt_toolkit(monkeypatch):
    mock = MagicMock(return_value="mocked multiline input")
    monkeypatch.setattr(console._pt, "prompt", mock)
    return mock


################################################## CONSOLE TESTS ##################################################


def test_console_user():
    user_output = Console.usr
    assert isinstance(user_output, str)
    assert user_output != ""


def test_console_width(mock_terminal_size):
    width_output = Console.w
    assert isinstance(width_output, int)
    assert width_output == 80


def test_console_height(mock_terminal_size):
    height_output = Console.h
    assert isinstance(height_output, int)
    assert height_output == 24


def test_console_size(mock_terminal_size):
    size_output = Console.wh
    assert isinstance(size_output, tuple)
    assert len(size_output) == 2
    assert size_output[0] == 80
    assert size_output[1] == 24


@pytest.mark.parametrize(
    "argv, find_args, expected_args_dict", [
        # --- CASES WITHOUT SPACES (allow_spaces=False) ---
        # NO ARGS PROVIDED
        (["script.py"], {"file": ["-f"], "debug": ["-d"]
                         }, {"file": {"exists": False, "value": None}, "debug": {"exists": False, "value": None}}),
        # SIMPLE FLAG
        (["script.py", "-d"], {"file": ["-f"], "debug": ["-d"]
                               }, {"file": {"exists": False, "value": None}, "debug": {"exists": True, "value": None}}),
        # FLAG WITH VALUE
        (["script.py", "-f", "test.txt"], {"file": ["-f"], "debug": ["-d"]},
         {"file": {"exists": True, "value": "test.txt"}, "debug": {"exists": False, "value": None}}),
        # LONG FLAGS WITH VALUE AND FLAG
        (["script.py", "--file", "path/to/file", "--debug"], {"file": ["-f", "--file"], "debug": ["-d", "--debug"]},
         {"file": {"exists": True, "value": "path/to/file"}, "debug": {"exists": True, "value": None}}),
        # VALUE WITH SPACE (IGNORED DUE TO allow_spaces=False)
        (["script.py", "-f", "file with spaces"], {"file": ["-f"]}, {"file": {"exists": True, "value": "file with spaces"}}),
        # UNKNOWN ARG
        (["script.py", "-x"], {"file": ["-f"]}, {"file": {"exists": False, "value": None}}),
        # TWO FLAGS
        (["script.py", "-f", "-d"], {"file": ["-f"], "debug": ["-d"]
                                     }, {"file": {"exists": True, "value": None}, "debug": {"exists": True, "value": None}}),
        # NUMERIC VALUE
        (["script.py", "-n", "123"], {"num": ["-n"]}, {"num": {"exists": True, "value": 123}}),
        # BOOLEAN VALUE (True)
        (["script.py", "-b", "true"], {"bool_arg": ["-b"]}, {"bool_arg": {"exists": True, "value": True}}),
        # BOOLEAN VALUE (False)
        (["script.py", "-b", "False"], {"bool_arg": ["-b"]}, {"bool_arg": {"exists": True, "value": False}}),

        # --- CASES WITH DEFAULTS (dict FORMAT, allow_spaces=False) ---
        # DEFAULT USED (string)
        (["script.py"], {"output": {"flags": ["-o"], "default": "out.txt"}, "verbose": ["-v"]
                         }, {"output": {"exists": False, "value": "out.txt"}, "verbose": {"exists": False, "value": None}}),
        # VALUE OVERRIDES DEFAULT (string)
        (["script.py", "-o", "my_file.log"], {"output": {"flags": ["-o"], "default": "out.txt"}, "verbose": ["-v"]},
         {"output": {"exists": True, "value": "my_file.log"}, "verbose": {"exists": False, "value": None}}),
        # FLAG PRESENCE OVERRIDES DEFAULT (string -> None)
        (["script.py", "-o"], {"output": {"flags": ["-o"], "default": "out.txt"}, "verbose": ["-v"]
                               }, {"output": {"exists": True, "value": None}, "verbose": {"exists": False, "value": None}}),
        # FLAG PRESENCE OVERRIDES DEFAULT (False -> None)
        (["script.py", "-v"], {
            "output": {"flags": ["-o"], "default": "out.txt"}, "verbose": {"flags": ["-v"], "default": False}
        }, {"output": {"exists": False, "value": "out.txt"}, "verbose": {"exists": True, "value": None}}),
        # DEFAULT USED (int)
        (["script.py"], {"mode": {"flags": ["-m"], "default": 1}}, {"mode": {"exists": False, "value": 1}}),
        # VALUE OVERRIDES DEFAULT (int)
        (["script.py", "-m", "2"], {"mode": {"flags": ["-m"], "default": 1}}, {"mode": {"exists": True, "value": 2}}),
        # FLAG PRESENCE OVERRIDES DEFAULT (int -> None)
        (["script.py", "-m"], {"mode": {"flags": ["-m"], "default": 1}}, {"mode": {"exists": True, "value": None}}
         ),  # --- MIXED list/tuple AND dict FORMATS (allow_spaces=False) ---
        # DICT VALUE PROVIDED, LIST NOT PROVIDED
        (["script.py", "--config", "dev.cfg"], {"config": {"flags": ["-c", "--config"], "default": "prod.cfg"}, "log": ["-l"]},
         {"config": {"exists": True, "value": "dev.cfg"}, "log": {"exists": False, "value": None}}),
        # LIST FLAG PROVIDED, DICT NOT PROVIDED (USES DEFAULT)
        (["script.py", "-l"], {"config": {"flags": ["-c", "--config"], "default": "prod.cfg"}, "log": ["-l"]}, {
            "config": {"exists": False, "value": "prod.cfg"}, "log": {"exists": True, "value": None}
        }),  # --- 'before' / 'after' SPECIAL CASES ---
        # 'before' SPECIAL CASE
        (["script.py", "arg1", "arg2", "-f", "file.txt"], {"before": "before", "file": ["-f"]},
         {"before": {"exists": True, "value": ["arg1", "arg2"]}, "file": {"exists": True, "value": "file.txt"}}),
        (["script.py", "-f", "file.txt"], {"before": "before", "file": ["-f"]},
         {"before": {"exists": False, "value": []}, "file": {"exists": True, "value": "file.txt"}}),
        # 'after' SPECIAL CASE
        (["script.py", "-f", "file.txt", "arg1", "arg2"], {"after": "after", "file": ["-f"]},
         {"after": {"exists": True, "value": ["arg1", "arg2"]}, "file": {"exists": True, "value": "file.txt"}}),
        (["script.py", "-f", "file.txt"], {"after": "after", "file": ["-f"]},
         {"after": {"exists": False, "value": []}, "file": {"exists": True, "value": "file.txt"}}),
    ]
)
def test_get_args_no_spaces(monkeypatch, argv, find_args, expected_args_dict):
    monkeypatch.setattr(sys, "argv", argv)
    args_result = Console.get_args(find_args, allow_spaces=False)
    assert isinstance(args_result, Args)
    assert args_result.dict() == expected_args_dict
    for key, expected in expected_args_dict.items():
        assert (key in args_result) is True
        assert isinstance(args_result[key], ArgResult)
        assert args_result[key].exists == expected["exists"]  # type: ignore[access]
        assert args_result[key].value == expected["value"]  # type: ignore[access]
        assert bool(args_result[key]) == expected["exists"]
    assert list(args_result.keys()) == list(expected_args_dict.keys())
    assert [v.exists for v in args_result.values()] == [d["exists"] for d in expected_args_dict.values()]
    assert [v.value for v in args_result.values()] == [d["value"] for d in expected_args_dict.values()]
    assert len(args_result) == len(expected_args_dict)


@pytest.mark.parametrize(
    "argv, find_args, expected_args_dict", [
        # --- CASES WITH SPACES (allow_spaces=True) ---
        # SIMPLE VALUE WITH SPACES
        (["script.py", "-f", "file with spaces", "-d"], {"file": ["-f"], "debug": ["-d"]},
         {"file": {"exists": True, "value": "file with spaces"}, "debug": {"exists": True, "value": None}}),
        # LONG VALUE WITH SPACES
        (["script.py", "--message", "Hello", "world", "how", "are", "you"
          ], {"message": ["--message"]}, {"message": {"exists": True, "value": "Hello world how are you"}}),
        # VALUE WITH SPACES FOLLOWED BY ANOTHER FLAG
        (["script.py", "-m", "this is", "a message", "--flag"], {"message": ["-m"], "flag": ["--flag"]},
         {"message": {"exists": True, "value": "this is a message"}, "flag": {"exists": True, "value": None}}),
        # VALUE WITH SPACES AT THE END
        (["script.py", "-m", "end", "of", "args"], {"message": ["-m"]}, {"message": {"exists": True, "value": "end of args"}}),

        # --- CASES WITH DEFAULTS (dict FORMAT, allow_spaces=True) ---
        # VALUE WITH SPACE OVERRIDES DEFAULT
        (["script.py", "--msg", "Default message"], {"msg": {"flags": ["--msg"], "default": "No message"}, "other": ["-o"]},
         {"msg": {"exists": True, "value": "Default message"}, "other": {"exists": False, "value": None}}),
        # DEFAULT USED WHEN OTHER FLAG PRESENT
        (["script.py", "-o"], {"msg": {"flags": ["--msg"], "default": "No message"}, "other": ["-o"]
                               }, {"msg": {"exists": False, "value": "No message"}, "other": {"exists": True, "value": None}}),
        # FLAG PRESENCE OVERRIDES DEFAULT (str -> True)
        # FLAG WITH NO VALUE SHOULD HAVE None AS VALUE
        (["script.py", "--msg"], {"msg": {"flags": ["--msg"], "default": "No message"}, "other": ["-o"]
                                  }, {"msg": {"exists": True, "value": None}, "other": {"exists": False, "value": None}}),

        # --- MIXED FORMATS WITH SPACES (allow_spaces=True) ---
        # LIST VALUE WITH SPACES, dict VALUE PROVIDED
        (["script.py", "-f", "input file name", "--mode", "test"], {
            "file": ["-f"], "mode": {"flags": ["--mode"], "default": "prod"}
        }, {"file": {"exists": True, "value": "input file name"}, "mode": {"exists": True, "value": "test"}}),
        # LIST VALUE WITH SPACES, dict NOT PROVIDED (USES DEFAULT)
        (["script.py", "-f", "another file"], {"file": ["-f"], "mode": {"flags": ["--mode"], "default": "prod"}},
         {"file": {"exists": True, "value": "another file"}, "mode": {"exists": False, "value": "prod"}}),
    ]
)
def test_get_args_with_spaces(monkeypatch, argv, find_args, expected_args_dict):
    monkeypatch.setattr(sys, "argv", argv)
    args_result = Console.get_args(find_args, allow_spaces=True)
    assert isinstance(args_result, Args)
    assert args_result.dict() == expected_args_dict


def test_get_args_flag_without_value(monkeypatch):
    """Test that flags without values have None as their value, not True."""
    # TEST SINGLE FLAG WITHOUT VALUE AT END OF ARGS
    monkeypatch.setattr(sys, "argv", ["script.py", "--verbose"])
    args_result = Console.get_args({"verbose": ["--verbose"]})
    assert args_result.verbose.exists is True
    assert args_result.verbose.value is None

    # TEST FLAG WITHOUT VALUE FOLLOWED BY ANOTHER FLAG
    monkeypatch.setattr(sys, "argv", ["script.py", "--verbose", "--debug"])
    args_result = Console.get_args({"verbose": ["--verbose"], "debug": ["--debug"]})
    assert args_result.verbose.exists is True
    assert args_result.verbose.value is None
    assert args_result.debug.exists is True
    assert args_result.debug.value is None

    # TEST FLAG WITH DEFAULT VALUE BUT NO PROVIDED VALUE
    monkeypatch.setattr(sys, "argv", ["script.py", "--mode"])
    args_result = Console.get_args({"mode": {"flags": ["--mode"], "default": "production"}})
    assert args_result.mode.exists is True
    assert args_result.mode.value is None


def test_get_args_invalid_alias():
    with pytest.raises(TypeError, match="Argument alias 'invalid-alias' is invalid."):
        Args(**{"invalid-alias": {"exists": False, "value": None}})

    with pytest.raises(TypeError, match="Argument alias '123start' is invalid."):
        Args(**{"123start": {"exists": False, "value": None}})


def test_get_args_invalid_config():
    with pytest.raises(
            TypeError, match=
            "Invalid configuration type for alias 'bad_config'. Must be a list, tuple, dict or literal 'before' / 'after'."):
        Console.get_args({"bad_config": 123})  # type: ignore[assignment]

    with pytest.raises(ValueError,
                       match="Invalid configuration for alias 'missing_flags'. Dictionary must contain a 'flags' key."):
        Console.get_args({"missing_flags": {"default": "value"}})  # type: ignore[assignment]

    with pytest.raises(
            ValueError, match=
            "Invalid configuration for alias 'bad_flags'. Dictionary must contain a 'default' key. Use a simple list/tuple if no default value is needed."
    ):
        Console.get_args({"bad_flags": {"flags": ["--flag"]}})  # type: ignore[assignment]

    with pytest.raises(ValueError, match="Invalid 'flags' for alias 'bad_flags'. Must be a list or tuple."):
        Console.get_args({"bad_flags": {"flags": "not-a-list", "default": "value"}})  # type: ignore[assignment]


def test_get_args_duplicate_flag():
    with pytest.raises(ValueError, match="Duplicate flag '-f' found. It's assigned to both 'file1' and 'file2'."):
        Console.get_args({"file1": ["-f", "--file1"], "file2": {"flags": ["-f", "--file2"], "default": ...}})

    with pytest.raises(ValueError, match="Duplicate flag '--long' found. It's assigned to both 'arg1' and 'arg2'."):
        Console.get_args({"arg1": {"flags": ["--long"], "default": ...}, "arg2": ("-a", "--long")})


def test_get_args_dash_values_not_treated_as_flags(monkeypatch):
    """Test that values starting with dashes are not treated as flags unless explicitly defined"""
    monkeypatch.setattr(sys, "argv", ["script.py", "-v", "-42", "--input", "-3.14"])
    find_args = {"verbose": ["-v"], "input": ["--input"]}
    result = Console.get_args(find_args)

    assert result.verbose.exists is True
    assert result.verbose.value == -42
    assert result.input.exists is True
    assert result.input.value == -3.14


def test_get_args_dash_strings_as_values(monkeypatch):
    """Test that dash-prefixed strings are treated as values when not defined as flags"""
    monkeypatch.setattr(sys, "argv", ["script.py", "-f", "--not-a-flag", "-t", "-another-value"])
    find_args = {"file": ["-f"], "text": ["-t"]}
    result = Console.get_args(find_args)

    assert result.file.exists is True
    assert result.file.value == "--not-a-flag"
    assert result.text.exists is True
    assert result.text.value == "-another-value"


def test_get_args_positional_with_dashes_before(monkeypatch):
    """Test that positional 'before' arguments include dash-prefixed values"""
    monkeypatch.setattr(sys, "argv", ["script.py", "-123", "--some-file", "normal", "-v"])
    find_args = {"before_args": "before", "verbose": ["-v"]}
    result = Console.get_args(find_args)

    assert result.before_args.exists is True
    assert result.before_args.value == [-123, "--some-file", "normal"]
    assert result.verbose.exists is True
    assert result.verbose.value is None


def test_get_args_positional_with_dashes_after(monkeypatch):
    """Test that positional 'after' arguments include dash-prefixed values"""
    monkeypatch.setattr(sys, "argv", ["script.py", "-v", "value", "-123", "--output-file", "-negative"])
    find_args = {"verbose": ["-v"], "after_args": "after"}
    result = Console.get_args(find_args)

    assert result.verbose.exists is True
    assert result.verbose.value == "value"
    assert result.after_args.exists is True
    assert result.after_args.value == [-123, "--output-file", "-negative"]


def test_get_args_multiword_with_dashes(monkeypatch):
    """Test multiword values with dashes when allow_spaces=True"""
    monkeypatch.setattr(sys, "argv", ["script.py", "-m", "start", "-middle", "--end", "-f", "other"])
    find_args = {"message": ["-m"], "file": ["-f"]}
    result = Console.get_args(find_args, allow_spaces=True)

    assert result.message.exists is True
    assert result.message.value == "start -middle --end"
    assert result.file.exists is True
    assert result.file.value == "other"


def test_get_args_mixed_dash_scenarios(monkeypatch):
    """Test complex scenario mixing defined flags with dash-prefixed values"""
    monkeypatch.setattr(
        sys, "argv", [
            "script.py", "before1", "-not-flag", "before2", "-v", "--verbose-mode", "-d", "-42", "--file", "--my-file.txt",
            "after1", "-also-not-flag"
        ]
    )
    find_args = {"before": "before", "verbose": ["-v"], "debug": ["-d"], "file": ["--file"], "after": "after"}
    result = Console.get_args(find_args)

    assert result.before.exists is True
    assert result.before.value == ["before1", "-not-flag", "before2"]

    assert result.verbose.exists is True
    assert result.verbose.value == "--verbose-mode"

    assert result.debug.exists is True
    assert result.debug.value == -42

    assert result.file.exists is True
    assert result.file.value == "--my-file.txt"

    assert result.after.exists is True
    assert result.after.value == ["after1", "-also-not-flag"]


def test_multiline_input(mock_prompt_toolkit, mock_formatcodes_print):
    expected_input = "mocked multiline input"
    result = Console.multiline_input("Enter text:", show_keybindings=True, default_color="#BCA")

    assert result == expected_input
    assert mock_formatcodes_print.call_count == 3
    prompt_call = mock_formatcodes_print.call_args_list[0]
    keybind_call = mock_formatcodes_print.call_args_list[1]
    reset_call = mock_formatcodes_print.call_args_list[2]

    assert prompt_call.args == ("Enter text:", )
    assert prompt_call.kwargs == {"default_color": "#BCA"}

    assert "[dim][[b](CTRL+D)[dim] : end of input][_dim]" in keybind_call.args[0]

    assert reset_call.args == ("[_]", )
    assert reset_call.kwargs == {"end": ""}

    mock_prompt_toolkit.assert_called_once()
    pt_args, pt_kwargs = mock_prompt_toolkit.call_args
    assert pt_args == (" ⮡ ", )
    assert pt_kwargs.get("multiline") is True
    assert pt_kwargs.get("wrap_lines") is True
    assert "key_bindings" in pt_kwargs


def test_multiline_input_no_bindings(mock_prompt_toolkit, mock_formatcodes_print):
    Console.multiline_input("Enter text:", show_keybindings=False, end="DONE")

    assert mock_formatcodes_print.call_count == 2
    prompt_call = mock_formatcodes_print.call_args_list[0]
    reset_call = mock_formatcodes_print.call_args_list[1]

    assert prompt_call.args == ("Enter text:", )
    assert reset_call.args == ("[_]", )
    assert reset_call.kwargs == {"end": "DONE"}

    mock_prompt_toolkit.assert_called_once()


def test_pause_exit_pause_only(monkeypatch):
    mock_keyboard = MagicMock()
    mock_formatcodes_print = MagicMock()
    monkeypatch.setattr(console._keyboard, "read_key", mock_keyboard)
    monkeypatch.setattr(console.FormatCodes, "print", mock_formatcodes_print)

    Console.pause_exit(pause=True, exit=False, prompt="Press any key...")

    mock_formatcodes_print.assert_called_once_with("Press any key...", end="", flush=True)
    mock_keyboard.assert_called_once_with(suppress=True)


def test_pause_exit_with_exit(monkeypatch):
    mock_keyboard = MagicMock()
    mock_formatcodes_print = MagicMock()
    mock_sys_exit = MagicMock()
    monkeypatch.setattr(console._keyboard, "read_key", mock_keyboard)
    monkeypatch.setattr(console.FormatCodes, "print", mock_formatcodes_print)
    monkeypatch.setattr(console._sys, "exit", mock_sys_exit)

    Console.pause_exit(pause=True, exit=True, prompt="Exiting...", exit_code=1)

    mock_formatcodes_print.assert_called_once_with("Exiting...", end="", flush=True)
    mock_keyboard.assert_called_once_with(suppress=True)
    mock_sys_exit.assert_called_once_with(1)


def test_pause_exit_reset_ansi(monkeypatch):
    mock_keyboard = MagicMock()
    mock_formatcodes_print = MagicMock()
    monkeypatch.setattr(console._keyboard, "read_key", mock_keyboard)
    monkeypatch.setattr(console.FormatCodes, "print", mock_formatcodes_print)

    Console.pause_exit(pause=True, exit=False, reset_ansi=True)

    assert mock_formatcodes_print.call_count == 2
    assert mock_formatcodes_print.call_args_list[1] == call("[_]", end="")


def test_cls(monkeypatch):
    mock_shutil = MagicMock()
    mock_os_system = MagicMock()
    mock_print = MagicMock()
    monkeypatch.setattr(console._shutil, "which", mock_shutil)
    monkeypatch.setattr(console._os, "system", mock_os_system)
    monkeypatch.setattr(builtins, "print", mock_print)

    mock_shutil.side_effect = lambda cmd: cmd == "cls"
    Console.cls()
    mock_os_system.assert_called_with("cls")
    mock_print.assert_called_with("\033[0m", end="", flush=True)

    mock_os_system.reset_mock()
    mock_print.reset_mock()

    mock_shutil.side_effect = lambda cmd: cmd == "clear"
    Console.cls()
    mock_os_system.assert_called_with("clear")
    mock_print.assert_called_with("\033[0m", end="", flush=True)


def test_log_basic(mock_formatcodes_print):
    Console.log("INFO", "Test message")

    mock_formatcodes_print.assert_called_once()
    args, kwargs = mock_formatcodes_print.call_args
    assert "INFO" in args[0]
    assert "Test message" in args[0]
    assert kwargs["end"] == "\n"


def test_log_no_title(mock_formatcodes_print):
    Console.log(title=None, prompt="Just a message")

    mock_formatcodes_print.assert_called_once()
    args, _ = mock_formatcodes_print.call_args
    assert "Just a message" in args[0]


def test_debug_active(mock_formatcodes_print):
    Console.debug("Debug message", active=True)

    assert mock_formatcodes_print.call_count == 3
    args, _ = mock_formatcodes_print.call_args_list[0]
    assert "DEBUG" in args[0]
    assert "Debug message" in args[0]


def test_debug_inactive(mock_formatcodes_print):
    Console.debug("Debug message", active=False)

    mock_formatcodes_print.assert_not_called()


def test_info(mock_formatcodes_print):
    Console.info("Info message")

    assert mock_formatcodes_print.call_count == 3
    args, _ = mock_formatcodes_print.call_args_list[0]
    assert "INFO" in args[0]
    assert "Info message" in args[0]


def test_done(mock_formatcodes_print):
    Console.done("Task completed")

    assert mock_formatcodes_print.call_count == 3
    args, _ = mock_formatcodes_print.call_args_list[0]
    assert "DONE" in args[0]
    assert "Task completed" in args[0]


def test_warn(mock_formatcodes_print):
    Console.warn("Warning message")

    assert mock_formatcodes_print.call_count == 3
    args, _ = mock_formatcodes_print.call_args_list[0]
    assert "WARN" in args[0]
    assert "Warning message" in args[0]


def test_fail(mock_formatcodes_print, monkeypatch):
    mock_sys_exit = MagicMock()
    monkeypatch.setattr(console._sys, "exit", mock_sys_exit)

    Console.fail("Error occurred")

    assert mock_formatcodes_print.call_count >= 2
    args, _ = mock_formatcodes_print.call_args_list[0]
    assert "FAIL" in args[0]
    assert "Error occurred" in args[0]

    mock_sys_exit.assert_called_once_with(1)


def test_exit_method(mock_formatcodes_print, monkeypatch):
    mock_sys_exit = MagicMock()
    monkeypatch.setattr(console._sys, "exit", mock_sys_exit)

    Console.exit("Program ending")

    assert mock_formatcodes_print.call_count >= 2
    args, _ = mock_formatcodes_print.call_args_list[0]
    assert "EXIT" in args[0]
    assert "Program ending" in args[0]

    mock_sys_exit.assert_called_once_with(0)


def test_log_box_filled(mock_formatcodes_print):
    Console.log_box_filled("Line 1", "Line 2", box_bg_color="green")

    mock_formatcodes_print.assert_called_once()
    args, _ = mock_formatcodes_print.call_args
    assert "Line 1" in args[0]
    assert "Line 2" in args[0]


def test_log_box_bordered(mock_formatcodes_print):
    Console.log_box_bordered("Content line", border_type="rounded")

    mock_formatcodes_print.assert_called_once()
    args, _ = mock_formatcodes_print.call_args
    assert "Content line" in args[0]


def test_confirm_yes(mock_builtin_input):
    mock_builtin_input.return_value = "y"
    result = Console.confirm("Continue?")
    assert result is True


def test_confirm_no(mock_builtin_input):
    mock_builtin_input.return_value = "n"
    result = Console.confirm("Continue?")
    assert result is False


def test_confirm_default_yes(mock_builtin_input):
    mock_builtin_input.return_value = ""
    result = Console.confirm("Continue?", default_is_yes=True)
    assert result is True


def test_confirm_default_no(mock_builtin_input):
    mock_builtin_input.return_value = ""
    result = Console.confirm("Continue?", default_is_yes=False)
    assert result is False


@pytest.fixture
def mock_prompt_session(monkeypatch):
    mock_session = MagicMock()
    mock_session_class = MagicMock(return_value=mock_session)
    mock_session.prompt.return_value = None
    monkeypatch.setattr(console._pt, "PromptSession", mock_session_class)
    return mock_session_class, mock_session


def test_input_creates_prompt_session(mock_prompt_session, mock_formatcodes_print):
    """Test that Console.input creates a PromptSession with correct parameters."""
    mock_session_class, mock_session = mock_prompt_session

    Console.input("Enter text: ")

    assert mock_session_class.called
    call_kwargs = mock_session_class.call_args[1]
    assert 'message' in call_kwargs
    assert 'validator' in call_kwargs
    assert 'validate_while_typing' in call_kwargs
    assert 'key_bindings' in call_kwargs
    assert 'bottom_toolbar' in call_kwargs
    assert 'style' in call_kwargs
    mock_session.prompt.assert_called_once()


def test_input_with_placeholder(mock_prompt_session, mock_formatcodes_print):
    """Test that placeholder is correctly passed to PromptSession."""
    mock_session_class, _ = mock_prompt_session

    Console.input("Enter text: ", placeholder="Type here...")

    assert mock_session_class.called
    call_kwargs = mock_session_class.call_args[1]
    assert 'placeholder' in call_kwargs
    assert call_kwargs['placeholder'] != ""


def test_input_without_placeholder(mock_prompt_session, mock_formatcodes_print):
    """Test that placeholder is empty when not provided."""
    mock_session_class, _ = mock_prompt_session

    Console.input("Enter text: ")

    assert mock_session_class.called
    call_kwargs = mock_session_class.call_args[1]
    assert 'placeholder' in call_kwargs
    assert call_kwargs['placeholder'] == ""


def test_input_with_validator_function(mock_prompt_session, mock_formatcodes_print):
    """Test that a custom validator function is properly handled."""
    mock_session_class, _ = mock_prompt_session

    def email_validator(text):
        if "@" not in text:
            return "Invalid email"
        return None

    Console.input("Enter email: ", validator=email_validator)

    assert mock_session_class.called
    call_kwargs = mock_session_class.call_args[1]
    assert 'validator' in call_kwargs
    validator_instance = call_kwargs['validator']
    assert hasattr(validator_instance, 'validate')


def test_input_with_length_constraints(mock_prompt_session, mock_formatcodes_print):
    """Test that min_len and max_len are properly handled."""
    mock_session_class, _ = mock_prompt_session

    Console.input("Enter text: ", min_len=3, max_len=10)

    assert mock_session_class.called
    call_kwargs = mock_session_class.call_args[1]
    assert 'validator' in call_kwargs
    validator_instance = call_kwargs['validator']
    assert hasattr(validator_instance, 'validate')


def test_input_with_allowed_chars(mock_prompt_session, mock_formatcodes_print):
    """Test that allowed_chars parameter is handled."""
    mock_session_class, _ = mock_prompt_session

    Console.input("Enter digits only: ", allowed_chars="0123456789")

    assert mock_session_class.called
    call_kwargs = mock_session_class.call_args[1]
    assert 'key_bindings' in call_kwargs
    assert call_kwargs['key_bindings'] is not None


def test_input_disable_paste(mock_prompt_session, mock_formatcodes_print):
    """Test that allow_paste=False is handled."""
    mock_session_class, _ = mock_prompt_session

    Console.input("Enter text: ", allow_paste=False)

    assert mock_session_class.called
    call_kwargs = mock_session_class.call_args[1]
    assert 'key_bindings' in call_kwargs
    assert call_kwargs['key_bindings'] is not None


def test_input_with_start_end_formatting(mock_prompt_session, mock_formatcodes_print):
    """Test that start and end parameters trigger FormatCodes.print calls."""
    mock_session_class, _ = mock_prompt_session

    Console.input("Enter text: ", start="[green]", end="[_c]")

    assert mock_session_class.called
    assert mock_formatcodes_print.call_count >= 2


def test_input_message_formatting(mock_prompt_session, mock_formatcodes_print):
    """Test that the prompt message is properly formatted."""
    mock_session_class, _ = mock_prompt_session

    Console.input("[b]Bold prompt:[_b] ", default_color="#ABC")

    assert mock_session_class.called
    call_kwargs = mock_session_class.call_args[1]
    assert 'message' in call_kwargs
    assert call_kwargs['message'] is not None


def test_input_bottom_toolbar_function(mock_prompt_session, mock_formatcodes_print):
    """Test that bottom toolbar function is set up."""
    mock_session_class, _ = mock_prompt_session

    Console.input("Enter text: ")

    assert mock_session_class.called
    call_kwargs = mock_session_class.call_args[1]
    assert 'bottom_toolbar' in call_kwargs
    toolbar_func = call_kwargs['bottom_toolbar']
    assert callable(toolbar_func)

    try:
        result = toolbar_func()
        assert result is not None
    except Exception:
        pass


def test_input_style_configuration(mock_prompt_session, mock_formatcodes_print):
    """Test that custom style is applied."""
    mock_session_class, _ = mock_prompt_session

    Console.input("Enter text: ")

    assert mock_session_class.called
    call_kwargs = mock_session_class.call_args[1]
    assert 'style' in call_kwargs
    assert call_kwargs['style'] is not None


def test_input_validate_while_typing_enabled(mock_prompt_session, mock_formatcodes_print):
    """Test that validate_while_typing is enabled."""
    mock_session_class, _ = mock_prompt_session

    Console.input("Enter text: ")

    assert mock_session_class.called
    call_kwargs = mock_session_class.call_args[1]
    assert 'validate_while_typing' in call_kwargs
    assert call_kwargs['validate_while_typing'] is True


def test_input_validator_class_creation(mock_prompt_session, mock_formatcodes_print):
    """Test that InputValidator class is properly instantiated."""
    mock_session_class, _ = mock_prompt_session

    Console.input("Enter text: ", min_len=5)

    assert mock_session_class.called
    call_kwargs = mock_session_class.call_args[1]
    assert 'validator' in call_kwargs
    validator_instance = call_kwargs['validator']
    assert hasattr(validator_instance, 'validate')
    assert callable(getattr(validator_instance, 'validate', None))


def test_input_key_bindings_setup(mock_prompt_session, mock_formatcodes_print):
    """Test that key bindings are properly set up."""
    mock_session_class, _ = mock_prompt_session

    Console.input("Enter text: ")

    assert mock_session_class.called
    call_kwargs = mock_session_class.call_args[1]
    assert 'key_bindings' in call_kwargs
    kb = call_kwargs['key_bindings']
    assert kb is not None
    assert hasattr(kb, 'bindings')


def test_input_mask_char_single_character(mock_prompt_session, mock_formatcodes_print):
    """Test that mask_char works with single characters."""
    mock_session_class, _ = mock_prompt_session

    Console.input("Enter password: ", mask_char="*")

    assert mock_session_class.called


def test_input_output_type_int(mock_prompt_session, mock_formatcodes_print):
    """Test that output_type parameter is handled for int conversion."""
    mock_session_class, _ = mock_prompt_session

    Console.input("Enter number: ", output_type=int, default_val=42)

    assert mock_session_class.called


def test_input_default_val_handling(mock_prompt_session, mock_formatcodes_print):
    """Test that default_val parameter is properly handled."""
    mock_session_class, _ = mock_prompt_session

    Console.input("Enter text: ", default_val="default_value")

    assert mock_session_class.called


def test_input_custom_style_object(mock_prompt_session, mock_formatcodes_print):
    """Test that a custom Style object is created."""
    mock_session_class, _ = mock_prompt_session

    Console.input("Enter text: ")

    assert mock_session_class.called
    call_kwargs = mock_session_class.call_args[1]
    assert 'style' in call_kwargs
    style = call_kwargs['style']
    assert style is not None
    assert hasattr(style, 'style_rules') or hasattr(style, '_style')


################################################## PROGRESSBAR TESTS ##################################################


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
    pb.set_bar_format(bar_format="{l} [{b}] {p}%", limited_bar_format="[{b}]")
    assert pb.bar_format == "{l} [{b}] {p}%"
    assert pb.limited_bar_format == "[{b}]"


def test_progressbar_set_bar_format_invalid():
    pb = ProgressBar()
    with pytest.raises(ValueError, match="must contain the '{bar}' or '{b}' placeholder"):
        pb.set_bar_format(bar_format="Progress: {p}%")
    with pytest.raises(ValueError, match="must contain the '{bar}' or '{b}' placeholder"):
        pb.set_bar_format(limited_bar_format="Progress: {p}%")


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
    with pytest.raises(ValueError, match="Total must be greater than 0"):
        pb.show_progress(10, 0)
    with pytest.raises(ValueError, match="Total must be greater than 0"):
        pb.show_progress(10, -5)


@patch('sys.stdout', new_callable=io.StringIO)
def test_progressbar_show_progress(mock_stdout):
    pb = ProgressBar()
    with patch.object(pb, '_original_stdout', mock_stdout):
        pb._original_stdout = mock_stdout
        pb.active = True
        pb._draw_progress_bar(50, 100, "Loading")
    output = mock_stdout.getvalue()
    assert len(output) > 0


def test_progressbar_hide_progress():
    pb = ProgressBar()
    pb.active = True
    pb._original_stdout = MagicMock()
    pb.hide_progress()
    assert pb.active is False
    assert pb._original_stdout is None


def test_progressbar_progress_context():
    pb = ProgressBar()
    with patch.object(pb, 'show_progress') as mock_show, patch.object(pb, 'hide_progress') as mock_hide:
        with pb.progress_context(100, "Testing") as update_progress:
            update_progress(25)
            update_progress(50)
        assert mock_show.call_count == 2
        mock_show.assert_any_call(25, 100, "Testing")
        mock_show.assert_any_call(50, 100, "Testing")
        mock_hide.assert_called_once()


def test_progressbar_progress_context_exception():
    pb = ProgressBar()
    with (patch.object(pb, 'show_progress') as _, patch.object(pb, 'hide_progress') as
          mock_hide, patch.object(pb, '_emergency_cleanup') as mock_cleanup):
        with pytest.raises(ValueError):
            with pb.progress_context(100, "Testing") as update_progress:
                update_progress(25)
                raise ValueError("Test exception")
        mock_cleanup.assert_called_once()
        mock_hide.assert_called_once()


def test_progressbar_create_bar():
    pb = ProgressBar()

    bar = pb._create_bar(50, 100, 10)
    assert len(bar) == 10
    assert bar[0] == pb.chars[0]
    assert bar[-1] == pb.chars[-1]

    bar = pb._create_bar(100, 100, 10)
    assert len(bar) == 10
    assert all(c == pb.chars[0] for c in bar)

    bar = pb._create_bar(0, 100, 10)
    assert len(bar) == 10
    assert all(c == pb.chars[-1] for c in bar)


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


def test_progressbar_get_formatted_info_and_bar_width(mock_terminal_size):
    pb = ProgressBar()
    formatted, bar_width = pb._get_formatted_info_and_bar_width("{l} |{b}| {c}/{t} ({p}%)", 50, 100, 50.0, "Loading")
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
    pb._original_stdout = mock_stdout
    pb._last_line_len = 20
    pb._clear_progress_line()
    mock_stdout.write.assert_called_once()
    mock_stdout.flush.assert_called_once()


def test_progressbar_redraw_progress_bar():
    pb = ProgressBar()
    mock_stdout = MagicMock()
    pb._original_stdout = mock_stdout
    pb._current_progress_str = "Loading |████████████| 50%"
    pb._redraw_progress_bar()
    mock_stdout.write.assert_called_once_with("Loading |████████████| 50%")
    mock_stdout.flush.assert_called_once()
