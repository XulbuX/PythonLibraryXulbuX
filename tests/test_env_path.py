from xulbux.env_path import EnvPath

from pathlib import Path

#
###################################################### EnvPath TESTS #####################################################


def test_get_paths():
    paths = EnvPath.paths()
    paths_list = EnvPath.paths(as_list=True)
    assert paths
    assert paths_list
    assert isinstance(paths, Path)
    assert isinstance(paths_list, list)
    assert len(paths_list) > 0
    assert all(isinstance(path, Path) for path in paths_list)
    assert isinstance(paths_list[0], Path)


def test_add_path():
    EnvPath.add_path(base_dir=True)


def test_has_path():
    assert EnvPath.has_path(base_dir=True)


def test_remove_path():
    EnvPath.remove_path(base_dir=True)
    assert not EnvPath.has_path(base_dir=True)
