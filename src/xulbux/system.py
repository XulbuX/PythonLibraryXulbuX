"""
Provides OS-level integration and automation helpers.

Features include copying to clipboard, opening files, executing shell
commands, installing dependencies, and managing application restarts.
"""

from . import console as _console_module
from . import file_sys as _file_sys_module
from .ansi import S
from .base.types import MissingLibsMsgs

import ctypes as _ctypes
import getpass as _getpass
import multiprocessing as _multiprocessing
import os as _os
import platform as _platform
import shutil as _shutil
import socket as _socket
import subprocess as _subprocess
import sys as _sys
import time as _time
from collections.abc import Sequence
from contextlib import suppress as _suppress
from pathlib import Path
from typing import Literal, overload


def is_elevated() -> bool:
    """Whether the current process has elevated privileges or not."""

    with _suppress(Exception):
        if _os.name == "nt":
            return _ctypes.windll.shell32.IsUserAnAdmin() != 0  # type: ignore[attr-defined]
        elif _os.name == "posix":
            return _os.geteuid() == 0  # type:ignore[attr-defined]

    return False


def is_win() -> bool:
    """Whether the current operating system is Windows or not."""

    return _sys.platform == "win32"


def is_linux() -> bool:
    """Whether the current operating system is Linux or not."""

    return _sys.platform.startswith("linux")


def is_mac() -> bool:
    """Whether the current operating system is macOS or not."""

    return _sys.platform == "darwin"


def is_unix() -> bool:
    """Whether the current operating system is a Unix-like OS (Linux, macOS, BSD, …) or not."""

    return _os.name == "posix"


def get_hostname() -> str:
    """The network hostname of the current machine."""

    try:
        return _socket.gethostname()
    except Exception:
        return "unknown"


def get_username() -> str:
    """The name of the current user."""

    with _suppress(Exception):
        return _getpass.getuser()

    try:
        return _os.getlogin()
    except Exception:
        return "unknown"


def get_os_name() -> str:
    """The name of the operating system (e.g., `Windows`, `Linux`, …)."""

    return _platform.system()


def get_os_version() -> str:
    """The version of the operating system."""

    try:
        return _platform.version()
    except Exception:
        return "unknown"


def get_architecture() -> str:
    """The CPU architecture (e.g., `x86_64`, `ARM`, …)."""

    return _platform.machine()


def get_cpu_count() -> int:
    """The number of CPU cores available."""

    try:
        return _multiprocessing.cpu_count()
    except (NotImplementedError, AttributeError):
        return 1


def get_python_version() -> str:
    """The version string of the currently running Python interpreter (e.g., `3.10.4`)."""

    return _platform.python_version()


@overload
def get_env_path(*, as_list: Literal[True]) -> list[Path]: ...
@overload
def get_env_path(*, as_list: Literal[False] = False) -> Path: ...
@overload
def get_env_path(*, as_list: bool = False) -> Path | list[Path]: ...


def get_env_path(*, as_list: bool = False) -> Path | list[Path]:
    """Get the PATH environment variable.\n
    ----------------------------------------------------------------------------------------------------
    *   `as_list` – If true, returns the paths as a list of `Path`s; otherwise, as a single `Path`."""

    paths_str = _os.environ.get("PATH", "")

    if as_list:
        return [Path(path) for path in paths_str.split(_os.pathsep) if path]

    return Path(paths_str)


def has_env_path(path: Path | str | None = None, /, *, cwd: bool = False, base_dir: bool = False) -> bool:
    """Check if a path is present in the PATH environment variable.\n
    ----------------------------------------------------------------------------------------------------
    *   `path` – The path to check for.
    *   `cwd` – If true, uses the current working directory as the path.
    *   `base_dir` – If true, uses the script's base directory as the path."""

    return bool(
        _get_env_path_target(path, cwd=cwd, base_dir=base_dir).resolve()
        in {env_path.resolve() for env_path in get_env_path(as_list=True)}
    )


def add_env_path(path: Path | str | None = None, /, *, cwd: bool = False, base_dir: bool = False) -> None:
    """Add a path to the PATH environment variable.\n
    ----------------------------------------------------------------------------------------------------
    *   `path` – The path to add.
    *   `cwd` – If true, uses the current working directory as the path.
    *   `base_dir` – If true, uses the script's base directory as the path."""

    path_obj = _get_env_path_target(path, cwd=cwd, base_dir=base_dir)

    if not has_env_path(path_obj):
        _persistent_env_path(path_obj)


def remove_env_path(path: Path | str | None = None, /, *, cwd: bool = False, base_dir: bool = False) -> None:
    """Remove a path from the PATH environment variable.\n
    ----------------------------------------------------------------------------------------------------
    *   `path` – The path to remove.
    *   `cwd` – If true, uses the current working directory as the path.
    *   `base_dir` – If true, uses the script's base directory as the path."""

    path_obj = _get_env_path_target(path, cwd=cwd, base_dir=base_dir)

    if has_env_path(path_obj):
        _persistent_env_path(path_obj, remove=True)


def elevate(win_title: str | None = None, args: Sequence[str] | None = None) -> bool:
    """Attempts to start a new process with elevated privileges.\n
    ----------------------------------------------------------------------------------------------------
    *   `win_title` – The window title of the elevated process (only on Windows).
    *   `args` – A list of additional arguments to be passed to the elevated process.
    ----------------------------------------------------------------------------------------------------
    After the elevated process started, the original process will exit.\n
    This means, that this method has to be run at the beginning of the program or<br>
    or else the program has to continue in a new window after elevation.\n
    ----------------------------------------------------------------------------------------------------
    Returns `True` if the current process already has elevated privileges and raises<br>
    a `PermissionError` if the user denied the elevation or the elevation failed.\n
    ----------------------------------------------------------------------------------------------------
    #### Example Usage

    ```python
    import xulbux as xx

    # Request administrator / root privileges:
    if xx.system.elevate(win_title="Elevated Setup"):
        print("Running with elevated permissions.")
    else:
        print("Elevation failed or was denied.")
    ```"""

    if is_elevated():
        return True

    args_list = args or []

    # Windows:
    if _os.name == "nt":
        if win_title:
            args_str = (
                '-c "import ctypes; '
                f'ctypes.windll.kernel32.SetConsoleTitleW(\\"{win_title}\\"); '
                f'exec(open(\\"{_sys.argv[0]}\\").read())" ' + " ".join(args_list)
            )
        else:
            args_str = f'-c "exec(open(\\"{_sys.argv[0]}\\").read())" {" ".join(args_list)}'

        if _ctypes.windll.shell32.ShellExecuteW(None, "runas", _sys.executable, args_str, None, 1) <= 32:  # type: ignore[attr-defined]
            raise PermissionError("Failed to launch elevated process") from None
        else:
            raise SystemExit(0)

    # Unix-like (Linux/macOS):
    else:
        cmd = ["pkexec"]

        if win_title:
            cmd.extend(["--description", win_title])
        cmd.extend([_sys.executable, *_sys.argv[1:], *args_list])

        proc = _subprocess.Popen(cmd)
        proc.wait()
        if proc.returncode != 0:
            raise PermissionError("Process elevation was denied") from None
        raise SystemExit(0)


def restart(prompt: object = "", /, *, wait: int = 0, continue_program: bool = False, force: bool = False) -> None:
    """Restarts the system with some advanced options\n
    ----------------------------------------------------------------------------------------------------
    *   `prompt` – The message to be displayed in the systems restart notification.
    *   `wait` – The time to wait until restarting in seconds.
    *   `continue_program` – Whether to continue the current Python program
        after calling this function.
    *   `force` – Whether to force a restart even if other processes are still running."""

    if wait < 0:
        raise ValueError(f"The 'wait' parameter must be non-negative, got {wait!r}")

    _SystemRestartHelper(prompt, wait=wait, continue_program=continue_program, force=force)()


def check_libs(
    lib_names: list[str],
    /,
    *,
    install_missing: bool = False,
    missing_libs_msgs: MissingLibsMsgs | None = None,
    confirm_install: bool = True,
) -> list[str] | None:
    """Checks if the given list of libraries are installed and optionally installs missing libraries.\n
    ----------------------------------------------------------------------------------------------------
    *   `lib_names` – A list of library names to check.
    *   `install_missing` – Whether to directly missing libraries
        will be installed automatically using pip.
    *   `missing_libs_msgs` – Two messages:
        -   The first one is displayed when missing libraries are found.
        -   The second one is the confirmation message before installing missing libraries.
    *   `confirm_install` – Whether the user will be asked
        for confirmation before installing missing libraries.
    ----------------------------------------------------------------------------------------------------
    If some libraries are missing or they could not be installed,
    their names will be returned as a list.<br>
    If all libraries are installed (or were installed successfully), `None` will be returned.\n
    ----------------------------------------------------------------------------------------------------
    #### Example Usage

    ```python
    import xulbux as xx

    # Check and prompt to install missing packages:
    missing = xx.system.check_libs(
        ["requests", "pytest"],
        install_missing=True,
        confirm_install=True,
    )
    ```"""

    if missing_libs_msgs is None:
        missing_libs_msgs = {
            "found_missing": "The following required libraries are missing:",
            "should_install": "Do you want to install them now?",
        }
    return _SystemCheckLibsHelper(
        lib_names, install_missing=install_missing, missing_libs_msgs=missing_libs_msgs, confirm_install=confirm_install
    )()


def _get_env_path_target(path: Path | str | None = None, /, *, cwd: bool = False, base_dir: bool = False) -> Path:
    """Internal method to get the normalized `path`, CWD path or script directory path.\n
    ----------------------------------------------------------------------------------------------------
    Raise an error if no path is provided and neither `cwd` or `base_dir` is true."""

    if cwd:
        if base_dir:
            raise ValueError("Both 'cwd' and 'base_dir' cannot be True at the same time")
        return _file_sys_module.get_cwd()
    elif base_dir:
        return _file_sys_module.get_script_dir()

    if path is None:
        raise ValueError("No path provided\nPlease provide a 'path' or set either 'cwd' or 'base_dir' to True")

    return Path(path) if isinstance(path, str) else path


def _persistent_env_path(path: Path, /, *, remove: bool = False) -> None:
    """Internal method to add or remove a path from the PATH environment variable,<br>
    persistently, across sessions, as well as the current session."""

    current_paths = get_env_path(as_list=True)
    path_resolved = path.resolve()

    if remove:
        # Filter out the path to remove:
        current_paths = [env_path for env_path in current_paths if env_path.resolve() != path_resolved]
    else:
        # Add the new path if not already present:
        if path_resolved not in {env_path.resolve() for env_path in current_paths}:
            current_paths = [*current_paths, path_resolved]

    # Convert to strings only for setting the environment variable:
    path_strings = [str(env_path) for env_path in current_paths]
    _os.environ["PATH"] = new_path = _os.pathsep.join(dict.fromkeys([env_path for env_path in path_strings if env_path]))

    # Windows:
    if _sys.platform == "win32":
        try:
            winreg = __import__("winreg")
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_ALL_ACCESS)
            winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
            winreg.CloseKey(key)

        except Exception as exc:
            raise RuntimeError(f"Failed to update PATH in registry:\n  {str(exc).replace('\n', '  \n')}") from exc

    # Unix-like (Linux/macOS):
    else:
        home_path = Path.home()
        bashrc = home_path / ".bashrc"
        zshrc = home_path / ".zshrc"
        shell_rc_file = bashrc if bashrc.exists() else zshrc

        with open(shell_rc_file, "r+", encoding="utf-8") as file:
            content = file.read()
            file.seek(0)

            if remove:
                new_content = [line for line in content.splitlines() if not line.endswith(f':{path_resolved}"')]
                file.write("\n".join(new_content))
            else:
                file.write(f'{content.rstrip()}\n# Added by `python-lib-xulbux`.\nexport PATH="{new_path}"\n')

            file.truncate()

        _subprocess.run(f"source {shell_rc_file}", shell=True, executable="/bin/bash")


class _SystemRestartHelper:
    """Internal, callable helper class to handle system restart with platform-specific logic."""

    def __init__(self, prompt: object, /, *, wait: int, continue_program: bool, force: bool) -> None:
        self.prompt: object = prompt
        self.wait: int = wait
        self.continue_program: bool = continue_program
        self.force: bool = force

    def __call__(self) -> None:
        if (system := _platform.system().lower()) == "windows":
            self.restart_windows()
        elif system in {"linux", "darwin"}:
            self.restart_posix()
        else:
            raise NotImplementedError(f"Restart not implemented for '{system}' systems")

    def check_running_processes(self, command: str | list[str], /, skip_lines: int = 0) -> None:
        """Check if processes are running and raise error if force is False."""

        if self.force:
            return

        if isinstance(command, str):
            output = _subprocess.check_output(command, shell=True).decode()
        else:
            output = _subprocess.check_output(command).decode()

        processes: list[str] = []

        for line in output.splitlines()[skip_lines:]:
            if not line.strip():
                continue

            line_lower = line.lower()
            has_proc = False

            for proc in {"bash", "cmd", "powershell", "ps", "pwsh", "python", "sh", "tasklist", "zsh"}:
                if proc in line_lower:
                    has_proc = True
                    break

            if not has_proc:
                processes.append(line)

        if len(processes) > 0:  # Excluding Python and shell processes.
            raise RuntimeError("Processes are still running\nTo restart anyway set parameter 'force' to True")

    def restart_windows(self) -> None:
        """Handle Windows system restart."""

        self.check_running_processes("tasklist", skip_lines=3)

        if self.prompt:
            _subprocess.run(["shutdown", "/r", "/t", str(self.wait), "/c", str(self.prompt)])
        else:
            _subprocess.run(["shutdown", "/r", "/t", "0"])

        if self.continue_program:
            self.wait_for_restart()

    def restart_posix(self) -> None:
        """Handle Linux/macOS system restart."""

        self.check_running_processes(["ps", "-A"], skip_lines=1)

        if self.prompt:
            if _shutil.which("notify-send"):
                _subprocess.Popen(["notify-send", "System Restart", str(self.prompt)])
            else:
                _console_module.info(f"System Restart: {self.prompt}")
            _time.sleep(self.wait)

        try:
            _subprocess.run(["sudo", "shutdown", "-r", "now"])
        except _subprocess.CalledProcessError:
            raise PermissionError("Failed to restart: insufficient privileges\nEnsure sudo permissions are granted") from None

        if self.continue_program:
            self.wait_for_restart()

    def wait_for_restart(self) -> None:
        """Wait and print message before restart."""

        print(f"Restarting in {self.wait} seconds...")
        _time.sleep(self.wait)


class _SystemCheckLibsHelper:
    """Internal, callable helper class to check and install missing Python libraries."""

    def __init__(
        self, lib_names: list[str], /, *, install_missing: bool, missing_libs_msgs: MissingLibsMsgs, confirm_install: bool
    ) -> None:
        self.lib_names: list[str] = lib_names
        self.install_missing: bool = install_missing
        self.missing_libs_msgs: MissingLibsMsgs = missing_libs_msgs
        self.confirm_install: bool = confirm_install

    def __call__(self) -> list[str] | None:
        if not (missing := self.find_missing_libs()):
            return None
        elif not self.install_missing:
            return missing

        if self.confirm_install and not self.confirm_installation(missing):
            return missing

        return self.install_libs(missing)

    def find_missing_libs(self) -> list[str]:
        """Find which libraries are missing."""

        import importlib.util

        missing: list[str] = []
        for lib in self.lib_names:
            try:
                if importlib.util.find_spec(lib) is None:
                    missing.append(lib)
            except (ImportError, ValueError, AttributeError):
                missing.append(lib)
        return missing

    def confirm_installation(self, missing: list[str], /) -> bool:
        """Ask user for confirmation before installing libraries."""

        S(S.BOLD(self.missing_libs_msgs["found_missing"]), *[(S.DIM(" • "), S.ITALIC(lib)) for lib in missing], "").print()

        return _console_module.confirm(self.missing_libs_msgs["should_install"], end="\n")

    def install_libs(self, missing: list[str], /) -> list[str] | None:
        """Install missing libraries using pip."""

        for lib in missing[:]:
            with _suppress(_subprocess.CalledProcessError):
                _subprocess.check_call([_sys.executable, "-m", "pip", "install", lib])
                missing.remove(lib)

        return None if len(missing) == 0 else missing
