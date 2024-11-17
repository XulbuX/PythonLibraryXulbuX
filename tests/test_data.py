import XulbuX as xx


# ! DON'T CHANGE THIS DATA !
d_comments = {
    "key1": [
        ">> COMMENT IN THE BEGINNING OF THE STRING <<  value1",
        "value2  >> COMMENT IN THE END OF THE STRING",
        "val>> COMMENT IN THE MIDDLE OF THE STRING <<ue3",
        ">> FULL VALUE IS A COMMENT  value4",
    ],
    ">> FULL KEY + ALL ITS VALUES ARE A COMMENT  key2": ["value", "value", "value"],
    "key3": ">> ALL THE KEYS VALUES ARE COMMENTS  value",
}

d1_equal = {
    "key1": ["value1", "value2", "val__ue3", ["value1", "value2", "value3"]],
    "key2": ["value1", "value2", "val__ue3", ["value1", "value2", "value3"]],
    "key3": "value",
}
d2_equal = {
    "key1": ["value1", "value2", "val__ue3", ["value1", "value2", "value3"]],
    "key2": ["value1", "value2", "val__ue3", ["value1", "value2", "value3"]],
    "key3": "CHANGED value",
}

d1_path_id = {"healthy": {"fruit": ["apples", "bananas", "oranges"], "vegetables": ["carrots", "broccoli", "celery"]}}
d2_path_id = {"school": {"material": ["pencil", "paper", "rubber"], "subjects": ["math", "science", "history"]}}


def test_remove_comments():
    assert xx.Data.remove_comments(d_comments, comment_sep="__") == {
        "key1": ["value1", "value2", "val__ue3", ["value1", "value2", "value3"]],
        "key3": None,
    }


def test_is_equal():
    assert xx.Data.is_equal(d1_equal, d2_equal) == False
    assert xx.Data.is_equal(d1_equal, d2_equal, ignore_paths="key3") == True


def test_path_id():
    id1, id2 = xx.Data.get_path_id(d1_path_id, ["healthy->fruit->bananas", "healthy->vegetables->2"])
    assert id1 == "1>001"
    assert id2 == "1>012"
    assert xx.Data.get_value_by_path_id(d1_path_id, id1) == "bananas"
    assert xx.Data.get_value_by_path_id(d1_path_id, id2) == "celery"
    assert xx.Data.set_value_by_path_id(d2_path_id, ["1>001::NEW1", "1>012::NEW2"]) == {
        "school": {"material": ["pencil", "NEW1", "rubber"], "subjects": ["math", "science", "NEW2"]}
    }
