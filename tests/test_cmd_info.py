import XulbuX as xx


def test_console_user():
    user_output = xx.Console.user()
    assert isinstance(user_output, str)
    assert user_output != ""


def test_console_width():
    width_output = xx.Console.w()
    assert isinstance(width_output, int)
    assert width_output != 0
    assert width_output >= 0


def test_console_height():
    height_output = xx.Console.h()
    assert isinstance(height_output, int)
    assert height_output != 0
    assert height_output >= 0
