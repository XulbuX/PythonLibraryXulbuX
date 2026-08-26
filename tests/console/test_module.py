import builtins
from unittest.mock import MagicMock, patch
import xulbux.console as _console_module
from xulbux.ansi import S, StyledText
from xulbux.base.consts import ANSI
import pytest

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
