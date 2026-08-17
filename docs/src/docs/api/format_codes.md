<!-- FormatCodes.clean_ansi() -->

```python
(
    # Cleaned string:
    "Hello World!",
    # Removed codes:
    (
        (0, "\x1b[91m"),
        (5, "\x1b[39m"),  # Auto reset code.
        (6, "\x1b[1m"),
    ),
)
```

Another example:

```python
(
    # Cleaned string:
    "Hello World!",
    # Removed codes:
    (
        (0, "\x1b[1m"),
        (6, "\x1b[0m"),
    ),
)
```
