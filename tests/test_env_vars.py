import xulbux as xx


def test_get_paths():
    paths = xx.EnvPath.paths()
    paths_list = xx.EnvPath.paths(as_list=True)
    assert paths
    assert paths_list
    assert isinstance(paths, str)
    assert isinstance(paths_list, list)
    assert len(paths_list) > 0
    assert isinstance(paths_list[0], str)


def test_add_path():
    xx.EnvPath.add_path(base_dir=True)


def test_has_path():
    assert xx.EnvPath.has_path(base_dir=True)


def test_remove_path():
    xx.EnvPath.remove_path(base_dir=True)
    assert not xx.EnvPath.has_path(base_dir=True)
