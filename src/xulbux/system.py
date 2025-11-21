"""
This module provides the `System` class, which offers
methods to interact with the underlying operating system.
"""

from .base.types import MissingLibsMsgs

from .format_codes import FormatCodes
from .console import Console

from typing import Optional
import subprocess as _subprocess
import platform as _platform
import ctypes as _ctypes
import time as _time
import sys as _sys
import os as _os


class _IsElevated:

    def __get__(self, obj, owner=None):
        try:
            if _os.name == "nt":
                return _ctypes.windll.shell32.IsUserAnAdmin() != 0  # type: ignore[attr-defined]
            elif _os.name == "posix":
                return _os.geteuid() == 0  # type: ignore[attr-defined]
        except Exception:
            pass
        return False


class System:
    """This class provides methods to interact with the underlying operating system."""

    is_elevated: bool = _IsElevated()  # type: ignore[assignment]
    """Is `True` if the current process has elevated privileges and `False` otherwise."""

    @staticmethod
    def restart(prompt: object = "", wait: int = 0, continue_program: bool = False, force: bool = False) -> None:
        """Restarts the system with some advanced options\n
        --------------------------------------------------------------------------------------------------
        - `prompt` -⠀the message to be displayed in the systems restart notification
        - `wait` -⠀the time to wait until restarting in seconds
        - `continue_program` -⠀whether to continue the current Python program after calling this function
        - `force` -⠀whether to force a restart even if other processes are still running"""
        if not isinstance(wait, int):
            raise TypeError(f"The 'wait' parameter must be an integer, got {type(wait)}")
        elif wait < 0:
            raise ValueError(f"The 'wait' parameter must be non-negative, got {wait!r}")
        if not isinstance(continue_program, bool):
            raise TypeError(f"The 'continue_program' parameter must be a boolean, got {type(continue_program)}")
        if not isinstance(force, bool):
            raise TypeError(f"The 'force' parameter must be a boolean, got {type(force)}")

        if (system := _platform.system().lower()) == "windows":
            if not force:
                output = _subprocess.check_output("tasklist", shell=True).decode()
                processes = [line.split()[0] for line in output.splitlines()[3:] if line.strip()]
                if len(processes) > 2:  # EXCLUDING THE PYTHON PROCESS AND CONSOLE
                    raise RuntimeError("Processes are still running. Use the parameter `force=True` to restart anyway.")

            if prompt:
                _os.system(f'shutdown /r /t {wait} /c "{prompt}"')
            else:
                _os.system("shutdown /r /t 0")

            if continue_program:
                print(f"Restarting in {wait} seconds...")
                _time.sleep(wait)

        elif system in {"linux", "darwin"}:
            if not force:
                output = _subprocess.check_output(["ps", "-A"]).decode()
                processes = output.splitlines()[1:]  # EXCLUDE HEADER
                if len(processes) > 2:  # EXCLUDING THE PYTHON PROCESS AND PS
                    raise RuntimeError("Processes are still running. Use the parameter `force=True` to restart anyway.")

            if prompt:
                _subprocess.Popen(["notify-send", "System Restart", str(prompt)])
                _time.sleep(wait)

            try:
                _subprocess.run(["sudo", "shutdown", "-r", "now"])
            except _subprocess.CalledProcessError:
                raise PermissionError("Failed to restart: insufficient privileges. Ensure sudo permissions are granted.")

            if continue_program:
                print(f"Restarting in {wait} seconds...")
                _time.sleep(wait)

        else:
            raise NotImplementedError(f"Restart not implemented for '{system}' systems.")

    @staticmethod
    def check_libs(
        lib_names: list[str],
        install_missing: bool = False,
        missing_libs_msgs: MissingLibsMsgs = {
            "found_missing": "The following required libraries are missing:",
            "should_install": "Do you want to install them now?",
        },
        confirm_install: bool = True,
    ) -> Optional[list[str]]:
        """Checks if the given list of libraries are installed and optionally installs missing libraries.\n
        ------------------------------------------------------------------------------------------------------------
        - `lib_names` -⠀a list of library names to check
        - `install_missing` -⠀whether to directly missing libraries will be installed automatically using pip
        - `missing_libs_msgs` -⠀two messages: the first one is displayed when missing libraries are found,
          the second one is the confirmation message before installing missing libraries
        - `confirm_install` -⠀whether the user will be asked for confirmation before installing missing libraries\n
        ------------------------------------------------------------------------------------------------------------
        If some libraries are missing or they could not be installed, their names will be returned as a list.
        If all libraries are installed (or were installed successfully), `None` will be returned."""
        if not isinstance(lib_names, list):
            raise TypeError(f"The 'lib_names' parameter must be a list, got {type(lib_names)}")
        elif not all(isinstance(lib, str) for lib in lib_names):
            raise TypeError("All items in the 'lib_names' list must be strings.")
        if not isinstance(install_missing, bool):
            raise TypeError(f"The 'install_missing' parameter must be a boolean, got {type(install_missing)}")
        if not isinstance(missing_libs_msgs, dict):
            raise TypeError(f"The 'missing_libs_msgs' parameter must be a dict, got {type(missing_libs_msgs)}")
        elif not all(key in missing_libs_msgs for key in {"found_missing", "should_install"}):
            raise ValueError("The 'missing_libs_msgs' dict must contain the keys 'found_missing' and 'should_install'.")
        if not isinstance(confirm_install, bool):
            raise TypeError(f"The 'confirm_install' parameter must be a boolean, got {type(confirm_install)}")

        missing = []
        for lib in lib_names:
            try:
                __import__(lib)
            except ImportError:
                missing.append(lib)

        if not missing:
            return None
        elif not install_missing:
            return missing

        if confirm_install:
            FormatCodes.print(f"[b]({missing_libs_msgs['found_missing']})")
            for lib in missing:
                FormatCodes.print(f" [dim](•) [i]{lib}[_i]")
            print()
            if not Console.confirm(missing_libs_msgs["should_install"], end="\n"):
                return missing

        try:
            for lib in missing:
                try:
                    _subprocess.check_call([_sys.executable, "-m", "pip", "install", lib])
                    missing.remove(lib)
                except _subprocess.CalledProcessError:
                    pass

            if len(missing) == 0:
                return None
            else:
                return missing

        except _subprocess.CalledProcessError:
            return missing

    @staticmethod
    def elevate(win_title: Optional[str] = None, args: list = []) -> bool:
        """Attempts to start a new process with elevated privileges.\n
        ---------------------------------------------------------------------------------
        - `win_title` -⠀the window title of the elevated process (only on Windows)
        - `args` -⠀a list of additional arguments to be passed to the elevated process\n
        ---------------------------------------------------------------------------------
        After the elevated process started, the original process will exit.<br>
        This means, that this method has to be run at the beginning of the program or
        or else the program has to continue in a new window after elevation.\n
        ---------------------------------------------------------------------------------
        Returns `True` if the current process already has elevated privileges and raises
        a `PermissionError` if the user denied the elevation or the elevation failed."""
        if not isinstance(win_title, (str, type(None))):
            raise TypeError(f"The 'win_title' parameter must be a string or None, got {type(win_title)}")
        if not isinstance(args, list):
            raise TypeError(f"The 'args' parameter must be a list, got {type(args)}")

        if System.is_elevated:
            return True

        if _os.name == "nt":  # WINDOWS
            if win_title:
                args_str = f'-c "import ctypes; ctypes.windll.kernel32.SetConsoleTitleW(\\"{win_title}\\"); exec(open(\\"{_sys.argv[0]}\\").read())" {" ".join(args)}"'
            else:
                args_str = f'-c "exec(open(\\"{_sys.argv[0]}\\").read())" {" ".join(args)}'

            result = _ctypes.windll.shell32.ShellExecuteW(None, "runas", _sys.executable, args_str, None, 1)
            if result <= 32:
                raise PermissionError("Failed to launch elevated process.")
            else:
                _sys.exit(0)

        else:  # POSIX
            cmd = ["pkexec"]
            if win_title:
                cmd.extend(["--description", win_title])
            cmd.extend([_sys.executable] + _sys.argv[1:] + ([] if args is None else args))

            proc = _subprocess.Popen(cmd)
            proc.wait()
            if proc.returncode != 0:
                raise PermissionError("Process elevation was denied.")
            _sys.exit(0)
