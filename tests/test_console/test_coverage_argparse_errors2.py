import sys
from xulbux.console import ArgumentParser
import pytest


def test_argparse_missing_opt_value(monkeypatch: pytest.MonkeyPatch):
    parser = ArgumentParser()
    parser.add_opt(["-x"], expects_value="X")
    monkeypatch.setattr(sys, "argv", ["prog", "-x"])
    with pytest.raises(SystemExit):
        parser.parse()


def test_argparse_missing_opt_value_with_choices(monkeypatch: pytest.MonkeyPatch):
    parser = ArgumentParser()
    parser.add_opt(["-x"], expects_value="X", choices=["a", "b"])
    monkeypatch.setattr(sys, "argv", ["prog", "-x", "-h"])  # Next token is help_opt
    with pytest.raises(SystemExit):
        parser.parse()


def test_argparse_missing_required_arg(monkeypatch: pytest.MonkeyPatch):
    parser = ArgumentParser()
    parser.add_arg("arg1", required=True)
    monkeypatch.setattr(sys, "argv", ["prog"])
    with pytest.raises(SystemExit):
        parser.parse()


def test_argparse_missing_required_arg_choices(monkeypatch: pytest.MonkeyPatch):
    parser = ArgumentParser()
    parser.add_arg("arg1", required=True, choices=["a"])
    monkeypatch.setattr(sys, "argv", ["prog"])
    with pytest.raises(SystemExit):
        parser.parse()


def test_argparse_missing_required_opt(monkeypatch: pytest.MonkeyPatch):
    parser = ArgumentParser()
    parser.add_opt(["-x"], required=True)
    monkeypatch.setattr(sys, "argv", ["prog"])
    with pytest.raises(SystemExit):
        parser.parse()


def test_argparse_invalid_choice_opt(monkeypatch: pytest.MonkeyPatch):
    parser = ArgumentParser()
    parser.add_opt(["-x"], expects_value="X", choices=["a"])
    monkeypatch.setattr(sys, "argv", ["prog", "-x=b"])
    with pytest.raises(SystemExit):
        parser.parse()


def test_argparse_unrecognized_arg(monkeypatch: pytest.MonkeyPatch):
    parser = ArgumentParser()
    parser.add_arg("arg1", nargs=1)
    monkeypatch.setattr(sys, "argv", ["prog", "val1", "val2"])
    with pytest.raises(SystemExit):
        parser.parse()


def test_argparse_unrecognized_opt(monkeypatch: pytest.MonkeyPatch):
    parser = ArgumentParser()
    monkeypatch.setattr(sys, "argv", ["prog", "-z"])
    with pytest.raises(SystemExit):
        parser.parse()


def test_argparse_plus_nargs_minimum(monkeypatch: pytest.MonkeyPatch):
    parser = ArgumentParser()
    parser.add_arg("arg1", nargs="+")
    parser.add_arg("arg2", nargs=1)
    monkeypatch.setattr(sys, "argv", ["prog", "val1", "val2"])
    res = parser.parse()
    assert res.arg1.values == ("val1",)
    assert res.arg2.values == ("val2",)


def test_argparse_no_args_but_extra(monkeypatch: pytest.MonkeyPatch):
    parser = ArgumentParser()
    monkeypatch.setattr(sys, "argv", ["prog", "extra"])
    with pytest.raises(SystemExit):
        parser.parse()
