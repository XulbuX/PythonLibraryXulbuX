"""
Functions for logging and other small actions within the console.\n
----------------------------------------------------------------------------------------------------------
You can also use special formatting codes directly inside the log message to change their appearance.
For more detailed information about formatting codes, see the the `xx_format_codes` module documentation.
"""

from ._consts_ import COLOR, CHARS
from .xx_format_codes import FormatCodes, _COMPILED
from .xx_string import String
from .xx_color import Color, Rgba, Hexa

from prompt_toolkit.key_binding.key_bindings import KeyBindings
from typing import Optional, Literal, Any
import prompt_toolkit as _prompt_toolkit
import pyperclip as _pyperclip
import keyboard as _keyboard
import getpass as _getpass
import shutil as _shutil
import mouse as _mouse
import sys as _sys
import os as _os


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


class ArgResult:
    """Exists: if the argument was found or not\n
    Value: the value from behind the found argument"""

    def __init__(self, exists: bool, value: Any):
        self.exists = exists
        self.value = value

    def __bool__(self):
        return self.exists


class Args:
    """Stores found command arguments under their aliases with their results."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if not key.isidentifier():
                raise TypeError(f"Argument alias '{key}' is invalid. It must be a valid Python variable name.")
            setattr(self, key, ArgResult(**value))

    def __len__(self):
        return len(vars(self))

    def __contains__(self, key):
        return hasattr(self, key)

    def __getitem__(self, key):
        if isinstance(key, int):
            return list(self.__iter__())[key]
        return getattr(self, key)

    def __iter__(self):
        for key, value in vars(self).items():
            yield (key, {"exists": value.exists, "value": value.value})

    def dict(self) -> dict[str, dict[str, Any]]:
        """Returns the arguments as a dictionary."""
        return {k: {"exists": v.exists, "value": v.value} for k, v in vars(self).items()}

    def keys(self):
        """Returns the argument aliases as `dict_keys([...])`."""
        return vars(self).keys()

    def values(self):
        """Returns the argument results as `dict_values([...])`."""
        return vars(self).values()

    def items(self):
        """Yields tuples of `(alias, {'exists': bool, 'value': Any})`."""
        for key, value in self.__iter__():
            yield (key, value)


class Console:

    w: int = _ConsoleWidth()  # type: ignore[assignment]
    """The width of the console in characters."""
    h: int = _ConsoleHeight()  # type: ignore[assignment]
    """The height of the console in lines."""
    wh: tuple[int, int] = _ConsoleSize()  # type: ignore[assignment]
    """A tuple with the width and height of
    the console in characters and lines."""
    usr: str = _ConsoleUser()  # type: ignore[assignment]
    """The name of the current user."""

    @staticmethod
    def get_args(
        find_args: dict[str, list[str] | tuple[str, ...] | dict[str, list[str] | tuple[str, ...] | Any]],
        allow_spaces: bool = False
    ) -> Args:
        """Will search for the specified arguments in the command line
        arguments and return the results as a special `Args` object.\n
        ----------------------------------------------------------------
        The `find_args` dictionary can have the following structures for each alias:
        1. Simple list/tuple of flags (when no default value is needed):
           ```python
           "alias_name": ["-f", "--flag"]
           ```
        2. Dictionary with 'flags' and optional 'default':
           ```python
           "alias_name": {
               "flags": ["-f", "--flag"],
               "default": "some_value"  # Optional
           }
           ```
        Example `find_args`:
        ```python
        find_args={
            "arg1": { # With default
                "flags": ["-a1", "--arg1"],
                "default": "default_val"
            },
            "arg2": ("-a2", "--arg2"), # Without default (original format)
            "arg3": ["-a3"],          # Without default (list format)
            "arg4": { # Flag with default True
                "flags": ["-f"],
                "default": True
            }
        }
        ```
        If the script is called via the command line:\n
        `python script.py -a1 "value1" --arg2 -f`\n
        ...it would return an `Args` object where:
        - `args.arg1.exists` is `True`, `args.arg1.value` is `"value1"`
        - `args.arg2.exists` is `True`, `args.arg2.value` is `True` (flag present without value)
        - `args.arg3.exists` is `False`, `args.arg3.value` is `None` (not present, no default)
        - `args.arg4.exists` is `True`, `args.arg4.value` is `True` (flag present, overrides default)
        - If an arg defined in `find_args` is *not* present in the command line:
            - `exists` will be `False`
            - `value` will be the specified `default` value, or `None` if no default was specified.\n
        ----------------------------------------------------------------
        Normally if `allow_spaces` is false, it will take a space as
        the end of an args value. If it is true, it will take spaces as
        part of the value until the next arg is found.
        (Multiple spaces will become one space in the value.)"""
        args = _sys.argv[1:]
        args_len = len(args)
        arg_lookup = {}
        results = {}
        for alias, config in find_args.items():
            flags = None
            default_value = None
            if isinstance(config, (list, tuple)):
                flags = config
            elif isinstance(config, dict):
                if "flags" not in config:
                    raise ValueError(f"Invalid configuration for alias '{alias}'. Dictionary must contain a 'flags' key.")
                flags = config["flags"]
                default_value = config.get("default")
                if not isinstance(flags, (list, tuple)):
                    raise ValueError(f"Invalid 'flags' for alias '{alias}'. Must be a list or tuple.")
            else:
                raise TypeError(f"Invalid configuration type for alias '{alias}'. Must be a list, tuple, or dict.")
            results[alias] = {"exists": False, "value": default_value}
            for flag in flags:
                if flag in arg_lookup:
                    raise ValueError(
                        f"Duplicate flag '{flag}' found. It's assigned to both '{arg_lookup[flag]}' and '{alias}'."
                    )
                arg_lookup[flag] = alias
        i = 0
        while i < args_len:
            arg = args[i]
            alias = arg_lookup.get(arg)
            if alias:
                results[alias]["exists"] = True
                value_found_after_flag = False
                if i + 1 < args_len and not args[i + 1].startswith("-"):
                    if not allow_spaces:
                        results[alias]["value"] = String.to_type(args[i + 1])
                        i += 1
                        value_found_after_flag = True
                    else:
                        value_parts = []
                        j = i + 1
                        while j < args_len and not args[j].startswith("-"):
                            value_parts.append(args[j])
                            j += 1
                        if value_parts:
                            results[alias]["value"] = String.to_type(" ".join(value_parts))
                            i = j - 1
                            value_found_after_flag = True
                if not value_found_after_flag:
                    results[alias]["value"] = True
            i += 1
        return Args(**results)

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
        title_bg_color: Optional[Rgba | Hexa] = None,
        default_color: Optional[Rgba | Hexa] = None,
        _console_tabsize: int = 8,
    ) -> None:
        """Will print a formatted log message:
        - `title` -⠀the title of the log message (e.g. `DEBUG`, `WARN`, `FAIL`, etc.)
        - `prompt` -⠀the log message
        - `format_linebreaks` -⠀whether to format (indent after) the line breaks or not
        - `start` -⠀something to print before the log is printed
        - `end` -⠀something to print after the log is printed (e.g. `\\n`)
        - `title_bg_color` -⠀the background color of the `title`
        - `default_color` -⠀the default text color of the `prompt`
        - `_console_tabsize` -⠀the tab size of the console (default is 8)\n
        -----------------------------------------------------------------------------------
        The log message can be formatted with special formatting codes. For more detailed
        information about formatting codes, see `xx_format_codes` module documentation."""
        title = "" if title is None else title.strip().upper()
        title_len, tab_len = len(title) + 4, _console_tabsize - ((len(title) + 4) % _console_tabsize)
        title_color = "_color" if not title_bg_color else Color.text_color_for_on_bg(title_bg_color)
        if format_linebreaks:
            clean_prompt, removals = FormatCodes.remove_formatting(str(prompt), get_removals=True, _ignore_linebreaks=True)
            prompt_lst = (String.split_count(l, Console.w - (title_len + tab_len)) for l in str(clean_prompt).splitlines())
            prompt_lst = (
                item for lst in prompt_lst for item in ([""] if lst == [] else (lst if isinstance(lst, list) else [lst]))
            )
            prompt = f"\n{' ' * title_len}\t".join(
                Console.__add_back_removed_parts(list(prompt_lst), removals)  # type: ignore[assignment]
            )
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
    def __add_back_removed_parts(split_string: list[str], removals: tuple[tuple[int, str], ...]) -> list[str]:
        """Adds back the removed parts into the split string parts at their original positions."""
        lengths, cumulative_pos = [len(s) for s in split_string], [0]
        for length in lengths:
            cumulative_pos.append(cumulative_pos[-1] + length)
        result, offset_adjusts = split_string.copy(), [0] * len(split_string)
        last_idx, total_length = len(split_string) - 1, cumulative_pos[-1]

        def find_string_part(pos: int) -> int:
            left, right = 0, len(cumulative_pos) - 1
            while left < right:
                mid = (left + right) // 2
                if cumulative_pos[mid] <= pos < cumulative_pos[mid + 1]:
                    return mid
                elif pos < cumulative_pos[mid]:
                    right = mid
                else:
                    left = mid + 1
            return left

        for pos, removal in removals:
            if pos >= total_length:
                result[last_idx] = result[last_idx] + removal
                continue
            i = find_string_part(pos)
            adjusted_pos = (pos - cumulative_pos[i]) + offset_adjusts[i]
            parts = [result[i][:adjusted_pos], removal, result[i][adjusted_pos:]]
            result[i] = ''.join(parts)
            offset_adjusts[i] += len(removal)
        return result

    @staticmethod
    def debug(
        prompt: object = "Point in program reached.",
        active: bool = True,
        format_linebreaks: bool = True,
        start: str = "",
        end: str = "\n",
        title_bg_color: Rgba | Hexa = COLOR.yellow,
        default_color: Rgba | Hexa = COLOR.text,
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
        title_bg_color: Rgba | Hexa = COLOR.blue,
        default_color: Rgba | Hexa = COLOR.text,
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
        title_bg_color: Rgba | Hexa = COLOR.teal,
        default_color: Rgba | Hexa = COLOR.text,
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
        title_bg_color: Rgba | Hexa = COLOR.orange,
        default_color: Rgba | Hexa = COLOR.text,
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
        title_bg_color: Rgba | Hexa = COLOR.red,
        default_color: Rgba | Hexa = COLOR.text,
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
        title_bg_color: Rgba | Hexa = COLOR.magenta,
        default_color: Rgba | Hexa = COLOR.text,
        pause: bool = False,
        exit: bool = True,
        reset_ansi=True,
    ) -> None:
        """A preset for `log()`: `EXIT` log message with the options to pause
        at the message and exit the program after the message was printed."""
        Console.log("EXIT", prompt, format_linebreaks, start, end, title_bg_color, default_color)
        Console.pause_exit(pause, exit, reset_ansi=reset_ansi)

    @staticmethod
    def log_box_filled(
        *values: object,
        start: str = "",
        end: str = "\n",
        box_bg_color: Rgba | Hexa = "green",
        default_color: Rgba | Hexa = "#000",
        w_padding: int = 2,
        w_full: bool = False,
    ) -> None:
        """Will print a box with a colored background, containing a formatted log message:
        - `*values` -⠀the box content (each value is on a new line)
        - `start` -⠀something to print before the log box is printed (e.g. `\\n`)
        - `end` -⠀something to print after the log box is printed (e.g. `\\n`)
        - `box_bg_color` -⠀the background color of the box
        - `default_color` -⠀the default text color of the `*values`
        - `w_padding` -⠀the horizontal padding (in chars) to the box content
        - `w_full` -⠀whether to make the box be the full console width or not\n
        -----------------------------------------------------------------------------------
        The box content can be formatted with special formatting codes. For more detailed
        information about formatting codes, see `xx_format_codes` module documentation."""
        lines, unfmt_lines, max_line_len = Console.__prepare_log_box(values)
        pad_w_full = (Console.w - (max_line_len + (2 * w_padding))) if w_full else 0
        lines = [
            f"[bg:{box_bg_color}]{' ' * w_padding}{line}" + " " *
            ((w_padding + max_line_len - len(unfmt)) + pad_w_full) + "[*]" for line, unfmt in zip(lines, unfmt_lines)
        ]
        pady = " " * (Console.w if w_full else max_line_len + (2 * w_padding))
        FormatCodes.print(
            f"{start}[bg:{box_bg_color}]{pady}[*]\n"
            + _COMPILED["formatting"].sub(lambda m: f"{m.group(0)}[bg:{box_bg_color}]", "\n".join(lines))
            + f"\n[bg:{box_bg_color}]{pady}[*]",
            default_color=default_color or "#000",
            sep="\n",
            end=end,
        )

    @staticmethod
    def log_box_bordered(
        *values: object,
        start: str = "",
        end: str = "\n",
        border_type: Literal["standard", "rounded", "strong", "double"] = "rounded",
        border_style: str | Rgba | Hexa = f"dim|{COLOR.gray}",
        default_color: Optional[Rgba | Hexa] = None,
        w_padding: int = 1,
        w_full: bool = False,
        _border_chars: Optional[tuple[str, str, str, str, str, str, str, str]] = None,
    ) -> None:
        """Will print a bordered box, containing a formatted log message:
        - `*values` -⠀the box content (each value is on a new line)
        - `start` -⠀something to print before the log box is printed (e.g. `\\n`)
        - `end` -⠀something to print after the log box is printed (e.g. `\\n`)
        - `border_type` -⠀one of the predefined border character sets
        - `default_color` -⠀the default text color of the `*values`
        - `w_padding` -⠀the horizontal padding (in chars) to the box content
        - `w_full` -⠀whether to make the box be the full console width or not
        - `_border_chars` -⠀define your own border characters set (overwrites `border_type`)\n
        ---------------------------------------------------------------------------------------
        The box content can be formatted with special formatting codes. For more detailed
        information about formatting codes, see `xx_format_codes` module documentation.\n
        ---------------------------------------------------------------------------------------
        The `border_type` can be one of the following:
        - `"standard" = ('┌', '─', '┐', '│', '┘', '─', '└', '│')`
        - `"rounded" = ('╭', '─', '╮', '│', '╯', '─', '╰', '│')`
        - `"strong" = ('┏', '━', '┓', '┃', '┛', '━', '┗', '┃')`
        - `"double" = ('╔', '═', '╗', '║', '╝', '═', '╚', '║')`\n
        The order of the characters is always:
        1. top-left corner
        2. top border
        3. top-right corner
        4. right border
        5. bottom-right corner
        6. bottom border
        7. bottom-left corner
        8. left border"""
        borders = {
            "standard": ('┌', '─', '┐', '│', '┘', '─', '└', '│'),
            "rounded": ('╭', '─', '╮', '│', '╯', '─', '╰', '│'),
            "strong": ('┏', '━', '┓', '┃', '┛', '━', '┗', '┃'),
            "double": ('╔', '═', '╗', '║', '╝', '═', '╚', '║'),
        }
        border_chars = borders.get(border_type, borders["standard"]) if _border_chars is None else _border_chars
        lines, unfmt_lines, max_line_len = Console.__prepare_log_box(values)
        pad_w_full = (Console.w - (max_line_len + (2 * w_padding)) - (len(border_chars[1] * 2))) if w_full else 0
        border_l = f"[{border_style}]{border_chars[7]}[_]"
        border_r = f"[{border_style}]{border_chars[3]}[_]"
        lines = [
            f"{border_l}{' ' * w_padding}{line}[_]" + " " * ((w_padding + max_line_len - len(unfmt)) + pad_w_full) + border_r
            for line, unfmt in zip(lines, unfmt_lines)
        ]
        border_t = f"[{border_style}]{border_chars[0]}{border_chars[1] * (Console.w - (len(border_chars[1] * 2)) if w_full else max_line_len + (2 * w_padding))}{border_chars[2]}[_]"
        border_b = f"[{border_style}]{border_chars[6]}{border_chars[5] * (Console.w - (len(border_chars[1] * 2)) if w_full else max_line_len + (2 * w_padding))}{border_chars[4]}[_]"
        FormatCodes.print(
            f"{start}{border_t}[_]\n" + "\n".join(lines) + f"\n{border_b}[_]",
            default_color=default_color,
            sep="\n",
            end=end,
        )

    @staticmethod
    def __prepare_log_box(values: tuple[object, ...]) -> tuple[list[str], list[tuple[str, tuple[tuple[int, str], ...]]], int]:
        """Prepares the log box content and returns it along with the max line length."""
        lines = [line.rstrip() for val in values for line in str(val).splitlines()]
        unfmt_lines = [FormatCodes.remove_formatting(line) for line in lines]
        max_line_len = max(len(line) for line in unfmt_lines)
        return lines, unfmt_lines, max_line_len  # type: ignore[return]

    @staticmethod
    def confirm(
        prompt: object = "Do you want to continue?",
        start="",
        end="\n",
        default_color: Rgba | Hexa = COLOR.cyan,
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
        default_color: Rgba | Hexa = COLOR.cyan,
        show_keybindings=True,
        input_prefix=" ⮡ ",
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

        FormatCodes.print(start + str(prompt), default_color=default_color)
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
        default_color: Rgba | Hexa = COLOR.cyan,
        allowed_chars: str = CHARS.all,  # type: ignore[assignment]
        min_len: Optional[int] = None,
        max_len: Optional[int] = None,
        mask_char: Optional[str] = None,
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
        FormatCodes.print(start + str(prompt), default_color=default_color, end="")
        result = ""
        select_all = False
        last_line_count = 1
        last_console_width = 0

        def update_display(console_width: int) -> None:
            nonlocal last_line_count, last_console_width
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
            if event.name is not None and ((allowed_chars == CHARS.all or event.name in allowed_chars) and
                                           (max_len is None or len(result) < max_len)):
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
                elif event.name is not None and len(event.name) == 1:
                    handle_character_input()
                else:
                    select_all = False
                    update_display(Console.w)

    @staticmethod
    def pwd_input(
        prompt: object = "Password: ",
        start="",
        end="\n",
        default_color: Rgba | Hexa = COLOR.cyan,
        allowed_chars: str = CHARS.standard_ascii,
        min_len: Optional[int] = None,
        max_len: Optional[int] = None,
        reset_ansi: bool = True,
    ) -> Optional[str]:
        """Password input (preset for `Console.restricted_input()`)
        that always masks the entered characters with asterisks."""
        return Console.restricted_input(
            prompt=prompt,
            start=start,
            end=end,
            default_color=default_color,
            allowed_chars=allowed_chars,
            min_len=min_len,
            max_len=max_len,
            mask_char="*",
            reset_ansi=reset_ansi,
        )
