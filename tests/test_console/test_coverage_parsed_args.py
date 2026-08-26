from xulbux.console import ParsedArgData, ParsedArgs
import pytest


def test_parsed_arg_data_val_cast_error():
    data = ParsedArgData(exists=True, values=("not_an_int",))
    with pytest.raises(ValueError, match="Failed to cast value"):
        data.val(int)


def test_parsed_arg_data_vals_cast_error():
    data = ParsedArgData(exists=True, values=("1", "not_an_int", "3"))
    with pytest.raises(ValueError, match="Failed to cast value"):
        data.vals(int)


def test_parsed_arg_data_str_not_exists():
    data = ParsedArgData(exists=False, values=())
    assert str(data) == ""


def test_parsed_args_getattr_underscore():
    args = ParsedArgs()
    with pytest.raises(AttributeError, match="has no attribute '_some_attr'"):
        _ = args._some_attr


def test_parsed_args_getattr_missing():
    args = ParsedArgs()
    with pytest.raises(AttributeError, match="Argument 'missing' is not defined"):
        _ = args.missing


def test_parsed_args_getattr_missing_with_available():
    args = ParsedArgs()
    args._add_arg("foo", ParsedArgData())
    with pytest.raises(AttributeError, match="Available arguments: 'foo'"):
        _ = args.missing
