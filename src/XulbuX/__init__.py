"""
 >>> import XulbuX as xx
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  • CUSTOM TYPES:
     • rgba(int,int,int,float)
     • hsla(int,int,int,float)
     • hexa(str)
  • PATH OPERATIONS          xx.Path
  • FILE OPERATIONS          xx.File
  • JSON FILE OPERATIONS     xx.Json
  • SYSTEM ACTIONS           xx.System
  • MANAGE ENVIRONMENT VARS  xx.EnvVars
  • CMD LOG AND ACTIONS      xx.Cmd
  • PRETTY PRINTING          xx.FormatCodes
  • COLOR OPERATIONS         xx.Color
  • DATA OPERATIONS          xx.Data
  • STR OPERATIONS           xx.String
  • CODE STRING OPERATIONS   xx.Code
  • REGEX PATTERN TEMPLATES  xx.Regex
"""

__version__ = '1.5.6'
__author__ = 'XulbuX'
__email__ = 'xulbux.real@gmail.com'
__license__ = 'MIT'
__copyright__ = 'Copyright (c) 2024 XulbuX'
__url__ = 'https://github.com/XulbuX-dev/Python/tree/main/Libraries/XulbuX'
__description__ = 'A library which includes a lot of really helpful functions.'
__all__ = [
    '__help__', '_consts_', 'xx_cmd', 'xx_code', 'xx_color', 'xx_data', 'xx_env_vars', 'xx_file',
    'xx_format_codes', 'xx_json', 'xx_path', 'xx_regex', 'xx_string', 'xx_system'
]

from src.XulbuX.__help__ import help
from src.XulbuX._consts_ import *
from src.XulbuX.xx_cmd import *
from src.XulbuX.xx_code import *
from src.XulbuX.xx_color import *
from src.XulbuX.xx_data import *
from src.XulbuX.xx_env_vars import *
from src.XulbuX.xx_file import *
from src.XulbuX.xx_format_codes import *
from src.XulbuX.xx_json import *
from src.XulbuX.xx_path import *
from src.XulbuX.xx_regex import *
from src.XulbuX.xx_string import *
from src.XulbuX.xx_system import *
