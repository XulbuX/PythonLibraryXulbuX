from collections import namedtuple
from xulbux import Console
import pytest
import os


@pytest.fixture
def mock_terminal_size(monkeypatch):
    TerminalSize = namedtuple('TerminalSize', ['columns', 'lines'])
    mock_get_terminal_size = lambda: TerminalSize(columns=80, lines=24)
    monkeypatch.setattr(os, 'get_terminal_size', mock_get_terminal_size)


def test_console_user():
    user_output = Console.usr
    assert isinstance(user_output, str)
    assert user_output != ""


def test_console_width(mock_terminal_size):
    width_output = Console.w
    assert isinstance(width_output, int)
    assert width_output == 80


def test_console_height(mock_terminal_size):
    height_output = Console.h
    assert isinstance(height_output, int)
    assert height_output == 24


def test_console_size(mock_terminal_size):
    size_output = Console.wh
    assert isinstance(size_output, tuple)
    assert len(size_output) == 2
    assert size_output[0] == 80
    assert size_output[1] == 24
