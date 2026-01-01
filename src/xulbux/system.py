"""
This module provides the `System` class, which includes
methods to interact with the underlying operating system.
"""

from .base.types import MissingLibsMsgs

from .format_codes import FormatCodes
from .console import Console

from typing import Optional
from mypy_extensions import mypyc_attr
import subprocess as _subprocess
import platform as _platform
import ctypes as _ctypes
import time as _time
import sys as _sys
import os as _os


@mypyc_attr(native_class=False)
class _SystemMeta(type):

    @property
    def is_elevated(cls) -> bool:
        """Whether the current process has elevated privileges or not."""
        try:
            if _os.name == "nt":
                return getattr(_ctypes, "windll").shell32.IsUserAnAdmin() != 0
            elif _os.name == "posix":
                return _os.geteuid() == 0  # type: ignore[attr-defined]
        except Exception:
            pass
        return False

    @property
    def is_win(cls) -> bool:
        """Whether the current operating system is Windows or not."""
        return _platform.system() == "Windows"


class System(metaclass=_SystemMeta):
    """This class provides methods to interact with the underlying operating system."""

    @classmethod
    def restart(cls, prompt: object = "", wait: int = 0, continue_program: bool = False, force: bool = False) -> None:
        """Restarts the system with some advanced options\n
        --------------------------------------------------------------------------------------------------
        - `prompt` -⠀the message to be displayed in the systems restart notification
        - `wait` -⠀the time to wait until restarting in seconds
        - `continue_program` -⠀whether to continue the current Python program after calling this function
        - `force` -⠀whether to force a restart even if other processes are still running"""
        if wait < 0:
            raise ValueError(f"The 'wait' parameter must be non-negative, got {wait!r}")

        _SystemRestartHelper(prompt, wait, continue_program, force)()

    @classmethod
    def check_libs(
        cls,
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
        return _SystemCheckLibsHelper(lib_names, install_missing, missing_libs_msgs, confirm_install)()

    @classmethod
    def elevate(cls, win_title: Optional[str] = None, args: Optional[list] = None) -> bool:
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
        if cls.is_elevated:
            return True

        args_list = args or []

        if _os.name == "nt":  # WINDOWS
            if win_title:
                args_str = f'-c "import ctypes; ctypes.windll.kernel32.SetConsoleTitleW(\\"{win_title}\\"); exec(open(\\"{_sys.argv[0]}\\").read())" {" ".join(args_list)}"'
            else:
                args_str = f'-c "exec(open(\\"{_sys.argv[0]}\\").read())" {" ".join(args_list)}'

            result = getattr(_ctypes, "windll").shell32.ShellExecuteW(None, "runas", _sys.executable, args_str, None, 1)
            if result <= 32:
                raise PermissionError("Failed to launch elevated process.")
            else:
                _sys.exit(0)

        else:  # POSIX
            cmd = ["pkexec"]
            if win_title:
                cmd.extend(["--description", win_title])
            cmd.extend([_sys.executable] + _sys.argv[1:] + args_list)

            proc = _subprocess.Popen(cmd)
            proc.wait()
            if proc.returncode != 0:
                raise PermissionError("Process elevation was denied.")
            _sys.exit(0)


class _SystemRestartHelper:
    """Internal, callable helper class to handle system restart with platform-specific logic."""

    def __init__(self, prompt: object, wait: int, continue_program: bool, force: bool):
        self.prompt = prompt
        self.wait = wait
        self.continue_program = continue_program
        self.force = force

    def __call__(self) -> None:
        if (system := _platform.system().lower()) == "windows":
            self.restart_windows()
        elif system in {"linux", "darwin"}:
            self.restart_posix()
        else:
            raise NotImplementedError(f"Restart not implemented for '{system}' systems.")

    def check_running_processes(self, command: str | list[str], skip_lines: int = 0) -> None:
        """Check if processes are running and raise error if force is False."""
        if self.force:
            return

        if isinstance(command, str):
            output = _subprocess.check_output(command, shell=True).decode()
        else:
            output = _subprocess.check_output(command).decode()

        processes = [line for line in output.splitlines()[skip_lines:] if line.strip()]
        if len(processes) > 2:  # EXCLUDING PYTHON AND SHELL PROCESSES
            raise RuntimeError("Processes are still running.\nTo restart anyway set parameter 'force' to True.")

    def restart_windows(self) -> None:
        """Handle Windows system restart."""
        self.check_running_processes("tasklist", skip_lines=3)

        if self.prompt:
            _os.system(f'shutdown /r /t {self.wait} /c "{self.prompt}"')
        else:
            _os.system("shutdown /r /t 0")

        if self.continue_program:
            self.wait_for_restart()

    def restart_posix(self) -> None:
        """Handle Linux/macOS system restart."""
        self.check_running_processes(["ps", "-A"], skip_lines=1)

        if self.prompt:
            _subprocess.Popen(["notify-send", "System Restart", str(self.prompt)])
            _time.sleep(self.wait)

        try:
            _subprocess.run(["sudo", "shutdown", "-r", "now"])
        except _subprocess.CalledProcessError:
            raise PermissionError("Failed to restart: insufficient privileges.\nEnsure sudo permissions are granted.")

        if self.continue_program:
            self.wait_for_restart()

    def wait_for_restart(self) -> None:
        """Wait and print message before restart."""
        print(f"Restarting in {self.wait} seconds...")
        _time.sleep(self.wait)


class _SystemCheckLibsHelper:
    """Internal, callable helper class to check and install missing Python libraries."""

    def __init__(
        self,
        lib_names: list[str],
        install_missing: bool,
        missing_libs_msgs: MissingLibsMsgs,
        confirm_install: bool,
    ):
        self.lib_names = lib_names
        self.install_missing = install_missing
        self.missing_libs_msgs = missing_libs_msgs
        self.confirm_install = confirm_install

    def __call__(self) -> Optional[list[str]]:
        missing = self.find_missing_libs()

        if not missing:
            return None
        elif not self.install_missing:
            return missing

        if self.confirm_install and not self.confirm_installation(missing):
            return missing

        return self.install_libs(missing)

    def find_missing_libs(self) -> list[str]:
        """Find which libraries are missing."""
        missing = []
        for lib in self.lib_names:
            try:
                __import__(lib)
            except ImportError:
                missing.append(lib)
        return missing

    def confirm_installation(self, missing: list[str]) -> bool:
        """Ask user for confirmation before installing libraries."""
        FormatCodes.print(f"[b]({self.missing_libs_msgs['found_missing']})")
        for lib in missing:
            FormatCodes.print(f" [dim](•) [i]{lib}[_i]")
        print()
        return Console.confirm(self.missing_libs_msgs["should_install"], end="\n")

    def install_libs(self, missing: list[str]) -> Optional[list[str]]:
        """Install missing libraries using pip."""
        for lib in missing[:]:
            try:
                _subprocess.check_call([_sys.executable, "-m", "pip", "install", lib])
                missing.remove(lib)
            except _subprocess.CalledProcessError:
                pass

        return None if len(missing) == 0 else missing
