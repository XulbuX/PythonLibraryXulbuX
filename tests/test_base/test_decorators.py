import sys
from typing import Any
from unittest.mock import MagicMock, patch
from xulbux.base.decorators import _noop_decorator, deprecated, mypyc_attr


def test_noop_decorator_returns_same_object() -> None:
    def sample_func() -> str:
        return "result"

    assert _noop_decorator(sample_func) is sample_func


def test_mypyc_attr_with_installed_mypy_extensions() -> None:
    mock_module = MagicMock()
    mock_decorator = MagicMock(side_effect=_noop_decorator)
    mock_module.mypyc_attr.return_value = mock_decorator

    with patch.dict(sys.modules, {"mypy_extensions": mock_module}):
        decorator = mypyc_attr(native_class=False)
        mock_module.mypyc_attr.assert_called_once_with(native_class=False)

        class SampleClass:
            pass

        assert decorator(SampleClass) is SampleClass


def test_mypyc_attr_fallback_when_mypy_extensions_missing() -> None:
    with patch.dict(sys.modules, {"mypy_extensions": None}):
        decorator = mypyc_attr(native_class=False)
        assert decorator is _noop_decorator

        class SampleClass:
            pass

        assert decorator(SampleClass) is SampleClass


def test_deprecated_decorator_on_standard_function() -> None:
    @deprecated("Use new_function instead")
    def old_function() -> int:
        return 42

    assert old_function() == 42  # pyright:ignore[reportDeprecated]


def test_deprecated_branch_for_python_3_13_plus() -> None:
    mock_dep_factory = MagicMock(return_value=_noop_decorator)
    mock_warnings = MagicMock(deprecated=mock_dep_factory)

    with (
        patch.object(sys, "version_info", (3, 13)),
        patch.dict(sys.modules, {"warnings": mock_warnings}),
    ):
        decorator = deprecated("Deprecated in 3.13")

        def sample_func() -> int:
            return 123

        result = decorator(sample_func)
        assert result is sample_func
        mock_dep_factory.assert_called_once_with("Deprecated in 3.13")


def test_deprecated_fallback_for_python_under_3_13_without_typing_extensions() -> None:
    class SampleClass:
        pass

    with patch.object(sys, "version_info", (3, 12)), patch.dict(sys.modules, {"typing_extensions": None}):
        decorator = deprecated("Deprecated feature")
        result = decorator(SampleClass)
        assert result is SampleClass
        assert getattr(SampleClass, "__deprecated__", None) == "Deprecated feature"


def test_deprecated_wrapper_for_immutable_callable() -> None:
    class CustomCallable:
        def __call__(self, *args: Any, **kwargs: Any) -> str:
            return "callable_output"

        def __setattr__(self, name: str, value: Any) -> None:
            raise TypeError("Cannot set attribute on this object")

    target = CustomCallable()
    decorator = deprecated("Deprecated callable")
    wrapped = decorator(target)

    assert wrapped is not target
    assert wrapped() == "callable_output"


def test_deprecated_wrapper_for_immutable_class() -> None:
    class ImmutableMeta(type):
        def __setattr__(cls, name: str, value: Any) -> None:
            raise TypeError("Cannot set attribute on this class")

    class ImmutableClass(metaclass=ImmutableMeta):
        pass

    decorator = deprecated("Deprecated class")
    result = decorator(ImmutableClass)
    assert result is ImmutableClass
