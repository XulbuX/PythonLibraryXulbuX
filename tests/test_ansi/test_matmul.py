from xulbux.ansi import _Style


def test_matmul_fallback():
    class DummyStyle(_Style):
        pass

    # This should trigger `AttributeError` and set `_oc`:
    res = DummyStyle(123) @ "hello"
    assert "hello" in res.text  # pyright:ignore[reportOperatorIssue]
