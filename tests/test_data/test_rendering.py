import xulbux.data as _data_module
from xulbux.ansi import S
from xulbux.data import _DataRenderHelper
import pytest


def test_render_compactness_levels():
    sample_data = {"a": [1, 2, 3], "b": {"c": 4}}

    rendered_expanded = _data_module.render(sample_data, compactness=0)
    assert "\n" in rendered_expanded.raw

    rendered_compact = _data_module.render(sample_data, compactness=2)
    assert "\n" not in rendered_compact.raw

    rendered_auto = _data_module.render(sample_data, compactness=1)
    assert len(rendered_auto.raw) > 0

    rendered_primitive = _data_module.render(42)  # pyright:ignore[reportArgumentType]
    assert rendered_primitive.raw == "42"


def test_render_json_mode():
    sample_data = {"text": "hello", "active": True, "count": 42, "empty": None}
    rendered_json = _data_module.render(sample_data, as_json=True)
    assert '"text": "hello"' in rendered_json.raw
    assert '"active": true' in rendered_json.raw
    assert '"count": 42' in rendered_json.raw
    assert '"empty": null' in rendered_json.raw

    rendered_special = _data_module.render({"inf": float("inf"), "nan": float("nan")}, as_json=True)
    assert '"inf": null' in rendered_special.raw
    assert '"nan": null' in rendered_special.raw


def test_render_syntax_highlighting():
    rendered_hl = _data_module.render({"a": 1, "b": "str"}, syntax_highlighting=True)
    assert rendered_hl.ansi != rendered_hl.raw

    custom_hl = _data_module.render({"a": 1}, syntax_highlighting={"number": S.RED})
    assert custom_hl is not None


def test_render_data_types_formatting():
    assert _data_module.render({"bytes": b"hello"}, as_json=False).ansi != ""
    assert _data_module.render({"bytearray": bytearray(b"hello")}, as_json=False).ansi != ""
    assert _data_module.render({"bytes": b"\xff\xfe"}, as_json=False).ansi != ""
    assert _data_module.render({"bytes": b"\xff\xfe"}, as_json=True).raw != ""
    assert _data_module.render({"complex": 1 + 2j}, as_json=False).ansi != ""
    assert _data_module.render({"complex": 1 + 2j}, as_json=True).raw != ""
    assert _data_module.render({1, 2}).ansi != ""
    assert _data_module.render(frozenset([1, 2])).ansi != ""
    assert _data_module.render(set()).ansi != ""
    assert _data_module.render(frozenset()).ansi != ""
    assert _data_module.render((1,)).ansi != ""
    assert _data_module.render([1, 2], as_json=True).raw != ""

    class CustomObject:
        def __init__(self) -> None:
            self.attr = "value"

    assert _data_module.render({"custom": CustomObject()}).raw != ""


def test_render_complexity_calculation():
    rendered_nested = _data_module.render(
        {"tuple": (1, (2,)), "set": {1, frozenset([2])}, "frozen": frozenset([1, 2]), "list": [1, [2]]},
        compactness=1,
    )
    assert len(rendered_nested.raw) > 0


def test_should_expand_compactness_2():
    helper = _DataRenderHelper([1], indent=0, compactness=2, max_width=10, sep=",", as_json=False, syntax_highlighting=False)
    assert helper.should_expand([1]) is False


def test_render_validation_errors():
    with pytest.raises(ValueError, match="must be a non-negative integer"):
        _data_module.render({}, indent=-1)

    with pytest.raises(ValueError, match="must be a positive integer"):
        _data_module.render({}, max_width=0)

    with pytest.raises(TypeError, match="must be a dict or bool"):
        _data_module.render({}, syntax_highlighting="invalid_type")  # pyright:ignore[reportArgumentType]
