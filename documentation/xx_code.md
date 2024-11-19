# `Code`
This class includes methods, used to work with strings, which include code.

<br>

### `Code.add_indent()`

This method will add `indent` spaces at the beginning of each line.<br>
**Params:**
- <code>code: *str*</code> the string to add the indent to
- <code>indent: *int*</code> the amount of spaces to add (*default* `4`)

**Returns:** the indented string

<br>

### `Code.get_tab_spaces()`

This method will try to get the amount of spaces that are used for indentation.<br>
**Param:** <code>code: *str*</code> the string to get the tab spaces from<br>
**Returns:** the amount of spaces used for indentation

<br>

### `Code.change_tab_size()`

This method will change the amount of spaces used for indentation.<br>
**Params:**
- <code>code: *str*</code> the string to change the tab size of
- <code>new_tab_size: *int*</code> the amount of spaces to use for indentation
- <code>remove_empty_lines: *bool*</code> whether to remove empty lines in the process

**Returns:** the string with the new tab size (*and no empty lines if* `remove_empty_lines` *is true*)

<br>

### `Code.get_func_calls()`

This method will try to get all the function/method calls (*JavaScript, Python, etc. style functions/methods*).<br>
**Param:** <code>code: *str*</code> the string to get the function/method calls from<br>
**Returns:** a list of function/method calls

<br>

### `Code.is_js()`

This method will check if the code is likely to be JavaScript.<br>
**Param:** <code>code: *str*</code> the string to check<br>
**Returns:** `True` if the code is likely to be JavaScript and `False` otherwise