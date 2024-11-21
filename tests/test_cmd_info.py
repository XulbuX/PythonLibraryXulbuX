from xulbux import Console


def test_console_user():
    user_output = Console.user()
    assert isinstance(user_output, str)
    assert user_output != ""


def test_console_width():
    width_output = Console.w()
    assert isinstance(width_output, int)
    assert width_output != 0
    assert width_output >= 0


def test_console_height():
    height_output = Console.h()
    assert isinstance(height_output, int)
    assert height_output != 0
    assert height_output >= 0
