import XulbuX as xx


def test_get_paths():
    paths = xx.EnvVars.get_paths()
    paths_list = xx.EnvVars.get_paths(as_list=True)
    assert paths
    assert paths_list
    assert isinstance(paths, str)
    assert isinstance(paths_list, list)
    assert len(paths_list) > 0
    assert isinstance(paths_list[0], str)


xx.EnvVars.add_path(base_dir=True)
