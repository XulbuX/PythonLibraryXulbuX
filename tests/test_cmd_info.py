import src.XulbuX as xx


def test_user_not_empty():
    user_output = xx.Cmd.user()
    assert user_output != ""  # Check that user() does not return an empty string

def test_width_not_zero():
    width_output = xx.Cmd.w()
    assert width_output != 0  # Check that w() does not return zero

def test_height_not_zero():
    height_output = xx.Cmd.h()
    assert height_output != 0  # Check that h() does not return zero

def test_width_not_negative():
    width_output = xx.Cmd.w()
    assert width_output >= 0  # Check that w() does not return a negative value

def test_height_not_negative():
    height_output = xx.Cmd.h()
    assert height_output >= 0  # Check that h() does not return a negative value
