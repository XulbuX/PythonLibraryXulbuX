from xulbux.console import ArgumentParser
import pytest


def test_argparser_init_empty_prefix_chars():
    with pytest.raises(ValueError, match="The 'prefix_chars' parameter cannot be empty"):
        ArgumentParser(prefix_chars="")


def test_argparser_init_invalid_help_opts():
    with pytest.raises(ValueError, match="contains invalid option"):
        ArgumentParser(help_opts={"invalid_opt"})


def test_argparser_add_arg_invalid_name():
    parser = ArgumentParser()
    with pytest.raises(ValueError, match="cannot start with an underscore"):
        parser.add_arg("_hidden")
    with pytest.raises(ValueError, match="cannot start with prefix char"):
        parser.add_arg("-invalid")


def test_argparser_add_arg_duplicate():
    parser = ArgumentParser()
    parser.add_arg("foo")
    with pytest.raises(ValueError, match="is already defined"):
        parser.add_arg("foo")


def test_argparser_add_arg_invalid_nargs():
    parser = ArgumentParser()
    with pytest.raises(ValueError, match="must be an integer >= 1"):
        parser.add_arg("foo1", nargs=0)
    with pytest.raises(ValueError, match="must be an integer >= 1 or one of"):
        parser.add_arg("foo2", nargs="invalid")  # pyright:ignore[reportArgumentType]


def test_argparser_add_opt_empty_opts():
    parser = ArgumentParser()
    with pytest.raises(ValueError, match="The 'opts' parameter cannot be empty"):
        parser.add_opt([])


def test_argparser_add_opt_invalid_opt():
    parser = ArgumentParser()
    with pytest.raises(ValueError, match="contains invalid option"):
        parser.add_opt(["invalid"])


def test_argparser_add_opt_overlap_help():
    parser = ArgumentParser()
    with pytest.raises(ValueError, match="overlap with help options"):
        parser.add_opt(["-h"])


def test_argparser_add_opt_overlap_existing():
    parser = ArgumentParser()
    parser.add_opt(["-f"])
    with pytest.raises(ValueError, match="overlap with existing argument"):
        parser.add_opt(["-f"])


def test_argparser_add_opt_invalid_alias():
    parser = ArgumentParser()
    with pytest.raises(ValueError, match="cannot start with an underscore"):
        parser.add_opt(["-f"], "_f")


def test_argparser_add_opt_duplicate_alias():
    parser = ArgumentParser()
    parser.add_opt(["-f"], "f")
    with pytest.raises(ValueError, match="is already defined"):
        parser.add_opt(["-a"], "f")


def test_argparser_add_opt_invalid_expects_value():
    parser = ArgumentParser()
    with pytest.raises(ValueError, match="must be False or a string"):
        parser.add_opt(["-f"], expects_value="!nv@lid")
