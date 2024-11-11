"""
Functions for logging and other small actions within the console:
- `Cmd.get_args()`
- `Cmd.user()`
- `Cmd.is_admin()`
- `Cmd.pause_exit()`
- `Cmd.cls()`
- `Cmd.log()`
- `Cmd.debug()`
- `Cmd.info()`
- `Cmd.done()`
- `Cmd.warn()`
- `Cmd.fail()`
- `Cmd.exit()`
- `Cmd.confirm()`
- `Cmd.restricted_input()`
- `Cmd.pwd_input()`\n
----------------------------------------------------------------------------------------------------------
You can also use special formatting codes directly inside the log message to change their appearance.<br>
For more detailed information about formatting codes, see the the `xx_format_codes` description.
"""


from ._consts_ import DEFAULT, CHARS
from .xx_format_codes import *
from .xx_string import *
from .xx_color import *

from contextlib import suppress
import subprocess as _subprocess
import pyperclip as _pyperclip
import keyboard as _keyboard
import getpass as _getpass
import ctypes as _ctypes
import shutil as _shutil
import mouse as _mouse
import sys as _sys
import os as _os




class Cmd:

    @staticmethod
    def get_args(find_args:dict) -> dict:
        args = _sys.argv[1:]
        results = {}
        for arg_key, arg_group in find_args.items():
            value = None
            exists = False
            for arg in arg_group:
                if arg in args:
                    exists = True
                    arg_index = args.index(arg)
                    if arg_index + 1 < len(args) and not args[arg_index + 1].startswith('-'):
                        value = String.to_type(args[arg_index + 1])
                    break
            results[arg_key] = {'exists': exists, 'value': value}
        return results

    def w() -> int: return getattr(_shutil.get_terminal_size(), 'columns', 80)
    def h() -> int: return getattr(_shutil.get_terminal_size(), 'lines', 24)
    def wh() -> tuple[int,int]: return Cmd.w(), Cmd.h()
    def user() -> str: return _os.getenv('USER') or _os.getenv('USERNAME') or _getpass.getuser()

    @staticmethod
    def is_admin() -> bool:
        try:
            if _os.name == 'nt':
                return _ctypes.windll.shell32.IsUserAnAdmin() != 0
            elif _os.name == 'posix':
                return _os.geteuid() == 0
            else:
                return False
        except:
            return False

    @staticmethod
    def pause_exit(pause:bool = False, exit:bool = False, last_prompt:object = '', exit_code:int = 0, reset_ansi:bool = False) -> None:
        """Will print the `last_prompt` and then pause the program if `pause` is set<br>
        to `True` and after the pause, exit the program if `exit` is set to `True`."""
        print(last_prompt, end='', flush=True)
        if reset_ansi: FormatCodes.print('[_]', end='')
        if pause: _keyboard.read_event()
        if exit: _sys.exit(exit_code)

    @staticmethod
    def cls() -> None:
        """Will clear the console in addition to completely resetting the ANSI formats."""
        if _shutil.which('cls'): _os.system('cls')
        elif _shutil.which('clear'): _os.system('clear')
        print('\033[0m', end='', flush=True)

    @staticmethod
    def log(title:str, prompt:object, start:str = '', end:str = '\n', title_bg_color:hexa|rgba = None, default_color:hexa|rgba = None) -> None:
        """Will print a formatted log message:<br>
        `title` -⠀the title of the log message (e.g. `DEBUG`, `WARN`, `FAIL`, etc.)<br>
        `prompt` -⠀the log message<br>
        `start` -⠀something to print before the log is printed<br>
        `end` -⠀something to print after the log is printed (e.g. `\\n\\n`)<br>
        `title_bg_color` -⠀the background color of the `title`<br>
        `default_color` -⠀the default text color of the `prompt`\n
        --------------------------------------------------------------------------------
        The log message supports special formatting codes. For more detailed<br>
        information about formatting codes, see `xx_format_codes` class description."""
        title_color = '_color' if not title_bg_color else Color.text_color_for_on_bg(title_bg_color)
        if title: FormatCodes.print(f'{start}  [bold][{title_color}]{f"[BG:{title_bg_color}]" if title_bg_color else ""} {title.upper()}: [_]\t{f"[{default_color}]" if default_color else ""}{str(prompt)}[_]', default_color, end=end)
        else: FormatCodes.print(f'{start}  {f"[{default_color}]" if default_color else ""}{str(prompt)}[_]', default_color, end=end)

    @staticmethod
    def debug(prompt:object = 'Point in program reached.', active:bool = True, start:str = '\n', end:str = '\n\n', title_bg_color:hexa|rgba = DEFAULT.color['yellow'], default_color:hexa|rgba = DEFAULT.text_color, pause:bool = False, exit:bool = False) -> None:
        """A preset for `log()`: `DEBUG` log message with the options to pause<br>
        at the message and exit the program after the message was printed."""
        if active:
            Cmd.log('DEBUG', prompt, start, end, title_bg_color, default_color)
            Cmd.pause_exit(pause, exit)

    @staticmethod
    def info(prompt:object = 'Program running.', start:str = '\n', end:str = '\n\n', title_bg_color:hexa|rgba = DEFAULT.color['blue'], default_color:hexa|rgba = DEFAULT.text_color, pause:bool = False, exit:bool = False) -> None:
        """A preset for `log()`: `INFO` log message with the options to pause<br>
        at the message and exit the program after the message was printed."""
        Cmd.log('INFO', prompt, start, end, title_bg_color, default_color)
        Cmd.pause_exit(pause, exit)

    @staticmethod
    def done(prompt:object = 'Program finished.', start:str = '\n', end:str = '\n\n', title_bg_color:hexa|rgba = DEFAULT.color['teal'], default_color:hexa|rgba = DEFAULT.text_color, pause:bool = False, exit:bool = False) -> None:
        """A preset for `log()`: `DONE` log message with the options to pause<br>
        at the message and exit the program after the message was printed."""
        Cmd.log('DONE', prompt, start, end, title_bg_color, default_color)
        Cmd.pause_exit(pause, exit)

    @staticmethod
    def warn(prompt:object = 'Important message.', start:str = '\n', end:str = '\n\n', title_bg_color:hexa|rgba = DEFAULT.color['orange'], default_color:hexa|rgba = DEFAULT.text_color, pause:bool = False, exit:bool = False) -> None:
        """A preset for `log()`: `WARN` log message with the options to pause<br>
        at the message and exit the program after the message was printed."""
        Cmd.log('WARN', prompt, start, end, title_bg_color, default_color)
        Cmd.pause_exit(pause, exit)

    @staticmethod
    def fail(prompt:object = 'Program error.', start:str = '\n', end:str = '\n\n', title_bg_color:hexa|rgba = DEFAULT.color['red'], default_color:hexa|rgba = DEFAULT.text_color, pause:bool = False, exit:bool = True, reset_ansi=True) -> None:
        """A preset for `log()`: `FAIL` log message with the options to pause<br>
        at the message and exit the program after the message was printed."""
        Cmd.log('FAIL', prompt, start, end, title_bg_color, default_color)
        Cmd.pause_exit(pause, exit, reset_ansi=reset_ansi)

    @staticmethod
    def exit(prompt:object = 'Program ended.', start:str = '\n', end:str = '\n\n', title_bg_color:hexa|rgba = DEFAULT.color['magenta'], default_color:hexa|rgba = DEFAULT.text_color, pause:bool = False, exit:bool = True, reset_ansi=True) -> None:
        """A preset for `log()`: `EXIT` log message with the options to pause<br>
        at the message and exit the program after the message was printed."""
        Cmd.log('EXIT', prompt, start, end, title_bg_color, default_color)
        Cmd.pause_exit(pause, exit, reset_ansi=reset_ansi)

    @staticmethod
    def input(prompt:object = '', default_color:hexa|rgba = DEFAULT.color['cyan']) -> None:
        """Acts like a standard Python `input()` but the prompt can be formatted with special formatting codes.<br>
        For more detailed information about formatting codes, see the `xx_format_codes` description."""
        return input(FormatCodes.to_ansi(str(prompt), default_color))

    @staticmethod
    def confirm(prompt:object = 'Do you want to continue?', start = '\n', end = '\n', default_color:hexa|rgba = DEFAULT.color['cyan'], default_is_yes:bool = True) -> None:
        """Ask a yes/no question.\n
        -----------------------------------------------------------------------------------
        The question can be formatted with special formatting codes. For more detailed<br>
        information about formatting codes, see the `xx_format_codes` description."""
        confirmed = input(FormatCodes.to_ansi(f'{start}  {str(prompt)} [_|dim](({"Y" if default_is_yes else "y"}/{"n" if default_is_yes else "N"}):  )', default_color)).strip().lower() in (('', 'y', 'yes') if default_is_yes else ('y', 'yes'))
        if end: Cmd.log('', '') if end == '\n' else Cmd.log('', end[1:]) if end.startswith('\n') else Cmd.log('', end)
        return confirmed

    @staticmethod
    def restricted_input(prompt:object = '', allowed_chars:str = CHARS.all, min_length:int = None, max_length:int = None, mask_char:str = None) -> str|None:
        """Acts like a standard Python `input()` with the advantage, that you can specify:
        - what text characters the user is allowed to type and
        - the minimum and/or maximum length of the users input
        - optional mask character (hide user input, e.g. for passwords)\n
        -----------------------------------------------------------------------------------
        The input can be formatted with special formatting codes. For more detailed<br>
        information about formatting codes, see the `xx_format_codes` description."""
        print(prompt, end='', flush=True)
        result, select_all, last_line_count, last_console_width = '', False, 1, 0
        def filter_pasted_text(text:str) -> str:
            if allowed_chars == CHARS.all: return text
            return ''.join(char for char in text if char in allowed_chars)
        def update_display(console_width:int) -> None:
            nonlocal select_all, last_line_count, last_console_width
            lines = String.split_every_chars(str(prompt) + (mask_char * len(result) if mask_char else result), console_width)
            line_count = len(lines)
            if (line_count > 1 or line_count < last_line_count) and not last_line_count == 1:
                if last_console_width > console_width: line_count *= 2
                for _ in range(line_count if line_count < last_line_count and not line_count > last_line_count else line_count - 2 if line_count > last_line_count else line_count - 1):
                    _sys.stdout.write('\033[2K\r\033[A')
            prompt_len = len(str(prompt)) if prompt else 0
            prompt_str, input_str = lines[0][:prompt_len], lines[0][prompt_len:] if len(lines) == 1 else '\n'.join([lines[0][prompt_len:]] + lines[1:])  # SEPARATE THE PROMPT AND THE INPUT
            _sys.stdout.write('\033[2K\r' + prompt_str + ('\033[7m' if select_all else '') + input_str + '\033[0m')
            last_line_count, last_console_width = line_count, console_width
        while True:
            event = _keyboard.read_event()
            if event.event_type == 'down':
                if event.name == 'enter':
                    if min_length is not None and len(result) < min_length:
                        continue
                    print()
                    return result.rstrip('\n')
                elif event.name in ('backspace', 'delete', 'entf'):
                    if select_all: result, select_all = '', False
                    elif result and event.name == 'backspace':
                        result = result[:-1]
                    update_display(Cmd.w())
                elif (event.name == 'v' and _keyboard.is_pressed('ctrl')) or _mouse.is_pressed('right'):
                    if select_all: result, select_all = '', False
                    filtered_text = filter_pasted_text(_pyperclip.paste())
                    if max_length is None or len(result) + len(filtered_text) <= max_length:
                        result += filtered_text
                        update_display(Cmd.w())
                elif event.name == 'a' and _keyboard.is_pressed('ctrl'):
                    select_all = True
                    update_display(Cmd.w())
                elif event.name == 'c' and _keyboard.is_pressed('ctrl') and select_all:
                    with suppress(KeyboardInterrupt):  # PREVENT CTRL+C FROM RAISING A `KeyboardInterrupt` EXCEPTION
                        select_all = False
                        update_display(Cmd.w())
                        _pyperclip.copy(result)
                elif event.name == 'esc':
                    return
                elif event.name == 'space':
                    if (allowed_chars == CHARS.all or ' ' in allowed_chars) and (max_length is None or len(result) < max_length):
                        result += ' '
                        update_display(Cmd.w())
                elif len(event.name) == 1:
                    if (allowed_chars == CHARS.all or event.name in allowed_chars) and (max_length is None or len(result) < max_length):
                        result += event.name
                        update_display(Cmd.w())
                else:  # ANY DISALLOWED OR NON-DEFINED KEY PRESSED
                    select_all = False
                    update_display(Cmd.w())

    @staticmethod
    def pwd_input(prompt:object = 'Password: ', allowed_chars:str = CHARS.standard_ascii, min_length:int = None, max_length:int = None) -> str:
        """Password input that masks the entered characters with asterisks."""
        return Cmd.restricted_input(prompt, allowed_chars, min_length, max_length, mask_char='*')
