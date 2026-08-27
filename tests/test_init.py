import xulbux
import pytest


def test_getattr_submodule() -> None:
    assert xulbux.S is not None


def test_getattr_module() -> None:
    assert xulbux.string is not None
    assert xulbux.console is not None


def test_getattr_invalid() -> None:
    with pytest.raises(AttributeError):
        _ = xulbux.non_existent_attribute


def test_dir() -> None:
    assert isinstance(dir(xulbux), list)
    assert "S" in dir(xulbux)


def test_getattr_direct() -> None:
    res_s = xulbux.S
    assert res_s is not None
    res_console = xulbux.console
    assert res_console is not None

    with pytest.raises(AttributeError):
        _ = xulbux.invalid


def test_dir_direct() -> None:
    assert "S" in xulbux.__dir__()
