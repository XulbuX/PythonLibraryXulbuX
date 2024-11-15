# `Code`
This class includes functions, used to work with strings, that are code.

<br>

### `Code.add_indent()`

This function will add `indent` spaces at the beginning of each line.<br>
**Params:**
- <code>code: *str*</code> the string to add the indent to
- <code>indent: *int*</code> the amount of spaces to add (*default* `4`)

**Returns:** the indented string

<br>

### `Code.get_tab_spaces()`

This function will try to get the amount of spaces that are used for indentation.<br>
**Params:**
- <code>code: *str*</code> the string to get the tab spaces from

**Returns:** the amount of spaces used for indentation

<br>

### `Code.change_tab_size()`

This function will change the amount of spaces used for indentation.<br>
**Params:**
- <code>code: *str*</code> the string to change the tab size of
- <code>new_tab_size: *int*</code> the amount of spaces to use for indentation
- <code>remove_empty_lines: *bool*</code> whether to remove empty lines in the process

**Returns:** the string with the new tab size (*and no empty lines if* `remove_empty_lines` *is true*)

<br>

### `Code.get_func_calls()`

This function will try to get all the function calls (*JavaScript, Python, etc. style functions*).<br>
**Params:**
- <code>code: *str*</code> the string to get the function calls from

**Returns:** a list of function calls

<br>

### `Code.is_js()`

This function will check if the code is likely to be JavaScript.<br>
**Params:**
- <code>code: *str*</code> the string to check

**Returns:** `True` if the code is likely to be JavaScript and `False` otherwise