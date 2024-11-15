<br>

**$\color{#8085FF}\Huge\textsf{XulbuX}$**

-------------------------------------------------------------

**$\color{#8085FF}\textsf{XulbuX}$** is a library which includes a lot of really helpful classes, types and functions.<br>
For the libraries latest changes, see the [change log](https://github.com/XulbuX-dev/Python/blob/main/Libraries/XulbuX/CHANGELOG.md).

<br>

# Installation

Open a console and run the command:
```css
pip install XulbuX
```
This should install the latest version of the library, along with some other required libraries.<br>
To upgrade the library (*if there is a new release*) run the following command in your console:
```css
pip install --upgrade XulbuX
```

<br>

# Usage

This imports the full library under the alias `xx`, so it"s classes, types and functions are accessible with `xx.Class.method()`, `xx.type()` and `xx.function()`:
```python
import XulbuX as xx
```
So you don"t have to write `xx` in front of the library"s types, you can import them directly:
```python
from XulbuX import rgba, hsla, hexa
```

<br>

# Modules

- [xx_color](xx_color.md)
- [xx_cmd](xx_cmd.md)
- [xx_code](xx_code.md)


<br>

### `String.normalize_spaces()`

This function will replace all special space characters with normal spaces.<br>
**Params:**
- <code>code: *str*</code> the string to normalize
- <code>tab_spaces: *int*</code> the amount of spaces to replace tab characters with (*default* `4`)

**Returns:** the normalized string
<br>



<br id="bottom">
<br>

--------------------------------------------------------------
[View this library on PyPI](https://pypi.org/project/XulbuX/)

<div style="width:45px; height:45px; right:10px; position:absolute">
  <a href="#top"><abbr title="go to top" style="text-decoration:none">
    <div style="
      font-size: 2em;
      font-weight: bold;
      background: #88889845;
      border-radius: 0.2em;
      text-align: center;
      justify-content: center;
    "><span style="display:none">go to top </span>🠩</div>
  </abbr></a>
</div>
