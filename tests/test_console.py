from xulbux import Console, Args, ArgResult
from xulbux import xx_console

from unittest.mock import MagicMock
from collections import namedtuple
import builtins
import pytest
import sys


@pytest.fixture
def mock_terminal_size(monkeypatch):
    TerminalSize = namedtuple('TerminalSize', ['columns', 'lines'])
    mock_get_terminal_size = lambda: TerminalSize(columns=80, lines=24)
    monkeypatch.setattr(xx_console._os, 'get_terminal_size', mock_get_terminal_size)


@pytest.fixture
def mock_formatcodes_print(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr(xx_console.FormatCodes, 'print', mock)
    return mock


@pytest.fixture
def mock_builtin_input(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr(builtins, 'input', mock)
    return mock


@pytest.fixture
def mock_prompt_toolkit(monkeypatch):
    mock = MagicMock(return_value="mocked multiline input")
    monkeypatch.setattr(xx_console._prompt_toolkit, 'prompt', mock)
    return mock


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
                               }, {"file": {"exists": False, "value": None}, "debug": {"exists": True, "value": True}}),
        # FLAG WITH VALUE
        (["script.py", "-f", "test.txt"], {"file": ["-f"], "debug": ["-d"]},
         {"file": {"exists": True, "value": "test.txt"}, "debug": {"exists": False, "value": None}}),
        # LONG FLAGS WITH VALUE AND FLAG
        (["script.py", "--file", "path/to/file", "--debug"], {"file": ["-f", "--file"], "debug": ["-d", "--debug"]},
         {"file": {"exists": True, "value": "path/to/file"}, "debug": {"exists": True, "value": True}}),
        # VALUE WITH SPACE (IGNORED DUE TO allow_spaces=False)
        (["script.py", "-f", "file with spaces"], {"file": ["-f"]}, {"file": {"exists": True, "value": "file with spaces"}}),
        # UNKNOWN ARG
        (["script.py", "-x"], {"file": ["-f"]}, {"file": {"exists": False, "value": None}}),
        # TWO FLAGS
        (["script.py", "-f", "-d"], {"file": ["-f"], "debug": ["-d"]
                                     }, {"file": {"exists": True, "value": True}, "debug": {"exists": True, "value": True}}),
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
        # FLAG PRESENCE OVERRIDES DEFAULT (string -> True)
        (["script.py", "-o"], {"output": {"flags": ["-o"], "default": "out.txt"}, "verbose": ["-v"]
                               }, {"output": {"exists": True, "value": True}, "verbose": {"exists": False, "value": None}}),
        # FLAG PRESENCE OVERRIDES DEFAULT (False -> True)
        (["script.py", "-v"], {
            "output": {"flags": ["-o"], "default": "out.txt"}, "verbose": {"flags": ["-v"], "default": False}
        }, {"output": {"exists": False, "value": "out.txt"}, "verbose": {"exists": True, "value": True}}),
        # DEFAULT USED (int)
        (["script.py"], {"mode": {"flags": ["-m"], "default": 1}}, {"mode": {"exists": False, "value": 1}}),
        # VALUE OVERRIDES DEFAULT (int)
        (["script.py", "-m", "2"], {"mode": {"flags": ["-m"], "default": 1}}, {"mode": {"exists": True, "value": 2}}),
        # FLAG PRESENCE OVERRIDES DEFAULT (int -> True)
        (["script.py", "-m"], {"mode": {"flags": ["-m"], "default": 1}}, {"mode": {"exists": True, "value": True}}),

        # --- MIXED list/tuple AND dict FORMATS (allow_spaces=False) ---
        # DICT VALUE PROVIDED, LIST NOT PROVIDED
        (["script.py", "--config", "dev.cfg"], {"config": {"flags": ["-c", "--config"], "default": "prod.cfg"}, "log": ["-l"]},
         {"config": {"exists": True, "value": "dev.cfg"}, "log": {"exists": False, "value": None}}),
        # LIST FLAG PROVIDED, DICT NOT PROVIDED (USES DEFAULT)
        (["script.py", "-l"], {"config": {"flags": ["-c", "--config"], "default": "prod.cfg"}, "log": ["-l"]
                               }, {"config": {"exists": False, "value": "prod.cfg"}, "log": {"exists": True, "value": True}}),
    ]
)
def test_get_args_no_spaces(monkeypatch, argv, find_args, expected_args_dict):
    monkeypatch.setattr(sys, 'argv', argv)
    args_result = Console.get_args(find_args, allow_spaces=False)
    assert isinstance(args_result, Args)
    assert args_result.dict() == expected_args_dict
    for key, expected in expected_args_dict.items():
        assert (key in args_result) is True
        assert isinstance(args_result[key], ArgResult)
        assert args_result[key].exists == expected["exists"]
        assert args_result[key].value == expected["value"]
        assert bool(args_result[key]) == expected["exists"]
    assert list(args_result.keys()) == list(expected_args_dict.keys())
    assert [v.exists for v in args_result.values()] == [d['exists'] for d in expected_args_dict.values()]
    assert [v.value for v in args_result.values()] == [d['value'] for d in expected_args_dict.values()]
    assert len(args_result) == len(expected_args_dict)


@pytest.mark.parametrize(
    "argv, find_args, expected_args_dict", [
        # --- CASES WITH SPACES (allow_spaces=True) ---
        # SIMPLE VALUE WITH SPACES
        (["script.py", "-f", "file with spaces", "-d"], {"file": ["-f"], "debug": ["-d"]},
         {"file": {"exists": True, "value": "file with spaces"}, "debug": {"exists": True, "value": True}}),
        # LONG VALUE WITH SPACES
        (["script.py", "--message", "Hello", "world", "how", "are", "you"
          ], {"message": ["--message"]}, {"message": {"exists": True, "value": "Hello world how are you"}}),
        # VALUE WITH SPACES FOLLOWED BY ANOTHER FLAG
        (["script.py", "-m", "this is", "a message", "--flag"], {"message": ["-m"], "flag": ["--flag"]},
         {"message": {"exists": True, "value": "this is a message"}, "flag": {"exists": True, "value": True}}),
        # VALUE WITH SPACES AT THE END
        (["script.py", "-m", "end", "of", "args"], {"message": ["-m"]}, {"message": {"exists": True, "value": "end of args"}}),

        # --- CASES WITH DEFAULTS (dict FORMAT, allow_spaces=True) ---
        # VALUE WITH SPACE OVERRIDES DEFAULT
        (["script.py", "--msg", "Default message"], {"msg": {"flags": ["--msg"], "default": "No message"}, "other": ["-o"]},
         {"msg": {"exists": True, "value": "Default message"}, "other": {"exists": False, "value": None}}),
        # DEFAULT USED WHEN OTHER FLAG PRESENT
        (["script.py", "-o"], {"msg": {"flags": ["--msg"], "default": "No message"}, "other": ["-o"]
                               }, {"msg": {"exists": False, "value": "No message"}, "other": {"exists": True, "value": True}}),
        # FLAG PRESENCE OVERRIDES DEFAULT (str -> True)
        (["script.py", "--msg"], {"msg": {"flags": ["--msg"], "default": "No message"}, "other": ["-o"]
                                  }, {"msg": {"exists": True, "value": True}, "other": {"exists": False, "value": None}}),

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
    monkeypatch.setattr(sys, 'argv', argv)
    args_result = Console.get_args(find_args, allow_spaces=True)
    assert isinstance(args_result, Args)
    assert args_result.dict() == expected_args_dict


def test_get_args_invalid_alias():
    with pytest.raises(TypeError, match="Argument alias 'invalid-alias' is invalid."):
        Args(**{"invalid-alias": {"exists": False, "value": None}})

    with pytest.raises(TypeError, match="Argument alias '123start' is invalid."):
        Args(**{"123start": {"exists": False, "value": None}})


def test_get_args_invalid_config():
    with pytest.raises(TypeError, match="Invalid configuration type for alias 'bad_config'. Must be a list, tuple, or dict."):
        Console.get_args({"bad_config": 123})

    with pytest.raises(ValueError,
                       match="Invalid configuration for alias 'missing_flags'. Dictionary must contain a 'flags' key."):
        Console.get_args({"missing_flags": {"default": "value"}})

    with pytest.raises(ValueError, match="Invalid 'flags' for alias 'bad_flags'. Must be a list or tuple."):
        Console.get_args({"bad_flags": {"flags": "not-a-list"}})


def test_get_args_duplicate_flag():
    with pytest.raises(ValueError, match="Duplicate flag '-f' found. It's assigned to both 'file1' and 'file2'."):
        Console.get_args({"file1": ["-f", "--file1"], "file2": {"flags": ["-f", "--file2"]}})

    with pytest.raises(ValueError, match="Duplicate flag '--long' found. It's assigned to both 'arg1' and 'arg2'."):
        Console.get_args({"arg1": {"flags": ["--long"]}, "arg2": ("-a", "--long")})


def test_multiline_input(mock_prompt_toolkit, mock_formatcodes_print):
    expected_input = "mocked multiline input"
    result = Console.multiline_input("Enter text:", show_keybindings=True, default_color="#BCA")

    assert result == expected_input
    assert mock_formatcodes_print.call_count == 3
    prompt_call = mock_formatcodes_print.call_args_list[0]
    keybind_call = mock_formatcodes_print.call_args_list[1]
    reset_call = mock_formatcodes_print.call_args_list[2]

    assert prompt_call.args == ("Enter text:", )
    assert prompt_call.kwargs == {'default_color': '#BCA'}

    assert "[dim][[b](CTRL+D)[dim] : end of input][_dim]" in keybind_call.args[0]

    assert reset_call.args == ('[_]', )
    assert reset_call.kwargs == {'end': ''}

    mock_prompt_toolkit.assert_called_once()
    pt_args, pt_kwargs = mock_prompt_toolkit.call_args
    assert pt_args == (" ⤷ ", )
    assert pt_kwargs.get('multiline') is True
    assert pt_kwargs.get('wrap_lines') is True
    assert 'key_bindings' in pt_kwargs


def test_multiline_input_no_bindings(mock_prompt_toolkit, mock_formatcodes_print):
    Console.multiline_input("Enter text:", show_keybindings=False, end="DONE")

    assert mock_formatcodes_print.call_count == 2
    prompt_call = mock_formatcodes_print.call_args_list[0]
    reset_call = mock_formatcodes_print.call_args_list[1]

    assert prompt_call.args == ("Enter text:", )
    assert reset_call.args == ('[_]', )
    assert reset_call.kwargs == {'end': 'DONE'}

    mock_prompt_toolkit.assert_called_once()
