# `EnvPath`
This class includes methods to work with the PATH variable from environment variables.<br>

<br>

### `EnvPath.paths()`

This method will return the PATH variable as a string or a list with the separated paths.<br>
**Param:** <code>as_list: *bool* = *False*</code> whether to return the paths as a list or a string<br>
**Returns:** the PATH variable as a string or a list

<br>

### `EnvPath.has_path()`

This method will check if a path is present in the PATH variable.<br>
**Params:**
- <code>path: *str* = *None*</code> the path to check<br>
- <code>cwd: *bool* = *False*</code> whether to check if CWD path is present<br>
- <code>base_dir: *bool* = *False*</code> whether to check if the base directory path is present

**Returns:** `True` if the path is present in the PATH variable, `False` otherwise

<br>

### `EnvPath.add_path()`

This method will add a path to the PATH variable (*if it's not already present*).<br>
**Params:**
- <code>path: *str* = *None*</code> the path to add<br>
- <code>cwd: *bool* = *False*</code> whether to add the current working directory path<br>
- <code>base_dir: *bool* = *False*</code> whether to add the base directory path

<br>

### `EnvPath.remove_path()`

This method will remove a path from the PATH variable (*if it's present*).<br>
**Params:**
- <code>path: *str* = *None*</code> the path to remove<br>
- <code>cwd: *bool* = *False*</code> whether to remove the current working directory path<br>
- <code>base_dir: *bool* = *False*</code> whether to remove the base directory path