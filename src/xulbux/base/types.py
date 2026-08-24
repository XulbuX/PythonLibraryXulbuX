"""
Provides custom type definitions and TypeVars used throughout the library.

Includes type aliases for complex structures and protocol definitions.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, NotRequired, Protocol, TypedDict, cast, overload

if TYPE_CHECKING:
    from collections.abc import Iterable
    from sys import version_info as _vi
    from xulbux.ansi import Renderable

    if _vi >= (3, 13):
        from typing import TypeIs
    else:
        from typing_extensions import TypeIs


# ******************************************************** PRIMITIVES *********************************************************

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


# ************************************************** COLLECTIONS & ITERABLES **************************************************

type PathsList = list[Path] | list[str] | list[Path | str] | tuple[Path, ...] | tuple[str, ...] | tuple[Path | str, ...]
"""Union of all supported collection types for paths."""


def is_paths_list(obj: object, /) -> TypeIs[PathsList]:
    """Returns true if `obj` is an instance that matches the `PathsList` type."""

    if isinstance(obj, (list, tuple)):
        # Don't use `all()` as for-loop is more performant:
        for item in cast("list[Any] | tuple[Any, ...]", obj):  # ruff: ignore[reimplemented-builtin]
            if not isinstance(item, (Path, str)):
                return False
        return True

    return False


type DataObj = list[Any] | tuple[Any, ...] | set[Any] | frozenset[Any] | dict[Any, Any]
"""Union of supported data structures used in the `data` module."""


def is_data_obj(obj: object, /) -> TypeIs[DataObj]:
    """Returns true if `obj` is an instance that matches the `DataObj` type."""

    return isinstance(obj, (list, tuple, set, frozenset, dict))


type SeqOrSet[T] = list[T] | tuple[T, ...] | set[T] | frozenset[T]
"""Union of all built-in sequence and set types (`list`, `tuple`, `set`, `frozenset`)."""


@overload
def is_seq_or_set(obj: object, /) -> TypeIs[SeqOrSet[Any]]: ...
@overload
def is_seq_or_set[T](obj: object, item_type: type[T] | tuple[type[T], ...], /) -> TypeIs[SeqOrSet[T]]: ...
@overload
def is_seq_or_set(obj: object, item_type: None, /) -> TypeIs[SeqOrSet[Any]]: ...


def is_seq_or_set(obj: object, item_type: type[Any] | tuple[type[Any], ...] | None = None, /) -> bool:
    """Returns true if `obj` is an instance that matches the `SeqOrSet` type,<br>
    optionally checking if all contained elements are instances of `item_type`.\n
    ----------------------------------------------------------------------------------------------------
    *   `obj` – The object to check.
    *   `item_type` – An optional type or tuple of types to check each contained element against."""

    if not isinstance(obj, (list, tuple, set, frozenset)):
        return False
    elif item_type is None:
        return True

    # Don't use `all()` as for-loop is more performant:
    for item in cast("Iterable[Any]", obj):  # ruff: ignore[reimplemented-builtin]
        if not isinstance(item, item_type):
            return False

    return True


# ********************************************************** COLORS ***********************************************************


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
    """The red channel in range [0, 255] inclusive."""
    green: Int_0_255
    """The green channel in range [0, 255] inclusive."""
    blue: Int_0_255
    """The blue channel in range [0, 255] inclusive."""
    alpha: NotRequired[Float_0_1 | None]
    """The alpha channel in range [0.0, 1.0] inclusive or `None` if not set."""


class HslaDict(TypedDict):
    """Dictionary schema for HSLA color components."""

    hue: Int_0_360
    """The hue channel in range [0, 360] inclusive."""
    sat: Int_0_100
    """The saturation channel in range [0, 100] inclusive."""
    light: Int_0_100
    """The lightness channel in range [0, 100] inclusive."""
    alpha: NotRequired[Float_0_1 | None]
    """The alpha channel in range [0.0, 1.0] inclusive or `None` if not set."""


class HexaDict(TypedDict):
    """Dictionary schema for HEXA color components."""

    red: str
    """The red channel in range [0, 255] inclusive."""
    green: str
    """The green channel in range [0, 255] inclusive."""
    blue: str
    """The blue channel in range [0, 255] inclusive."""
    alpha: NotRequired[str | None]
    """The alpha channel in range [0.0, 1.0] inclusive or `None` if not set."""


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


# **************************************************** SYSTEM & UTILITIES *****************************************************


class AllTextChars:
    """Sentinel class indicating all characters are allowed."""

    ...


class MissingLibsMsgs(TypedDict):
    """Configuration schema for custom messages in `system.check_libs()` when checking library dependencies."""

    found_missing: str
    """Message to display when one or more libraries are missing."""
    should_install: str
    """Confirmation message to ask the user if they want to install the missing libraries."""


class ProgressUpdater(Protocol):
    """Protocol for a progress updater function used in terminal progress bars."""

    @overload
    def __call__(self, current: int) -> None:
        """Update the current progress value."""
        ...

    @overload
    def __call__(self, current: int, label: Renderable) -> None:
        """Update the current progress value and label."""
        ...

    @overload
    def __call__(self, *, label: Renderable) -> None:
        """Update the progress label only (keyword-only)."""

    def __call__(self, current: int | None = None, label: Renderable | None = None) -> None:
        """Update the current progress value and/or label."""
        ...
