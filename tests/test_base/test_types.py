import typing
from pathlib import Path
from xulbux.base.types import ProgressUpdater, is_paths_list


def test_is_paths_list():
    assert is_paths_list([Path("."), "test"]) is True
    assert is_paths_list(["test", "test2"]) is True
    assert is_paths_list((Path("."), "test")) is True
    assert is_paths_list(("test",)) is True

    assert is_paths_list([Path("."), 123]) is False
    assert is_paths_list([123, 456]) is False
    assert is_paths_list("not a list") is False


def test_progress_updater_protocol():
    class DummyUpdater(ProgressUpdater):
        def __call__(self, current: typing.Any = None, label: typing.Any = None):  # pyright:ignore[reportIncompatibleMethodOverride]
            super().__call__(current=current, label=label)  # type:ignore[safe-super] # pyright:ignore[reportAbstractUsage, reportArgumentType]

    updater = DummyUpdater()
    updater(current=1)
