# **$\color{#8085FF}\Huge\textsf{XulbuX}$**

**$\color{#8085FF}\textsf{XulbuX}$** is a library which includes a lot of really helpful classes, types and functions.

For precise information about the library, see the library's [Wiki page](https://github.com/XulbuX-dev/PythonLibraryXulbuX/wiki).<br>
For the libraries latest changes, see the [change log](https://github.com/XulbuX-dev/PythonLibraryXulbuX/blob/main/CHANGELOG.md).


## Installation

Open a console and run the command:
```css
pip install xulbux
```
This should install the latest version of the library, along with some other required libraries.<br>
To upgrade the library (*if there is a new release*) run the following command in your console:
```css
pip install --upgrade xulbux
```


## Usage

Import the full library under the alias `xx`, so it's classes, types and functions are accessible with `xx.Class.method()`, `xx.type()` and `xx.function()`:
```python
import xulbux as xx
```
So you don't have to write `xx` in front of the library's types, you can import them directly:
```python
from xulbux import rgba, hsla, hexa
```


The library **$\color{#8085FF}\textsf{XulbuX}$** (*below used as* `xx` *with above imported types*) contains the following modules:
```python
  • CUSTOM TYPES:
     • rgba(int,int,int,float)
     • hsla(int,int,int,float)
     • hexa(str)
  • PATH OPERATIONS          xx.Path
  • FILE OPERATIONS          xx.File
  • JSON FILE OPERATIONS     xx.Json
  • SYSTEM ACTIONS           xx.System
  • MANAGE THE ENV PATH VAR  xx.EnvPath
  • CONSOLE LOG AND ACTIONS  xx.Console
  • EASY PRETTY PRINTING     xx.FormatCodes
  • WORKING WITH COLORS      xx.Color
  • DATA OPERATIONS          xx.Data
  • STRING OPERATIONS        xx.String
  • CODE STRING OPERATIONS   xx.Code
  • REGEX PATTERN TEMPLATES  xx.Regex
```


<br>

--------------------------------------------------------------
[View this library on PyPI](https://pypi.org/project/XulbuX/)
