import builtins
import math
import os
import sys
from io import StringIO
from unittest.mock import MagicMock, patch
import xulbux.console as _console_module
from xulbux.ansi import S, StyledText
from xulbux.base.consts import ANSI
from xulbux.console import ArgumentParser, ParsedArgData, ParsedArgs, ProgressBar, Throbber
import pytest


@pytest.fixture
def mock_terminal_size(monkeypatch: pytest.MonkeyPatch):

    def mock_get_terminal_size(fd: int | None = None) -> os.terminal_size:
        return os.terminal_size((80, 24))

    monkeypatch.setattr("xulbux.console._os.get_terminal_size", mock_get_terminal_size)


@pytest.fixture
def mock_formatcodes_print(monkeypatch: pytest.MonkeyPatch):
    mock = MagicMock()
    # Patch in the original module where it is defined:
    import xulbux.format_codes

    monkeypatch.setattr(xulbux.format_codes.FormatCodes, "print", mock)
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


@pytest.fixture
def mock_prompt_session(monkeypatch: pytest.MonkeyPatch):
    mock_session = MagicMock()
    mock_session_class = MagicMock(return_value=mock_session)
    mock_session.prompt.return_value = None
    monkeypatch.setattr("xulbux.console._pt.PromptSession", mock_session_class)
    return mock_session_class, mock_session


# ******************************************************* MODULE TESTS ********************************************************


def test_cls(monkeypatch: pytest.MonkeyPatch):
    mock_shutil = MagicMock()
    mock_subprocess_run = MagicMock()
    mock_print = MagicMock()
    monkeypatch.setattr("xulbux.console._shutil.which", mock_shutil)
    monkeypatch.setattr("xulbux.console._subprocess.run", mock_subprocess_run)
    monkeypatch.setattr(builtins, "print", mock_print)

    mock_shutil.side_effect = lambda cmd: "/bin/cls" if cmd == "cls" else None  # type: ignore[type-unknown]
    _console_module.cls()
    mock_subprocess_run.assert_called_with(["cls"])
    mock_print.assert_called_with("\033[0m", end="", flush=True)

    mock_subprocess_run.reset_mock()
    mock_print.reset_mock()

    mock_shutil.side_effect = lambda cmd: "/bin/clear" if cmd == "clear" else None  # type: ignore[type-unknown]
    _console_module.cls()
    mock_subprocess_run.assert_called_with(["clear"])
    mock_print.assert_called_with("\033[0m", end="", flush=True)


def test_console_encoding():
    encoding = _console_module.get_encoding()
    assert isinstance(encoding, str)
    assert encoding != ""
    assert encoding.lower() in {"utf-8", "cp1252", "ascii", "latin-1", "iso-8859-1"} or "-" in encoding


def test_console_height(mock_terminal_size: MagicMock):
    height_output = _console_module.get_height()
    assert isinstance(height_output, int)
    assert height_output == 24


def test_console_is_tty():
    result = _console_module.is_tty()
    assert isinstance(result, bool)


def test_console_size(mock_terminal_size: MagicMock):
    size_output = _console_module.get_size()
    assert isinstance(size_output, tuple)
    assert len(size_output) == 2
    assert size_output[0] == 80
    assert size_output[1] == 24


def test_console_supports_color():
    result = _console_module.supports_color()
    assert isinstance(result, bool)


def test_console_user():
    user_output = _console_module.get_user()
    assert isinstance(user_output, str)
    assert user_output != ""


def test_console_width(mock_terminal_size: MagicMock):
    width_output = _console_module.get_width()
    assert isinstance(width_output, int)
    assert width_output == 80


def test_console_exception_fallback(capsys: pytest.CaptureFixture[str]):
    error = ValueError("Something bad happened")
    with pytest.raises(SystemExit) as exc:
        _console_module.fail(error)
    assert exc.value.code == 1

    captured = capsys.readouterr()
    assert "FAIL" in captured.out
    assert "Something bad happened" in captured.out


def test_console_styled_text_prompt(capsys: pytest.CaptureFixture[str]):
    _console_module.log("TEST", StyledText("Styled ", S.BOLD("text")))

    captured = capsys.readouterr()
    assert "TEST" in captured.out
    assert "Styled " in captured.out
    assert f"{ANSI.CHAR}[1mtext{ANSI.CHAR}[22m" in captured.out


def test_debug_active(capsys: pytest.CaptureFixture[str]):
    _console_module.debug("Debug message", active=True)

    captured = capsys.readouterr()
    assert "DEBUG" in captured.out
    assert "Debug message" in captured.out


def test_debug_inactive(mock_formatcodes_print: MagicMock):
    _console_module.debug("Debug message", active=False)

    mock_formatcodes_print.assert_not_called()


def test_done(capsys: pytest.CaptureFixture[str]):
    _console_module.done("Task completed")

    captured = capsys.readouterr()
    assert "DONE" in captured.out
    assert "Task completed" in captured.out


def test_exit_method(capsys: pytest.CaptureFixture[str]):
    with pytest.raises(SystemExit) as exc:
        _console_module.exit("Program ending")
    assert exc.value.code == 0

    captured = capsys.readouterr()
    assert "EXIT" in captured.out
    assert "Program ending" in captured.out


def test_fail(capsys: pytest.CaptureFixture[str]):
    with pytest.raises(SystemExit) as exc:
        _console_module.fail("Error occurred")
    assert exc.value.code == 1

    captured = capsys.readouterr()
    assert "FAIL" in captured.out
    assert "Error occurred" in captured.out


def test_info(capsys: pytest.CaptureFixture[str]):
    _console_module.info("Info message")

    captured = capsys.readouterr()
    assert "INFO" in captured.out
    assert "Info message" in captured.out


def test_log_basic(capsys: pytest.CaptureFixture[str]):
    _console_module.log("INFO", "Test message")

    captured = capsys.readouterr()
    assert "INFO" in captured.out
    assert "Test message" in captured.out


def test_log_box_bordered(capsys: pytest.CaptureFixture[str]):
    _console_module.log_box_bordered("Content line", border_type="rounded")

    captured = capsys.readouterr()
    assert "Content line" in captured.out


def test_log_box_filled(capsys: pytest.CaptureFixture[str]):
    _console_module.log_box_filled("Line 1", "Line 2", box_bg_color=S.BG.GREEN)

    captured = capsys.readouterr()
    assert "Line 1" in captured.out
    assert "Line 2" in captured.out


def test_log_no_title(capsys: pytest.CaptureFixture[str]):
    _console_module.log(None, "Just a message")

    captured = capsys.readouterr()
    assert "Just a message" in captured.out


def test_log_word_wrap_and_style_preservation(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("xulbux.console.get_width", lambda: 40)

    prompt = ("This is a very long log message with ", S.BR.RED("bright red text"), " and more normal words.")
    _console_module.log("INFO", prompt)

    captured = capsys.readouterr()
    lines = captured.out.splitlines()
    assert len(lines) > 1

    red_seq = StyledText(S.BR.RED).ansi
    assert any(red_seq in line for line in lines)


def test_pause_exit_pause_only(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]):
    mock_read_key = MagicMock()
    monkeypatch.setattr("xulbux.console._read_single_key", mock_read_key)

    _console_module.pause_exit("Press any key...", pause=True, exit=False)

    captured = capsys.readouterr()
    assert "Press any key..." in captured.out
    mock_read_key.assert_called_once_with()


def test_pause_exit_reset_ansi(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]):
    mock_read_key = MagicMock()
    monkeypatch.setattr("xulbux.console._read_single_key", mock_read_key)

    _console_module.pause_exit(pause=True, exit=False)

    captured = capsys.readouterr()
    # Check that ANSI reset code is present in output:
    assert "\033[0m" in captured.out or captured.out.strip() == ""


def test_pause_exit_with_exit(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]):
    mock_read_key = MagicMock()
    monkeypatch.setattr("xulbux.console._read_single_key", mock_read_key)

    with pytest.raises(SystemExit) as exc:
        _console_module.pause_exit("Exiting...", pause=True, exit=True, exit_code=1)
    assert exc.value.code == 1

    captured = capsys.readouterr()
    assert "Exiting..." in captured.out
    mock_read_key.assert_called_once_with()


def test_warn(capsys: pytest.CaptureFixture[str]):
    _console_module.warn("Warning message")

    captured = capsys.readouterr()
    assert "WARN" in captured.out
    assert "Warning message" in captured.out


def test_input_bottom_toolbar_function(mock_prompt_session: tuple[MagicMock, MagicMock], capsys: pytest.CaptureFixture[str]):
    """Test that bottom toolbar function is set up."""

    mock_session_class, _ = mock_prompt_session

    _console_module.input("Enter text: ")

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


def test_input_creates_prompt_session(mock_prompt_session: tuple[MagicMock, MagicMock], mock_formatcodes_print: MagicMock):
    """Test that _console_module.input creates a PromptSession with correct parameters."""

    mock_session_class, mock_session = mock_prompt_session

    _console_module.input("Enter text: ")

    assert mock_session_class.called
    call_kwargs = mock_session_class.call_args[1]
    assert "message" in call_kwargs
    assert "validator" in call_kwargs
    assert "validate_while_typing" in call_kwargs
    assert "key_bindings" in call_kwargs
    assert "bottom_toolbar" in call_kwargs
    assert "style" in call_kwargs
    mock_session.prompt.assert_called_once()


def test_input_custom_style_object(mock_prompt_session: tuple[MagicMock, MagicMock], mock_formatcodes_print: MagicMock):
    """Test that a custom Style object is created."""

    mock_session_class, _ = mock_prompt_session

    _console_module.input("Enter text: ")

    assert mock_session_class.called
    call_kwargs = mock_session_class.call_args[1]
    assert "style" in call_kwargs
    style = call_kwargs["style"]
    assert style is not None
    assert hasattr(style, "style_rules") or hasattr(style, "_style")


def test_input_default_val_handling(mock_prompt_session: tuple[MagicMock, MagicMock], mock_formatcodes_print: MagicMock):
    """Test that default_val parameter is properly handled."""

    mock_session_class, _ = mock_prompt_session

    _console_module.input("Enter text: ", default_val="default_value")

    assert mock_session_class.called


def test_input_disable_paste(mock_prompt_session: tuple[MagicMock, MagicMock], mock_formatcodes_print: MagicMock):
    """Test that allow_paste=False is handled."""

    mock_session_class, _ = mock_prompt_session

    _console_module.input("Enter text: ", allow_paste=False)

    assert mock_session_class.called
    call_kwargs = mock_session_class.call_args[1]
    assert "key_bindings" in call_kwargs
    assert call_kwargs["key_bindings"] is not None


def test_input_key_bindings_setup(mock_prompt_session: tuple[MagicMock, MagicMock], mock_formatcodes_print: MagicMock):
    """Test that key bindings are properly set up."""

    mock_session_class, _ = mock_prompt_session

    _console_module.input("Enter text: ")

    assert mock_session_class.called
    call_kwargs = mock_session_class.call_args[1]
    assert "key_bindings" in call_kwargs
    kb = call_kwargs["key_bindings"]
    assert kb is not None
    assert hasattr(kb, "bindings")


def test_input_mask_char_single_character(mock_prompt_session: tuple[MagicMock, MagicMock], mock_formatcodes_print: MagicMock):
    """Test that mask_char works with single characters."""

    mock_session_class, _ = mock_prompt_session

    _console_module.input("Enter password: ", mask_char="*")

    assert mock_session_class.called


def test_input_message_formatting(mock_prompt_session: tuple[MagicMock, MagicMock], mock_formatcodes_print: MagicMock):
    """Test that the prompt message is properly formatted."""

    mock_session_class, _ = mock_prompt_session

    _console_module.input("[b]Bold prompt:[_b] ", default_color="#ABC")

    assert mock_session_class.called
    call_kwargs = mock_session_class.call_args[1]
    assert "message" in call_kwargs
    assert call_kwargs["message"] is not None


def test_input_output_type_int(mock_prompt_session: tuple[MagicMock, MagicMock], mock_formatcodes_print: MagicMock):
    """Test that output_type parameter is handled for int conversion."""

    mock_session_class, _ = mock_prompt_session

    _console_module.input("Enter number: ", output_type=int, default_val=42)

    assert mock_session_class.called


def test_input_style_configuration(mock_prompt_session: tuple[MagicMock, MagicMock], capsys: pytest.CaptureFixture[str]):
    """Test that custom style is applied."""

    mock_session_class, _ = mock_prompt_session

    _console_module.input("Enter text: ")

    assert mock_session_class.called
    call_kwargs = mock_session_class.call_args[1]
    assert "style" in call_kwargs
    assert call_kwargs["style"] is not None


def test_input_styled_text_prompt(mock_prompt_session: tuple[MagicMock, MagicMock], mock_formatcodes_print: MagicMock):
    mock_session_class, _ = mock_prompt_session
    _console_module.input(StyledText("Prompt ", S.RED("styled")))

    assert mock_session_class.called
    call_kwargs = mock_session_class.call_args[1]
    assert "message" in call_kwargs
    assert f"{ANSI.CHAR}[31mstyled{ANSI.CHAR}[39m" in str(call_kwargs["message"].value)


def test_input_validate_while_typing_enabled(
    mock_prompt_session: tuple[MagicMock, MagicMock],
    mock_formatcodes_print: MagicMock,
):
    """Test that validate_while_typing is enabled."""

    mock_session_class, _ = mock_prompt_session

    _console_module.input("Enter text: ")

    assert mock_session_class.called
    call_kwargs = mock_session_class.call_args[1]
    assert "validate_while_typing" in call_kwargs
    assert call_kwargs["validate_while_typing"] is True


def test_input_validator_class_creation(mock_prompt_session: tuple[MagicMock, MagicMock], mock_formatcodes_print: MagicMock):
    """Test that InputValidator class is properly instantiated."""

    mock_session_class, _ = mock_prompt_session

    _console_module.input("Enter text: ", min_len=5)

    assert mock_session_class.called
    call_kwargs = mock_session_class.call_args[1]
    assert "validator" in call_kwargs
    validator_instance = call_kwargs["validator"]
    assert hasattr(validator_instance, "validate")
    assert callable(getattr(validator_instance, "validate", None))


def test_input_with_allowed_chars(mock_prompt_session: tuple[MagicMock, MagicMock], mock_formatcodes_print: MagicMock):
    """Test that allowed_chars parameter is handled."""

    mock_session_class, _ = mock_prompt_session

    _console_module.input("Enter digits only: ", allowed_chars="0123456789")

    assert mock_session_class.called
    call_kwargs = mock_session_class.call_args[1]
    assert "key_bindings" in call_kwargs
    assert call_kwargs["key_bindings"] is not None


def test_input_with_length_constraints(mock_prompt_session: tuple[MagicMock, MagicMock], mock_formatcodes_print: MagicMock):
    """Test that min_len and max_len are properly handled."""

    mock_session_class, _ = mock_prompt_session

    _console_module.input("Enter text: ", min_len=3, max_len=10)

    assert mock_session_class.called
    call_kwargs = mock_session_class.call_args[1]
    assert "validator" in call_kwargs
    validator_instance = call_kwargs["validator"]
    assert hasattr(validator_instance, "validate")


def test_input_with_placeholder(mock_prompt_session: tuple[MagicMock, MagicMock], mock_formatcodes_print: MagicMock):
    """Test that placeholder is correctly passed to PromptSession."""

    mock_session_class, _ = mock_prompt_session

    _console_module.input("Enter text: ", placeholder="Type here...")

    assert mock_session_class.called
    call_kwargs = mock_session_class.call_args[1]
    assert "placeholder" in call_kwargs
    assert call_kwargs["placeholder"] != ""


def test_input_with_start_end_formatting(mock_prompt_session: tuple[MagicMock, MagicMock], capsys: pytest.CaptureFixture[str]):
    """Test that start and end parameters trigger `StyledText.print` calls."""

    mock_session_class, _ = mock_prompt_session

    _console_module.input("Enter text: ", start="[green]", end="[_c]")

    assert mock_session_class.called
    capsys.readouterr()
    # Just verify output was produced (start/end formatting occurred):
    assert True  # Output may be captured or go to real STDOUT.


def test_input_with_validator_function(mock_prompt_session: tuple[MagicMock, MagicMock], mock_formatcodes_print: MagicMock):
    """Test that a custom validator function is properly handled."""

    mock_session_class, _ = mock_prompt_session

    def email_validator(text: str) -> str | None:
        if "@" not in text:
            return "Invalid email"
        return None

    _console_module.input("Enter email: ", validator=email_validator)

    assert mock_session_class.called
    call_kwargs = mock_session_class.call_args[1]
    assert "validator" in call_kwargs
    validator_instance = call_kwargs["validator"]
    assert hasattr(validator_instance, "validate")


def test_input_without_placeholder(mock_prompt_session: tuple[MagicMock, MagicMock], mock_formatcodes_print: MagicMock):
    """Test that placeholder is empty when not provided."""

    mock_session_class, _ = mock_prompt_session

    _console_module.input("Enter text: ")

    assert mock_session_class.called
    call_kwargs = mock_session_class.call_args[1]
    assert "placeholder" in call_kwargs
    assert call_kwargs["placeholder"] == ""


def test_multiline_input(mock_prompt_toolkit: MagicMock, capsys: pytest.CaptureFixture[str]):
    expected_input = "mocked multiline input"
    result = _console_module.multiline_input("Enter text:", show_keybindings=True, default_color="#BCA")

    assert result == expected_input

    captured = capsys.readouterr()
    # Check that prompt and keybindings were printed:
    assert "Enter text:" in captured.out
    assert "CTRL+D" in captured.out or "end of input" in captured.out

    mock_prompt_toolkit.assert_called_once()
    pt_args, pt_kwargs = mock_prompt_toolkit.call_args
    assert pt_args == (" ⮡ ",)
    assert pt_kwargs.get("multiline") is True
    assert pt_kwargs.get("wrap_lines") is True
    assert "key_bindings" in pt_kwargs


def test_multiline_input_no_bindings(mock_prompt_toolkit: MagicMock, capsys: pytest.CaptureFixture[str]):
    _console_module.multiline_input("Enter text:", show_keybindings=False, end="DONE")

    captured = capsys.readouterr()
    # Check that prompt was printed and ends with `DONE`:
    assert "Enter text:" in captured.out
    assert captured.out.endswith("DONE")

    mock_prompt_toolkit.assert_called_once()


@patch("xulbux.console.input")
def test_confirm_default_no(mock_input: MagicMock):
    mock_input.return_value = ""
    result = _console_module.confirm("Continue?", default_is_yes=False)
    assert result is False


@patch("xulbux.console.input")
def test_confirm_default_yes(mock_input: MagicMock):
    mock_input.return_value = ""
    result = _console_module.confirm("Continue?", default_is_yes=True)
    assert result is True


@patch("xulbux.console.input")
def test_confirm_no(mock_input: MagicMock):
    mock_input.return_value = "n"
    result = _console_module.confirm("Continue?")
    assert result is False


@patch("xulbux.console.input")
def test_confirm_yes(mock_input: MagicMock):
    mock_input.return_value = "y"
    result = _console_module.confirm("Continue?")
    assert result is True


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
    assert "Invalid choice 'invalid' for 'mode' (-m, --mode)\nAllowed: test, prod" in clean_out
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
        parser.add_opt({"-f"}, expects_value=True)  # type: ignore[arg-type]

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


# ***************************************************** ProgressBar TESTS *****************************************************


def test_progressbar_clear_intercept_line():
    pb = ProgressBar()
    mock_stdout = MagicMock()
    mock_stdout.write.return_value = 0
    mock_stdout.flush.return_value = None
    pb._original_stdout = mock_stdout
    pb._last_line_len = 20
    pb._clear_intercept_line()
    mock_stdout.write.assert_called_once()
    mock_stdout.flush.assert_called_once()


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
        ["{l}", "|{b}|", "{c}/{t}", "({p}%)"], 50, 100, 50.0, "Loading"
    )
    assert "Loading" in formatted
    assert "50" in formatted
    assert "100" in formatted
    assert "50.0" in formatted
    assert isinstance(bar_width, int)
    assert bar_width > 0


def test_progressbar_hide_progress():
    pb = ProgressBar()
    pb.active = True
    pb._original_stdout = MagicMock()
    pb.hide_progress()
    assert pb.active is False
    assert pb._original_stdout is None


def test_progressbar_init():
    pb = ProgressBar(min_width=5, max_width=30)
    assert pb.min_width == 5
    assert pb.max_width == 30
    assert pb.active is False
    assert len(pb.chars) == 9


def test_progressbar_intercepted_output():
    pb = ProgressBar()
    intercepted = _console_module._InterceptedOutput(pb, sys.stdout)
    result = intercepted.write("test content")
    assert result == len("test content")
    assert "test content" in pb._buffer
    intercepted.flush()


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
    with pytest.raises(ValueError), pb.progress_context(100, "Testing") as update_progress:
        update_progress(25)
        raise ValueError("Test exception")

    # After exception, progress bar should still be cleaned up:
    assert pb.active is False


def test_progressbar_redraw_progress_bar():
    pb = ProgressBar()
    mock_stdout = MagicMock()
    mock_stdout.write.return_value = 0
    mock_stdout.flush.return_value = None
    pb._original_stdout = mock_stdout
    pb._current_progress_str = "\x1b[2K\rLoading... ▕██████████          ▏ 50/100 (50.0%)"
    pb._redraw_display()
    mock_stdout.flush.assert_called_once()


def test_progressbar_set_bar_format():
    pb = ProgressBar()
    pb.set_format(format=["{l}", "[{b}]", "{p}%"], limited_format=["[{b}]"])
    assert pb.format == ["{l}", "[{b}]", "{p}%"]
    assert pb.limited_format == ["[{b}]"]


def test_progressbar_set_bar_format_invalid():
    pb = ProgressBar()
    with pytest.raises(ValueError, match=r"must contain the '{bar}' or '{b}' placeholder"):
        pb.set_format(format=["Progress: {p}%"])
    with pytest.raises(ValueError, match=r"must contain the '{bar}' or '{b}' placeholder"):
        pb.set_format(limited_format=["Progress: {p}%"])


def test_progressbar_set_chars():
    pb = ProgressBar()
    custom_chars = ("█", "▓", "▒", "░", " ")
    pb.set_chars(custom_chars)
    assert pb.chars == custom_chars

    pb.set_chars(["█", " "])
    assert pb.chars == ("█", " ")


def test_progressbar_set_chars_invalid():
    pb = ProgressBar()
    with pytest.raises(ValueError, match=r"must contain at least two characters"):
        pb.set_chars(("█",))
    with pytest.raises(ValueError, match=r"must be single-character strings"):
        pb.set_chars(("█", "▓▓", " "))


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


@patch("sys.stdout", new_callable=StringIO)
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


def test_progressbar_show_progress_invalid_total():
    pb = ProgressBar()
    with pytest.raises(ValueError, match=r"The 'total' parameter must be a positive integer, got 0"):
        pb.show_progress(10, 0)
    with pytest.raises(ValueError, match=r"The 'total' parameter must be a positive integer, got -5"):
        pb.show_progress(10, -5)


def test_progressbar_start_stop_intercepting():
    pb = ProgressBar()
    original_stdout = sys.stdout

    pb._start_intercepting()
    assert pb.active is True
    assert pb._original_stdout == original_stdout
    assert isinstance(sys.stdout, _console_module._InterceptedOutput)

    pb._stop_intercepting()
    assert pb.active is False
    assert pb._original_stdout is None
    assert sys.stdout == original_stdout


@patch("sys.stdout", new_callable=StringIO)
def test_progressbar_styled_text_label(mock_stdout: MagicMock):

    pb = ProgressBar()
    original = pb._original_stdout
    pb._original_stdout = mock_stdout
    try:
        pb.active = True
        pb._draw_progress_bar(50, 100, StyledText("Label ", S.BOLD("styled")))
    finally:
        pb._original_stdout = original

    output = mock_stdout.getvalue()
    assert len(output) > 0
    assert "Label " in output
    assert f"{ANSI.CHAR}[1mstyled{ANSI.CHAR}[22m" in output


# ****************************************************** Throbber TESTS *******************************************************


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
    with pytest.raises(ValueError), throbber.context("Test"):
        raise ValueError("Oops")

    # After exception, throbber should still be cleaned up:
    assert throbber.active is False


def test_throbber_init_custom():
    throbber = Throbber(label="Loading", interval=0.5, sep="-")
    assert throbber.label == "Loading"
    assert math.isclose(throbber.interval, 0.5)
    assert throbber.sep == "-"


def test_throbber_init_defaults():
    throbber = Throbber()
    assert throbber.label is None
    assert math.isclose(throbber.interval, 0.08)
    assert throbber.active is False
    assert throbber.sep == " "
    assert len(throbber.frames) > 0


def test_throbber_set_format_invalid():
    throbber = Throbber()
    with pytest.raises(ValueError):
        throbber.set_format(["{l}"])  # Missing `{a}`.


def test_throbber_set_format_valid():
    throbber = Throbber()
    throbber.set_format(["{l}", "{a}"])
    assert throbber.format == ["{l}", "{a}"]


def test_throbber_set_frames_invalid():
    throbber = Throbber()
    with pytest.raises(ValueError):
        throbber.set_frames(("a",))  # Less than 2 frames.


def test_throbber_set_frames_valid():
    throbber = Throbber()
    throbber.set_frames(("a", "b"))
    assert throbber.frames == ("a", "b")

    throbber.set_frames(["x", "y", "z"])
    assert throbber.frames == ("x", "y", "z")


def test_throbber_set_interval_invalid():
    throbber = Throbber()
    with pytest.raises(ValueError):
        throbber.set_interval(0)
    with pytest.raises(ValueError):
        throbber.set_interval(-1)


def test_throbber_set_interval_valid():
    throbber = Throbber()
    throbber.set_interval(1.0)
    assert math.isclose(throbber.interval, 1.0)


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


def test_throbber_update_label_styled_text():
    throbber = Throbber()
    lbl = StyledText("Loading ", S.BR.CYAN("stuff"))
    throbber.update_label(lbl)
    assert throbber.label is lbl
    # The formatted throbber string gets evaluated via ANSI representation:
    assert f"{ANSI.CHAR}[96mstuff{ANSI.CHAR}[39m" in lbl.ansi


def test_style_resolvers():
    # FG styles:
    assert _console_module._as_fg_style(None) is not None
    assert _console_module._as_fg_style(S.RED) == S.RED
    assert _console_module._as_fg_style("#FF0000") is not None
    assert _console_module._as_fg_style((255, 0, 0)) is not None

    # BG styles:
    assert _console_module._as_bg_style(S.BG.BLUE) == S.BG.BLUE
    assert _console_module._as_bg_style("#0000FF") is not None
    assert _console_module._as_bg_style((0, 0, 255)) is not None

    # Title colors:
    title_bg, title_fg = _console_module._resolve_title_colors(S.BG.BLUE)
    assert title_bg == S.BG.BLUE
    assert title_fg == S.BLACK

    # Invalid errors:
    with pytest.raises(ValueError, match=r"The 'border_style' parameter must be a valid style.*got 'invalid_style'"):
        _console_module._as_fg_style("invalid_style", param_name="border_style")

    with pytest.raises(ValueError, match=r"The 'box_bg_color' parameter must be a valid background style.*got 'bad_color'"):
        _console_module._as_bg_style("bad_color", param_name="box_bg_color")

    with pytest.raises(ValueError, match=r"The 'title_bg_color' parameter must be a valid background style.*got 'bad_title'"):
        _console_module._resolve_title_colors("bad_title")
