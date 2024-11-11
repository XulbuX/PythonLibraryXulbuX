import subprocess as _subprocess
import platform as _platform
import time as _time
import sys as _sys
import os as _os




class System:

    @staticmethod
    def restart(prompt:object = None, wait:int = 0, continue_program:bool = False, force:bool = False) -> None:
        """Starts a system restart:<br>
        `prompt` is the message to be displayed in the systems restart notification.<br>
        `wait` is the time to wait until restarting in seconds.<br>
        `continue_program` is whether to continue the current Python program after calling this function.<br>
        `force` is whether to force a restart even if other processes are still running."""
        system = _platform.system().lower()
        if system == 'windows':
            if not force:
                output = _subprocess.check_output('tasklist', shell=True).decode()
                processes = [line.split()[0] for line in output.splitlines()[3:] if line.strip()]
                if len(processes) > 2:  # EXCLUDING THE PYTHON PROCESS AND CMD
                    raise RuntimeError('Processes are still running. Use the parameter `force=True` to restart anyway.')
            if prompt:
                _os.system(f'shutdown /r /t {wait} /c "{prompt}"')
            else:
                _os.system('shutdown /r /t 0')
            if continue_program:
                print(f'Restarting in {wait} seconds...')
                _time.sleep(wait)
        elif system in ['linux', 'darwin']:
            if not force:
                output = _subprocess.check_output(['ps', '-A']).decode()
                processes = output.splitlines()[1:]  # EXCLUDE HEADER
                if len(processes) > 2:  # EXCLUDING THE PYTHON PROCESS AND PS
                    raise RuntimeError('Processes are still running. Use the parameter `force=True` to restart anyway.')
            if prompt:
                _subprocess.Popen(['notify-send', 'System Restart', prompt])
                _time.sleep(wait)
            try:
                _subprocess.run(['sudo', 'shutdown', '-r', 'now'])
            except _subprocess.CalledProcessError:
                raise PermissionError('Failed to restart: insufficient privileges. Ensure sudo permissions are granted.')
            if continue_program:
                print(f'Restarting in {wait} seconds...')
                _time.sleep(wait)
        else:
            raise NotImplementedError(f'Restart not implemented for `{system}`')

    @staticmethod
    def check_libs(lib_names:list[str], install_missing:bool = False, confirm_install:bool = True) -> None|list[str]:
        """Checks if the given list of libraries are installed. If not:
        - If `install_missing` is `False` the missing libraries will be returned as a list.
        - If `install_missing` is `True` the missing libraries will be installed. If `confirm_install` is `True` the user will first be asked if they want to install the missing libraries."""
        missing = []
        for lib in lib_names:
            try: __import__(lib)
            except ImportError: missing.append(lib)
        if not missing:
            return None
        elif not install_missing:
            return missing
        if confirm_install:
            print('The following required libraries are missing:')
            for lib in missing:
                print(f'- {lib}')
            if input('Do you want to install them now (Y/n):  ').strip().lower() not in ['', 'y', 'yes']:
                raise ImportError('Missing required libraries.')
        try:
            _subprocess.check_call([_sys.executable, '-m', 'pip', 'install'] + missing)
            return None
        except _subprocess.CalledProcessError:
            return missing
