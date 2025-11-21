"""
This module contains all custom type definitions used throughout the library.
"""

from typing import TYPE_CHECKING, Annotated, TypeAlias, TypedDict, Optional, Union, Any
import regex as _rx
import re as _re

# PREVENT CIRCULAR IMPORTS
if TYPE_CHECKING:
    from ..color import rgba, hsla, hexa

#
################################################## Annotated ##################################################

Int_0_100 = Annotated[int, "Integer constrained to the range [0, 100] inclusive."]
"""Integer constrained to the range [0, 100] inclusive."""
Int_0_255 = Annotated[int, "Integer constrained to the range [0, 255] inclusive."]
"""Integer constrained to the range [0, 255] inclusive."""
Int_0_360 = Annotated[int, "Integer constrained to the range [0, 360] inclusive."]
"""Integer constrained to the range [0, 360] inclusive."""
Float_0_1 = Annotated[float, "Float constrained to the range [0.0, 1.0] inclusive."]
"""Float constrained to the range [0.0, 1.0] inclusive."""

FormattableString = Annotated[str, "String made to be formatted with the `.format()` method."]
"""String made to be formatted with the `.format()` method."""

#
################################################## TypeAlias ##################################################

Pattern: TypeAlias = _re.Pattern[str] | _rx.Pattern[str]
"""Matches compiled regex patterns from both the `re` and `regex` libraries."""
Match: TypeAlias = _re.Match[str] | _rx.Match[str]
"""Matches regex match objects from both the `re` and `regex` libraries."""

DataStructure: TypeAlias = Union[list, tuple, set, frozenset, dict]
"""Union of supported data structures used in the `data` module."""
IndexIterable: TypeAlias = Union[list, tuple, set, frozenset]
"""Union of all iterable types that support indexing operations."""

Rgba: TypeAlias = Union[
    tuple[Int_0_255, Int_0_255, Int_0_255],
    tuple[Int_0_255, Int_0_255, Int_0_255, Float_0_1],
    list[Int_0_255],
    list[Union[Int_0_255, Float_0_1]],
    dict[str, Union[int, float]],
    "rgba",
    str,
]
"""Matches all supported RGBA color value formats."""
Hsla: TypeAlias = Union[
    tuple[Int_0_360, Int_0_100, Int_0_100],
    tuple[Int_0_360, Int_0_100, Int_0_100, Float_0_1],
    list[Union[Int_0_360, Int_0_100]],
    list[Union[Int_0_360, Int_0_100, Float_0_1]],
    dict[str, Union[int, float]],
    "hsla",
    str,
]
"""Matches all supported HSLA color value formats."""
Hexa: TypeAlias = Union[str, int, "hexa"]
"""Matches all supported hexadecimal color value formats."""

AnyRgba: TypeAlias = Any
"""Generic type alias for RGBA color values in any supported format (type checking disabled)."""
AnyHsla: TypeAlias = Any
"""Generic type alias for HSLA color values in any supported format (type checking disabled)."""
AnyHexa: TypeAlias = Any
"""Generic type alias for hexadecimal color values in any supported format (type checking disabled)."""

#
################################################## Sentinel ##################################################


class AllTextChars:
    """Sentinel class indicating all characters are allowed."""
    ...


#
################################################## TypedDict ##################################################


class ArgConfigWithDefault(TypedDict):
    """Configuration schema for a flagged CLI argument that has a specified default value."""
    flags: set[str]
    default: str


class ArgResultRegular(TypedDict):
    """Result schema for a parsed regular flagged CLI argument."""
    exists: bool
    value: Optional[str]


class ArgResultPositional(TypedDict):
    """Result schema for parsed positional (`"before"`/`"after"`) CLI arguments."""
    exists: bool
    values: list[str]


class MissingLibsMsgs(TypedDict):
    """Configuration schema for custom messages in `System.check_libs()` when checking library dependencies."""
    found_missing: str
    should_install: str
