"""
Provides custom type definitions and TypeVars used throughout the library.

Includes type aliases for complex structures and protocol definitions.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, NotRequired, Protocol, TypedDict, cast

if TYPE_CHECKING:
    import sys
    from xulbux.ansi import Renderable

    if sys.version_info >= (3, 13):
        from typing import TypeIs
    else:
        from typing_extensions import TypeIs


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


def is_paths_list(obj: object, /) -> TypeIs[PathsList]:
    """Returns true if `obj` is an instance that matches the `PathsList` type."""

    return isinstance(obj, list) and all(isinstance(item, (Path, str)) for item in cast("list[Any]", obj))


type DataObj = list[Any] | tuple[Any, ...] | set[Any] | frozenset[Any] | dict[Any, Any]
"""Union of supported data structures used in the `data` module."""


def is_data_obj(obj: object, /) -> TypeIs[DataObj]:
    """Returns true if `obj` is an instance that matches the `DataObj` type."""

    return isinstance(obj, (list, tuple, set, frozenset, dict))


type IndexIterable = list[Any] | tuple[Any, ...] | set[Any] | frozenset[Any]
"""Union of all iterable types that support indexing operations."""


def is_index_iterable(obj: object, /) -> TypeIs[IndexIterable]:
    """Returns true if `obj` is an instance that matches the `IndexIterable` type."""

    return isinstance(obj, (list, tuple, set, frozenset))


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

    def __call__(self, current: int | None = None, label: Renderable | None = None) -> None:
        """Update the current progress value and/or label."""
        ...
