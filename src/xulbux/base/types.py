"""
This module contains all custom type definitions used throughout the library.
"""

from typing import TypedDict, Optional, Protocol, Literal, Union, Any
from pathlib import Path

# fmt: OFF


####################################################### Primitives #######################################################

type Int_0_100 = int
"""Integer constrained to the range [0, 100] inclusive."""
type Int_0_255 = int
"""Integer constrained to the range [0, 255] inclusive."""
type Int_0_360 = int
"""Integer constrained to the range [0, 360] inclusive."""
type Float_0_1 = float
"""Float constrained to the range [0.0, 1.0] inclusive."""

type FormattableString = str
"""String made to be formatted with the `.format()` method."""


################################################# Collections & Iterables ################################################

type PathsList = Union[list[Path], list[str], list[Union[Path, str]]]
"""Union of all supported list types for a list of paths."""

type DataObj = Union[list[Any], tuple[Any, ...], set[Any], frozenset[Any], dict[Any, Any]]
"""Union of supported data structures used in the `data` module."""

DataObjTT: tuple[
    type[list[Any]],
    type[tuple[Any, ...]],
    type[set[Any]],
    type[frozenset[Any]],
    type[dict[Any, Any]],
] = (list, tuple, set, frozenset, dict)
"""Tuple of supported data structures used in the `data` module."""

type IndexIterable = Union[list[Any], tuple[Any, ...], set[Any], frozenset[Any]]
"""Union of all iterable types that support indexing operations."""

IndexIterableTT: tuple[
    type[list[Any]],
    type[tuple[Any, ...]],
    type[set[Any]],
    type[frozenset[Any]],
] = (list, tuple, set, frozenset)
"""Tuple of all iterable types that support indexing operations."""


######################################################### Colors #########################################################

class _RgbaObj(Protocol):
    """Protocol for rgba-like color objects (structurally matches `rgba`)."""
    red: int
    green: int
    blue: int
    alpha: Optional[float]

class _HslaObj(Protocol):
    """Protocol for hsla-like color objects (structurally matches `hsla`)."""
    hue: int
    sat: int
    light: int
    alpha: Optional[float]

class _HexaObj(Protocol):
    """Protocol for hexa-like color objects (structurally matches `hexa`)."""
    red: int
    green: int
    blue: int
    alpha: Optional[float]

class RgbaDict(TypedDict):
    """Dictionary schema for RGBA color components."""
    red: Int_0_255
    green: Int_0_255
    blue: Int_0_255
    alpha: Optional[Float_0_1]

class HslaDict(TypedDict):
    """Dictionary schema for HSLA color components."""
    hue: Int_0_360
    sat: Int_0_100
    light: Int_0_100
    alpha: Optional[Float_0_1]

class HexaDict(TypedDict):
    """Dictionary schema for HEXA color components."""
    red: str
    green: str
    blue: str
    alpha: Optional[str]

type Rgba = Union[
    tuple[Int_0_255, Int_0_255, Int_0_255],
    tuple[Int_0_255, Int_0_255, Int_0_255, Optional[Float_0_1]],
    list[Int_0_255],
    list[Union[Int_0_255, Optional[Float_0_1]]],
    RgbaDict,
    _RgbaObj,
    str,
]
"""Matches all supported RGBA color value formats."""

type Hsla = Union[
    tuple[Int_0_360, Int_0_100, Int_0_100],
    tuple[Int_0_360, Int_0_100, Int_0_100, Optional[Float_0_1]],
    list[Union[Int_0_360, Int_0_100]],
    list[Union[Int_0_360, Int_0_100, Optional[Float_0_1]]],
    HslaDict,
    _HslaObj,
    str,
]
"""Matches all supported HSLA color value formats."""

type Hexa = Union[str, int, _HexaObj]
"""Matches all supported HEXA color value formats."""

type AnyRgba = Any
"""Generic type alias for RGBA color values in any format (type checking disabled)."""
type AnyHsla = Any
"""Generic type alias for HSLA color values in any format (type checking disabled)."""
type AnyHexa = Any
"""Generic type alias for HEXA color values in any format (type checking disabled)."""


###################################################### CLI Arguments #####################################################

class ArgConfigWithDefault(TypedDict):
    """Configuration schema for a flagged command-line argument that has a specified default value."""
    flags: set[str]
    default: str

class ArgData(TypedDict):
    """Schema for the resulting data of parsing a single command-line argument."""
    exists: bool
    is_pos: bool
    values: tuple[str, ...]
    flag: Optional[str]

type ArgParseConfig = Union[set[str], ArgConfigWithDefault, Literal["before", "after"]]
"""Matches the command-line-parsing configuration of a single argument."""
type ArgParseConfigs = dict[str, ArgParseConfig]
"""Matches the command-line-parsing configurations of multiple arguments, packed in a dictionary."""


################################################### System & Utilities ###################################################

class AllTextChars:
    """Sentinel class indicating all characters are allowed."""
    ...

class MissingLibsMsgs(TypedDict):
    """Configuration schema for custom messages in `System.check_libs()` when checking library dependencies."""
    found_missing: str
    should_install: str

class ProgressUpdater(Protocol):
    """Protocol for a progress updater function used in terminal progress bars."""

    def __call__(self, current: Optional[int] = None, label: Optional[str] = None) -> None:
        """Update the current progress value and/or label."""
        ...
