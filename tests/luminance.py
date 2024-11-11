from XulbuX import Color, rgba, hsla, hexa

import math as _math



@staticmethod
def luminance(r:int, g:int, b:int, output_type:type = None) -> int|float:
    """Gets the colors luminance using the luminance formula.\n
    ------------------------------------------------------------
    The param `output_type` can be set to:<br>
    *`int`*   =⠀integer in [0, 100]<br>
    *`float`* =⠀float in [0.0, 1.0]<br>
    `None`    =⠀integer in [0, 255]"""
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    if r < 0.03928: r = r / 12.92
    else: r = ((r + 0.055) / 1.055) ** 2.4
    if g < 0.03928: g = g / 12.92
    else: g = ((g + 0.055) / 1.055) ** 2.4
    if b < 0.03928: b = b / 12.92
    else: b = ((b + 0.055) / 1.055) ** 2.4
    l = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return round(l * 100) if isinstance(output_type, int) else round(l * 255) if output_type is None else l



print(f'luminance((0, 0, 0)):        {luminance(0, 0, 0)}')
print(f'luminance((255, 255, 255)):  {luminance(255, 255, 255)}')
print(f'luminance((255, 0, 0)):      {luminance(255, 0, 0)}')
print(f'luminance((0, 255, 0)):      {luminance(0, 255, 0)}')
print(f'luminance((0, 0, 255)):      {luminance(0, 0, 255)}')
print(f'luminance((255, 255, 0)):    {luminance(255, 255, 0)}')
print(f'luminance((255, 0, 255)):    {luminance(255, 0, 255)}')
print(f'luminance((0, 255, 255)):    {luminance(0, 255, 255)}')
print(f'luminance((128, 128, 128)):  {luminance(128, 128, 128)}')
