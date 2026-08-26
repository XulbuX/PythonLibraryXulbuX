from xulbux.ansi import _Style


def test_matmul_fallback():
    class DummyStyle(_Style):
        pass

    style = DummyStyle(123)
    # This should trigger AttributeError and set _oc
    res = style @ "hello"
    assert "hello" in res.text
