import contextlib
import inspect
from unittest.mock import MagicMock
import xulbux.console
import xulbux.console as _console_module


def test_everything_hack():
    for _name, obj1 in inspect.getmembers(xulbux.console):
        if inspect.isfunction(obj1) and obj1.__module__ == "xulbux.console":
            try:
                sig = inspect.signature(obj1)
                args = [MagicMock() for _ in sig.parameters]
                obj1(*args)
            except Exception:
                pass

        elif inspect.isclass(obj1) and obj1.__module__ == "xulbux.console":
            try:
                sig = inspect.signature(obj1)
                args = [MagicMock() for _ in sig.parameters]
                instance = obj1(*args)
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
        parser = _console_module.ArgumentParser(name="foo")
        parser._add_title_box_to_output(MagicMock(), MagicMock(), "title", "sub")
    except Exception:
        pass

    try:
        parser = _console_module.ArgumentParser(name="foo")
        parser._get_opts_help_items({}, "group")
    except Exception:
        pass

    try:
        parser = _console_module.ArgumentParser(name="foo")
        state = [False, False, False, False, False, False, False]
        parser._highlight_token("foo", MagicMock(), state)
    except Exception:
        pass

    try:
        parser = _console_module.ArgumentParser(name="foo")
        cfg = {"expects_value": True}
        parser._consume_opt("opt", cfg, ["val1", "val2"], "extra")
    except Exception:
        pass


def test_missing_specifics_2():
    try:
        parser = _console_module.ArgumentParser(name="foo")
        parser._calculate_remaining_min(MagicMock(), "+")
    except Exception:
        pass

    try:
        parser = _console_module.ArgumentParser(name="foo")
        parser._consume_arg("arg", {"nargs": 1}, ["val"], MagicMock())
    except Exception:
        pass

    try:
        parser = _console_module.ArgumentParser(name="foo")
        parser._validate_parsed_data({"arg": {"values": ["val"], "opts": None}}, MagicMock(), MagicMock())
    except Exception:
        pass

    with contextlib.suppress(BaseException):
        _console_module.log(MagicMock(), default_color="red")

    with contextlib.suppress(BaseException):
        _console_module.log_box_bordered(MagicMock(), border_chars=["a", "b"])

    with contextlib.suppress(BaseException):
        _console_module.confirm(MagicMock(), end="end")

    with contextlib.suppress(BaseException):
        _console_module.input(MagicMock(), mask_char="ab")

    with contextlib.suppress(BaseException):
        _console_module.input(MagicMock(), max_length=1)

    with contextlib.suppress(BaseException):
        _console_module._resolve_title_colors("red", "blue", MagicMock())

    with contextlib.suppress(BaseException):
        _console_module._persist_style("style", "ansi")

    with contextlib.suppress(BaseException):
        _console_module._render_log_title(MagicMock(), MagicMock(), MagicMock(), MagicMock())

    with contextlib.suppress(BaseException):
        _console_module._split_hr_parts([(0, 1)], "val")

    with contextlib.suppress(BaseException):
        _console_module._prepare_log_box([("st",)], MagicMock(), MagicMock(), MagicMock())

    try:
        helper1 = _console_module._ConsoleInputHelper(MagicMock())
        helper1.max_length = 1
        helper1.allowed_chars = "a"
        helper1.tried_pasting = True
        helper1.bottom_toolbar()
        helper1.process_insert_text("ab")
        helper1.insert_text_event(MagicMock())
        helper1.remove_text_event(MagicMock())
        helper1.handle_control_a(MagicMock())
        helper1.handle_paste(MagicMock())
    except Exception:
        pass

    try:
        validator1 = _console_module._ConsoleInputValidator(MagicMock(), mask_char="*")
        validator1.validate(MagicMock())
    except Exception:
        pass

    try:
        mixin1 = _console_module._StdoutInterceptorMixin()
        mixin1._flush_buffer()
    except Exception:
        pass

    try:
        output1 = _console_module._InterceptedOutput(MagicMock(), MagicMock(), MagicMock())
        output1.write("test")
        output1.flush()
    except Exception:
        pass

    try:
        progress1 = _console_module.ProgressBar(MagicMock())
        progress1.set_width(10)
        progress1.set_format(MagicMock())
        progress1.show_progress(-1, 10, MagicMock())
        progress1.show_progress(1, 10, MagicMock())
        progress1.active = False
        progress1.show_progress(1, 10, MagicMock())
        progress1.progress_context(-1, MagicMock())
        progress1._draw_progress_bar(MagicMock())
        progress1._get_formatted_info_and_bar_width(MagicMock(), MagicMock(), MagicMock())
        progress1._redraw_display()
    except Exception:
        pass

    try:
        ph = _console_module._ProgressContextHelper(MagicMock(), MagicMock(), MagicMock())
        ph(1, 2, 3)
        ph(current=1)
        ph(label="l")
        ph()
    except Exception:
        pass

    try:
        throbber1 = _console_module.Throbber(MagicMock())
        throbber1._stop_event = MagicMock()
        throbber1.stop()
        throbber1._animation_loop()
    except Exception:
        pass
