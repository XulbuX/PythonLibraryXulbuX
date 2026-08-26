import sys
import typing
from typing import Any
from unittest.mock import patch
from xulbux.base.decorators import _noop_decorator, deprecated, mypyc_attr


def test_noop_decorator():
    def dummy():
        pass

    assert _noop_decorator(dummy) is dummy


def test_mypyc_attr_import_error():
    # Force ImportError on mypy_extensions:
    with patch.dict(sys.modules, {"mypy_extensions": None}):
        dec = mypyc_attr(native_class=False)
        assert dec is _noop_decorator

        def dummy():
            pass

        assert dec(dummy) is dummy


def test_deprecated_import_error_typing_extensions():
    # Test when sys.version_info < (3, 13) and typing_extensions fails to import:
    class DummyClass:
        pass

    with patch.object(sys, "version_info", (3, 10)), patch.dict(sys.modules, {"typing_extensions": None}):
        dec = deprecated("test msg")
        assert dec(DummyClass) is DummyClass
        assert getattr(DummyClass, "__deprecated__", None) == "test msg"


def test_deprecated_mypyc_wrapper():
    # Test when _dep fails because it can't set attributes on the arg (e.g. MyPyC func):
    class CExtFunc:
        # Simulate a C extension / MyPyC function that rejects arbitrary attributes:
        def __call__(self, *args: typing.Any, **kwargs: typing.Any):
            return "called"

        def __setattr__(self, name: str, value: Any) -> None:
            raise TypeError("cannot set attribute")

    # We mock typing_extensions.deprecated or warnings.deprecated to raise TypeError when applied:
    func = CExtFunc()

    # We want to force the except (AttributeError, TypeError) block to trigger.
    # To do this, we can let typing_extensions.deprecated be used, which internally tries to set __deprecated__.
    # If we pass CExtFunc, it should raise TypeError:

    dec = deprecated("test")
    wrapped = dec(func)
    assert wrapped is not func
    assert wrapped() == "called"
    assert hasattr(wrapped, "__deprecated__")


def test_deprecated_mypyc_wrapper_class():
    # If the thing failing is a class, it just returns arg:
    class BuiltinClass(type):
        def __setattr__(self, name: str, value: Any) -> None:
            raise TypeError("cannot set attribute")

    class MyBuiltin(metaclass=BuiltinClass):
        pass

    dec = deprecated("test")
    wrapped = dec(MyBuiltin)
    assert wrapped is MyBuiltin
