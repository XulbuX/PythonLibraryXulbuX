import contextlib
import os
import sys
from pathlib import Path
from unittest.mock import patch
from xulbux import file_sys
import pytest


def test_get_script_dir_frozen():
    with patch.object(sys, "frozen", True, create=True), patch.object(sys, "executable", "mocked.exe"):
        res = file_sys.get_script_dir()
        assert res.name == "." or res == Path("mocked.exe").parent


def test_get_script_dir_spec():
    class Spec:
        origin = "mocked_origin.py"

    class Mod:
        __spec__ = Spec()

    with patch.dict(sys.modules, {"__main__": Mod()}):
        res = file_sys.get_script_dir()
        assert res == Path("mocked_origin.py").resolve().parent


def test_get_script_dir_runtime_error():
    class Mod:
        __spec__ = None

    with patch.dict(sys.modules, {"__main__": Mod()}), pytest.raises(RuntimeError):
        file_sys.get_script_dir()


def test_remove_unsupported_item_fake():
    class FakePath:
        def exists(self):
            return True

        def is_file(self):
            return False

        def is_symlink(self):
            return False

        def is_dir(self):
            return False

    with patch("xulbux.file_sys.Path", return_value=FakePath()):
        file_sys.remove("fake")


def test_remove_exception_fake():
    class FakePath:
        def exists(self):
            return True

        def is_file(self):
            return True

        def is_symlink(self):
            return False

        def is_dir(self):
            return False

        def unlink(self):
            raise PermissionError("mocked")

    with patch("xulbux.file_sys.Path", return_value=FakePath()), pytest.raises(RuntimeError):
        file_sys.remove("fake")


def test_extend_path_absolute():

    with patch.dict(os.environ, {"MY_ROOT": "C:\\" if os.name == "nt" else "/"}):
        val = "%MY_ROOT%foo" if os.name == "nt" else "$MY_ROOT/foo"
        file_sys.extend_path(val)


def test_extend_path_absolute_no_drive():
    from unittest.mock import PropertyMock

    with (
        patch("pathlib.Path.is_absolute", return_value=True),
        patch("pathlib.Path.drive", new_callable=PropertyMock, return_value=""),
    ):
        file_sys.extend_path("foo")


def test_find_path_is_file(tmp_path: Path):
    f = tmp_path / "test.txt"
    f.touch()
    res = file_sys._ExtendPathHelper(Path("test.txt/extra"), search_dirs=[tmp_path], fuzzy_match=True, raise_error=False)()
    assert res == f


def test_get_closest_match_exception():
    with patch.object(Path, "iterdir", side_effect=PermissionError("mocked")):
        res = file_sys._ExtendPathHelper.get_closest_match(Path("."), "foo")
        assert res is None


def test_find_path_no_drive_absolute():
    from pathlib import Path
    from unittest.mock import PropertyMock
    from xulbux.file_sys import _ExtendPathHelper

    with (
        patch("pathlib.Path.is_absolute", return_value=True),
        patch("pathlib.Path.drive", new_callable=PropertyMock, return_value=""),
    ):
        helper = _ExtendPathHelper(Path("dummy_path"), search_dirs=[], fuzzy_match=False, raise_error=False)
        with contextlib.suppress(Exception):
            helper()

def test_extend_path_helper_windows_drive():
    from unittest.mock import patch, MagicMock
    from xulbux.file_sys import _ExtendPathHelper
    from pathlib import Path
    
    mock_path = MagicMock()
    mock_path.is_absolute.return_value = True
    mock_path.drive = "C:"
    mock_path.parts = ["C:\\", "foo"]
    
    with patch("xulbux.file_sys.Path", side_effect=lambda *args: mock_path if not args else Path(*args)) as mock_Path:
        helper = _ExtendPathHelper(mock_path, [], fuzzy_match=False, raise_error=False)
        helper()
        assert len(helper.search_dirs) > 0
