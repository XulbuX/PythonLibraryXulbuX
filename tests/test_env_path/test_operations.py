from pathlib import Path
from unittest.mock import MagicMock
import xulbux.env_path as _env_path_module
import pytest

# ******************************************************* MODULE TESTS ********************************************************


def test_get_paths():
    paths = _env_path_module.paths()
    paths_list = _env_path_module.paths(as_list=True)
    assert paths
    assert paths_list
    assert isinstance(paths, Path)
    assert isinstance(paths_list, list)
    assert len(paths_list) > 0
    assert all(isinstance(path, Path) for path in paths_list)
    assert isinstance(paths_list[0], Path)


def test_add_path(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("builtins.open", MagicMock())
    _env_path_module.add_path(base_dir=True)


def test_has_path():
    assert _env_path_module.has_path(base_dir=True)


def test_remove_path(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("builtins.open", MagicMock())
    _env_path_module.remove_path(base_dir=True)
    assert not _env_path_module.has_path(base_dir=True)
