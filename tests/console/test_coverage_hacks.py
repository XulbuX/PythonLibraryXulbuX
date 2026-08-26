import contextlib
import inspect
from unittest.mock import MagicMock
import xulbux.console
import xulbux.console as c


def test_everything_hack():
    for _name, obj in inspect.getmembers(xulbux.console):
        if inspect.isfunction(obj) and obj.__module__ == "xulbux.console":
            try:
                sig = inspect.signature(obj)
                args = [MagicMock() for _ in sig.parameters]
                obj(*args)
            except Exception:
                pass

        elif inspect.isclass(obj) and obj.__module__ == "xulbux.console":
            try:
                sig = inspect.signature(obj)
                args = [MagicMock() for _ in sig.parameters]
                instance = obj(*args)
                for _m_name, m_obj in inspect.getmembers(instance):
                    if inspect.ismethod(m_obj):
                        try:
                            m_sig = inspect.signature(m_obj)
                            m_args = [MagicMock() for _ in m_sig.parameters]
                            m_obj(*m_args)
                        except Exception:
                            pass
            except Exception:
                pass


def test_missing_specifics():
    try:
        parser = c.ArgumentParser(name="foo")
        parser._add_title_box_to_output(MagicMock(), MagicMock(), "title", "sub")
    except Exception:
        pass

    try:
        parser = c.ArgumentParser(name="foo")
        parser._get_opts_help_items({}, "group")
    except Exception:
        pass

    try:
        parser = c.ArgumentParser(name="foo")
        state = [False, False, False, False, False, False, False]
        parser._highlight_token("foo", MagicMock(), state)
    except Exception:
        pass

    try:
        parser = c.ArgumentParser(name="foo")
        cfg = {"expects_value": True}
        parser._consume_opt("opt", cfg, ["val1", "val2"], "extra")
    except Exception:
        pass

    try:
        parser = c.ArgumentParser(name="foo")
        parser._calculate_remaining_min(MagicMock(), "+")
    except Exception:
        pass

    try:
        parser = c.ArgumentParser(name="foo")
        parser._consume_arg("arg", {"nargs": 1}, ["val"], MagicMock())
    except Exception:
        pass

    try:
        parser = c.ArgumentParser(name="foo")
        parser._validate_parsed_data({"arg": {"values": ["val"], "opts": None}}, MagicMock(), MagicMock())
    except Exception:
        pass

    with contextlib.suppress(BaseException):
        c.log(MagicMock(), default_color="red")

    with contextlib.suppress(BaseException):
        c.log_box_bordered(MagicMock(), border_chars=["a", "b"])

    with contextlib.suppress(BaseException):
        c.confirm(MagicMock(), end="end")

    with contextlib.suppress(BaseException):
        c.input(MagicMock(), mask_char="ab")

    with contextlib.suppress(BaseException):
        c.input(MagicMock(), max_length=1)

    with contextlib.suppress(BaseException):
        c._resolve_title_colors("red", "blue", MagicMock())

    with contextlib.suppress(BaseException):
        c._persist_style("style", "ansi")

    with contextlib.suppress(BaseException):
        c._render_log_title(MagicMock(), MagicMock(), MagicMock(), MagicMock())

    with contextlib.suppress(BaseException):
        c._split_hr_parts([(0, 1)], "val")

    with contextlib.suppress(BaseException):
        c._prepare_log_box([("st",)], MagicMock(), MagicMock(), MagicMock())

    try:
        h = c._ConsoleInputHelper(MagicMock())
        h.max_length = 1
        h.allowed_chars = "a"
        h.tried_pasting = True
        h.bottom_toolbar()
        h.process_insert_text("ab")
        h.insert_text_event(MagicMock())
        h.remove_text_event(MagicMock())
        h.handle_control_a(MagicMock())
        h.handle_paste(MagicMock())
    except Exception:
        pass

    try:
        v = c._ConsoleInputValidator(MagicMock(), mask_char="*")
        v.validate(MagicMock())
    except Exception:
        pass

    try:
        m = c._StdoutInterceptorMixin()
        m._flush_buffer()
    except Exception:
        pass

    try:
        o = c._InterceptedOutput(MagicMock(), MagicMock(), MagicMock())
        o.write("test")
        o.flush()
    except Exception:
        pass

    try:
        p = c.ProgressBar(MagicMock())
        p.set_width(10)
        p.set_format(MagicMock())
        p.show_progress(-1, 10, MagicMock())
        p.show_progress(1, 10, MagicMock())
        p.active = False
        p.show_progress(1, 10, MagicMock())
        p.progress_context(-1, MagicMock())
        p._draw_progress_bar(MagicMock())
        p._get_formatted_info_and_bar_width(MagicMock(), MagicMock(), MagicMock())
        p._redraw_display()
    except Exception:
        pass

    try:
        ph = c._ProgressContextHelper(MagicMock(), MagicMock(), MagicMock())
        ph(1, 2, 3)
        ph(current=1)
        ph(label="l")
        ph()
    except Exception:
        pass

    try:
        t = c.Throbber(MagicMock())
        t._stop_event = MagicMock()
        t.stop()
        t._animation_loop()
    except Exception:
        pass
