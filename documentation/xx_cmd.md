# `Cmd`
This class includes functions for logging and other actions within the console.

<br>

### `Cmd.get_args()`

This function is used to get the command arguments, for if the current file is run via the console as a command.<br>
**Params:**<br>
- <code>find_args: *dict*</code> a dictionary that specifies, which arguments you are looking for and under which alias they should be returned, if found. This dictionary could look something like this:
  ```python
  {
      "filepath": ["-f", "--file", "-p", "--path", "-fp", "--filepath", "--file-path"],
      "help":     ["-h", "--help"],
      "debug":    ["-d", "--debug"]
  }
  ```
  For this example, the command line could look like this:
  ```bash
  python main.py -f /path/to/file -d
  ```
  To get one value, you can allow multiple arguments, just like for the file path in the above example.

**Returns:**<br>
The function will return a dictionary, with the specified aliases and two values per alias:
1. `"exists"` is `True`  if one of the listed arguments is found and `False` otherwise
2. `"value"` is the value of the argument (`None` *if the argument has no value*)

So for the example command line from above, the function would return a dictionary:
```python
{
    "filepath": { "exists": True, "value": "/path/to/file" },
    "help":     { "exists": False, "value": None },
    "debug":    { "exists": True, "value": None }
}
```

<br>

### `Cmd.user()`

**Returns:** the username of the user of the current console session

<br>

### `Cmd.is_admin()`

**Returns:** `True` if the current console session is run as administrator and `False` otherwise

<br>

### `Cmd.pause_exit()`

Will print a prompt and then pause and/or exit the program.<br>
**Params:**
- <code>pause: *bool*</code> whether to pause the program at the message or not
- <code>exit: *bool*</code> whether to exit the program after the message was printed (*and the program was unpaused if* `pause` *is true*) or not
- <code>prompt: *str*</code> the prompt to print before pausing and/or exiting the program
- <code>exit_code: *int*</code> the exit code to use if `exit` is true
- <code>reset_ansi: *bool*</code> whether to reset the ANSI codes after the message was printed

<br>

### `Cmd.cls()`

Will clear the console in addition to completely resetting the ANSI formats.

<br>

### <span id="cmd-log">`Cmd.log()`</span>

Will print a nicely formatted log message.<br>
**Params:**
- <code>title: *str*</code> the title of the log message
- <code>prompt: *object*</code> the prompt to print before the log message
- <code>start: *str*</code> the string to print before the log message
- <code>end: *str*</code> the string to print after the log message (*default* `\n`)
- <code>title_bg_color: *hexa*|*rgba*</code> the background color of the title
- <code>default_color: *hexa*|*rgba*</code> the default color of the log message
The log message supports special formatting codes. For more detailed information about formatting codes, see the [`xx_format_codes` documentation](xx_format_codes.md).

<br>

### `Cmd.debug()`, `Cmd.info()`, `Cmd.done()`, `Cmd.warn()`, `Cmd.fail()`, `Cmd.exit()`

These functions are all presets for the [`Cmd.log()`](#cmd-log) function, with the options to pause at the message and exit the program after the message was printed. That means, they have the same params as the `Cmd.log()` function, with the two additional ones.<br>
**Additional Params:**
- <code>pause: *bool*</code> whether to pause the program at the message or not (*different default depending on the log preset*)
- <code>exit: *bool*</code> whether to exit the program after the message was printed (*and the program was unpaused if* `pause` *is true*) or not (*different default depending on the log preset*)

<br>

### `Cmd.confirm()`

This function can be used to ask a yes/no question.<br>
Like in the [`Cmd.log()`](#cmd-log) function, it is possible to use special formatting codes inside the `prompt`.<br>
**Params:**
- <code>prompt: *object*</code> the prompt to print before the question
- <code>start: *str*</code> the string to print before the question
- <code>end: *str*</code> the string to print after the question (*default* `\n`)
- <code>default_color: *hexa*|*rgba*</code> the default color of the question
- <code>default_is_yes: *bool*</code> whether the default answer is yes or no (*if the user continues without entering anything or an unrecognized answer*)

**Returns:**
- `True` if the user enters `Y` or `yes` and `False` otherwise
- If the user entered nothing:
  - `True` if `default_is_yes` is true
  - `False` if `default_is_yes` is false

<br>

### <span id="cmd-restricted_input">`Cmd.restricted_input()`</span>

This function acts like a standard Python `input()` with the advantage, that you can specify:
- what text characters the user is allowed to type and
- the minimum and/or maximum length of the user's input
- optional mask character (hide user input, e.g. for passwords)
- reset the ANSI formatting codes after the user continues

Like in the [`Cmd.log()`](#cmd-log) function, it is possible to use special formatting codes inside the `prompt`.<br>
**Params:**
- <code>prompt: *object*</code> the prompt to print before the input
- <code>allowed_chars: *str*</code> the allowed text characters the user can type (*default is all characters*)
- <code>min_length: *int*</code> the minimum length of the user's input (*user can not confirm the input before this length is reached*)
- <code>max_length: *int*</code> the maximum length of the user's input (*user cannot keep on writing if this length is reached*)
- <code>mask_char: *str*</code> the mask character to hide the user's input
- <code>reset_ansi: *bool*</code> whether to reset the ANSI formatting codes after the user continues

**Returns:** the user's entry as a string

<br>

### `Cmd.pwd_input()`
This function almost works like the [`Cmd.restricted_input()`](#cmd-restricted_input) function, but it always hides the user's input.<br>
It has no additional parameters.