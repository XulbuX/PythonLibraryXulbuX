"""
Functions for logging and other small actions within the console.\n
----------------------------------------------------------------------------------------------------------
You can also use special formatting codes directly inside the log message to change their appearance.
For more detailed information about formatting codes, see the the `xx_format_codes` module documentation.
"""

from ._consts_ import COLOR, CHARS
from .xx_format_codes import FormatCodes, _COMPILED
from .xx_string import String
from .xx_color import Color, rgba, hexa

from prompt_toolkit.key_binding.key_bindings import KeyBindings
from typing import Optional
import prompt_toolkit as _prompt_toolkit
import pyperclip as _pyperclip
import keyboard as _keyboard
import getpass as _getpass
import shutil as _shutil
import mouse as _mouse
import sys as _sys
import os as _os


# YAPF: disable
class _ConsoleWidth:
    def __get__(self, obj, owner=None):
        return _os.get_terminal_size().columns

class _ConsoleHeight:
    def __get__(self, obj, owner=None):
        return _os.get_terminal_size().lines

class _ConsoleSize:
    def __get__(self, obj, owner=None):
        size = _os.get_terminal_size()
        return (size.columns, size.lines)

class _ConsoleUser:
    def __get__(self, obj, owner=None):
        return _os.getenv("USER") or _os.getenv("USERNAME") or _getpass.getuser()
# YAPF: enable


class Console:

    w: int = _ConsoleWidth()
    h: int = _ConsoleHeight()
    wh: tuple[int, int] = _ConsoleSize()
    usr: str = _ConsoleUser()

    @staticmethod
    def get_args(find_args: dict) -> dict[str, dict[str, any]]:
        args = _sys.argv[1:]
        results = {}
        for arg_key, arg_group in find_args.items():
            value = None
            exists = False
            for arg in arg_group:
                if arg in args:
                    exists = True
                    arg_index = args.index(arg)
                    if arg_index + 1 < len(args) and not args[arg_index + 1].startswith("-"):
                        value = String.to_type(args[arg_index + 1])
                    break
            results[arg_key] = {"exists": exists, "value": value}
        return results

    @staticmethod
    def pause_exit(
        pause: bool = False,
        exit: bool = False,
        prompt: object = "",
        exit_code: int = 0,
        reset_ansi: bool = False,
    ) -> None:
        """Will print the `last_prompt` and then pause the program if `pause` is set
        to `True` and after the pause, exit the program if `exit` is set to `True`."""
        print(prompt, end="", flush=True)
        if reset_ansi:
            FormatCodes.print("[_]", end="")
        if pause:
            _keyboard.read_event()
        if exit:
            _sys.exit(exit_code)

    @staticmethod
    def cls() -> None:
        """Will clear the console in addition to completely resetting the ANSI formats."""
        if _shutil.which("cls"):
            _os.system("cls")
        elif _shutil.which("clear"):
            _os.system("clear")
        print("\033[0m", end="", flush=True)

    @staticmethod
    def log(
        title: Optional[str] = None,
        prompt: object = "",
        format_linebreaks: bool = True,
        start: str = "",
        end: str = "\n",
        title_bg_color: hexa | rgba = None,
        default_color: hexa | rgba = None,
        _console_tabsize: int = 8,
    ) -> None:
        """Will print a formatted log message:
        - `title` -⠀the title of the log message (e.g. `DEBUG`, `WARN`, `FAIL`, etc.)
        - `prompt` -⠀the log message
        - `format_linebreaks` -⠀whether to format (indent after) the line breaks or not
        - `start` -⠀something to print before the log is printed
        - `end` -⠀something to print after the log is printed (e.g. `\\n`)
        - `title_bg_color` -⠀the background color of the `title`
        - `default_color` -⠀the default text color of the `prompt`\n
        -----------------------------------------------------------------------------------
        The log message can be formatted with special formatting codes. For more detailed
        information about formatting codes, see `xx_format_codes` module documentation."""
        title = "" if title is None else title.strip().upper()
        title_len, tab_len = len(title) + 4, _console_tabsize - ((len(title) + 4) % _console_tabsize)
        title_color = "_color" if not title_bg_color else Color.text_color_for_on_bg(title_bg_color)
        if format_linebreaks:
            prompt_lst = (String.split_count(l, Console.w - (title_len + tab_len)) for l in str(prompt).splitlines())
            prompt_lst = (item for lst in prompt_lst for item in (lst if isinstance(lst, list) else [lst]))
            prompt = f"\n{' ' * title_len}\t".join(prompt_lst)
        else:
            prompt = str(prompt)
        if title == "":
            FormatCodes.print(
                f'{start}  {f"[{default_color}]" if default_color else ""}{str(prompt)}[_]',
                default_color=default_color,
                end=end,
            )
        else:
            FormatCodes.print(
                f'{start}  [bold][{title_color}]{f"[BG:{title_bg_color}]" if title_bg_color else ""} {title} [_]'
                + f'\t{f"[{default_color}]" if default_color else ""}{prompt}[_]',
                default_color=default_color,
                end=end,
            )

    @staticmethod
    def debug(
        prompt: object = "Point in program reached.",
        active: bool = True,
        format_linebreaks: bool = True,
        start: str = "",
        end: str = "\n",
        title_bg_color: hexa | rgba = COLOR.yellow,
        default_color: hexa | rgba = COLOR.text,
        pause: bool = False,
        exit: bool = False,
    ) -> None:
        """A preset for `log()`: `DEBUG` log message with the options to pause
        at the message and exit the program after the message was printed.
        If `active` is false, no debug message will be printed."""
        if active:
            Console.log("DEBUG", prompt, format_linebreaks, start, end, title_bg_color, default_color)
            Console.pause_exit(pause, exit)

    @staticmethod
    def info(
        prompt: object = "Program running.",
        format_linebreaks: bool = True,
        start: str = "",
        end: str = "\n",
        title_bg_color: hexa | rgba = COLOR.blue,
        default_color: hexa | rgba = COLOR.text,
        pause: bool = False,
        exit: bool = False,
    ) -> None:
        """A preset for `log()`: `INFO` log message with the options to pause
        at the message and exit the program after the message was printed."""
        Console.log("INFO", prompt, format_linebreaks, start, end, title_bg_color, default_color)
        Console.pause_exit(pause, exit)

    @staticmethod
    def done(
        prompt: object = "Program finished.",
        format_linebreaks: bool = True,
        start: str = "",
        end: str = "\n",
        title_bg_color: hexa | rgba = COLOR.teal,
        default_color: hexa | rgba = COLOR.text,
        pause: bool = False,
        exit: bool = False,
    ) -> None:
        """A preset for `log()`: `DONE` log message with the options to pause
        at the message and exit the program after the message was printed."""
        Console.log("DONE", prompt, format_linebreaks, start, end, title_bg_color, default_color)
        Console.pause_exit(pause, exit)

    @staticmethod
    def warn(
        prompt: object = "Important message.",
        format_linebreaks: bool = True,
        start: str = "",
        end: str = "\n",
        title_bg_color: hexa | rgba = COLOR.orange,
        default_color: hexa | rgba = COLOR.text,
        pause: bool = False,
        exit: bool = False,
    ) -> None:
        """A preset for `log()`: `WARN` log message with the options to pause
        at the message and exit the program after the message was printed."""
        Console.log("WARN", prompt, format_linebreaks, start, end, title_bg_color, default_color)
        Console.pause_exit(pause, exit)

    @staticmethod
    def fail(
        prompt: object = "Program error.",
        format_linebreaks: bool = True,
        start: str = "",
        end: str = "\n",
        title_bg_color: hexa | rgba = COLOR.red,
        default_color: hexa | rgba = COLOR.text,
        pause: bool = False,
        exit: bool = True,
        reset_ansi=True,
    ) -> None:
        """A preset for `log()`: `FAIL` log message with the options to pause
        at the message and exit the program after the message was printed."""
        Console.log("FAIL", prompt, format_linebreaks, start, end, title_bg_color, default_color)
        Console.pause_exit(pause, exit, reset_ansi=reset_ansi)

    @staticmethod
    def exit(
        prompt: object = "Program ended.",
        format_linebreaks: bool = True,
        start: str = "",
        end: str = "\n",
        title_bg_color: hexa | rgba = COLOR.magenta,
        default_color: hexa | rgba = COLOR.text,
        pause: bool = False,
        exit: bool = True,
        reset_ansi=True,
    ) -> None:
        """A preset for `log()`: `EXIT` log message with the options to pause
        at the message and exit the program after the message was printed."""
        Console.log("EXIT", prompt, format_linebreaks, start, end, title_bg_color, default_color)
        Console.pause_exit(pause, exit, reset_ansi=reset_ansi)

    @staticmethod
    def log_box(
        *values: object,
        start: str = "",
        end: str = "\n",
        box_bg_color: str | hexa | rgba = "green",
        default_color: hexa | rgba = "#000",
        w_padding: int = 2,
        w_full: bool = False,
    ) -> None:
        """Will print a box, containing a formatted log message:
        - `*values` -⠀the box content (each value is on a new line)
        - `start` -⠀something to print before the log box is printed
        - `end` -⠀something to print after the log box is printed (e.g. `\\n`)
        - `box_bg_color` -⠀the background color of the box
        - `default_color` -⠀the default text color of the `*values`
        - `w_padding` -⠀the horizontal padding (in chars) to the box content
        - `w_full` -⠀whether to make the box be the full console width or not\n
        -----------------------------------------------------------------------------------
        The box content can be formatted with special formatting codes. For more detailed
        information about formatting codes, see `xx_format_codes` module documentation."""
        lines = [line.strip() for val in values for line in val.splitlines()]
        unfmt_lines = [FormatCodes.remove_formatting(line) for line in lines]
        max_line_len = max(len(line) for line in unfmt_lines)
        pad_w_full = (Console.w - (max_line_len + (2 * w_padding))) if w_full else 0
        lines = [
            f"[bg:{box_bg_color}]{' ' * w_padding}{line}" + " " *
            ((w_padding + max_line_len - len(unfmt)) + pad_w_full) + "[_bg]" for line, unfmt in zip(lines, unfmt_lines)
        ]
        pady = " " * (Console.w if w_full else max_line_len + (2 * w_padding))
        FormatCodes.print(
            f"{start}[bg:{box_bg_color}]{pady}[_bg]\n"
            + _COMPILED["formatting"].sub(lambda m: f"{m.group(0)}[bg:{box_bg_color}]", "\n".join(lines))
            + f"\n[bg:{box_bg_color}]{pady}[_bg]",
            default_color=default_color,
            sep="\n",
            end=end,
        )

    @staticmethod
    def confirm(
        prompt: object = "Do you want to continue?",
        start="",
        end="\n",
        default_color: hexa | rgba = COLOR.cyan,
        default_is_yes: bool = True,
    ) -> bool:
        """Ask a yes/no question.\n
        ---------------------------------------------------------------------------------------
        The prompt can be formatted with special formatting codes. For more detailed
        information about formatting codes, see the `xx_format_codes` module documentation."""
        confirmed = input(
            FormatCodes.to_ansi(
                f'{start}  {str(prompt)} [_|dim](({"Y" if default_is_yes else "y"}/{"n" if default_is_yes else "N"}):  )',
                default_color,
            )
        ).strip().lower() in (("", "y", "yes") if default_is_yes else ("y", "yes"))
        if end:
            Console.log("", end, end="")
        return confirmed

    @staticmethod
    def multiline_input(
        prompt: object = "",
        start="",
        end="\n",
        default_color: hexa | rgba = COLOR.cyan,
        show_keybindings=True,
        input_prefix=" ⤷ ",
        reset_ansi=True,
    ) -> str:
        """An input where users can input (and paste) text over multiple lines.\n
        -----------------------------------------------------------------------------------
        - `prompt` -⠀the input prompt
        - `start` -⠀something to print before the input
        - `end` -⠀something to print after the input (e.g. `\\n`)
        - `default_color` -⠀the default text color of the `prompt`
        - `show_keybindings` -⠀whether to show the special keybindings or not
        - `input_prefix` -⠀the prefix of the input line
        - `reset_ansi` -⠀whether to reset the ANSI codes after the input or not
        -----------------------------------------------------------------------------------
        The input prompt can be formatted with special formatting codes. For more detailed
        information about formatting codes, see `xx_format_codes` module documentation."""
        kb = KeyBindings()

        @kb.add("c-d", eager=True)  # CTRL+D
        def _(event):
            event.app.exit(result=event.app.current_buffer.document.text)

        FormatCodes.print(start + prompt, default_color=default_color)
        if show_keybindings:
            FormatCodes.print("[dim][[b](CTRL+D)[dim] : end of input][_dim]")
        input_string = _prompt_toolkit.prompt(input_prefix, multiline=True, wrap_lines=True, key_bindings=kb)
        FormatCodes.print("[_]" if reset_ansi else "", end=end[1:] if end.startswith("\n") else end)
        return input_string

    @staticmethod
    def restricted_input(
        prompt: object = "",
        start="",
        end="\n",
        default_color: hexa | rgba = COLOR.cyan,
        allowed_chars: str = CHARS.all,
        min_len: int = None,
        max_len: int = None,
        mask_char: str = None,
        reset_ansi: bool = True,
    ) -> Optional[str]:
        """Acts like a standard Python `input()` with the advantage, that you can specify:
        - what text characters the user is allowed to type and
        - the minimum and/or maximum length of the users input
        - optional mask character (hide user input, e.g. for passwords)
        - reset the ANSI formatting codes after the user continues\n
        ---------------------------------------------------------------------------------------
        The input can be formatted with special formatting codes. For more detailed
        information about formatting codes, see the `xx_format_codes` module documentation."""
        FormatCodes.print(start + prompt, default_color=default_color, end="")
        result = ""
        select_all = False
        last_line_count = 1
        last_console_width = 0

        def update_display(console_width: int) -> None:
            nonlocal select_all, last_line_count, last_console_width
            lines = String.split_count(str(prompt) + (mask_char * len(result) if mask_char else result), console_width)
            line_count = len(lines)
            if (line_count > 1 or line_count < last_line_count) and not last_line_count == 1:
                if last_console_width > console_width:
                    line_count *= 2
                for _ in range(line_count if line_count < last_line_count and not line_count > last_line_count else (
                        line_count - 2 if line_count > last_line_count else line_count - 1)):
                    _sys.stdout.write("\033[2K\r\033[A")
            prompt_len = len(str(prompt)) if prompt else 0
            prompt_str = lines[0][:prompt_len]
            input_str = (
                lines[0][prompt_len:] if len(lines) == 1 else "\n".join([lines[0][prompt_len:]] + lines[1:])
            )  # SEPARATE THE PROMPT AND THE INPUT
            _sys.stdout.write(
                "\033[2K\r" + FormatCodes.to_ansi(prompt_str) + ("\033[7m" if select_all else "") + input_str + "\033[27m"
            )
            last_line_count, last_console_width = line_count, console_width

        def handle_enter():
            if min_len is not None and len(result) < min_len:
                return False
            FormatCodes.print(f"[_]{end}" if reset_ansi else end, default_color=default_color)
            return True

        def handle_backspace_delete():
            nonlocal result, select_all
            if select_all:
                result, select_all = "", False
            elif result and event.name == "backspace":
                result = result[:-1]
            update_display(Console.w)

        def handle_paste():
            nonlocal result, select_all
            if select_all:
                result, select_all = "", False
            filtered_text = "".join(char for char in _pyperclip.paste() if allowed_chars == CHARS.all or char in allowed_chars)
            if max_len is None or len(result) + len(filtered_text) <= max_len:
                result += filtered_text
                update_display(Console.w)

        def handle_select_all():
            nonlocal select_all
            select_all = True
            update_display(Console.w)

        def handle_character_input():
            nonlocal result
            if (allowed_chars == CHARS.all or event.name in allowed_chars) and (max_len is None or len(result) < max_len):
                result += event.name
                update_display(Console.w)

        while True:
            event = _keyboard.read_event()
            if event.event_type == "down":
                if event.name == "enter" and handle_enter():
                    return result.rstrip("\n")
                elif event.name in ("backspace", "delete", "entf"):
                    handle_backspace_delete()
                elif (event.name == "v" and _keyboard.is_pressed("ctrl")) or _mouse.is_pressed("right"):
                    handle_paste()
                elif event.name == "a" and _keyboard.is_pressed("ctrl"):
                    handle_select_all()
                elif event.name == "c" and _keyboard.is_pressed("ctrl"):
                    raise KeyboardInterrupt
                elif event.name == "esc":
                    return None
                elif event.name == "space":
                    handle_character_input()
                elif len(event.name) == 1:
                    handle_character_input()
                else:
                    select_all = False
                    update_display(Console.w)

    @staticmethod
    def pwd_input(
        prompt: object = "Password: ",
        start="",
        end="\n",
        default_color: hexa | rgba = COLOR.cyan,
        allowed_chars: str = CHARS.standard_ascii,
        min_len: int = None,
        max_len: int = None,
        reset_ansi: bool = True,
    ) -> str:
        """Password input (preset for `Console.restricted_input()`)
        that always masks the entered characters with asterisks."""
        return Console.restricted_input(prompt, start, end, default_color, allowed_chars, min_len, max_len, "*", reset_ansi)
