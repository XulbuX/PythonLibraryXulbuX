from xulbux.ansi import Term
from xulbux.base.consts import ANSI

ESC = ANSI.CHAR


def test_term_constants():
    assert f"{ESC}[2K" == Term.CLEAR_LINE
    assert f"{ESC}[2J" == Term.CLEAR_SCREEN
    assert f"{ESC}[?25l" == Term.HIDE_CURSOR
    assert f"{ESC}[?25h" == Term.SHOW_CURSOR
    assert f"{ESC}[?1049h" == Term.ALT_SCREEN
    assert f"{ESC}[?1049l" == Term.MAIN_SCREEN


def test_term_cursor_movement():
    assert Term.up(3) == f"{ESC}[3A"
    assert Term.down() == f"{ESC}[1B"
    assert Term.left(2) == f"{ESC}[2D"
    assert Term.right(5) == f"{ESC}[5C"
    assert Term.prev_line(2) == f"{ESC}[2F"
    assert Term.next_line() == f"{ESC}[1E"
    assert Term.move(4, 7) == f"{ESC}[4;7H"


def test_term_save_restore_and_title():
    assert Term.save() == f"{ESC}[s"
    assert Term.restore() == f"{ESC}[u"
    assert Term.title("hi") == f"{ESC}]2;hi\x07"
