
<!-- API: <xx.regex.get_args> -->
```python
import xulbux as xx

parsed_args = xx.console.get_args({
    "text_before": "before",  # Positional values before first flag.
    "arg1": {"-A", "--arg1"},  # Normal flags.
    "arg2": {  # Flags with specified default value.
        "flags": {"-B", "--arg2"},
        "default": "default value",
    },
    "text_after": "after",  # Positional values after last flag's value.
})
```

Resulting `ParsedArgs` structure:

```python
ParsedArgs(
    # Found 2 values before the first flag:
    text_before=ParsedArgData(exists=True, is_pos=True, values=["Hello", "World"], flag=None),
    # Found one of the specified flags with a value:
    arg1=ParsedArgData(exists=True, is_pos=False, values=["42"], flag="--arg1"),
    # Didn't find any of the specified flags, used the default value:
    arg2=ParsedArgData(exists=False, is_pos=False, values=["default value"], flag=None),
    # Found 1 value after the last flag's value:
    text_after=ParsedArgData(exists=True, is_pos=True, values=["Goodbye"], flag=None),
)
```
<!-- API: </xx.regex.get_args> -->

<!-- API: <xx.regex.log_box_bordered> -->
```python
import xulbux as xx

xx.console.log_box_bordered(
    "Content",
    "{hr}",
    "More content",
    "Another line",
)
```
<!-- API: </xx.regex.log_box_bordered> -->

<!-- API: <xx.regex.input> -->
```python
import xulbux as xx


def email_validator(user_input: str) -> Optional[str]:
    if not re.match(r"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}", user_input):
        return "Enter a valid E-Mail address (example@domain.com)"


user_input = xx.console.input(
    prompt="E-Mail: ",
    placeholder="example@domain.com",
    validator=email_validator,
)
```
<!-- API: </xx.regex.input> -->

<!-- API: <ProgressBar.set_chars> -->
```python
ProgressBar.set_chars(("█", "▓", "▒", "░", " "))
```
<!-- API: </ProgressBar.set_chars> -->

<!-- API: <ProgressBar.progress_context> -->
```python
with ProgressBar().progress_context(500, "Loading...") as update_progress:
    update_progress(0)  # Show empty bar at start.

    for i in range(400):
        # Do some work...
        update_progress(i)  # Update progress.

    update_progress(label="Finalizing...")  # Update label.

    for i in range(400, 500):
        # Do some work...
        update_progress(i, f"Finalizing ({i})")  # Update both.
```
<!-- API: </ProgressBar.progress_context> -->

<!-- API: <Throbber.context> -->
```python
with Throbber().context("Starting...") as update_label:
    time.sleep(2)
    update_label("Processing...")
    time.sleep(3)
    update_label("Finishing...")
    time.sleep(2)
```
<!-- API: </Throbber.context> -->
