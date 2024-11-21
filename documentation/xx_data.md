# `Data`
This class includes methods, used to work with lists, tuples, sets, frozensets and dictionaries.<br>

<br>

### `chars_count()`

This method will return the sum of the amount of all the characters (*including the keys if it's a dictionary*) in data.<br>
**Param:** <code>data: *list* | *tuple* | *set* | *frozenset* | *dict*</code> the data to count the characters in<br>
**Returns:** the sum of the amount of all the characters

<br>

### `strip()`

This method will remove all leading and trailing whitespaces from data items.<br>
**Param:** <code>data: *list* | *tuple* | *set* | *frozenset* | *dict*</code> the data to strip<br>
**Returns:** the stripped data

<br>

### `remove_empty_items()`

This method will remove empty items from data.<br>
**Params:**
- <code>data: *list* | *tuple* | *set* | *frozenset* | *dict*</code> the data to remove empty items from
- <code>spaces_are_empty: *bool* = False</code> whether to count items with only spaces as empty

**Returns:** the data with the empty items removed

<br>

### `remove_duplicates()`

This method will remove duplicate items from data.<br>
**Param:** <code>data: *list* | *tuple* | *set* | *frozenset* | *dict*</code> the data to remove duplicates from<br>
**Returns:** the data with the duplicates removed

<br>

### <span id="data-removecomments">`remove_comments()`</span>

This method will remove custom defined comments from the data's keys, items and values.<br>
**Params:**
- <code>data: *list* | *tuple* | *set* | *frozenset* | *dict*</code> the data to remove comments from
- <code>comment_start: *str* = ">>"</code> the string that marks the start of a comment
- <code>comment_end: *str* = "<<"</code> the string that marks the end of a comment
- <code>comment_sep: *str* = ""</code> a string with which a comment will be replaced, if it is in the middle of a string

**Returns:** the data with the comments removed

**Example:**
```python
data = {
    "key1": [
        ">> COMMENT IN THE BEGINNING OF THE STRING <<  value1",
        "value2  >> COMMENT IN THE END OF THE STRING",
        "val>> COMMENT IN THE MIDDLE OF THE STRING <<ue3",
        ">> FULL VALUE IS A COMMENT  value4"
    ],
    ">> FULL KEY + ALL ITS VALUES ARE A COMMENT  key2": [
        "value",
        "value",
        "value"
    ],
    "key3": ">> ALL THE KEYS VALUES ARE COMMENTS  value"
}

processed_data = Data.remove_comments(
    data,
    comment_start=">>",
    comment_end="<<",
    comment_sep="__"
)
```
For this example, `processed_data` would be:
```python
{
    "key1": [
        "value1",
        "value2",
        "val__ue3"
    ],
    "key3": None
}
```
**This is because:**<br>
For `key1`, all the comments will just be removed, except at `value3` and `value4`:<br>
 `value3` The comment is removed and the parts left and right are joined through `comment_sep`.<br>
 `value4` The whole value is removed, since the whole value was a comment.<br>
For `key2`, the key, including its whole values will be removed.<br>
For `key3`, since all its values are just comments, the key will still exist, but with a value of `None`.

<br>

### `is_equal()`

This method will check if two data structures are equal (*comments not ignored*).<br>
**Params:**
- <code>data1: *list* | *tuple* | *set* | *frozenset* | *dict*</code> the first data structure to compare
- <code>data2: *list* | *tuple* | *set* | *frozenset* | *dict*</code> the second data structure to compare
- <code>ignore_paths: *str* | *list*[*str*] = ""</code> parts of the structure to ignore while comparing (*see* [`Data.get_path_id()`](#data-getpathid-valuepaths))
- <code>path_sep: *str* = "->"</code> the separator to separate the parts of the path (*see* [`Data.get_path_id()`](#data-getpathid-valuepaths))
- <code>comment_start: *str* = ">>"</code> the string that marks the start of a comment (*see* [`Data.remove_comments()`](#data-removecomments))
- <code>comment_end: *str* = "<<"</code> the string that marks the end of a comment (*see* [`Data.remove_comments()`](#data-removecomments))

**Returns:** `True` if the data structures are equal, `False` otherwise

<br>

### <span id="data-getpathid">`get_path_id()`</span>

This method generates a unique ID based on the path to a specific value within a nested data structure.<br>
**Params:**
- <code>data: *list* | *tuple* | *set* | *frozenset* | *dict*</code> the data structure to get the path ID from
- <code>value_paths: *str* | *list*[*str*]</code> the path/s to the value/s to be updated
- <code>path_sep: *str* = "->"</code> the separator to separate the parts of the path
- <code>comment_start: *str* = ">>"</code> the string that marks the start of a comment (*see* [`Data.remove_comments()`](#data-removecomments))
- <code>comment_end: *str* = "<<"</code> the string that marks the end of a comment (*see* [`Data.remove_comments()`](#data-removecomments))
- <code>ignore_not_found: *bool* = False</code> if `True`, will not raise an exception if a path from `value_paths` is not found and instead return `None`

**Returns:** the generated path ID/s

<span id="data-getpathid-valuepaths">**Value Paths:**</span><br>
To more easily explain `value_paths`, we'll take this data structure for an example:
```python
{
    "healthy": {
        "fruit": ["apples", "bananas", "oranges"],
        "vegetables": ["carrots", "broccoli", "celery"]
    }
}
```
... if we would want to change the value of `"apples"` to `"strawberries"`, our value path would be `healthy->fruit->apples`. This is because the value `"apples"` is in the `"fruit"` with the parent dictionary  `"healthy"`.<br>
If we don't know that the value is `"apples"` we can also use the index of that value, so `healthy->fruit->0`, since the index of `"apples"` in the list under `healthy->fruit` is `0`.

**Path Separator:**<br>
The `path_sep` parameter is the separator between the keys/indexes in the value path. In the [example above](#data-getpathid-valuepaths), `->` is used as the separator (*which is also the default separator*).<br>

<br>

### `get_value_by_path_id()`

This method tries to retrieve a value, using the provided path ID (*generated with* [`Data.get_path_id()`](#data-getpathid)), within a nested data structure.<br>
**Params:**
- <code>data: *list* | *tuple* | *set* | *frozenset* | *dict*</code> the data structure to get the value from
- <code>path_id: *str*</code> the path ID to get the value from
- <code>get_key: *bool* = False</code> whether to return the value's key instead of the value itself

**Returns:** the value (*or key*) from the path ID location, as long as the structure of `data` hasn't changed since creating the path ID to that value.

<br>

### `set_value_by_path_id()`

This method updates a value (*or a list of values*), using the provided path ID (*generated with* [`Data.get_path_id()`](#data-getpathid)), within a nested data structure.<br>
**Params:**
- <code>data: *list* | *tuple* | *set* | *frozenset* | *dict*</code> the data structure to update
- <code>update_values: *str* | *list*[*str*]</code> the path ID/s along with the new value/s to be inserted
- <code>sep: *str* = "::"</code> the separator to separate the path ID/s and the new value/s

**Returns:** the updated data structure

<span id="data-setvaluebypathid-updatevalues">**Update Values:**</span><br>
The `update_values` parameter is a combination of the path ID and the new value to be inserted at the location, that ID points to.<br>
For example, if our path ID was `1>012` and we want to update the value at that location to `"Hello, world!"`, our update value would be `1>012::Hello, world!`.<br>
Sou you can update multiple values at once, you can also input a list of path IDs and new values, for example:
```python
[
    "1>012::new value 1",
    "1>203::new value 2",
    "1>124::new value 3",
    ...
]
```

**Separator:**<br>
The `sep` parameter is the separator between the path ID and the new value. In the [example above](#data-setvaluebypathid-updatevalues), `::` is used as the separator (*which is also the default separator*).

<br>

### `print()`

This method prints a nested data structure in a nicely formatted way.<br>
**Params:**
- <code>data: *list* | *tuple* | *set* | *frozenset* | *dict*</code> the data structure to print
- <code>indent: *int* = 4</code> the number of spaces used to indent the data structure
- <code>compactness: *int* = 1</code> the level of compactness of the data structure (*see* [`Data.to_str()`](#data-tostr-compactness))
- <code>sep: *str* = ", "</code> the separator to use inside of the formatted data structure
- <code>max_width: *int* = 127</code> the maximum amount of characters a line in the formatted data structure can have
- <code>as_json: *bool* = False</code> whether to print the data structure in JSON format

<br>

### `to_str()`

This method converts a nested data structure into a nicely formatted string.<br>
**Params:**
- <code>data: *list* | *tuple* | *set* | *frozenset* | *dict*</code> the data structure to convert
- <code>indent: *int* = 4</code> the number of spaces used to indent the data structure
- <code>compactness: *int* = 1</code> the level of compactness of the data structure
- <code>sep: *str* = ", "</code> the separator to use inside of the formatted data structure
- <code>max_width: *int* = 127</code> the maximum amount of characters a line in the formatted data structure can have
- <code>as_json: *bool* = False</code> whether to format the data structure in JSON format

<span id="data-tostr-compactness">**Compactness:**</span><br>
The `compactness` parameter can be set to three different levels:<br>
 `0` expands everything possible<br>
 `1` only expands if there's other data structures inside of the current item/value or if a line's characters amount is more than `max_width`<br>
 `2` keeps everything collapsed (all on one line)