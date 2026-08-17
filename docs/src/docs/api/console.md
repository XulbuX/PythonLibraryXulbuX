<!-- get_args() -->

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


<!-- log_box_bordered() -->

---

#### Example Usage

```python
import xulbux as xx

xx.console.log_box_bordered(
    "Content",
    "{hr}",
    "More content",
    "Another line",
)
```

<TerminalOutput>
<span class="line br-black">╭──────────────╮</span><br><span class="line"><span class="br-black">│</span> Content      <span class="br-black">│</span></span><br><span class="line br-black">├──────────────┤</span><br><span class="line"><span class="br-black">│</span> More content <span class="br-black">│</span></span><br><span class="line"><span class="br-black">│</span> Another line <span class="br-black">│</span></span><br><span class="line br-black">╰──────────────╯</span>
</TerminalOutput>
