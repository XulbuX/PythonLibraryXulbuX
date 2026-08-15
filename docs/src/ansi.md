# Ansi Module

This module provides the `StyledText` class together with the `S` and `Term` classes<br>
for building richly styled terminal output using a typed, operator-based syntax.

---


### The Easy Styling

First, let's take a look at a small example of what a highly styled output could look like using this module:

```python
StyledText(
    (
        "First normal & unstyled text. ",
        (S.BOLD | S.UNDERLINE | S.BR.BLUE)("Bright blue, bold, and underlined text."),
    ),
    (
        (S.hex("#000") | S.BG.hex("#F67"))("Black text with a red background."),
        " And then ",
        S.ITALIC("(boring)"),
        " plain text again.",
    ),
    sep="\n",
).print()
```

<TerminalOutput>
<p>First normal & unstyled text. <span class="b u br-blue">Bright blue, bold, and underlined text.</span></p>
<p><span class="#000 bg-#F67">Black text with a red background.</span> And then (<span class="i">boring</span>) plain text again.</p>
</TerminalOutput>

How all of this exactly works is explained in the sections below. 🠫


### Styles and Groups

In this module, you apply styles and colors using `S` attributes.<br>
Every style attribute supports two operators:

*   `|` combines two or more styles into a single immutable group, e.g.<br>
    `S.BOLD | S.RED`  →  bold + red foreground
*   `()` applies the style (or group) to the given text and auto-resets the style after it, e.g.<br>
    `S.BOLD("hello")`  →  bold "hello", reset back to normal afterwards<br>
    `(S.BOLD | S.RED)("hello")`  →  same idea, combined

A list of all possible style attributes can be found below.


### Auto Resetting Styles

Every `_Style`, `_StyleGroup`, `_ColorStyle` or `_Link` call automatically generates the<br>
matching reset sequence behind its text, just like shown in the following example:

```python
StyledText(
    ("This is plain text, ", S.BR.BLUE("which is bright blue now.")),
    "Now it was automatically reset to plain again.",
    sep="\n",
).print()
```

<TerminalOutput>
<p>This is plain text, <span class="br-blue">which is bright blue now.</span></p>
<p>Now it was automatically reset to plain again.</p>
</TerminalOutput>

Only the specific styles that were applied are reset; other styling in scope is left intact:

```python
StyledText(
    S.CYAN(
        "This is cyan text, ",
        S.DIM("which is dimmed now."),
        "\nNow it's not dimmed any more but still cyan.",
    ),
).print()
```

<TerminalOutput>
<span class="cyan"><p>This is cyan text, <span class="dim">which is dimmed now.</span></p>
<p>Now it's not dimmed any more but still cyan.</p></span>
</TerminalOutput>


### Bare (Open-Only) Styles

Passing a style object *without calling it* emits only its opening ANSI sequence at that<br>
position, with no matching close/reset appended. This is the typed equivalent of `[…]`<br>
(open bracket without closing braces) from the legacy string syntax:

```python
StyledText(
    S.RED,
    "[ERROR] Something went wrong!",
    S.RESET,
    " Back to normal.",
).print()
```

<TerminalOutput>
<span class="red">[ERROR] Something went wrong!</span> Back to normal.
</TerminalOutput>

Any style type supports bare usage: `S.RED` (`_Style`), `S.hex("#F67")` (`_ColorStyle`),<br>
`S.link("url")` (`_Link`), and `S.BOLD | S.RED` (`_StyleGroup`).<br>
Bare styles can also appear inside tuples and nested calls:

```python
StyledText(
    S.ITALIC("a", S.MAGENTA, "B", S.RESET_FG, "c"),
).print()
```

<TerminalOutput>
<span class="i">a<span class="magenta">B</span>c</span>
</TerminalOutput>


### Nesting and Multi-Segment Groups

A style call accepts either a single piece of text or any number of mixed segments.<br>
Strings, nested `_StyledSequence` calls, bare style objects, and raw tuples can be mixed freely:

*   `S.X("text")`               – Apply `X` to `"text"`, auto-reset after.
*   `S.X | S.Y`                 – Combine `X` and `Y` into a single group.
*   `(S.X | S.Y)("text")`       – Apply the group to `"text"`.
*   `S.X("a", S.Y("b"), "c")`   – Nested multi-segment: `Y` is applied only to `"b"`.
*   `S.X`                       – Bare: emit only the opening sequence, no auto-reset.
*   `("a", S.X("b"), "c")`      – Same-line group; passed as a single tuple to `StyledText(…)`.

Inside `StyledText(*segments, sep="\\n")`, every positional argument is treated as one<br>
logical line and joined by `sep`. An empty string argument `""` therefore produces a blank line.


### All Possible Style Attributes

*   Text styles:
    -   `S.BOLD`
    -   `S.DIM`
    -   `S.ITALIC`
    -   `S.UNDERLINE`
    -   `S.INVERSE`
    -   `S.HIDDEN`
    -   `S.STRIKE`
    -   `S.DOUBLE_UNDERLINE`
*   Standard foreground colors:
    -   `S.BLACK`, `S.RED`, `S.GREEN`, `S.YELLOW`,
        `S.BLUE`, `S.MAGENTA`, `S.CYAN`, `S.WHITE`
*   Bright foreground colors (`S.BR.*`):
    -   `S.BR.BLACK`, `S.BR.RED`, `S.BR.GREEN`, …
*   Standard background colors (`S.BG.*`):
    -   `S.BG.BLACK`, `S.BG.RED`, `S.BG.GREEN`, …
*   Bright background colors (`S.BG.BR.*`):
    -   `S.BG.BR.RED`, `S.BG.BR.GREEN`, …
*   24-bit true-color (foreground / background):
    -   `S.rgb(255, 96, 112)`
    -   `S.hex("#FF6070")`  or  `S.hex("F67")`
    -   `S.BG.rgb(0, 0, 0)`
    -   `S.BG.hex("#000")`
*   Hyperlinks (OSC 8):
    -   `S.link("https://example.com")("click here")`
    -   `(S.link("…") | S.BR.BLUE)("click here")`
*   Specific resets (only needed in advanced use; auto-reset usually covers it):
    -   `S.RESET_BOLD`, `S.RESET_DIM`, `S.RESET_ITALIC`, `S.RESET_UNDERLINE`,
        `S.RESET_INVERSE`, `S.RESET_HIDDEN`, `S.RESET_STRIKE`,
        `S.RESET_COLOR`, `S.RESET_BG`
*   Total reset (resets every previously applied styles):
    -   `S.RESET`


### Terminal Control – the `Term` class

`Term` exposes commonly used non-styling ANSI sequences for cursor- and screen-control.<br>
These are plain strings (or string-returning helpers), so they can be passed directly into a<br>
`StyledText(…)` call or written to `sys.stdout`:

*   `Term.CLEAR_LINE`       – Erase the entire current line.
*   `Term.CLEAR_SCREEN`     – Erase the whole screen.
*   `Term.HIDE_CURSOR`      – Hide the cursor.
*   `Term.SHOW_CURSOR`      – Show the cursor.
*   `Term.ALT_SCREEN`       – Enter the alternate screen buffer.
*   `Term.MAIN_SCREEN`      – Leave the alternate screen buffer.
*   `Term.up(n)`            – Move the cursor up by `n` rows.
*   `Term.down(n)`          – Move the cursor down by `n` rows.
*   `Term.right(n)`         – Move the cursor right by `n` columns.
*   `Term.left(n)`          – Move the cursor left by `n` columns.
*   `Term.move(row, col)`   – Move the cursor to an absolute `(row, col)` position.
*   `Term.title(text)`      – Set the terminal window / tab title (OSC 2).
*   `Term.save()`           – Save the current cursor position.
*   `Term.restore()`        – Restore the previously saved cursor position.

---

<!-- API: xulbux.ansi -->
