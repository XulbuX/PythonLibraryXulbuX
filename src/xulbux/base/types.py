"""
Provides custom type definitions and TypeVars used throughout the library.

Includes type aliases for complex structures and protocol definitions.
"""

from pathlib import Path
from typing import TYPE_CHECKING, Any, Final, Literal, NotRequired, Protocol, TypedDict

if TYPE_CHECKING:
    from xulbux.ansi import TextLike

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

type PathsList = list[Path] | list[str] | list[Path | str]
"""Union of all supported list types for a list of paths."""

type DataObj = list[Any] | tuple[Any, ...] | set[Any] | frozenset[Any] | dict[Any, Any]
"""Union of supported data structures used in the `data` module."""

DATA_OBJ_TT: Final[
    tuple[type[list[Any]], type[tuple[Any, ...]], type[set[Any]], type[frozenset[Any]], type[dict[Any, Any]]]
] = (list, tuple, set, frozenset, dict)
"""Type tuple of supported data structures used in the `data` module."""

type IndexIterable = list[Any] | tuple[Any, ...] | set[Any] | frozenset[Any]
"""Union of all iterable types that support indexing operations."""

INDEX_ITERABLE_TT: Final[tuple[type[list[Any]], type[tuple[Any, ...]], type[set[Any]], type[frozenset[Any]]]] = (
    list,
    tuple,
    set,
    frozenset,
)
"""Type tuple of all iterable types that support indexing operations."""


######################################################### Colors #########################################################


class _RgbaObj(Protocol):
    """Protocol for rgba-like color objects (structurally matches `rgba`)."""

    red: int
    green: int
    blue: int
    alpha: float | None


class _HslaObj(Protocol):
    """Protocol for hsla-like color objects (structurally matches `hsla`)."""

    hue: int
    sat: int
    light: int
    alpha: float | None


class _HexaObj(Protocol):
    """Protocol for hexa-like color objects (structurally matches `hexa`)."""

    red: int
    green: int
    blue: int
    alpha: float | None


class RgbaDict(TypedDict):
    """Dictionary schema for RGBA color components."""

    red: Int_0_255
    green: Int_0_255
    blue: Int_0_255
    alpha: NotRequired[Float_0_1 | None]


class HslaDict(TypedDict):
    """Dictionary schema for HSLA color components."""

    hue: Int_0_360
    sat: Int_0_100
    light: Int_0_100
    alpha: NotRequired[Float_0_1 | None]


class HexaDict(TypedDict):
    """Dictionary schema for HEXA color components."""

    red: str
    green: str
    blue: str
    alpha: NotRequired[str | None]


type Rgba = (
    tuple[Int_0_255, Int_0_255, Int_0_255]
    | tuple[Int_0_255, Int_0_255, Int_0_255, Float_0_1 | None]
    | list[Int_0_255]
    | list[Int_0_255 | Float_0_1 | None]
    | RgbaDict
    | _RgbaObj
    | str
)
"""Matches all supported RGBA color value formats."""

type Hsla = (
    tuple[Int_0_360, Int_0_100, Int_0_100]
    | tuple[Int_0_360, Int_0_100, Int_0_100, Float_0_1 | None]
    | list[Int_0_360 | Int_0_100]
    | list[Int_0_360 | Int_0_100 | Float_0_1 | None]
    | HslaDict
    | _HslaObj
    | str
)
"""Matches all supported HSLA color value formats."""

type Hexa = str | int | _HexaObj
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
    flag: str | None


type ArgParseConfig = set[str] | ArgConfigWithDefault | Literal["before", "after"]
"""Matches the command-line-parsing configuration of a single argument."""
type ArgParseConfigs = dict[str, ArgParseConfig]
"""Matches the command-line-parsing configurations of multiple arguments, packed in a dictionary."""


################################################### System & Utilities ###################################################


class AllTextChars:
    """Sentinel class indicating all characters are allowed."""

    ...


class MissingLibsMsgs(TypedDict):
    """Configuration schema for custom messages in `system.check_libs()` when checking library dependencies."""

    found_missing: str
    should_install: str


class ProgressUpdater(Protocol):
    """Protocol for a progress updater function used in terminal progress bars."""

    def __call__(self, current: int | None = None, label: "TextLike | None" = None) -> None:
        """Update the current progress value and/or label."""
        ...
