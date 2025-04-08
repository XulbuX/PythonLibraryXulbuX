from xulbux import EnvPath


def test_get_paths():
    paths = EnvPath.paths()
    paths_list = EnvPath.paths(as_list=True)
    assert paths
    assert paths_list
    assert isinstance(paths, str)
    assert isinstance(paths_list, list)
    assert len(paths_list) > 0
    assert isinstance(paths_list[0], str)


def test_add_path():
    EnvPath.add_path(base_dir=True)


def test_has_path():
    assert EnvPath.has_path(base_dir=True)


def test_remove_path():
    EnvPath.remove_path(base_dir=True)
    assert not EnvPath.has_path(base_dir=True)
