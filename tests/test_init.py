import xulbux
import pytest


def test_getattr_submodule() -> None:
    assert xulbux.FormatCodes is not None
    assert xulbux.S is not None


def test_getattr_module() -> None:
    assert xulbux.string is not None
    assert xulbux.console is not None


def test_getattr_invalid() -> None:
    with pytest.raises(AttributeError):
        _ = xulbux.non_existent_attribute


def test_dir() -> None:
    assert isinstance(dir(xulbux), list)
    assert "FormatCodes" in dir(xulbux)


def test_getattr_direct() -> None:
    res = xulbux.__getattr__("FormatCodes")
    assert res is not None
    res = xulbux.__getattr__("console")
    assert res is not None

    with pytest.raises(AttributeError):
        xulbux.__getattr__("invalid")


def test_dir_direct() -> None:
    assert "FormatCodes" in xulbux.__dir__()
